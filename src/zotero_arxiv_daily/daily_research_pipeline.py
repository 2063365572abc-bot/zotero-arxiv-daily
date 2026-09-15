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
from pyzotero import zotero
import pymupdf
import requests

from .executor import Executor
from .protocol import Paper, _request_llm
from .research_state import (
    ResearchRadarState,
    candidate_embedding_records,
    corpus_embedding_records,
    embedding_rerank_candidates,
    ensure_embeddings,
)


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
    retrieval_source: str = "unknown"
    freshness_bucket: int = 0
    freshness_label: str = "unknown"
    matched_terms: dict[str, list[str]] | None = None
    arxiv_id: str | None = None
    embedding_rank: int | None = None
    embedding_score: float | None = None
    score_breakdown: dict[str, float] | None = None
    matched_zotero_items: list[dict[str, Any]] | None = None


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
    arxiv_id: str | None = None


def daily_output_dir(root: str | Path = "outputs/daily", date: datetime | None = None) -> Path:
    date = date or datetime.now()
    return Path(root) / date.strftime("%Y-%m-%d")


def write_json(path: str | Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def paper_to_candidate(paper: Paper) -> CandidateRecord:
    return CandidateRecord(
        arxiv_id=getattr(paper, "arxiv_id", None),
        source=paper.source,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        url=paper.url,
        pdf_url=paper.pdf_url,
        published_date=getattr(paper, "published_date", None),
        categories=list(getattr(paper, "categories", []) or []),
        raw_score=paper.score,
        retrieval_source=getattr(paper, "retrieval_source", "unknown"),
        freshness_bucket=int(getattr(paper, "freshness_bucket", 0)),
        freshness_label=getattr(paper, "freshness_label", "unknown"),
        matched_terms=getattr(paper, "matched_terms", None),
        embedding_rank=getattr(paper, "embedding_rank", None),
        embedding_score=getattr(paper, "embedding_score", None),
        score_breakdown=getattr(paper, "score_breakdown", None),
        matched_zotero_items=getattr(paper, "matched_zotero_items", None),
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
                arxiv_id=getattr(paper, "arxiv_id", None),
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
                    f"{llm_score['reason']} Risk: {llm_score.get('risk', 'not provided')}"
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
            f"Source: {paper.source}\nURL: {paper.url}\n"
            f"arXiv ID: {getattr(paper, 'arxiv_id', '')}\n"
            f"Published: {getattr(paper, 'published_date', '')}\n"
            f"Freshness: {getattr(paper, 'freshness_label', 'unknown')}\n"
            f"Embedding rank: {getattr(paper, 'embedding_rank', '')}\n"
            f"Embedding score: {getattr(paper, 'embedding_score', '')}\n"
            f"Score breakdown: {json.dumps(getattr(paper, 'score_breakdown', {}) or {}, ensure_ascii=False)}\n"
            f"Matched Zotero papers: {json.dumps(getattr(paper, 'matched_zotero_items', [])[:5], ensure_ascii=False)}\n"
            f"Matched terms: {json.dumps(getattr(paper, 'matched_terms', {}) or {}, ensure_ascii=False)}"
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

必须给每一篇候选都返回一个 rankings 条目，paper_index 必须覆盖 1 到候选论文总数。
reason 和 risk 各不超过 60 个中文字符，避免输出过长导致 JSON 被截断。

请只返回 JSON，格式必须是：
{{"trend_summary":"中文总结今天候选池体现出的研究趋势，必须说明新鲜度限制","rejected_summary":"中文总结主要被降权/不选的论文类型","rankings":[{{"paper_index":1,"relevance_to_user":0,"method_novelty":0,"evidence_quality":0,"transferability":0,"trend_value":0,"resource_value":0,"best_role":"best_match|method_inspiration|trend_signal","reason":"中文理由","risk":"中文风险"}}]}}

候选论文：
{chr(10).join(paper_blocks)}
""".strip()


def rank_candidates_with_llm(
    papers: list[Paper],
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    include_summary: bool = False,
) -> tuple[list[Paper], dict[str, dict[str, Any]]] | tuple[list[Paper], dict[str, dict[str, Any]], dict[str, str]]:
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs["max_tokens"] = min(max(int(generation_kwargs.get("max_tokens") or 0), 3000), 6000)
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
    summary = {
        "trend_summary": str(payload.get("trend_summary") or ""),
        "rejected_summary": str(payload.get("rejected_summary") or ""),
    }
    if include_summary:
        return ranked, scores, summary
    return ranked, scores


def write_llm_ranking(
    papers: list[Paper],
    scores: dict[str, dict[str, Any]],
    output_dir: str | Path,
    summary: dict[str, str] | None = None,
) -> Path:
    payload = []
    for rank, paper in enumerate(papers, start=1):
        payload.append(
            {
                "rank": rank,
                "arxiv_id": getattr(paper, "arxiv_id", None),
                "title": paper.title,
                "url": paper.url,
                "published_date": getattr(paper, "published_date", None),
                "freshness_label": getattr(paper, "freshness_label", "unknown"),
                "matched_terms": getattr(paper, "matched_terms", None),
                **scores[paper.title],
            }
        )
    path = Path(output_dir) / "llm_ranking.json"
    write_json(path, {"summary": summary or {}, "rankings": payload})
    return path


def write_embedding_ranking(papers: list[Paper], output_dir: str | Path, filename: str) -> Path:
    payload = []
    for rank, paper in enumerate(papers, start=1):
        payload.append(
            {
                "rank": rank,
                **asdict(paper_to_candidate(paper)),
            }
        )
    path = Path(output_dir) / filename
    write_json(path, payload)
    return path


def write_llm_selection_audit(
    selected: list[SelectionRecord],
    top20: list[Paper],
    output_dir: str | Path,
    summary: dict[str, str] | None = None,
    fallback: str | None = None,
) -> Path:
    allowed = {getattr(paper, "arxiv_id", None) for paper in top20}
    selected_ids = [record.arxiv_id for record in selected]
    payload = {
        "selected_count": len(selected),
        "required_selected_count": 3,
        "selected_ids": selected_ids,
        "all_selected_from_top20": all(arxiv_id in allowed for arxiv_id in selected_ids),
        "freshness_labels": {
            record.arxiv_id or record.title: next(
                (getattr(paper, "freshness_label", "unknown") for paper in top20 if getattr(paper, "arxiv_id", None) == record.arxiv_id),
                "unknown",
            )
            for record in selected
        },
        "trend_summary": (summary or {}).get("trend_summary", ""),
        "rejected_summary": (summary or {}).get("rejected_summary", ""),
        "fallback": fallback,
    }
    path = Path(output_dir) / "llm_selection_audit.json"
    write_json(path, payload)
    return path


def rank_candidates_with_llm_batched(
    papers: list[Paper],
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    batch_size: int = 10,
) -> tuple[list[Paper], dict[str, dict[str, Any]], dict[str, str], int]:
    if not papers:
        return [], {}, {"trend_summary": "", "rejected_summary": ""}, 0
    batch_size = max(1, int(batch_size or 10))
    if len(papers) <= batch_size:
        ranked, scores, summary = rank_candidates_with_llm(
            papers,
            openai_client,
            llm_params,
            include_summary=True,
        )
        return ranked, scores, summary, 1

    all_scores: dict[str, dict[str, Any]] = {}
    trend_parts: list[str] = []
    rejected_parts: list[str] = []
    calls = 0
    for start in range(0, len(papers), batch_size):
        batch = papers[start : start + batch_size]
        _, batch_scores, batch_summary = rank_candidates_with_llm(
            batch,
            openai_client,
            llm_params,
            include_summary=True,
        )
        calls += 1
        all_scores.update(batch_scores)
        if batch_summary.get("trend_summary"):
            trend_parts.append(batch_summary["trend_summary"])
        if batch_summary.get("rejected_summary"):
            rejected_parts.append(batch_summary["rejected_summary"])

    if len(all_scores) < len(papers):
        raise ValueError(f"LLM batched selection returned {len(all_scores)} of {len(papers)} candidates")
    ranked = sorted(papers, key=lambda paper: all_scores[paper.title]["total"], reverse=True)
    for paper in ranked:
        paper.score = all_scores[paper.title]["total"]
    summary = {
        "trend_summary": "；".join(trend_parts),
        "rejected_summary": "；".join(rejected_parts),
    }
    return ranked, all_scores, summary, calls


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


def freshness_distribution(papers: list[Paper]) -> dict[str, int]:
    labels = ["latest_48h", "recent_7d", "recent_30d", "backfill", "unknown"]
    counts = {label: 0 for label in labels}
    for paper in papers:
        label = str(getattr(paper, "freshness_label", "unknown") or "unknown")
        counts[label] = counts.get(label, 0) + 1
    return counts


def retrieval_source_distribution(papers: list[Paper]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for paper in papers:
        source = str(getattr(paper, "retrieval_source", "unknown") or "unknown")
        counts[source] = counts.get(source, 0) + 1
    return dict(sorted(counts.items()))


def retrieve_daily_candidates(executor: Executor, candidate_count: int) -> list[Paper]:
    all_papers: list[Paper] = []
    for source, retriever in executor.retrievers.items():
        logger.info(f"Retrieving {source} papers for daily pipeline...")
        papers = retriever.retrieve_papers()
        logger.info(f"Retrieved {len(papers)} {source} papers")
        all_papers.extend(papers)
    return all_papers[:candidate_count]


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


def _zotero_collection_key(zot: Any, path_parts: list[str]) -> str | None:
    collections = zot.everything(zot.collections())
    parent_key: str | None = None
    for name in path_parts:
        match = next(
            (
                collection
                for collection in collections
                if collection.get("data", {}).get("name") == name
                and (collection.get("data", {}).get("parentCollection") or None) == parent_key
            ),
            None,
        )
        if match is None:
            payload = {"name": name}
            if parent_key:
                payload["parentCollection"] = parent_key
            created = zot.create_collections([payload])
            key = None
            if isinstance(created, dict):
                key = (created.get("success") or {}).get("0") or (created.get("successful") or {}).get("0")
            if not key:
                collections = zot.everything(zot.collections())
                match = next(
                    (
                        collection
                        for collection in collections
                        if collection.get("data", {}).get("name") == name
                        and (collection.get("data", {}).get("parentCollection") or None) == parent_key
                    ),
                    None,
                )
                key = match.get("key") if match else None
            parent_key = key
            collections = zot.everything(zot.collections())
        else:
            parent_key = match.get("key")
    return parent_key


def upload_selected_paper_to_zotero(
    config: DictConfig,
    record: SelectionRecord,
    folder: str | Path,
    run_date: str,
) -> dict[str, Any]:
    folder = Path(folder)
    result: dict[str, Any] = {
        "arxiv_id": record.arxiv_id,
        "title": record.title,
        "status": "failed",
        "item_key": None,
        "original_pdf_attachment_key": None,
        "card_pdf_attachment_key": None,
        "collection_path": "一多科研 / 单细胞转录组",
        "failure_reason": None,
        "run_date": run_date,
    }
    try:
        zot = zotero.Zotero(config.zotero.user_id, "user", config.zotero.api_key)
        existing = zot.everything(zot.items(q=record.title, itemType="conferencePaper || journalArticle || preprint"))
        item_key = None
        if existing:
            item_key = existing[0].get("key")
        else:
            template = zot.item_template("preprint")
            template.update(
                {
                    "title": record.title,
                    "abstractNote": record.abstract,
                    "url": record.url,
                    "archive": "arXiv",
                    "archiveLocation": record.arxiv_id or "",
                    "extra": (
                        f"Daily research radar selection: {run_date}\n"
                        f"Selection reason: {record.selection_reason}\n"
                        f"PDF: {record.pdf_url or ''}"
                    ),
                    "creators": [{"creatorType": "author", "name": author} for author in record.authors[:20]],
                    "tags": [
                        {"tag": "daily-arxiv"},
                        {"tag": "spatial-transcriptomics"},
                        {"tag": "machine-learning"},
                        {"tag": "embedding-selected"},
                        {"tag": "llm-selected"},
                        {"tag": "card-generated"},
                    ],
                }
            )
            created = zot.create_items([template])
            if isinstance(created, dict):
                item_key = (created.get("success") or {}).get("0") or (created.get("successful") or {}).get("0")
        if not item_key:
            raise RuntimeError("Zotero item creation did not return an item key")
        result["item_key"] = item_key

        collection_key = _zotero_collection_key(zot, ["一多科研", "单细胞转录组"])
        if collection_key:
            try:
                zot.addto_collection(collection_key, {"items": [item_key]})
            except Exception as exc:
                logger.warning(f"Failed to assign Zotero collection for {record.title}: {exc}")

        attachments = [
            (folder / "original.pdf", "original_pdf_attachment_key"),
            (folder / "文档分析.pdf", "card_pdf_attachment_key"),
        ]
        attachment_failures = []
        for path, key_name in attachments:
            if not path.exists():
                attachment_failures.append(f"{path.name}:missing")
                continue
            try:
                uploaded = zot.attachment_simple([str(path)], parentid=item_key)
                if isinstance(uploaded, dict):
                    result[key_name] = (uploaded.get("success") or {}).get("0") or (uploaded.get("successful") or {}).get("0")
            except Exception as exc:
                attachment_failures.append(f"{path.name}:{type(exc).__name__}: {exc}")
        result["status"] = "uploaded" if not attachment_failures else "partial"
        result["failure_reason"] = "; ".join(attachment_failures) if attachment_failures else None
    except Exception as exc:
        result["failure_reason"] = f"{type(exc).__name__}: {exc}"
    return result


def write_daily_report_markdown(output_dir: str | Path, audit: dict[str, Any], selected: list[SelectionRecord]) -> Path:
    output_dir = Path(output_dir)
    lines = [
        f"# Daily Research Radar - {output_dir.name}",
        "",
        "## Summary",
        "",
        f"- Raw candidates: {audit.get('raw_arxiv_count', 0)}",
        f"- Candidates kept: {audit.get('candidate_50_count', 0)}",
        f"- Top20 count: {audit.get('top20_count', 0)}",
        f"- Selected count: {audit.get('selected_count', 0)}",
        f"- PDF success: {audit.get('pdf_success_count', 0)}",
        f"- Card success: {audit.get('card_success_count', 0)}",
        f"- Zotero uploaded: {audit.get('zotero_upload_success_count', 0)}",
        "",
        "## Freshness",
        "",
    ]
    for label, count in (audit.get("freshness_distribution") or {}).items():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "## Selected Papers", ""])
    for index, record in enumerate(selected, start=1):
        lines.extend(
            [
                f"### {index}. {record.title}",
                "",
                f"- arXiv ID: {record.arxiv_id or 'unknown'}",
                f"- URL: {record.url}",
                f"- Score: {record.score}",
                f"- Role: {record.role}",
                f"- Reason: {record.selection_reason}",
                "",
            ]
        )
    lines.extend(
        [
            "## Audit",
            "",
            f"- Top20 from candidates: {audit.get('top20_from_candidates')}",
            f"- Top3 from Top20: {audit.get('top3_from_top20')}",
            f"- Candidate/Top20 Zotero uploads: {audit.get('candidate_or_top20_zotero_uploads')}",
            f"- Fallbacks: {', '.join(audit.get('fallbacks_used') or []) or 'none'}",
            "",
        ]
    )
    path = output_dir / "daily_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    write_json(output_dir / "daily_report.json", {"audit": audit, "selected": [asdict(record) for record in selected]})
    return path


def run_full_research_radar_pipeline(
    config: DictConfig,
    executor: Executor,
    output_dir: Path,
    *,
    candidate_count: int,
    top20_count: int,
    selected_count: int,
    llm_selection_batch_size: int,
    llm_selection_enabled: bool,
    card_mode: str,
    full_card_input_chars: int,
    full_card_output_tokens: int,
) -> Path:
    run_date = output_dir.name
    state_path = Path(str(_config_get(config, "daily_pipeline", "state_path", "state/research_radar.sqlite")))
    embedding_model = str(config.reranker.api.get("model") or "text-embedding-v4")
    embedding_batch_size = int(config.reranker.api.get("batch_size") or 10)
    llm_params = OmegaConf.to_container(config.llm, resolve=True) if hasattr(config, "llm") else None
    state = ResearchRadarState(state_path)
    embedding_client = OpenAI(
        api_key=config.reranker.api.key,
        base_url=config.reranker.api.base_url,
        timeout=float(config.reranker.api.get("timeout", 60)),
    )
    daily_audit: dict[str, Any] = {
        "status": "started",
        "run_date": run_date,
        "candidate_target": candidate_count,
        "top20_target": top20_count,
        "selected_target": selected_count,
        "embedding_model": embedding_model,
        "zotero_upload_attempted_for": "selected_top3_only",
        "candidate_or_top20_zotero_uploads": 0,
        "fallbacks_used": [],
    }
    try:
        corpus = executor.filter_corpus(executor.fetch_zotero_corpus())
        if not corpus:
            raise RuntimeError("No Zotero corpus papers found; cannot personalize candidate selection.")
        state.upsert_zotero_items(corpus, embedding_model)
        corpus_records = corpus_embedding_records(corpus, embedding_model)
        corpus_vectors, corpus_embed_audit = ensure_embeddings(
            state,
            corpus_records,
            entity_type="zotero",
            model=embedding_model,
            openai_client=embedding_client,
            batch_size=embedding_batch_size,
        )

        candidates = retrieve_daily_candidates(executor, candidate_count)
        state.upsert_arxiv_papers(candidates)
        write_candidates(candidates, output_dir, limit=candidate_count)
        write_embedding_ranking(candidates, output_dir, "candidates_50.json")
        if not candidates:
            write_selected_papers([], output_dir)
            daily_audit.update({"status": "no_candidates", "raw_arxiv_count": 0})
            write_json(output_dir / "daily_audit.json", daily_audit)
            write_daily_index(output_dir)
            return output_dir

        candidate_records = candidate_embedding_records(candidates, embedding_model)
        candidate_vectors, candidate_embed_audit = ensure_embeddings(
            state,
            candidate_records,
            entity_type="candidate",
            model=embedding_model,
            openai_client=embedding_client,
            batch_size=embedding_batch_size,
        )
        ranked, ranking_records = embedding_rerank_candidates(
            candidates,
            corpus,
            candidate_vectors,
            corpus_vectors,
        )
        top20 = ranked[: min(top20_count, len(ranked))]
        write_embedding_ranking(ranked, output_dir, "embedding_ranking_50.json")
        write_embedding_ranking(top20, output_dir, "top20_for_llm.json")
        for record in ranking_records:
            state.conn.execute(
                """
                INSERT INTO daily_rankings(run_date, arxiv_id, ranking_json)
                VALUES(?,?,?)
                ON CONFLICT(run_date, arxiv_id) DO UPDATE SET ranking_json=excluded.ranking_json
                """,
                (run_date, record.arxiv_id or record.title, json.dumps(asdict(record), ensure_ascii=False)),
            )
        state.conn.commit()

        llm_scores: dict[str, dict[str, Any]] = {}
        llm_summary: dict[str, str] = {}
        llm_model_calls = 0
        reranked_for_selection = top20
        selection_fallback = None
        if top20 and llm_selection_enabled and executor.openai_client is not None and llm_params is not None:
            try:
                reranked_for_selection, llm_scores, llm_summary, llm_model_calls = rank_candidates_with_llm_batched(
                    top20,
                    executor.openai_client,
                    llm_params,
                    batch_size=llm_selection_batch_size,
                )
                write_llm_ranking(reranked_for_selection, llm_scores, output_dir, summary=llm_summary)
            except Exception as exc:
                selection_fallback = f"embedding_top3_after_llm_failure:{type(exc).__name__}: {exc}"
                daily_audit["fallbacks_used"].append(selection_fallback)
                logger.warning(f"LLM Top20 selection failed; using embedding Top3: {exc}")
                write_json(output_dir / "llm_ranking.json", {
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "fallback": "embedding_top3",
                })
        else:
            selection_fallback = "llm_disabled_or_unconfigured"
            daily_audit["fallbacks_used"].append(selection_fallback)
            write_json(output_dir / "llm_ranking.json", {
                "status": "disabled_or_unconfigured",
                "fallback": "embedding_top3",
            })

        selected = select_papers_for_deep_read(reranked_for_selection, count=selected_count, llm_scores=llm_scores)
        write_selected_papers(selected, output_dir)
        write_llm_selection_audit(selected, top20, output_dir, summary=llm_summary, fallback=selection_fallback)
        for record in selected:
            state.conn.execute(
                """
                INSERT INTO daily_selections(run_date, arxiv_id, selection_json)
                VALUES(?,?,?)
                ON CONFLICT(run_date, arxiv_id) DO UPDATE SET selection_json=excluded.selection_json
                """,
                (run_date, record.arxiv_id or record.title, json.dumps(asdict(record), ensure_ascii=False)),
            )
        state.conn.commit()

        paper_folders: list[Path] = []
        zotero_uploads = []
        for index, record in enumerate(selected, start=1):
            folder = process_selected_paper(
                record,
                output_dir,
                index,
                executor.openai_client,
                llm_params,
                card_mode=card_mode,
                full_card_input_chars=full_card_input_chars,
                full_card_output_tokens=full_card_output_tokens,
            )
            paper_folders.append(folder)
            upload = upload_selected_paper_to_zotero(config, record, folder, run_date)
            zotero_uploads.append(upload)
            state.conn.execute(
                """
                INSERT INTO zotero_uploads(run_date, arxiv_id, upload_json)
                VALUES(?,?,?)
                ON CONFLICT(run_date, arxiv_id) DO UPDATE SET upload_json=excluded.upload_json
                """,
                (run_date, record.arxiv_id or record.title, json.dumps(upload, ensure_ascii=False)),
            )
            state.conn.commit()
        write_json(output_dir / "zotero_uploads.json", zotero_uploads)

        pdf_success_count = 0
        card_success_count = 0
        for folder in paper_folders:
            metadata_path = folder / "metadata.json"
            audit_path = folder / "audit-report.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                if metadata.get("download_status") == "downloaded":
                    pdf_success_count += 1
            if audit_path.exists():
                audit = json.loads(audit_path.read_text(encoding="utf-8"))
                if audit.get("status") in {"pass", "warning"}:
                    card_success_count += 1

        daily_audit.update(
            {
                "status": "complete",
                "raw_arxiv_count": len(candidates),
                "candidate_50_count": len(candidates),
                "top20_count": len(top20),
                "selected_count": len(selected),
                "embedding_audit": {
                    **state.embedding_audit(embedding_model),
                    "zotero_cache_hit_count": corpus_embed_audit["cache_hit_count"],
                    "zotero_api_create_count": corpus_embed_audit["api_create_count"],
                    "candidate_cache_hit_count": candidate_embed_audit["cache_hit_count"],
                    "candidate_api_create_count": candidate_embed_audit["api_create_count"],
                    "embedding_missing_count": 0,
                },
                "llm_model_calls": llm_model_calls,
                "freshness_distribution": freshness_distribution(candidates),
                "top20_from_candidates": all(paper in candidates for paper in top20),
                "top3_from_top20": all(record.arxiv_id in {getattr(paper, "arxiv_id", None) for paper in top20} for record in selected),
                "pdf_success_count": pdf_success_count,
                "card_success_count": card_success_count,
                "zotero_upload_success_count": sum(1 for item in zotero_uploads if item.get("status") == "uploaded"),
                "zotero_upload_partial_count": sum(1 for item in zotero_uploads if item.get("status") == "partial"),
            }
        )
        state.conn.execute(
            """
            INSERT INTO daily_runs(run_date, metadata_json, updated_at)
            VALUES(?,?,?)
            ON CONFLICT(run_date) DO UPDATE SET metadata_json=excluded.metadata_json, updated_at=excluded.updated_at
            """,
            (run_date, json.dumps(daily_audit, ensure_ascii=False), datetime.now().isoformat()),
        )
        state.conn.commit()
        write_json(output_dir / "daily_audit.json", daily_audit)
        write_daily_report_markdown(output_dir, daily_audit, selected)
        write_daily_index(output_dir)
        return output_dir
    finally:
        state.close()


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
    top20_count = _config_int(config, "daily_pipeline", "top20_count", 20)
    selected_count = _config_int(config, "daily_pipeline", "selected_count", 3)
    llm_rerank_count = _config_int(config, "daily_pipeline", "llm_rerank_count", 8)
    llm_selection_batch_size = _config_int(config, "daily_pipeline", "llm_selection_batch_size", 10)
    llm_selection_enabled = _config_bool(config, "daily_pipeline", "llm_selection_enabled", True)
    retrieval_only = _config_bool(config, "daily_pipeline", "retrieval_only", False)
    selection_only = _config_bool(config, "daily_pipeline", "selection_only", False)
    card_mode = _config_get(config, "daily_pipeline", "card_mode", "brief")
    full_card_input_chars = _config_int(config, "daily_pipeline", "full_card_input_chars", 55_000)
    full_card_output_tokens = _config_int(config, "daily_pipeline", "full_card_output_tokens", 12_000)
    output_dir = daily_output_dir(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    executor = Executor(config)
    mode = str(_config_get(config, "daily_pipeline", "mode", "full_research_radar"))
    if mode == "full_research_radar":
        return run_full_research_radar_pipeline(
            config,
            executor,
            output_dir,
            candidate_count=candidate_count,
            top20_count=top20_count,
            selected_count=selected_count,
            llm_selection_batch_size=llm_selection_batch_size,
            llm_selection_enabled=llm_selection_enabled,
            card_mode=card_mode,
            full_card_input_chars=full_card_input_chars,
            full_card_output_tokens=full_card_output_tokens,
        )

    if retrieval_only:
        candidates = retrieve_daily_candidates(executor, candidate_count)
        write_candidates(candidates, output_dir, limit=candidate_count)
        write_selected_papers([], output_dir)
        write_json(output_dir / "retrieval-manifest.json", {
            "status": "retrieval_only",
            "model_calls": 0,
            "embedding_calls": 0,
            "pdf_downloads": 0,
            "candidate_count": len(candidates),
            "retrieval_limit": candidate_count,
            "retrieval_sources": retrieval_source_distribution(candidates),
            "freshness_buckets": freshness_distribution(candidates),
        })
        write_daily_index(output_dir)
        return output_dir

    if selection_only:
        candidates = retrieve_daily_candidates(executor, candidate_count)
        write_candidates(candidates, output_dir, limit=candidate_count)
        llm_params = OmegaConf.to_container(config.llm, resolve=True) if hasattr(config, "llm") else None
        llm_scores: dict[str, dict[str, Any]] = {}
        llm_summary: dict[str, str] = {}
        llm_model_calls = 0
        reranked = candidates
        if candidates and llm_selection_enabled and executor.openai_client is not None and llm_params is not None:
            llm_pool = candidates[: min(llm_rerank_count, len(candidates))]
            logger.info(f"Sending {len(llm_pool)} title/abstract candidates to Qwen for selection-only scoring...")
            try:
                reranked, llm_scores, llm_summary, llm_model_calls = rank_candidates_with_llm_batched(
                    llm_pool,
                    executor.openai_client,
                    llm_params,
                    batch_size=llm_selection_batch_size,
                )
                write_llm_ranking(reranked, llm_scores, output_dir, summary=llm_summary)
            except Exception as exc:
                logger.warning(f"LLM candidate scoring failed; using deterministic retrieval ranking: {type(exc).__name__}: {exc}")
                write_json(output_dir / "llm_ranking.json", {
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "fallback": "deterministic_retrieval_ranking",
                })
        else:
            write_json(output_dir / "llm_ranking.json", {
                "status": "disabled_or_unconfigured",
                "fallback": "deterministic_retrieval_ranking",
            })
        selected = select_papers_for_deep_read(reranked, count=selected_count, llm_scores=llm_scores)
        write_selected_papers(selected, output_dir)
        write_json(output_dir / "selection-manifest.json", {
            "status": "selection_only",
            "model_calls": llm_model_calls,
            "embedding_calls": 0,
            "pdf_downloads": 0,
            "candidate_count": len(candidates),
            "selected_count": len(selected),
            "llm_pool_count": min(llm_rerank_count, len(candidates)),
            "llm_selection_batch_size": llm_selection_batch_size,
            "retrieval_sources": retrieval_source_distribution(candidates),
            "freshness_buckets": freshness_distribution(candidates),
            "trend_summary": llm_summary.get("trend_summary", ""),
            "rejected_summary": llm_summary.get("rejected_summary", ""),
        })
        write_daily_index(output_dir)
        return output_dir

    corpus = executor.filter_corpus(executor.fetch_zotero_corpus())
    if not corpus:
        raise RuntimeError("No Zotero corpus papers found; cannot personalize candidate selection.")

    candidates = retrieve_daily_candidates(executor, candidate_count)
    write_candidates(candidates, output_dir, limit=candidate_count)
    if not candidates:
        write_selected_papers([], output_dir)
        write_daily_index(output_dir)
        return output_dir

    llm_params = OmegaConf.to_container(config.llm, resolve=True) if hasattr(config, "llm") else None
    reranked = executor.reranker.rerank(candidates, corpus)
    llm_scores: dict[str, dict[str, Any]] = {}
    llm_summary: dict[str, str] = {}
    if llm_selection_enabled and executor.openai_client is not None and llm_params is not None:
        llm_pool = reranked[: min(llm_rerank_count, len(reranked))]
        logger.info(f"Sending {len(llm_pool)} title/abstract candidates to Qwen for scientific-value scoring...")
        try:
            reranked, llm_scores, llm_summary, _ = rank_candidates_with_llm_batched(
                llm_pool,
                executor.openai_client,
                llm_params,
                batch_size=llm_selection_batch_size,
            )
            write_llm_ranking(reranked, llm_scores, output_dir, summary=llm_summary)
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
