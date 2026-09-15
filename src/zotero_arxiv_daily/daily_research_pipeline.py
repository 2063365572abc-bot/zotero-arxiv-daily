from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Any

from loguru import logger
from omegaconf import DictConfig, OmegaConf
from openai import OpenAI
import pymupdf
import requests

from .executor import Executor
from .protocol import Paper, _request_llm


CARD_SECTIONS = [
    "01 基本信息",
    "02 一句话总结",
    "03 研究问题",
    "04 研究背景与发展路径",
    "05 论文识别的核心痛点",
    "06 核心思想",
    "07 方法总览",
    "08 核心模块拆解",
    "09 关键公式与符号",
    "10 实验设计与证据链",
    "11 对结论的正确理解",
    "12 作者明确承认的限制",
    "13 批判性分析",
    "14 学到的知识",
    "15 与既有知识的连接",
    "16 研究想法",
]

CARD_SECTION_MAP = {
    "01 基本信息": "basic_information",
    "02 一句话总结": "one_sentence_summary",
    "03 研究问题": "research_question",
    "04 研究背景与发展路径": "background_path",
    "05 论文识别的核心痛点": "pain_points",
    "06 核心思想": "core_idea",
    "07 方法总览": "method_overview",
    "08 核心模块拆解": "module_breakdown",
    "09 关键公式与符号": "formulas_and_symbols",
    "10 实验设计与证据链": "experiment_evidence_chain",
    "11 对结论的正确理解": "conclusion_boundaries",
    "12 作者明确承认的限制": "author_limitations",
    "13 批判性分析": "critical_analysis",
    "14 学到的知识": "learned_knowledge",
    "15 与既有知识的连接": "knowledge_connections",
    "16 研究想法": "research_ideas",
}


@dataclass
class CandidateRecord:
    source: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    pdf_url: str | None
    published_date: str | None
    categories: list[str]
    raw_score: float | None


@dataclass
class SelectionRecord:
    source: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    pdf_url: str | None
    score: float | None
    role: str
    scoring: dict[str, Any]
    selection_reason: str


def daily_output_dir(root: str | Path = "outputs/daily", date: datetime | None = None) -> Path:
    date = date or datetime.now()
    return Path(root) / date.strftime("%Y-%m-%d")


def write_json(path: str | Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def paper_to_candidate(paper: Paper) -> CandidateRecord:
    return CandidateRecord(
        source=paper.source,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        url=paper.url,
        pdf_url=paper.pdf_url,
        published_date=None,
        categories=[],
        raw_score=paper.score,
    )


def write_candidates(papers: list[Paper], output_dir: str | Path, limit: int = 20) -> Path:
    records = [asdict(paper_to_candidate(paper)) for paper in papers[:limit]]
    path = Path(output_dir) / "candidates.json"
    write_json(path, records)
    return path


def _selection_scoring(paper: Paper, role: str, llm_score: dict[str, Any] | None = None) -> dict[str, Any]:
    base_score = float(paper.score or 0.0)
    if llm_score:
        return {
            "relevance": llm_score["relevance_to_user"],
            "method_novelty": llm_score["method_novelty"],
            "evidence_quality": llm_score["evidence_quality"],
            "transferability": llm_score["transferability"],
            "resource_value": llm_score["resource_value"],
            "trend_value": llm_score["trend_value"],
            "total": llm_score["total"],
            "role": role,
            "needs_llm_scoring": False,
        }
    return {
        "relevance": min(30, round(base_score * 3, 2)),
        "method_novelty": None,
        "evidence_quality": None,
        "transferability": None,
        "resource_value": 10 if paper.pdf_url else 0,
        "trend_value": None,
        "total": round(base_score, 3),
        "role": role,
        "needs_llm_scoring": True,
    }


def select_papers_for_deep_read(
    papers: list[Paper],
    count: int = 3,
    llm_scores: dict[str, dict[str, Any]] | None = None,
) -> list[SelectionRecord]:
    roles = ["best_match", "method_inspiration", "trend_signal"]
    ranked = sorted(papers, key=lambda paper: paper.score if paper.score is not None else -1, reverse=True)
    if llm_scores:
        remaining = list(ranked)
        role_fields = {
            "best_match": "relevance_to_user",
            "method_inspiration": "method_novelty",
            "trend_signal": "trend_value",
        }
        role_selected: list[Paper] = []
        for role in roles[:count]:
            available = [paper for paper in remaining if paper.title in llm_scores]
            if not available:
                break
            field = role_fields[role]
            chosen = max(available, key=lambda paper: llm_scores[paper.title][field])
            role_selected.append(chosen)
            remaining.remove(chosen)
        ranked = role_selected + [paper for paper in ranked if paper not in role_selected]
    selected = []
    for index, paper in enumerate(ranked[:count]):
        role = roles[index] if index < len(roles) else "best_match"
        llm_score = (llm_scores or {}).get(paper.title)
        scoring = _selection_scoring(paper, role, llm_score)
        selected.append(
            SelectionRecord(
                source=paper.source,
                title=paper.title,
                authors=paper.authors,
                abstract=paper.abstract,
                url=paper.url,
                pdf_url=paper.pdf_url,
                score=paper.score,
                role=role,
                scoring=scoring,
                selection_reason=(
                    f"Selected as {role}; LLM total={llm_score['total']:.1f}/100. "
                    f"{llm_score['reason']}"
                    if llm_score is not None
                    else f"Selected as {role}; embedding score={paper.score:.3f}."
                ),
            )
        )
    return selected


def build_llm_selection_prompt(papers: list[Paper], llm_params: dict[str, Any]) -> str:
    profile = llm_params.get("research_profile") or (
        "single-cell foundation models, spatial transcriptomics, graph neural networks, "
        "multi-omics, biomedical AI, perturbation prediction, cell-state representation, "
        "and cross-modal alignment"
    )
    paper_blocks = []
    for index, paper in enumerate(papers, start=1):
        paper_blocks.append(
            f"PAPER {index}\nTitle: {paper.title}\nAbstract: {paper.abstract}\n"
            f"Source: {paper.source}\nURL: {paper.url}"
        )
    return f"""
你是用户的科研选题筛选助手。你的任务不是判断论文标题是否热门，而是从候选论文中找出最适合用户投入阅读时间的内容。

用户研究画像：
{profile}

只允许依据下面提供的标题、摘要和元数据评分。不要假设你看过论文 PDF，不要补写摘要中不存在的实验结果。
请为每篇论文给出 0-10 分的：
- relevance_to_user：与用户当前研究的直接相关性
- method_novelty：方法、任务或建模范式的新颖性
- evidence_quality：摘要中可见的证据强度；信息不足时降低分数
- transferability：迁移到用户研究问题的可能性
- trend_value：作为当前研究趋势信号的价值
- resource_value：摘要或元数据中明确出现的数据、代码、模型或资源价值

请只返回 JSON，格式必须是：
{{"rankings":[{{"paper_index":1,"relevance_to_user":0,"method_novelty":0,"evidence_quality":0,"transferability":0,"trend_value":0,"resource_value":0,"best_role":"best_match|method_inspiration|trend_signal","reason":"中文理由","risk":"中文风险"}}]}}

候选论文：
{chr(10).join(paper_blocks)}
""".strip()


def rank_candidates_with_llm(
    papers: list[Paper],
    openai_client: OpenAI,
    llm_params: dict[str, Any],
) -> tuple[list[Paper], dict[str, dict[str, Any]]]:
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs["max_tokens"] = min(max(int(generation_kwargs.get("max_tokens") or 0), 1200), 3000)
    params = {**llm_params, "generation_kwargs": generation_kwargs}
    content = _request_llm(
        openai_client,
        params,
        [
            {"role": "system", "content": "你是严谨的科研文献筛选器，只返回合法 JSON。"},
            {"role": "user", "content": build_llm_selection_prompt(papers, llm_params)},
        ],
        force_json=True,
    )
    payload = _json_from_llm_content(content)
    raw_rankings = payload.get("rankings")
    if not isinstance(raw_rankings, list):
        raise ValueError("LLM selection response has no rankings list")

    weights = {
        "relevance_to_user": 30,
        "method_novelty": 20,
        "evidence_quality": 20,
        "transferability": 15,
        "trend_value": 10,
        "resource_value": 5,
    }
    scores: dict[str, dict[str, Any]] = {}
    for item in raw_rankings:
        if not isinstance(item, dict):
            continue
        try:
            paper = papers[int(item["paper_index"]) - 1]
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        values = {field: max(0.0, min(10.0, float(item.get(field, 0)))) for field in weights}
        total = sum(values[field] * weight / 10 for field, weight in weights.items())
        scores[paper.title] = {
            **values,
            "total": round(total, 2),
            "best_role": str(item.get("best_role") or "best_match"),
            "reason": str(item.get("reason") or "未提供筛选理由"),
            "risk": str(item.get("risk") or "未提供风险说明"),
        }
    if len(scores) < len(papers):
        raise ValueError(f"LLM selection returned {len(scores)} of {len(papers)} candidates")
    ranked = sorted(papers, key=lambda paper: scores[paper.title]["total"], reverse=True)
    for paper in ranked:
        paper.score = scores[paper.title]["total"]
    return ranked, scores


def write_llm_ranking(papers: list[Paper], scores: dict[str, dict[str, Any]], output_dir: str | Path) -> Path:
    payload = []
    for rank, paper in enumerate(papers, start=1):
        payload.append({"rank": rank, "title": paper.title, "url": paper.url, **scores[paper.title]})
    path = Path(output_dir) / "llm_ranking.json"
    write_json(path, payload)
    return path


def write_selected_papers(selected: list[SelectionRecord], output_dir: str | Path) -> Path:
    path = Path(output_dir) / "selected_papers.json"
    write_json(path, [asdict(record) for record in selected])
    return path


def safe_folder_name(text: str, fallback: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return (cleaned[:120] or fallback).strip()


def paper_folder(output_dir: str | Path, index: int, title: str) -> Path:
    suffix = safe_folder_name(title, f"paper-{index}")
    return Path(output_dir) / f"paper-{index}" / suffix


def _file_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_pdf(path: str | Path, min_bytes: int = 50 * 1024) -> tuple[bool, str | None]:
    path = Path(path)
    if not path.exists():
        return False, "pdf_missing"
    if path.stat().st_size < min_bytes:
        return False, "pdf_too_small"
    with path.open("rb") as handle:
        if handle.read(4) != b"%PDF":
            return False, "not_pdf_header"
    try:
        doc = pymupdf.open(path)
        if doc.page_count < 1:
            return False, "pdf_has_no_pages"
    except Exception as exc:
        return False, f"pdf_open_failed: {exc}"
    return True, None


def download_pdf(pdf_url: str | None, output_pdf: str | Path, timeout: int = 60) -> dict[str, Any]:
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    metadata: dict[str, Any] = {
        "pdf_url": pdf_url,
        "download_status": "failed",
        "failure_reason": None,
        "sha256": None,
        "bytes": 0,
    }
    if not pdf_url:
        metadata["failure_reason"] = "missing_pdf_url"
        return metadata

    try:
        with requests.get(pdf_url, stream=True, timeout=(10, timeout)) as response:
            response.raise_for_status()
            with output_pdf.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
    except Exception as exc:
        metadata["failure_reason"] = f"download_error: {exc}"
        return metadata

    ok, reason = validate_pdf(output_pdf)
    if not ok:
        metadata["failure_reason"] = reason
        return metadata

    metadata["download_status"] = "downloaded"
    metadata["failure_reason"] = None
    metadata["sha256"] = _file_sha256(output_pdf)
    metadata["bytes"] = output_pdf.stat().st_size
    return metadata


def extract_source_bundle(pdf_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    pdf_path = Path(pdf_path)
    doc = pymupdf.open(pdf_path)
    pages = []
    for page_index, page in enumerate(doc, start=1):
        pages.append(
            {
                "page": page_index,
                "text": page.get_text().strip(),
                "blocks": [],
            }
        )
    bundle = {
        "pdf_sha256": _file_sha256(pdf_path),
        "page_count": doc.page_count,
        "pages": pages,
        "sections": [],
        "figures": [],
        "tables": [],
    }
    write_json(output_path, bundle)
    return bundle


def _first_non_empty_page(bundle: dict[str, Any]) -> int | None:
    for page in bundle.get("pages", []):
        if page.get("text"):
            return int(page["page"])
    return None


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _page_texts_for_llm(bundle: dict[str, Any], max_chars: int = 1500) -> tuple[str, list[str]]:
    pages = bundle.get("pages", [])
    if not pages:
        return "", ["source_bundle"]

    keyword_pattern = re.compile(
        r"\b(abstract|introduction|background|method|methods|approach|model|experiment|"
        r"experiments|evaluation|result|results|discussion|limitation|limitations|conclusion|"
        r"figure|table|equation|ablation|dataset|benchmark)\b",
        flags=re.IGNORECASE,
    )
    selected_indices: list[int] = []
    selected_indices.extend(range(min(4, len(pages))))
    selected_indices.extend(index for index, page in enumerate(pages) if keyword_pattern.search(page.get("text", "")[:1200]))
    if len(pages) > 4:
        selected_indices.extend(range(max(0, len(pages) - 3), len(pages)))

    seen: set[int] = set()
    chunks: list[str] = []
    refs: list[str] = []
    total = 0
    for index in selected_indices:
        if index in seen or index < 0 or index >= len(pages):
            continue
        seen.add(index)
        page = pages[index]
        text = _clean_text(page.get("text", ""))
        if not text:
            continue
        page_no = int(page.get("page") or index + 1)
        snippet = text[:900]
        block = f"[Paper: PDF p. {page_no}]\n{snippet}"
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining < 300:
                break
            block = block[:remaining]
        chunks.append(block)
        refs.append(f"[Paper: PDF p. {page_no}]")
        total += len(block)
        if total >= max_chars:
            break
    return "\n\n".join(chunks), refs or ["source_bundle"]


def _source_text_for_full_card(bundle: dict[str, Any], max_chars: int = 55_000) -> str:
    chunks: list[str] = []
    total = 0
    for page in bundle.get("pages", []):
        text = _clean_text(page.get("text", ""))
        if not text:
            continue
        page_no = int(page.get("page") or len(chunks) + 1)
        block = f"[Paper: PDF p. {page_no}]\n{text}\n"
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining > 1000:
                chunks.append(block[:remaining])
            break
        chunks.append(block)
        total += len(block)
    return "\n".join(chunks)


def _json_from_llm_content(content: str) -> dict[str, Any]:
    """Parse common Qwen/OpenAI-compatible JSON response variants."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM returned empty content")

    candidates = [content.strip()]
    for match in re.finditer(r"```(?:json)?\s*(.*?)\s*```", content, flags=re.DOTALL | re.IGNORECASE):
        candidates.insert(0, match.group(1).strip())

    # Some reasoning models add a short preamble or return an array directly.
    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            parsed = None
            for start, char in enumerate(candidate):
                if char not in "[{":
                    continue
                try:
                    parsed, _ = decoder.raw_decode(candidate[start:])
                    break
                except json.JSONDecodeError:
                    continue
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"rankings": parsed}
    preview = re.sub(r"\s+", " ", content).strip()[:300]
    raise ValueError(f"LLM did not return parseable JSON; preview={preview!r}")


def _normalise_card_sections(raw_sections: Any) -> dict[str, str]:
    if not isinstance(raw_sections, dict):
        raw_sections = {}
    sections: dict[str, str] = {}
    for section, key in CARD_SECTION_MAP.items():
        value = raw_sections.get(section)
        if value is None:
            value = raw_sections.get(key)
        if value is None:
            value = "Not assessable from supplied material."
        sections[section] = str(value).strip() or "Not assessable from supplied material."
    return sections


def build_one_shot_full_card_prompt(paper: SelectionRecord, bundle: dict[str, Any], max_input_chars: int = 55_000) -> str:
    source_text = _source_text_for_full_card(bundle, max_chars=max_input_chars)
    return f"""
你正在执行用户的“一多科研”单篇论文深读流程。请一次性输出一个完整的 Paper Card Markdown。

硬性要求：
- 只输出 Markdown，不要解释你将如何做。
- 中文解释，保留英文技术名词、模型名、数据集名、指标、公式符号。
- 不要夸大，不要伪造。
- 每个实质性论文事实都带来源指针，例如 [Paper: PDF p. 1]。
- 你的判断用 [Analysis]，研究想法用 [Hypothesis]。
- 不足以判断就写 Not assessable from supplied material。
- 作者明确限制和你的批判性分析分开。

开头必须包含：
> Source coverage: Full paper / Partial paper
> Extraction confidence: High / Mixed / Low
> Locator mode: page-grounded
> Primary analytical lens: methods/discovery/resource/clinical/materials/review
> Secondary analytical lens: None / ...
> Context verification: Paper-only
> Card completeness: Complete relative to supplied source / Partial

必须严格输出以下 16 节，顺序不能变：
## 01 基本信息
## 02 一句话总结
## 03 研究问题
## 04 研究背景与发展路径
## 05 论文识别的核心痛点
## 06 核心思想
## 07 方法总览
## 08 核心模块拆解
## 09 关键公式与符号
## 10 实验设计与证据链
## 11 对结论的正确理解
## 12 作者明确承认的限制
## 13 批判性分析
## 14 学到的知识
## 15 与既有知识的连接
## 16 研究想法

其中：
- 05 用表格：Pain point | Manifestation | Cause or author explanation | Evidence from the paper
- 08 用表格：Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal
- 10 用表格：Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source
- 12 用表格：Limitation | Specific manifestation | Future direction proposed by authors | Source
- 13 用表格：[Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis
- 16 每个 idea 包含：name、originating limitation/observation、core hypothesis、delta from paper、initial method、validation、failure modes、innovation status: unverified。

用户研究方向连接：single-cell foundation models、spatial transcriptomics、graph neural networks、multi-omics、biomedical AI、perturbation prediction、cell state representation、cross-modal alignment。没有直接关系时说明“弱连接/方法论连接”。

论文元数据：
Title: {paper.title}
Source: {paper.source}
URL: {paper.url}
PDF URL: {paper.pdf_url or "missing"}
Authors: {", ".join(paper.authors[:12])}
Abstract: {paper.abstract}
Selection role: {paper.role}
Selection reason: {paper.selection_reason}

论文全文摘录，已带 PDF 页码指针：
{source_text}
"""


def generate_one_shot_full_card_markdown(
    paper: SelectionRecord,
    bundle: dict[str, Any],
    output_path: str | Path,
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    max_input_chars: int = 55_000,
    max_output_tokens: int = 12_000,
) -> dict[str, Any]:
    prompt = build_one_shot_full_card_prompt(paper, bundle, max_input_chars=max_input_chars)
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs["max_tokens"] = max(int(generation_kwargs.get("max_tokens") or 0), max_output_tokens)
    generation_kwargs.setdefault("temperature", 0.2)
    generation_kwargs["stream"] = True

    logger.info(
        f"Streaming one-shot full Paper Card: title={paper.title} "
        f"prompt_chars={len(prompt)} max_output_tokens={generation_kwargs['max_tokens']}"
    )
    stream = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a rigorous source-grounded scientific paper reading assistant. Output only Markdown.",
            },
            {"role": "user", "content": prompt},
        ],
        **generation_kwargs,
    )
    parts: list[str] = []
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = getattr(chunk.choices[0], "delta", None)
        content = getattr(delta, "content", None) if delta is not None else None
        if content:
            parts.append(content)

    markdown = "".join(parts).strip()
    if not markdown:
        raise ValueError("LLM stream returned empty Paper Card")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    logger.info(f"One-shot full Paper Card written: title={paper.title} chars={len(markdown)}")
    return {
        "status": "one_shot_full_card",
        "prompt_chars": len(prompt),
        "card_chars": len(markdown),
        "model": generation_kwargs.get("model"),
        "max_input_chars": max_input_chars,
        "max_output_tokens": generation_kwargs["max_tokens"],
    }


def initial_paper_analysis(paper: SelectionRecord, bundle: dict[str, Any]) -> dict[str, Any]:
    page_ref = _first_non_empty_page(bundle)
    ref_text = f"p.{page_ref}" if page_ref is not None else "source_bundle"
    return {
        "bibliographic_position": f"{paper.title}，来源 {paper.source}。",
        "research_question": paper.abstract[:500] or "Not assessable from supplied material.",
        "background_route": "Not fully assessable before Huoshen chunk synthesis.",
        "pain_point": "Not fully assessable before Huoshen chunk synthesis.",
        "core_insight": paper.abstract[:500] or "Not assessable from supplied material.",
        "method_logic": "Not fully assessable before Huoshen chunk synthesis.",
        "experiments": "Not fully assessable before Huoshen chunk synthesis.",
        "evidence_chain": "Initial scaffold only; replace with chunk-grounded Huoshen analysis.",
        "limitations": "Not fully assessable before Huoshen chunk synthesis.",
        "connection_to_user_research": "需要结合 single-cell / spatial transcriptomics / multi-omics 研究画像进一步判断。",
        "testable_ideas": [],
        "page_refs": [ref_text],
        "status": "scaffold_needs_llm_synthesis",
    }


def write_initial_analysis(paper: SelectionRecord, bundle: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    analysis = initial_paper_analysis(paper, bundle)
    write_json(output_path, analysis)
    return analysis


def generate_deep_paper_analysis(
    paper: SelectionRecord,
    bundle: dict[str, Any],
    openai_client: OpenAI,
    llm_params: dict[str, Any],
) -> dict[str, Any]:
    source_excerpt, refs = _page_texts_for_llm(bundle)
    logger.info(f"Calling configured LLM for Paper Card: {paper.title}")
    lang = llm_params.get("language", "Chinese")
    user_profile = llm_params.get("research_profile") or (
        "single-cell foundation models, spatial transcriptomics, graph neural networks, "
        "multi-omics, biomedical AI, perturbation prediction, and cell-state representation"
    )
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs["max_tokens"] = max(int(generation_kwargs.get("max_tokens") or 0), 500)
    card_llm_params = {**llm_params, "generation_kwargs": generation_kwargs}
    prompt = f"""
Return only valid JSON with exactly these keys:
{{
  "tldr": "one concise Chinese sentence",
  "question": "one concise Chinese sentence",
  "method": "one concise Chinese sentence",
  "evidence": "one concise Chinese sentence",
  "limitation": "one concise Chinese sentence or Not assessable from supplied material.",
  "idea": "one testable hypothesis with validation and failure mode"
}}

Write concise Chinese. Preserve English technical terms. Include one source pointer like [Paper: PDF p. 1] where possible.

Paper:
Title: {paper.title}
Abstract: {paper.abstract}

PDF excerpt:
{source_excerpt}
"""
    content = _request_llm(
        openai_client,
        card_llm_params,
        [
            {
                "role": "system",
                "content": "You generate source-grounded scientific Paper Cards and return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        force_json=True,
    )
    payload = _json_from_llm_content(content)
    if isinstance(payload.get("sections"), dict):
        sections = _normalise_card_sections(payload.get("sections", {}))
    else:
        ref = refs[0] if refs else "[Paper: PDF p. 1]"

        def field(name: str, fallback: str = "Not assessable from supplied material.") -> str:
            value = str(payload.get(name) or "").strip()
            return value or fallback

        sections = _normalise_card_sections(
            {
                "basic_information": (
                    f"题名：{paper.title}；来源：{paper.source}；链接：{paper.url}。"
                    f"这篇论文在今日流程中被选为 {paper.role}，用于快速判断是否值得进入完整一多科研深读。"
                ),
                "one_sentence_summary": field("tldr"),
                "research_question": field("question"),
                "background_path": field("question"),
                "pain_points": field("question"),
                "core_idea": field("method"),
                "method_overview": field("method"),
                "module_breakdown": field("method"),
                "formulas_and_symbols": "Not assessable from supplied material in this smoke-test card.",
                "experiment_evidence_chain": field("evidence"),
                "conclusion_boundaries": field("evidence"),
                "author_limitations": field("limitation"),
                "critical_analysis": f"[Analysis] {field('limitation')}",
                "learned_knowledge": field("method"),
                "knowledge_connections": field("method"),
                "research_ideas": field("idea"),
            }
        )
        sections = {
            section: (body if "[Paper:" in body or "Not assessable" in body else f"{body} {ref}")
            for section, body in sections.items()
        }
    missing_sections = [section for section, body in sections.items() if "Not assessable from supplied material" in body]
    logger.info(f"Configured LLM Paper Card JSON received: {paper.title}")
    return {
        "status": "llm_enriched",
        "source_coverage": str(payload.get("source_coverage") or "Partial paper"),
        "extraction_confidence": str(payload.get("extraction_confidence") or "Mixed"),
        "locator_mode": "page-grounded",
        "primary_lens": str(payload.get("primary_lens") or "methods"),
        "secondary_lens": str(payload.get("secondary_lens") or "None"),
        "context_verification": str(payload.get("context_verification") or "Paper-only"),
        "card_completeness": str(payload.get("card_completeness") or "Partial"),
        "sections": sections,
        "page_refs": refs[:12],
        "quality_notes": payload.get("quality_notes") if isinstance(payload.get("quality_notes"), list) else [],
        "warnings": [f"not_assessable_section:{section}" for section in missing_sections],
    }


def write_deep_analysis(
    paper: SelectionRecord,
    bundle: dict[str, Any],
    output_path: str | Path,
    openai_client: OpenAI | None = None,
    llm_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if openai_client is None or llm_params is None:
        logger.warning(f"LLM client is not configured; writing scaffold card for {paper.title}")
        analysis = initial_paper_analysis(paper, bundle)
        analysis["failure_reason"] = "llm_client_not_configured"
        write_json(output_path, analysis)
        return analysis

    try:
        analysis = generate_deep_paper_analysis(paper, bundle, openai_client, llm_params)
    except Exception as exc:
        logger.warning(f"Failed to generate configured LLM Paper Card analysis for {paper.title}: {exc}")
        analysis = initial_paper_analysis(paper, bundle)
        analysis["status"] = "llm_enrichment_failed"
        analysis["failure_reason"] = str(exc)
    write_json(output_path, analysis)
    return analysis


def generate_paper_card_markdown(paper: SelectionRecord, analysis: dict[str, Any], output_path: str | Path) -> str:
    refs = ", ".join(str(ref) for ref in analysis.get("page_refs", [])) or "source_bundle"
    if isinstance(analysis.get("sections"), dict):
        section_values = _normalise_card_sections(analysis["sections"])
    else:
        section_values = {
            "01 基本信息": analysis.get("bibliographic_position", ""),
            "02 一句话总结": analysis.get("core_insight", ""),
            "03 研究问题": analysis.get("research_question", ""),
            "04 研究背景与发展路径": analysis.get("background_route", ""),
            "05 论文识别的核心痛点": analysis.get("pain_point", ""),
            "06 核心思想": analysis.get("core_insight", ""),
            "07 方法总览": analysis.get("method_logic", ""),
            "08 核心模块拆解": "Not fully assessable before Huoshen chunk synthesis.",
            "09 关键公式与符号": "Not fully assessable before formula-aware extraction.",
            "10 实验设计与证据链": analysis.get("evidence_chain", ""),
            "11 对结论的正确理解": analysis.get("core_insight", ""),
            "12 作者明确承认的限制": "Not fully assessable before full card synthesis.",
            "13 批判性分析": "This scaffold must be replaced or enriched by Huoshen chunk-grounded analysis before final use.",
            "14 学到的知识": analysis.get("connection_to_user_research", ""),
            "15 与既有知识的连接": "Not fully assessable before external context check.",
            "16 研究想法": "\n".join(f"- {idea}" for idea in analysis.get("testable_ideas", [])) or "Not assessable from supplied material.",
        }
    lines = [
        f"# {paper.title}",
        "",
        f"> Source coverage: {analysis.get('source_coverage', 'Partial paper')}",
        f"> Extraction confidence: {analysis.get('extraction_confidence', 'Mixed')}",
        f"> Locator mode: {analysis.get('locator_mode', 'page-grounded')}",
        f"> Primary analytical lens: {analysis.get('primary_lens', 'methods')}",
        f"> Secondary analytical lens: {analysis.get('secondary_lens', 'None')}",
        f"> Context verification: {analysis.get('context_verification', 'Paper-only')}",
        f"> Card completeness: {analysis.get('card_completeness', 'Partial')}",
        "",
        f"- Source: {paper.source}",
        f"- URL: {paper.url}",
        f"- PDF: {paper.pdf_url or 'missing'}",
        f"- Analysis status: {analysis.get('status', 'unknown')}",
        "",
    ]
    for section in CARD_SECTIONS:
        body = section_values.get(section, "Not assessable from supplied material.")
        if "[Paper:" not in body and "Not assessable" not in body:
            body = f"{body}\n\nSource refs: {refs}"
        lines.extend([f"## {section}", "", body, ""])
    markdown = "\n".join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(markdown, encoding="utf-8")
    return markdown


def audit_paper_card(folder: str | Path) -> dict[str, Any]:
    folder = Path(folder)
    errors: list[str] = []
    warnings: list[str] = []
    pdf_path = folder / "original.pdf"
    bundle_path = folder / "source_bundle.json"
    card_path = folder / "paper-card.md"

    ok, reason = validate_pdf(pdf_path)
    if not ok:
        errors.append(reason or "invalid_pdf")
    if not bundle_path.exists():
        errors.append("source_bundle_missing")
    if not card_path.exists():
        errors.append("paper_card_missing")
    else:
        card = card_path.read_text(encoding="utf-8")
        for section in CARD_SECTIONS:
            if f"## {section}" not in card:
                errors.append(f"missing_section:{section}")
        source_pointer_count = card.count("Source refs:") + card.count("[Paper:")
        if source_pointer_count < 5:
            warnings.append("fewer_than_5_source_refs")
        if "scaffold must be replaced" in card:
            warnings.append("scaffold_card_needs_llm_enrichment")
        if "llm_enrichment_failed" in card or "llm_client_not_configured" in card:
            warnings.append("llm_enrichment_not_completed")

    status = "failed" if errors else ("warning" if warnings else "pass")
    report = {"status": status, "errors": errors, "warnings": warnings}
    write_json(folder / "audit-report.json", report)
    return report


def export_markdown_to_pdf(markdown_path: str | Path, pdf_path: str | Path) -> None:
    markdown_path = Path(markdown_path)
    pdf_path = Path(pdf_path)
    text = markdown_path.read_text(encoding="utf-8")
    doc = pymupdf.open()
    width, height = 595, 842
    margin = 42
    fontsize = 9.5
    line_height = 14
    max_chars_per_line = 58

    def wrapped_lines(raw_text: str) -> list[str]:
        lines: list[str] = []
        for paragraph in raw_text.splitlines():
            if not paragraph:
                lines.append("")
                continue
            remaining = paragraph
            while remaining:
                lines.append(remaining[:max_chars_per_line])
                remaining = remaining[max_chars_per_line:]
        return lines

    page = doc.new_page(width=width, height=height)
    y = margin
    for line in wrapped_lines(text):
        if y > height - margin:
            page = doc.new_page(width=width, height=height)
            y = margin
        page.insert_text((margin, y), line, fontsize=fontsize, fontname="china-s")
        y += line_height if line else line_height * 0.7
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(pdf_path)


def write_daily_index(output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    papers = []
    for folder in sorted(output_dir.glob("paper-*/*")):
        audit_path = folder / "audit-report.json"
        metadata_path = folder / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
        papers.append(
            {
                "title": metadata.get("title") or folder.name,
                "status": "completed" if audit.get("status") in {"pass", "warning"} else "failed",
                "folder": str(folder),
                "original_pdf": str(folder / "original.pdf"),
                "card_md": str(folder / "paper-card.md"),
                "card_pdf": str(folder / "文档分析.pdf"),
                "audit_status": audit.get("status"),
                "failure_reason": metadata.get("failure_reason"),
            }
        )
    payload = {
        "date": output_dir.name,
        "candidate_count": len(json.loads((output_dir / "candidates.json").read_text(encoding="utf-8"))) if (output_dir / "candidates.json").exists() else 0,
        "selected_count": len(json.loads((output_dir / "selected_papers.json").read_text(encoding="utf-8"))) if (output_dir / "selected_papers.json").exists() else 0,
        "papers": papers,
    }
    path = output_dir / "index.json"
    write_json(path, payload)
    return path


def process_selected_paper(
    record: SelectionRecord,
    output_dir: str | Path,
    index: int,
    openai_client: OpenAI | None = None,
    llm_params: dict[str, Any] | None = None,
    card_mode: str = "brief",
    full_card_input_chars: int = 55_000,
    full_card_output_tokens: int = 12_000,
) -> Path:
    folder = paper_folder(output_dir, index, record.title)
    folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Processing selected paper {index}: {record.title}")
    metadata = asdict(record)
    pdf_path = folder / "original.pdf"
    download_meta = download_pdf(record.pdf_url, pdf_path)
    metadata.update(download_meta)
    write_json(folder / "metadata.json", metadata)
    if download_meta["download_status"] != "downloaded":
        logger.warning(f"Skipping card generation for {record.title}: {download_meta['failure_reason']}")
        write_json(folder / "audit-report.json", {"status": "failed", "errors": [download_meta["failure_reason"]], "warnings": []})
        return folder

    bundle = extract_source_bundle(pdf_path, folder / "source_bundle.json")
    if card_mode == "one_shot_full" and openai_client is not None and llm_params is not None:
        analysis = generate_one_shot_full_card_markdown(
            record,
            bundle,
            folder / "paper-card.md",
            openai_client,
            llm_params,
            max_input_chars=full_card_input_chars,
            max_output_tokens=full_card_output_tokens,
        )
        write_json(folder / "paper_analysis.json", analysis)
    else:
        analysis = write_deep_analysis(record, bundle, folder / "paper_analysis.json", openai_client, llm_params)
        generate_paper_card_markdown(record, analysis, folder / "paper-card.md")
    export_markdown_to_pdf(folder / "paper-card.md", folder / "文档分析.pdf")
    report = audit_paper_card(folder)
    logger.info(f"Finished selected paper {index}: audit_status={report['status']} title={record.title}")
    return folder


def _config_get(config: DictConfig, section: str, key: str, default: Any) -> Any:
    data = config.get(section, {})
    if hasattr(data, "get"):
        return data.get(key, default)
    return default


def _config_int(config: DictConfig, section: str, key: str, default: int) -> int:
    value = _config_get(config, section, key, default)
    if value in (None, "", "null"):
        return default
    return int(value)


def _config_bool(config: DictConfig, section: str, key: str, default: bool) -> bool:
    value = _config_get(config, section, key, default)
    if isinstance(value, bool):
        return value
    if value in (None, "", "null"):
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def run_daily_file_pipeline(config: DictConfig) -> Path:
    output_root = _config_get(config, "daily_pipeline", "output_dir", "outputs/daily")
    candidate_count = _config_int(config, "daily_pipeline", "candidate_count", 20)
    selected_count = _config_int(config, "daily_pipeline", "selected_count", 3)
    llm_rerank_count = _config_int(config, "daily_pipeline", "llm_rerank_count", 8)
    llm_selection_enabled = _config_bool(config, "daily_pipeline", "llm_selection_enabled", True)
    card_mode = _config_get(config, "daily_pipeline", "card_mode", "brief")
    full_card_input_chars = _config_int(config, "daily_pipeline", "full_card_input_chars", 55_000)
    full_card_output_tokens = _config_int(config, "daily_pipeline", "full_card_output_tokens", 12_000)
    output_dir = daily_output_dir(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    executor = Executor(config)
    corpus = executor.filter_corpus(executor.fetch_zotero_corpus())
    if not corpus:
        raise RuntimeError("No Zotero corpus papers found; cannot personalize candidate selection.")

    all_papers: list[Paper] = []
    for source, retriever in executor.retrievers.items():
        logger.info(f"Retrieving {source} papers for daily file pipeline...")
        papers = retriever.retrieve_papers()
        logger.info(f"Retrieved {len(papers)} {source} papers")
        all_papers.extend(papers)

    candidates = all_papers[:candidate_count]
    write_candidates(candidates, output_dir, limit=candidate_count)
    if not candidates:
        write_selected_papers([], output_dir)
        write_daily_index(output_dir)
        return output_dir

    llm_params = OmegaConf.to_container(config.llm, resolve=True) if hasattr(config, "llm") else None
    reranked = executor.reranker.rerank(candidates, corpus)
    llm_scores: dict[str, dict[str, Any]] = {}
    if llm_selection_enabled and executor.openai_client is not None and llm_params is not None:
        llm_pool = reranked[: min(llm_rerank_count, len(reranked))]
        logger.info(f"Sending {len(llm_pool)} title/abstract candidates to Qwen for scientific-value scoring...")
        try:
            reranked, llm_scores = rank_candidates_with_llm(llm_pool, executor.openai_client, llm_params)
            write_llm_ranking(reranked, llm_scores, output_dir)
        except Exception as exc:
            logger.warning(f"LLM candidate scoring failed; using embedding ranking: {type(exc).__name__}: {exc}")
            write_json(output_dir / "llm_ranking.json", {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "fallback": "embedding_ranking",
            })
    else:
        write_json(output_dir / "llm_ranking.json", {
            "status": "disabled_or_unconfigured",
            "fallback": "embedding_ranking",
        })
    selected = select_papers_for_deep_read(reranked, count=selected_count, llm_scores=llm_scores)
    write_selected_papers(selected, output_dir)
    for index, record in enumerate(selected, start=1):
        process_selected_paper(
            record,
            output_dir,
            index,
            executor.openai_client,
            llm_params,
            card_mode=card_mode,
            full_card_input_chars=full_card_input_chars,
            full_card_output_tokens=full_card_output_tokens,
        )
    write_daily_index(output_dir)
    return output_dir
