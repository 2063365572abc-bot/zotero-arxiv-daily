from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import time
from typing import Any
from urllib.parse import quote

from loguru import logger
from omegaconf import DictConfig, OmegaConf
from openai import OpenAI
from pyzotero import zotero
from pyzotero._upload import Zupload
import pymupdf
import requests

from .executor import Executor
from .protocol import Paper, _request_llm
from .research_state import (
    ResearchRadarState,
    _title_fingerprint,
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

QUICK_LOOK_FIELDS = [
    "研究背景",
    "核心假设或问题",
    "方法逻辑",
    "主要结果",
    "真正贡献",
    "与你研究方向的关系",
    "局限性",
    "是否值得精读",
    "发表状态",
]

DAILY_ZOTERO_COLLECTION_PATH = ["一多科研", "每日更新"]

QUICK_LOOK_CARD_SECTION_PREFIXES = [
    "01 基本信息",
    "03 研究问题",
    "04 研究背景与发展路径",
    "06 核心思想",
    "07 方法总览",
    "08 核心模块拆解",
    "10 实验设计与证据链",
    "11 对结论的正确理解",
    "12 作者明确承认的限制",
    "13 批判性分析",
    "15 与既有知识的连接",
]

CHINA_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")
ARXIV_VERSION_RE = re.compile(r"v\d+$", re.IGNORECASE)
MARKDOWN_HTML_TAG_RE = re.compile(r"</?[a-z][^>]*>", re.IGNORECASE)
WECHAT_FORMULA_RE = re.compile(r"(`|\$|\\\(|\\\[|\\frac|\\sum|\\int|\b[A-Za-z]_[A-Za-z0-9]|\b[A-Za-z]\^[A-Za-z0-9]|[ℍℝ∈∉∑∫√±µμσλ∗])")


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
    published_date: str | None = None


def daily_output_dir(root: str | Path = "outputs/daily", date: datetime | None = None) -> Path:
    date = date or datetime.now(CHINA_TZ)
    return Path(root) / date.strftime("%Y-%m-%d")


def write_json(path: str | Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def canonical_arxiv_id(arxiv_id: str | None) -> str:
    value = str(arxiv_id or "").strip()
    if not value:
        return ""
    value = value.rstrip("/").rsplit("/", 1)[-1]
    value = re.sub(r"\.pdf$", "", value, flags=re.IGNORECASE)
    return ARXIV_VERSION_RE.sub("", value).lower()


def paper_identity_key(paper: Paper) -> str:
    arxiv_id = canonical_arxiv_id(getattr(paper, "arxiv_id", None))
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{_title_fingerprint(paper.title)}"


def _score_for_paper(llm_scores: dict[str, dict[str, Any]], paper: Paper) -> dict[str, Any]:
    return llm_scores.get(paper_identity_key(paper)) or llm_scores.get(paper.title, {})


def _wechat_readability_errors(markdown: str, prefix: str) -> list[str]:
    errors: list[str] = []
    if MARKDOWN_HTML_TAG_RE.search(markdown):
        errors.append(f"{prefix}_contains_html_tag")
    if WECHAT_FORMULA_RE.search(markdown):
        errors.append(f"{prefix}_contains_formula_markup")
    return errors


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


DIRECT_RESEARCH_ANCHORS = [
    "single-cell",
    "single cell",
    "scRNA",
    "spatial transcript",
    "spatial omics",
    "spatial gene expression",
    "transcriptomic",
    "multi-omic",
    "multi-omics",
    "multiomics",
    "cell state",
    "cell atlas",
    "cell foundation",
    "cellular neighborhood",
    "cell-cell communication",
]


def _direct_research_anchor_score(paper: Paper) -> int:
    text = f"{paper.title}\n{paper.abstract}".lower()
    return sum(1 for term in DIRECT_RESEARCH_ANCHORS if term.lower() in text)


def _require_relevant_top3(
    papers: list[Paper],
    llm_scores: dict[str, dict[str, Any]],
    count: int,
) -> list[Paper]:
    eligible = [
        paper
        for paper in papers
        if float(_score_for_paper(llm_scores, paper).get("relevance_to_user", 0)) >= 4.0
    ]
    strong = [
        paper
        for paper in papers
        if float(_score_for_paper(llm_scores, paper).get("relevance_to_user", 0)) >= 5.0
    ]
    direct_eligible = [paper for paper in eligible if _direct_research_anchor_score(paper) >= 1]
    direct_strong = [paper for paper in strong if _direct_research_anchor_score(paper) >= 1]
    required_strong = min(2, count)
    if not direct_eligible:
        raise RuntimeError(
            "no_relevant_candidates: "
            f"Qwen found {len(direct_strong)} direct strong candidates (>=5) and {len(direct_eligible)} direct usable candidates (>=4); "
            "refusing to deep-read or upload unrelated papers"
        )
    if len(direct_eligible) < count or len(direct_strong) < required_strong:
        logger.warning(
            "Proceeding with partial high-relevance selection: "
            f"Qwen found {len(direct_strong)} direct strong candidates (>=5) and "
            f"{len(direct_eligible)} direct usable candidates (>=4); target was "
            f"{required_strong} direct strong and {count} direct usable candidates."
        )
    return direct_eligible


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
            available = [paper for paper in remaining if _score_for_paper(llm_scores, paper)]
            if not available:
                break
            field = role_fields[role]
            chosen = max(available, key=lambda paper: _score_for_paper(llm_scores, paper)[field])
            role_selected.append(chosen)
            remaining.remove(chosen)
        ranked = role_selected + [paper for paper in ranked if paper not in role_selected]
        direct_pool = [
            paper for paper in ranked
            if _direct_research_anchor_score(paper) >= 1
        ]
        if len(direct_pool) >= count:
            ranked = sorted(
                direct_pool,
                key=lambda paper: (
                    _score_for_paper(llm_scores, paper)["total"],
                    _direct_research_anchor_score(paper),
                    paper.score if paper.score is not None else -1,
                ),
                reverse=True,
            ) + [paper for paper in ranked if paper not in direct_pool]
    selected = []
    for index, paper in enumerate(ranked[:count]):
        role = roles[index] if index < len(roles) else "best_match"
        llm_score = _score_for_paper(llm_scores or {}, paper) or None
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
                published_date=getattr(paper, "published_date", None),
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

严格降权规则：
- 如果论文不直接涉及 single-cell、spatial transcriptomics、transcriptomics、multi-omics、cell state、perturbation、biomedical AI 中至少一个主题，relevance_to_user 最高只能给 4 分；
- 如果只是通用机器学习、时序预测、编译优化、地球观测、表格模型、纯数学/物理方法，method_novelty 可以高，但 best_role 不要给 best_match；
- 只有在候选池中直接生物/单细胞/空间组学论文不足 3 篇时，才允许选择纯方法启发论文进入 Top3；
- 单细胞/空间/多组学方向的直接论文优先级高于泛化方法论文。

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
    content = _request_llm_with_retry(
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
        scores[paper_identity_key(paper)] = {
            **values,
            "total": round(total, 2),
            "best_role": str(item.get("best_role") or "best_match"),
            "reason": str(item.get("reason") or "未提供筛选理由"),
            "risk": str(item.get("risk") or "未提供风险说明"),
        }
    if len(scores) < len(papers):
        raise ValueError(f"LLM selection returned {len(scores)} of {len(papers)} candidates")
    ranked = sorted(papers, key=lambda paper: _score_for_paper(scores, paper)["total"], reverse=True)
    for paper in ranked:
        paper.score = _score_for_paper(scores, paper)["total"]
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
                **_score_for_paper(scores, paper),
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
        try:
            _, batch_scores, batch_summary = rank_candidates_with_llm(
                batch,
                openai_client,
                llm_params,
                include_summary=True,
            )
            calls += 1
        except ValueError as exc:
            # Qwen can occasionally omit one JSON row despite a valid response.
            # Retry that batch once; a second incomplete response still fails
            # closed so an unscored paper can never enter Top3 by accident.
            if "LLM selection returned" not in str(exc):
                raise
            logger.warning(f"Retrying incomplete LLM selection batch: {exc}")
            _, batch_scores, batch_summary = rank_candidates_with_llm(
                batch,
                openai_client,
                llm_params,
                include_summary=True,
            )
            calls += 2
        all_scores.update(batch_scores)
        if batch_summary.get("trend_summary"):
            trend_parts.append(batch_summary["trend_summary"])
        if batch_summary.get("rejected_summary"):
            rejected_parts.append(batch_summary["rejected_summary"])

    if len(all_scores) < len(papers):
        raise ValueError(f"LLM batched selection returned {len(all_scores)} of {len(papers)} candidates")
    ranked = sorted(papers, key=lambda paper: _score_for_paper(all_scores, paper)["total"], reverse=True)
    for paper in ranked:
        paper.score = _score_for_paper(all_scores, paper)["total"]
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


def _paper_evidence_inventory(pages: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Build a small, page-grounded inventory before asking the model to read."""
    figures: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    equations: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    caption_re = re.compile(r"^\s*(Figure|Fig\.|Table)\s+(\d+[A-Za-z]?)\s*[:.]?\s*(.*)$", re.I)
    equation_re = re.compile(r"(?:^|\s)[(（](\d{1,3})[)）]\s*$")

    for page in pages:
        lines = str(page.get("text") or "").splitlines()
        for index, line in enumerate(lines):
            match = caption_re.match(line)
            if match:
                kind = "Table" if match.group(1).lower().startswith("table") else "Figure"
                number = match.group(2)
                key = (kind, number)
                if key not in seen:
                    seen.add(key)
                    caption_lines = [match.group(3).strip()]
                    for following in lines[index + 1 : index + 4]:
                        following = " ".join(following.split())
                        if not following or caption_re.match(following):
                            break
                        caption_lines.append(following)
                    item = {
                        "id": f"{kind} {number}",
                        "caption": " ".join(part for part in caption_lines if part),
                        "pdf_page": page["page"],
                    }
                    (tables if kind == "Table" else figures).append(item)
            equation_context = " ".join(lines[max(0, index - 3) : index + 1])
            equation_match = equation_re.search(line)
            if equation_match and not re.search(r"=|∈|∼|⊙|→|∥|≤|≥|≠|\barg\b", equation_context):
                equation_match = None
            if equation_match:
                number = equation_match.group(1)
                key = ("Equation", number)
                if key not in seen:
                    seen.add(key)
                    equations.append(
                        {
                            "id": f"Equation {number}",
                            "context": equation_context,
                            "pdf_page": page["page"],
                        }
                    )

    def natural_key(item: dict[str, Any]) -> tuple[int, str]:
        match = re.search(r"(\d+)([A-Za-z]?)$", str(item.get("id") or ""))
        return (int(match.group(1)), match.group(2)) if match else (999999, str(item.get("id") or ""))

    return {
        "figures": sorted(figures, key=natural_key),
        "tables": sorted(tables, key=natural_key),
        "equations": sorted(equations, key=natural_key),
    }


def extract_source_bundle(pdf_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    pdf_path = Path(pdf_path)
    doc = pymupdf.open(pdf_path)
    pages = []
    for page_index, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        blocks = []
        for block_index, block in enumerate(page.get_text("blocks"), start=1):
            block_text = str(block[4] or "").strip() if len(block) > 4 else ""
            if block_text:
                blocks.append({"block": block_index, "text": block_text})
        pages.append(
            {
                "page": page_index,
                "pdf_page": page_index,
                "text": text,
                "character_count": len(text),
                "blocks": blocks,
            }
        )
    evidence_inventory = _paper_evidence_inventory(pages)
    total_characters = sum(page["character_count"] for page in pages)
    extraction_confidence = "high" if all(page["character_count"] >= 50 for page in pages) else "mixed"
    bundle = {
        "schema_version": "1.1",
        "source_type": "pdf",
        "pdf_sha256": _file_sha256(pdf_path),
        "source_sha256": _file_sha256(pdf_path),
        "page_count": doc.page_count,
        "pages": pages,
        "sections": [
            {"title": line.strip(), "pdf_page": page["page"]}
            for page in pages
            for line in page["text"].splitlines()
            if re.match(r"^\s*(?:\d+(?:\.\d+)*\s+)?[A-Z][A-Za-z0-9 ,/&-]{2,80}\s*$", line.strip())
        ],
        "evidence_inventory": evidence_inventory,
        "figures": evidence_inventory["figures"],
        "tables": evidence_inventory["tables"],
        "extraction": {
            "engine": "PyMuPDF",
            "total_characters": total_characters,
            "confidence": extraction_confidence,
            "visual_pages_rendered": False,
        },
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


def _source_text_for_full_card(
    bundle: dict[str, Any], max_chars: int | None = 55_000, require_full_source: bool = False
) -> str:
    chunks: list[str] = []
    total = 0
    for page in bundle.get("pages", []):
        text = _clean_text(page.get("text", ""))
        if not text:
            continue
        page_no = int(page.get("page") or len(chunks) + 1)
        block = f"[Paper: PDF p. {page_no}]\n{text}\n"
        if max_chars is not None and total + len(block) > max_chars:
            if require_full_source:
                raise ValueError(
                    f"full_source_exceeds_limit: chars={total + len(block)} limit={max_chars}"
                )
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


def _request_llm_with_retry(
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    messages: list[dict[str, str]],
    *,
    force_json: bool = False,
    attempts: int = 3,
) -> str:
    last_error: Exception | None = None
    params = dict(llm_params)
    generation_kwargs = dict(params.get("generation_kwargs", {}))
    generation_kwargs.setdefault("timeout", 120)
    params["generation_kwargs"] = generation_kwargs
    for attempt in range(1, attempts + 1):
        try:
            return _request_llm(openai_client, params, messages, force_json=force_json)
        except Exception as exc:
            last_error = exc
            status_code = getattr(exc, "status_code", None)
            if status_code in {400, 401, 403}:
                raise RuntimeError("llm_request_failed_non_retriable") from exc
            if attempt >= attempts:
                break
            delay = min(2 ** (attempt - 1), 8)
            logger.warning(
                f"LLM request failed; retrying attempt {attempt + 1}/{attempts} in {delay}s: "
                f"{type(exc).__name__}: {exc}"
            )
            time.sleep(delay)
    raise RuntimeError(f"llm_request_failed_after_{attempts}_attempts") from last_error


def build_one_shot_full_card_prompt(
    paper: SelectionRecord,
    bundle: dict[str, Any],
    max_input_chars: int = 160_000,
    require_full_source: bool = True,
) -> str:
    source_text = _source_text_for_full_card(
        bundle,
        max_chars=max_input_chars,
        require_full_source=require_full_source,
    )
    inventory = bundle.get("evidence_inventory", {}) or {}
    inventory_text = json.dumps(inventory, ensure_ascii=False, indent=2)
    return f"""
你正在执行用户的“一多科研”单篇论文深读流程。请一次性输出一个完整的 Paper Card Markdown。

硬性要求：
- 只输出 Markdown，不要解释你将如何做。
- 中文解释，保留英文技术名词、模型名、数据集名、指标、公式符号。
- 不要夸大，不要伪造。
- 每个实质性论文事实都带来源指针，例如 [Paper: PDF p. 1]；页码必须来自输入文本的页码标记。
- 你的判断用 [Analysis]，研究想法用 [Hypothesis]。
- 不足以判断就写 Not assessable from supplied material。
- 作者明确限制和你的批判性分析分开。
- 必须完整覆盖输入中的主要 Figure、Table、Equation，并在相关章节中明确提及。
- 不要凭标题或常识补写作者机构、正式发表信息、代码地址或数据地址；这些信息不在本文证据中时写未核验。

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

输入源清单（必须覆盖）：
{inventory_text}

论文元数据：
Title: {paper.title}
Source: {paper.source}
URL: {paper.url}
PDF URL: {paper.pdf_url or "missing"}
Authors: {", ".join(paper.authors[:12])}
Published: {paper.published_date or "unknown"}
Abstract: {paper.abstract}
Selection role: {paper.role}
Selection reason: {paper.selection_reason}

论文全文，已逐页带 PDF 页码指针。下面内容是本次请求的完整输入，不得假设未提供的章节：
{source_text}
"""


def generate_one_shot_full_card_markdown(
    paper: SelectionRecord,
    bundle: dict[str, Any],
    output_path: str | Path,
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    max_input_chars: int = 160_000,
    max_output_tokens: int = 12_000,
    require_full_source: bool = True,
) -> dict[str, Any]:
    prompt = build_one_shot_full_card_prompt(
        paper,
        bundle,
        max_input_chars=max_input_chars,
        require_full_source=require_full_source,
    )
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
        "source_pages": len(bundle.get("pages", [])),
        "source_characters": sum(int(page.get("character_count", 0)) for page in bundle.get("pages", [])),
        "source_fully_included": bool(require_full_source),
        "evidence_inventory": {
            key: len(value or []) for key, value in (bundle.get("evidence_inventory", {}) or {}).items()
        },
        "model": generation_kwargs.get("model"),
        "max_input_chars": max_input_chars,
        "max_output_tokens": generation_kwargs["max_tokens"],
    }


def _card_excerpt_for_quick_look(card_markdown: str, max_chars: int = 8_000) -> str:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", card_markdown))
    if not matches:
        if len(card_markdown) <= max_chars:
            return card_markdown
        return card_markdown[:max_chars].rstrip() + "\n\n[Card excerpt truncated for quick look]"

    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(card_markdown)
        sections[heading] = card_markdown[start:end].strip()

    blocks: list[str] = []
    for prefix in QUICK_LOOK_CARD_SECTION_PREFIXES:
        for heading, body in sections.items():
            if heading.startswith(prefix):
                blocks.append(body)
                break
    if not blocks:
        if len(card_markdown) <= max_chars:
            return card_markdown
        return card_markdown[:max_chars].rstrip() + "\n\n[Card excerpt truncated for quick look]"

    excerpt = "\n\n".join(blocks)
    if len(excerpt) <= max_chars:
        return excerpt

    budget_per_block = max(700, max_chars // max(len(blocks), 1))
    shortened: list[str] = []
    for block in blocks:
        if len(block) <= budget_per_block:
            shortened.append(block)
        else:
            shortened.append(block[:budget_per_block].rstrip() + "\n[Section truncated for quick look]")
    excerpt = "\n\n".join(shortened)
    if len(excerpt) <= max_chars:
        return excerpt
    return excerpt[:max_chars].rstrip() + "\n\n[Card excerpt truncated for quick look]"


def build_paper_quick_look_prompt(
    paper: SelectionRecord,
    card_markdown: str,
    max_input_chars: int = 8_000,
) -> str:
    card_excerpt = _card_excerpt_for_quick_look(card_markdown, max_chars=max_input_chars)
    return f"""
你是“一多科研”的论文速读编辑。下面是一篇已经完成的完整 Paper Card。
请只把 Card 中已有内容整理成一份适合手机快速阅读的“论文速看”。

这是压缩、重排和改写任务，不是重新分析论文：
- 只能使用下面 Card 中出现的信息；
- 不得联网，不得调用常识补充信息；
- 不得编造或推断发布日期、作者、机构、期刊、实验结果、代码或数据；
- 数字、指标、模型名、数据集名和结论限定条件必须忠实保留；
- Card 没有明确支持的内容写“Card未提供”，不要自行补全；
- 将作者声称、实验结果和分析判断保持原有边界，不要把结论说得更强。
- 以专业科研编辑的标准压缩内容：每个栏目保留最关键的信息和必要证据，不复述 Card 的项目符号清单。
- 面向早晨手机阅读：语言必须清楚、短句、少黑话；遇到公式、变量、上下标、LaTeX 或 HTML 标记，不要照抄，只用一句中文解释它解决什么问题。
- 不得输出反引号代码、HTML 标签、数学公式、变量下标、特殊数学符号；模型名、数据集名、指标名可以保留，但具体公式和多项指标要压缩成自然语言。

基本元数据（只能原样整理，不能改写）：
- 标题：{paper.title}
- 发布时间：{paper.published_date or 'Card未提供'}
- 来源：{paper.source}；arXiv ID：{paper.arxiv_id or 'Card未提供'}
- 原文链接：{paper.url}

只输出 Markdown，不要输出代码块、JSON、解释或免责声明。
全文控制在 2,200 个中文字符以内；每个栏目按信息复杂度写 1—3 个短句，避免展开成长清单。
严格使用以下格式和顺序：

## {paper.title}

**标题与发布时间**
{paper.title}（{paper.published_date or 'Card未提供'}）

**作者和机构**
从 Card 的“01 基本信息”中整理；没有就写“Card未提供”。

**发表状态**
从 Card 的“01 基本信息”中提取 Publication、Source、发表平台、Journal、Venue、Conference 或期刊信息。
如果是 arXiv/bioRxiv/medRxiv/chemRxiv 预印本，明确写“arXiv 预印本”或对应预印本平台。
如果 Card 没有正式期刊、会议或发表状态，写“Card未提供”，不得联网查询，不得自行补充。

**研究背景**
只压缩 Card 第 04 节。

**核心假设或问题**
只压缩 Card 第 03 节和相关核心思想，不新增假设。

**方法逻辑**
用“输入、核心方法、输出”整理 Card 第 07—08 节；不要展示公式或变量名，要解释方法直觉和流程。

**主要结果**
只整理 Card 第 10—11 节已有的结果和结论。

**真正贡献**
只提炼 Card 第 06—07 节已经支持的贡献，不使用夸大性宣传语。

**与你研究方向的关系**
只整理 Card 第 15 节中关于空间转录组、机器学习、单细胞、多组学或相关方法的连接。

**局限性**
压缩 Card 第 12—13 节，区分作者明确限制和 Card 已有的批判性风险。

**是否值得精读**
根据 Card 已有证据给出“值得精读 / 可以选读 / 暂不推荐”，并用一句话说明理由。

**原文 PDF**：{paper.pdf_url or paper.url}

下面是唯一允许使用的 Card 关键章节摘录：
{card_excerpt}
""".strip()


def audit_paper_quick_look(markdown: str, paper: SelectionRecord) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not markdown.strip():
        errors.append("quick_look_empty")
    if paper.title not in markdown:
        errors.append("quick_look_missing_title")
    for field in QUICK_LOOK_FIELDS:
        if f"**{field}**" not in markdown:
            errors.append(f"quick_look_missing:{field}")
    if not paper.published_date:
        errors.append("quick_look_record_missing_published_date")
    if paper.published_date and paper.published_date not in markdown:
        errors.append("quick_look_missing_canonical_published_date")
    if paper.pdf_url and paper.pdf_url not in markdown and paper.url not in markdown:
        errors.append("quick_look_missing_original_link")
    if "```" in markdown:
        errors.append("quick_look_contains_code_fence")
    errors.extend(_wechat_readability_errors(markdown, "quick_look"))
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "1.0",
        "status": status,
        "character_count": len(markdown),
        "errors": errors,
        "warnings": warnings,
    }


def generate_paper_quick_look_markdown(
    paper: SelectionRecord,
    card_path: str | Path,
    output_path: str | Path,
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    max_input_chars: int = 8_000,
    max_output_tokens: int = 1_200,
) -> dict[str, Any]:
    card_markdown = Path(card_path).read_text(encoding="utf-8")
    prompt = build_paper_quick_look_prompt(paper, card_markdown, max_input_chars=max_input_chars)
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs.pop("stream", None)
    generation_kwargs["max_tokens"] = max_output_tokens
    generation_kwargs["temperature"] = min(float(generation_kwargs.get("temperature", 0.2)), 0.2)
    content = _request_llm_with_retry(
        openai_client,
        {**llm_params, "generation_kwargs": generation_kwargs},
        [
            {
                "role": "system",
                "content": "你是严格的科研 Card 整理器，只根据输入内容输出 Markdown，不添加任何外部事实。",
            },
            {"role": "user", "content": prompt},
        ],
    )
    markdown = _strip_markdown_fence(content)
    audit = audit_paper_quick_look(markdown, paper)
    repair_attempted = False
    if audit["status"] == "fail":
        repair_attempted = True
        repair_prompt = f"""
下面这份论文速看没有通过审计：{audit['errors']}。
请只根据原始 Card 摘录重写，不要新增任何事实，不要联网，不要改变标题、发布时间和链接。
必须去掉 HTML 标签、代码反引号、LaTeX、公式、变量下标、特殊数学符号，把它们改写成自然语言。
仍然严格使用原来的 Markdown 栏目顺序和字段名。

不合格版本：
{markdown}

原始任务和 Card 摘录：
{prompt}
""".strip()
        repaired = _request_llm_with_retry(
            openai_client,
            {**llm_params, "generation_kwargs": generation_kwargs},
            [
                {
                    "role": "system",
                    "content": "你是严格的科研 Card 整理器，只做格式和可读性修复，不添加任何外部事实。",
                },
                {"role": "user", "content": repair_prompt},
            ],
        )
        markdown = _strip_markdown_fence(repaired)
        audit = audit_paper_quick_look(markdown, paper)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    write_json(output_path.with_suffix(".json"), {
        "status": "generated" if audit["status"] != "fail" else "failed_audit",
        "prompt_chars": len(prompt),
        "card_chars": len(card_markdown),
        "quick_look_chars": len(markdown),
        "model": generation_kwargs.get("model"),
        "repair_attempted": repair_attempted,
        "audit": audit,
    })
    if audit["status"] == "fail":
        raise ValueError(f"paper_quick_look_audit_failed: {audit['errors']}")
    return {
        "status": "paper_quick_look",
        "prompt_chars": len(prompt),
        "card_chars": len(card_markdown),
        "quick_look_chars": len(markdown),
        "model": generation_kwargs.get("model"),
        "repair_attempted": repair_attempted,
        "audit": audit,
    }


def generate_daily_quote(
    output_path: str | Path,
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    max_output_tokens: int = 120,
) -> dict[str, Any]:
    prompt = (
        "请生成一句简短、克制、有启发性的原创中文科研寄语，适合放在早晨的科研论文速递开头。"
        "不要冒充名人名言，不要添加作者、出处、引号或解释，只输出一句话。"
    )
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs.pop("stream", None)
    generation_kwargs["max_tokens"] = max(int(generation_kwargs.get("max_tokens") or 0), max_output_tokens)
    generation_kwargs["temperature"] = max(float(generation_kwargs.get("temperature", 0.2)), 0.6)
    content = _request_llm_with_retry(
        openai_client,
        {**llm_params, "generation_kwargs": generation_kwargs},
        [
            {"role": "system", "content": "你是简洁、克制的中文科研晨间编辑。"},
            {"role": "user", "content": prompt},
        ],
    )
    quote = re.sub(r"\s+", " ", (content or "").strip()).strip("`#> \t")
    if not quote:
        raise ValueError("daily_quote_empty")
    if len(quote) > 80:
        quote = quote[:79].rstrip() + "…"
    result = {
        "status": "generated",
        "quote": quote,
        "model": generation_kwargs.get("model"),
        "prompt_chars": len(prompt),
    }
    write_json(output_path, result)
    return result


def build_three_card_digest_prompt(
    papers: list[SelectionRecord],
    card_markdowns: list[str],
    max_input_chars: int = 180_000,
    report_date: str | None = None,
    raw_fetched_count: int | None = None,
    quote: str | None = None,
    card_pdf_links: list[str] | None = None,
) -> str:
    if len(papers) != len(card_markdowns):
        raise ValueError("papers_and_cards_length_mismatch")
    blocks: list[str] = []
    total = 0
    for index, (paper, card) in enumerate(zip(papers, card_markdowns), start=1):
        card_pdf_link = (card_pdf_links or [""] * len(papers))[index - 1]
        published_date = _published_date_label(getattr(paper, "published_date", None)) or "unknown"
        block = (
            f"\n===== PAPER QUICK LOOK {index} =====\n"
            f"Title: {paper.title}\n"
            f"arXiv ID: {paper.arxiv_id or 'unknown'}\n"
            f"URL: {paper.url}\n"
            f"Published date: {published_date}\n"
            f"Original PDF URL: {paper.pdf_url or paper.url}\n"
            f"Card PDF link: {card_pdf_link or 'not provided'}\n"
            f"Selection role: {paper.role}\n"
            f"QUICK LOOK CONTENT:\n{card}\n"
        )
        total += len(block)
        if total > max_input_chars:
            raise ValueError(
                f"three_cards_exceed_limit: chars={total} limit={max_input_chars}"
            )
        blocks.append(block)

    report_date = report_date or datetime.now(CHINA_TZ).strftime("%Y-%m-%d")
    fetched = raw_fetched_count if raw_fetched_count is not None else "未记录"
    paper_count = len(papers)
    reading_order = " → ".join(f"{index:02d}" for index in range(1, paper_count + 1))
    quote_text = quote.strip() if quote and quote.strip() else ""
    quote_block = f"\n> {quote_text}\n" if quote_text else ""
    return f"""
你是“一多科研”的高级科研新闻速递编辑。下面提供的是 {paper_count} 篇已经完成全文深读后生成的“论文速看”。
请将它们整理成一份高级、简约、适合手机阅读的 Markdown 科研新闻速递。

输入边界：
- 论文内容只能来自下面 {paper_count} 篇 PAPER QUICK LOOK；不要重新分析 PDF；
- 标题、发布日期、作者、机构、链接必须使用输入中的值，不得修改、猜测或补充；
- 不得联网，不得添加论文 Card 之外的新事实；
- 今日首轮抓取数量必须原样使用：{fetched}；
- 今日寄语必须原样使用，不要改写；
- 只输出最终 Markdown，不要输出解释、免责声明、审计内容、JSON、HTML 或代码块。

内容要求：
- 开头标题必须是“每日速看”四个字，下面放日期、早上好和今日寄语；
- “今日主线”必须根据实际入选的 {paper_count} 篇速看动态生成，不能使用固定套话；
- 明确写出“今日首次从 arXiv 抓取 {fetched} 篇候选论文，最终精选 {len(papers)} 篇”；
- 每篇论文标题必须使用大号标题；日期和来源放在标题下方的独立信息行；
- 每篇必须先写“速读判断”，用引用块 `>` 写 1—2 句专业判断，说明这篇真正值得看的点；
- 每篇必须展示：发布时间与来源、作者和机构、发表状态、研究背景、核心假设或问题、方法逻辑、主要结果、真正贡献、与你研究方向的关系、局限性、是否值得精读；
- 每个栏目按信息复杂度写 1—3 个短句，避免展开成长清单；单篇正文控制在约 650—900 个中文字符，今日主线控制在约 150—220 个中文字符；
- 不要复制 Card 的项目符号清单、公式、变量名或多条指标；只保留最关键的一条证据；
- 方法逻辑必须像给科研同事做晨间速递：解释“它输入什么、怎么建模、输出什么”，不要展示公式、LaTeX、上下标变量、特殊数学符号或反引号代码；
- 如果输入中有公式或变量，只翻译成自然语言机制，例如“用一个可分解的邻域影响分数衡量细胞互作”，不要写变量表达式；
- 每篇结尾必须有原文 PDF 下载链接和 Paper Card PDF 下载链接；链接必须使用输入中的值；
- 结尾给出简短的今日精读顺序；
- 语言像专业科研新闻速递：克制、清楚、密度高，不写宣传口号；优先讲研究问题和判断，不堆砌术语。
- 全文不得超过 6,500 个中文字符；每篇论文正文控制在 650—900 个中文字符；
- 每个栏目最多 1 个短段落，不得复制输入中的长列表、公式、多个指标或逐条实验结果；
- 版式要好看但保持纯 Markdown：使用标题、引用块、粗体字段和分隔线；不要使用 HTML、表格、emoji 或复杂装饰符；
- “主要结果”最多保留最有代表性的 1—2 个结果，“局限性”最多保留最关键的 1—2 个限制；
- “真正贡献”和“与你研究方向的关系”必须是压缩后的专业判断，各不超过 2 句。

最终格式：

# 每日速看

**{report_date}**

早上好，一多。
{quote_block}
---

## 今日主线

根据实际入选论文速看动态生成一段简洁的研究趋势概览。

---

# 01｜论文标题

**发布时间 · 来源**
必须填写该篇 PAPER QUICK LOOK 中的准确日期；没有日期才写“Card未提供”，不得写 unknown。

> **速读判断**：用 1—2 句讲清楚这篇真正值得看的点，语气像专业科研博主的判断，不要复述摘要。

**作者和机构**

**发表状态**

**研究背景**

**核心假设或问题**

**方法逻辑**

**主要结果**

**真正贡献**

**与你研究方向的关系**

**局限性**

**是否值得精读**

[原文 PDF](...) · [下载 Paper Card](...)

---

# 02｜论文标题

如果有第 2 篇及后续论文，均按相同结构继续整理，编号到第 {paper_count} 篇为止；不要新增不存在的论文。

---

## 今日精读顺序

给出 {reading_order} 的简短排序理由；如果只有 1 篇，就说明它为什么值得今天优先精读。

实际入选论文速看如下：
{''.join(blocks)}
""".strip()


def _strip_markdown_fence(text: str) -> str:
    value = (text or "").strip()
    match = re.fullmatch(r"```(?:markdown|md)?\s*(.*?)\s*```", value, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else value


def audit_three_card_digest(
    markdown: str,
    papers: list[SelectionRecord],
    report_date: str | None = None,
    raw_fetched_count: int | None = None,
    card_pdf_links: list[str] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not markdown.strip():
        errors.append("digest_empty")
    if report_date and report_date not in markdown:
        errors.append("digest_wrong_or_missing_report_date")
    errors.extend(_wechat_readability_errors(markdown, "digest"))
    if "每日速看" not in markdown:
        errors.append("digest_missing_newsletter_title")
    for heading in ("今日主线", "今日精读顺序"):
        if heading not in markdown:
            errors.append(f"digest_missing:{heading}")
    for index, paper in enumerate(papers, start=1):
        if f"### {index}." not in markdown and f"{index}. {paper.title}" not in markdown:
            if f"# {index:02d}｜" not in markdown:
                errors.append(f"digest_missing_paper_slot:{index}")
        if paper.title not in markdown:
            errors.append(f"digest_missing_title:{paper.arxiv_id or paper.title}")
        if paper.url and paper.url not in markdown and (not paper.pdf_url or paper.pdf_url not in markdown):
            warnings.append(f"digest_missing_url:{paper.arxiv_id or paper.title}")
        if not paper.published_date:
            errors.append(f"digest_record_missing_published_date:{paper.arxiv_id or paper.title}")
        published_date = _published_date_label(paper.published_date)
        if published_date and published_date not in markdown:
            errors.append(f"digest_missing_published_date:{paper.arxiv_id or paper.title}")
        if published_date and paper.source:
            expected_source_line = f"{published_date} · {_source_label(paper.source)}"
            if expected_source_line not in markdown:
                errors.append(f"digest_missing_published_source:{paper.arxiv_id or paper.title}")
        if paper.pdf_url and paper.pdf_url not in markdown:
            warnings.append(f"digest_missing_original_pdf_url:{paper.arxiv_id or paper.title}")
        if card_pdf_links and index <= len(card_pdf_links):
            link = card_pdf_links[index - 1]
            if link and link not in markdown:
                errors.append(f"digest_missing_card_pdf_link:{paper.arxiv_id or paper.title}")
        if markdown.count("**速读判断**") < len(papers):
            errors.append(f"digest_missing:速读判断:{index}")
        for field in QUICK_LOOK_FIELDS:
            if markdown.count(f"**{field}**") < len(papers):
                errors.append(f"digest_missing:{field}:{index}")
    if raw_fetched_count is not None:
        expected = f"首次从 arXiv 抓取 {raw_fetched_count} 篇"
        if expected not in markdown:
            errors.append("digest_missing_canonical_raw_fetched_count")
    reading_order_index = markdown.find("## 今日精读顺序")
    if reading_order_index >= 0:
        reading_order = markdown[reading_order_index:].strip()
        if len(reading_order) < 45 or reading_order[-1] not in "。.!！?？）)":
            errors.append("digest_incomplete_reading_order")
    if len(markdown) > 6_500:
        errors.append("digest_exceeds_maximum_length")
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "1.0",
        "status": status,
        "character_count": len(markdown),
        "errors": errors,
        "warnings": warnings,
    }


def _ensure_digest_fetch_summary(
    markdown: str,
    raw_fetched_count: int | None,
    selected_count: int,
) -> str:
    if raw_fetched_count is None:
        return markdown
    expected = f"首次从 arXiv 抓取 {raw_fetched_count} 篇"
    if expected in markdown:
        return markdown
    line = f"今日首次从 arXiv 抓取 {raw_fetched_count} 篇候选论文，最终精选 {selected_count} 篇。"
    if "\n---\n\n## 今日主线" in markdown:
        return markdown.replace("\n---\n\n## 今日主线", f"\n\n{line}\n\n---\n\n## 今日主线", 1)
    if "## 今日主线" in markdown:
        return markdown.replace("## 今日主线", f"{line}\n\n---\n\n## 今日主线", 1)
    return markdown.rstrip() + f"\n\n{line}\n"


def _source_label(source: str | None) -> str:
    if not source:
        return ""
    if source.lower() == "arxiv":
        return "arXiv"
    return source


def public_report_file_url(base_url: str, report_date: str, filename: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/{quote(report_date)}/{quote(filename)}"


def _published_date_label(value: str | None) -> str:
    if not value:
        return ""
    value = str(value).strip()
    if not value:
        return ""
    if len(value) >= 10 and re.match(r"^\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    return value


def _ensure_digest_source_labels(markdown: str, papers: list[SelectionRecord]) -> str:
    updated = markdown
    for index, paper in enumerate(papers):
        if not paper.published_date or not paper.source:
            continue
        published_date = _published_date_label(paper.published_date)
        if not published_date:
            continue
        label = _source_label(paper.source)
        expected = f"{published_date} · {label}"
        title_start = updated.find(paper.title)
        if title_start < 0:
            continue
        next_starts = [
            pos for other in papers[index + 1:]
            if (pos := updated.find(other.title, title_start + len(paper.title))) >= 0
        ]
        title_end = min(next_starts) if next_starts else len(updated)
        segment = updated[title_start:title_end]
        if expected in segment or published_date not in segment:
            continue
        patched = segment.replace(published_date, expected, 1)
        updated = updated[:title_start] + patched + updated[title_end:]
    return updated


def generate_three_card_digest_markdown(
    papers: list[SelectionRecord],
    card_paths: list[str | Path],
    output_path: str | Path,
    openai_client: OpenAI,
    llm_params: dict[str, Any],
    max_input_chars: int = 180_000,
    max_output_tokens: int = 5_000,
    report_date: str | None = None,
    raw_fetched_count: int | None = None,
    quote: str | None = None,
    card_pdf_links: list[str] | None = None,
) -> dict[str, Any]:
    card_markdowns = [Path(path).read_text(encoding="utf-8") for path in card_paths]
    prompt = build_three_card_digest_prompt(
        papers,
        card_markdowns,
        max_input_chars=max_input_chars,
        report_date=report_date,
        raw_fetched_count=raw_fetched_count,
        quote=quote,
        card_pdf_links=card_pdf_links,
    )
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs.pop("stream", None)
    generation_kwargs["max_tokens"] = max_output_tokens
    generation_kwargs["temperature"] = min(float(generation_kwargs.get("temperature", 0.2)), 0.2)
    content = _request_llm_with_retry(
        openai_client,
        {**llm_params, "generation_kwargs": generation_kwargs},
        [
            {
                "role": "system",
                "content": "You are a rigorous scientific digest editor. Return only compact Markdown.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    markdown = _strip_markdown_fence(content)
    markdown = _ensure_digest_fetch_summary(markdown, raw_fetched_count, len(papers))
    markdown = _ensure_digest_source_labels(markdown, papers)
    audit = audit_three_card_digest(
        markdown,
        papers,
        report_date=report_date,
        raw_fetched_count=raw_fetched_count,
        card_pdf_links=card_pdf_links,
    )
    repair_attempted = False
    if audit["status"] == "fail":
        repair_attempted = True
        repair_prompt = f"""
下面这份每日速看没有通过审计：{audit['errors']}。
请只根据实际入选的 {len(papers)} 篇 PAPER QUICK LOOK 重写，不要新增任何事实，不要联网，不要改动标题、日期、来源或链接。
必须保留“# 每日速看”、报告日期、今日主线、全部实际入选论文和今日精读顺序。
必须去掉 HTML 标签、代码反引号、LaTeX、公式、变量下标、特殊数学符号，把它们改写成自然语言。
仍然保持高级、简约、手机可读的 Markdown 版式。

不合格版本：
{markdown}

原始任务和实际入选 PAPER QUICK LOOK：
{prompt}
""".strip()
        repaired = _request_llm_with_retry(
            openai_client,
            {**llm_params, "generation_kwargs": generation_kwargs},
            [
                {
                    "role": "system",
                    "content": "你是严格的科研速递编辑，只做结构和可读性修复，不添加任何外部事实。",
                },
                {"role": "user", "content": repair_prompt},
            ],
        )
        markdown = _strip_markdown_fence(repaired)
        markdown = _ensure_digest_fetch_summary(markdown, raw_fetched_count, len(papers))
        markdown = _ensure_digest_source_labels(markdown, papers)
        audit = audit_three_card_digest(
            markdown,
            papers,
            report_date=report_date,
            raw_fetched_count=raw_fetched_count,
            card_pdf_links=card_pdf_links,
        )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    write_json(output_path.with_suffix(".json"), {
        "status": "generated" if audit["status"] != "fail" else "failed_audit",
        "prompt_chars": len(prompt),
        "card_count": len(card_paths),
        "card_chars": [len(card) for card in card_markdowns],
        "model": generation_kwargs.get("model"),
        "report_date": report_date,
        "repair_attempted": repair_attempted,
        "audit": audit,
    })
    if audit["status"] == "fail":
        raise ValueError(f"three_card_digest_audit_failed: {audit['errors']}")
    return {
        "status": "three_card_digest",
        "prompt_chars": len(prompt),
        "digest_chars": len(markdown),
        "model": generation_kwargs.get("model"),
        "report_date": report_date,
        "repair_attempted": repair_attempted,
        "audit": audit,
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
    bundle: dict[str, Any] | None = None
    if not bundle_path.exists():
        errors.append("source_bundle_missing")
    else:
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"source_bundle_invalid:{type(exc).__name__}")
    if not card_path.exists():
        errors.append("paper_card_missing")
    else:
        card = card_path.read_text(encoding="utf-8")
        for section in CARD_SECTIONS:
            if f"## {section}" not in card:
                errors.append(f"missing_section:{section}")
        source_pointer_count = card.count("[Paper:")
        if source_pointer_count < 10:
            warnings.append("fewer_than_10_source_refs")
        if "Source coverage: Full paper" not in card:
            warnings.append("card_does_not_claim_full_paper_coverage")
        if "Extraction confidence: Low" in card:
            errors.append("low_extraction_confidence")
        if bundle is not None:
            page_count = int(bundle.get("page_count") or 0)
            invalid_pages = [
                int(match)
                for match in re.findall(r"\[Paper:\s*PDF p\.\s*(\d+)\]", card)
                if int(match) < 1 or int(match) > page_count
            ]
            if invalid_pages:
                errors.append(f"page_pointer_out_of_range:{sorted(set(invalid_pages))}")
            inventory = bundle.get("evidence_inventory", {}) or {}
            for key, label in (("figures", "figure"), ("tables", "table"), ("equations", "equation")):
                items = inventory.get(key, []) if isinstance(inventory, dict) else []
                missing = []
                for item in items:
                    item_id = str(item.get("id") or "")
                    number = re.search(r"(\d+[A-Za-z]?)$", item_id)
                    aliases = [item_id]
                    if number:
                        n = number.group(1)
                        if label == "figure":
                            aliases.extend([f"Figure {n}", f"Fig. {n}", f"图{n}", f"图 {n}"])
                        elif label == "table":
                            aliases.extend([f"Table {n}", f"表{n}", f"表 {n}"])
                        else:
                            aliases.extend([f"Equation {n}", f"Eq. {n}", f"公式{n}", f"公式 {n}"])
                    if not any(alias.lower() in card.lower() for alias in aliases if alias):
                        missing.append(item_id)
                if missing:
                    warnings.append(f"{key}_not_covered:{missing}")
                elif items:
                    logger.debug(f"Card covers all inventoried {key}: {len(items)}")
        if "[Analysis]" not in card:
            warnings.append("missing_analysis_provenance")
        if "[Hypothesis]" not in card:
            warnings.append("missing_hypothesis_provenance")
        analysis_path = folder / "paper_analysis.json"
        if analysis_path.exists():
            try:
                analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
                if analysis.get("source_fully_included") is False:
                    warnings.append("source_excerpted_for_context_limit")
            except (OSError, json.JSONDecodeError):
                warnings.append("paper_analysis_unreadable")
        if "scaffold must be replaced" in card:
            warnings.append("scaffold_card_needs_llm_enrichment")
        if "llm_enrichment_failed" in card or "llm_client_not_configured" in card:
            warnings.append("llm_enrichment_not_completed")

    status = "failed" if errors else ("warning" if warnings else "pass")
    report = {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "card_path": str(card_path),
        "source_bundle_path": str(bundle_path),
        "source_page_count": int((bundle or {}).get("page_count") or 0),
        "source_character_count": int((bundle or {}).get("extraction", {}).get("total_characters") or 0),
    }
    write_json(folder / "audit-report.json", report)
    return report


PDF_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def find_pdf_font_file() -> Path:
    env_font = os.getenv("DAILY_PIPELINE_PDF_FONT_FILE", "").strip()
    candidates = [env_font] if env_font else []
    candidates.extend(PDF_FONT_CANDIDATES)
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    raise RuntimeError(
        "No CJK PDF font found. Install fonts-noto-cjk on Linux or set "
        "DAILY_PIPELINE_PDF_FONT_FILE to a readable Chinese-capable TTF/TTC/OTF font."
    )


def _clean_pdf_markdown_inline(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = text.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    return re.sub(r"\s+", " ", text).strip()


def _pdf_display_units(text: str) -> float:
    units = 0.0
    for char in text:
        code = ord(char)
        if char == "\t":
            units += 4
        elif code <= 0x007F:
            units += 1
        elif 0xFF01 <= code <= 0xFF60:
            units += 2
        elif 0x4E00 <= code <= 0x9FFF:
            units += 2
        else:
            units += 1.7
    return units


def _wrap_pdf_text(text: str, max_units: float) -> list[str]:
    words = re.split(r"(\s+)", text.strip())
    lines: list[str] = []
    current = ""

    def flush_long(segment: str) -> None:
        nonlocal current
        chunk = ""
        for char in segment:
            candidate = f"{chunk}{char}"
            if chunk and _pdf_display_units(candidate) > max_units:
                if current:
                    lines.append(current.rstrip())
                    current = ""
                lines.append(chunk.rstrip())
                chunk = char
            else:
                chunk = candidate
        if chunk:
            if current:
                candidate = f"{current}{chunk}"
                if _pdf_display_units(candidate) <= max_units:
                    current = candidate
                else:
                    lines.append(current.rstrip())
                    current = chunk
            else:
                current = chunk

    for part in words:
        if not part:
            continue
        candidate = f"{current}{part}"
        if _pdf_display_units(part) > max_units:
            flush_long(part)
        elif current and _pdf_display_units(candidate) > max_units:
            lines.append(current.rstrip())
            current = part.lstrip()
        else:
            current = candidate
    if current.strip():
        lines.append(current.rstrip())
    return lines or [""]


def export_markdown_to_pdf(markdown_path: str | Path, pdf_path: str | Path) -> None:
    markdown_path = Path(markdown_path)
    pdf_path = Path(pdf_path)
    text = markdown_path.read_text(encoding="utf-8")
    font_file = find_pdf_font_file()

    width, height = 595, 842
    margin = 42
    content_width = width - (margin * 2)
    font_name = "YiDuoCJK"
    doc = pymupdf.open()
    page = doc.new_page(width=width, height=height)
    y = margin

    def ensure_space(required: float) -> None:
        nonlocal page, y
        if y + required > height - margin:
            page = doc.new_page(width=width, height=height)
            y = margin

    def draw_line(
        line: str,
        *,
        size: float,
        color: tuple[float, float, float] = (0, 0, 0),
        x_offset: float = 0,
        line_height: float | None = None,
    ) -> None:
        nonlocal y
        actual_line_height = line_height if line_height is not None else size * 1.55
        ensure_space(actual_line_height)
        page.insert_text(
            (margin + x_offset, y),
            line,
            fontsize=size,
            fontname=font_name,
            fontfile=str(font_file),
            color=color,
        )
        y += actual_line_height

    def draw_wrapped(
        body: str,
        *,
        size: float = 9.6,
        color: tuple[float, float, float] = (0.08, 0.08, 0.08),
        x_offset: float = 0,
        max_units: float = 84,
        spacing_after: float = 5,
    ) -> None:
        nonlocal y
        for line in _wrap_pdf_text(body, max_units):
            draw_line(line, size=size, color=color, x_offset=x_offset)
        y += spacing_after

    def draw_heading(title: str) -> None:
        nonlocal y
        y += 8
        ensure_space(32)
        rect = pymupdf.Rect(margin - 6, y - 16, margin + content_width + 6, y + 8)
        page.draw_rect(rect, fill=(0.93, 0.96, 0.99), color=(0.78, 0.84, 0.92), width=0.4)
        draw_line(title, size=12.8, color=(0.04, 0.12, 0.22), line_height=20)
        y += 4

    def is_table_row(line: str) -> bool:
        stripped_line = line.strip()
        return stripped_line.startswith("|") and stripped_line.endswith("|") and "|" in stripped_line[1:-1]

    def is_table_separator(line: str) -> bool:
        return bool(re.match(r"^\s*\|?[-:\s|]+\|?\s*$", line))

    def split_table_row(line: str) -> list[str]:
        return [_clean_pdf_markdown_inline(cell.strip()) for cell in line.strip().strip("|").split("|")]

    def draw_table(table_lines: list[str]) -> None:
        nonlocal y
        rows = [split_table_row(line) for line in table_lines if not is_table_separator(line)]
        rows = [[cell for cell in row] for row in rows if any(cell for cell in row)]
        if not rows:
            return
        header = rows[0]
        body_rows = rows[1:] if len(rows) > 1 else []
        draw_wrapped(" / ".join(cell for cell in header if cell), size=8.2, color=(0.32, 0.36, 0.42), max_units=100, spacing_after=3)
        for row in body_rows:
            y_before = y
            ensure_space(36)
            for index, cell in enumerate(row):
                if not cell:
                    continue
                label = header[index] if index < len(header) and header[index] else f"Field {index + 1}"
                draw_wrapped(
                    f"{label}: {cell}",
                    size=8.1,
                    color=(0.12, 0.12, 0.12),
                    x_offset=8,
                    max_units=96,
                    spacing_after=1,
                )
            if y == y_before:
                continue
            y += 5

    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.rstrip()
        if not stripped:
            y += 4
            index += 1
            continue

        if stripped.startswith(">"):
            quote = _clean_pdf_markdown_inline(stripped.lstrip("> "))
            draw_wrapped(quote, size=8.5, color=(0.35, 0.38, 0.42), max_units=94, spacing_after=2)
            index += 1
            continue

        heading_match = re.match(r"^#{1,3}\s+(.+)$", stripped)
        if heading_match:
            draw_heading(_clean_pdf_markdown_inline(heading_match.group(1)))
            index += 1
            continue

        if is_table_separator(stripped):
            index += 1
            continue

        if is_table_row(stripped):
            table_lines: list[str] = []
            while index < len(lines) and (is_table_row(lines[index]) or is_table_separator(lines[index])):
                table_lines.append(lines[index])
                index += 1
            draw_table(table_lines)
            continue

        bullet_match = re.match(r"^\s*[-*]\s+(.+)$", stripped)
        if bullet_match:
            draw_wrapped(
                f"- {_clean_pdf_markdown_inline(bullet_match.group(1))}",
                size=9.3,
                x_offset=10,
                max_units=82,
                spacing_after=2,
            )
            index += 1
            continue

        ordered_match = re.match(r"^\s*(\d+)[.)]\s+(.+)$", stripped)
        if ordered_match:
            draw_wrapped(
                f"{ordered_match.group(1)}. {_clean_pdf_markdown_inline(ordered_match.group(2))}",
                size=9.3,
                x_offset=10,
                max_units=82,
                spacing_after=2,
            )
            index += 1
            continue

        draw_wrapped(_clean_pdf_markdown_inline(stripped), max_units=86)
        index += 1

    page_count = len(doc)
    for index, pdf_page in enumerate(doc, start=1):
        footer = f"Paper Card | {markdown_path.stem} | {index}/{page_count}"
        pdf_page.insert_text(
            (margin, height - 22),
            footer,
            fontsize=7.5,
            fontname=font_name,
            fontfile=str(font_file),
            color=(0.45, 0.45, 0.45),
        )

    doc.set_metadata(
        {
            "title": markdown_path.stem,
            "subject": "YiDuo Research Paper Card",
            "creator": "zotero-arxiv-daily",
        }
    )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(pdf_path)

    extracted = "\n".join(page.get_text() for page in pymupdf.open(pdf_path))
    normalized_extracted = re.sub(r"\s+", " ", extracted.replace("\u00a0", " ")).strip()
    if "01 基本信息" not in normalized_extracted or len(normalized_extracted) < 200:
        raise RuntimeError(f"PDF export verification failed for {pdf_path}: extracted text is incomplete.")


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


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    deduped: list[Paper] = []
    seen: set[str] = set()
    for paper in papers:
        key = paper_identity_key(paper)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(paper)
    return deduped


def retrieve_daily_candidates(executor: Executor, candidate_count: int) -> list[Paper]:
    all_papers: list[Paper] = []
    for source, retriever in executor.retrievers.items():
        logger.info(f"Retrieving {source} papers for daily pipeline...")
        papers = retriever.retrieve_papers()
        logger.info(f"Retrieved {len(papers)} {source} papers")
        all_papers.extend(papers)
    all_papers.sort(
        key=lambda paper: (
            str(getattr(paper, "published_date", "") or ""),
            paper.score if paper.score is not None else -1,
        ),
        reverse=True,
    )
    return deduplicate_papers(all_papers)[:candidate_count]


def filter_previously_promoted_candidates(
    candidates: list[Paper],
    *,
    excluded_arxiv_ids: set[str],
    zotero_title_fingerprints: set[str],
    retry_arxiv_ids: set[str] | None = None,
) -> tuple[list[Paper], list[dict[str, str]]]:
    filtered: list[Paper] = []
    excluded: list[dict[str, str]] = []
    retry_arxiv_ids = retry_arxiv_ids or set()
    normalized_excluded_ids = {canonical_arxiv_id(arxiv_id) for arxiv_id in excluded_arxiv_ids}
    normalized_retry_ids = {canonical_arxiv_id(arxiv_id) for arxiv_id in retry_arxiv_ids}
    seen_candidate_keys: set[str] = set()
    for paper in candidates:
        arxiv_id = str(getattr(paper, "arxiv_id", "") or "")
        normalized_arxiv_id = canonical_arxiv_id(arxiv_id)
        title_fingerprint = _title_fingerprint(paper.title)
        candidate_key = paper_identity_key(paper)
        if candidate_key in seen_candidate_keys:
            excluded.append({"arxiv_id": arxiv_id, "title": paper.title, "reason": "duplicate_candidate"})
            continue
        seen_candidate_keys.add(candidate_key)
        if normalized_arxiv_id and normalized_arxiv_id in normalized_excluded_ids:
            excluded.append({"arxiv_id": arxiv_id, "title": paper.title, "reason": "previously_selected_or_uploaded"})
            continue
        if title_fingerprint and title_fingerprint in zotero_title_fingerprints and normalized_arxiv_id not in normalized_retry_ids:
            excluded.append({"arxiv_id": arxiv_id, "title": paper.title, "reason": "already_in_zotero_by_title"})
            continue
        filtered.append(paper)
    return filtered, excluded


def process_selected_paper(
    record: SelectionRecord,
    output_dir: str | Path,
    index: int,
    openai_client: OpenAI | None = None,
    llm_params: dict[str, Any] | None = None,
    card_mode: str = "one_shot_full",
    full_card_input_chars: int = 160_000,
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
    write_text = _source_text_for_full_card(bundle, max_chars=None, require_full_source=False)
    (folder / "fulltext.md").write_text(write_text, encoding="utf-8")
    if card_mode == "one_shot_full" and openai_client is not None and llm_params is not None:
        try:
            try:
                analysis = generate_one_shot_full_card_markdown(
                    record,
                    bundle,
                    folder / "paper-card.md",
                    openai_client,
                    llm_params,
                    max_input_chars=full_card_input_chars,
                    max_output_tokens=full_card_output_tokens,
                    require_full_source=True,
                )
            except ValueError as exc:
                if not str(exc).startswith("full_source_exceeds_limit:"):
                    raise
                logger.warning(
                    f"Full source exceeds model context limit for {record.title}; "
                    "retrying with an explicitly bounded source excerpt."
                )
                analysis = generate_one_shot_full_card_markdown(
                    record,
                    bundle,
                    folder / "paper-card.md",
                    openai_client,
                    llm_params,
                    max_input_chars=full_card_input_chars,
                    max_output_tokens=full_card_output_tokens,
                    require_full_source=False,
                )
            write_json(folder / "paper_analysis.json", analysis)
        except Exception as exc:
            logger.error(f"Full Paper Card generation failed for {record.title}: {exc}")
            write_json(folder / "paper_analysis.json", {
                "status": "one_shot_full_card_failed",
                "failure_reason": f"{type(exc).__name__}: {exc}",
            })
            write_json(folder / "audit-report.json", {
                "status": "failed",
                "errors": [f"one_shot_full_card_failed:{type(exc).__name__}"],
                "warnings": [],
                "failure_reason": str(exc),
            })
            return folder
    elif card_mode == "one_shot_full":
        report = {
            "status": "failed",
            "errors": ["full_card_llm_client_not_configured"],
            "warnings": [],
        }
        write_json(folder / "audit-report.json", report)
        return folder
    else:
        analysis = write_deep_analysis(record, bundle, folder / "paper_analysis.json", openai_client, llm_params)
        generate_paper_card_markdown(record, analysis, folder / "paper-card.md")
    export_markdown_to_pdf(folder / "paper-card.md", folder / "文档分析.pdf")
    report = audit_paper_card(folder)
    if card_mode == "one_shot_full" and report["status"] == "failed":
        logger.error(f"Full Paper Card failed quality gate for {record.title}: {report}")
    elif card_mode == "one_shot_full" and report["status"] != "pass":
        logger.warning(f"Full Paper Card passed with warnings for {record.title}: {report}")
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
                key = _zotero_object_key(match)
            parent_key = key
            collections = zot.everything(zot.collections())
        else:
            parent_key = _zotero_object_key(match)
    return parent_key


def _zotero_object_key(value: Any) -> str | None:
    """Read a Zotero object key across pyzotero/API response shapes."""
    if not isinstance(value, dict):
        return None
    return value.get("key") or (value.get("data") or {}).get("key")


def _zotero_attachment_key(response: Any, filename: str) -> str | None:
    """Extract an attachment key from pyzotero's list-based upload response."""
    if not isinstance(response, dict):
        return None
    for bucket in ("success", "unchanged", "successful"):
        entries = response.get(bucket) or []
        if isinstance(entries, dict):
            entries = list(entries.values())
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict):
                entry_filename = Path(str(entry.get("filename") or entry.get("title") or "")).name
                if entry_filename == filename or _zotero_object_key(entry):
                    return _zotero_object_key(entry)
            elif isinstance(entry, str) and entry:
                return entry
    return None


def _find_zotero_attachment_key(zot: Any, item_key: str, filename: str) -> str | None:
    """Verify an uploaded child attachment exists under the parent item."""
    for attempt in range(4):
        queries = []
        try:
            queries.append(zot.children(item_key))
        except Exception as exc:
            logger.warning(f"Zotero children lookup failed for {item_key}: {type(exc).__name__}: {exc}")
        try:
            queries.append(zot.items(parentItem=item_key))
        except Exception as exc:
            logger.warning(f"Zotero parent item lookup failed for {item_key}: {type(exc).__name__}: {exc}")
        for children in queries:
            for child in children or []:
                data = (child.get("data") or {}) if isinstance(child, dict) else {}
                if data.get("title") == filename or Path(str(data.get("filename") or "")).name == filename:
                    return _zotero_object_key(child)
        if attempt < 3:
            time.sleep(2)
    return None


def _upload_zotero_attachment(zot: Any, path: Path, parent_key: str) -> dict[str, Any]:
    """Upload a stored file while keeping the API filename separate from its local path."""
    template = zot.item_template("attachment", linkmode="imported_file")
    template.update(
        {
            "title": path.name,
            "filename": path.name,
            "contentType": "application/pdf",
        }
    )
    return Zupload(zot, [template], parentid=parent_key, basedir=path.parent).upload()


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
        "collection_path": " / ".join(DAILY_ZOTERO_COLLECTION_PATH),
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

        collection_key = _zotero_collection_key(zot, DAILY_ZOTERO_COLLECTION_PATH)
        if collection_key:
            try:
                item = zot.item(item_key)
                if not isinstance(item, dict):
                    raise RuntimeError(f"Zotero item lookup returned no object for {item_key}")
                zot.addto_collection(collection_key, item)
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
                uploaded = _upload_zotero_attachment(zot, path, item_key)
                attachment_key = _zotero_attachment_key(uploaded, path.name)
                if not attachment_key:
                    bucket_counts = {
                        bucket: len(uploaded.get(bucket) or [])
                        for bucket in ("success", "unchanged", "failure", "successful")
                        if isinstance(uploaded, dict) and uploaded.get(bucket)
                    }
                    logger.warning(
                        f"Zotero attachment response had no key for {path.name} under {item_key}; "
                        f"response_buckets={bucket_counts}"
                    )
                    attachment_key = _find_zotero_attachment_key(zot, item_key, path.name)
                if not attachment_key:
                    attachment_failures.append(f"{path.name}:remote_attachment_not_found")
                else:
                    result[key_name] = attachment_key
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
            f"- Retrieval sources: {json.dumps(audit.get('retrieval_sources') or {}, ensure_ascii=False)}",
            f"- Retrieval fallback sources: {json.dumps(audit.get('retrieval_fallback_sources') or {}, ensure_ascii=False)}",
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
    quick_look_input_chars: int = 8_000,
    quick_look_output_tokens: int = 1_200,
    three_card_digest_input_chars: int = 180_000,
    three_card_digest_output_tokens: int = 3_200,
    quote_enabled: bool = True,
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
        "zotero_upload_attempted_for": "selected_high_relevance_only",
        "candidate_or_top20_zotero_uploads": 0,
        "fallbacks_used": [],
    }
    try:
        corpus = executor.filter_corpus(executor.fetch_zotero_corpus())
        incomplete_upload_titles = state.incomplete_zotero_upload_title_fingerprints(before_date=run_date)
        if incomplete_upload_titles:
            corpus = [
                item for item in corpus
                if _title_fingerprint(item.title) not in incomplete_upload_titles
            ]
            daily_audit["incomplete_zotero_corpus_excluded_count"] = len(incomplete_upload_titles)
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

        raw_candidates = retrieve_daily_candidates(executor, candidate_count)
        state.upsert_arxiv_papers(raw_candidates)
        excluded_arxiv_ids = state.previously_selected_or_uploaded_arxiv_ids(before_date=run_date)
        retry_arxiv_ids = state.incomplete_zotero_upload_arxiv_ids(before_date=run_date)
        zotero_titles = state.zotero_title_fingerprints()
        candidates, excluded_candidates = filter_previously_promoted_candidates(
            raw_candidates,
            excluded_arxiv_ids=excluded_arxiv_ids,
            zotero_title_fingerprints=zotero_titles,
            retry_arxiv_ids=retry_arxiv_ids,
        )
        retrieval_sources = retrieval_source_distribution(candidates)
        daily_audit["retrieval_sources"] = retrieval_sources
        daily_audit["retrieval_fallback_sources"] = {
            source: count
            for source, count in retrieval_sources.items()
            if source not in {"api", "unknown"}
        }
        write_json(output_dir / "excluded_candidates.json", excluded_candidates)
        write_candidates(candidates, output_dir, limit=candidate_count)
        write_embedding_ranking(candidates, output_dir, "candidates_50.json")
        if not candidates:
            write_selected_papers([], output_dir)
            daily_audit.update(
                {
                    "status": "no_candidates",
                    "raw_arxiv_count": len(raw_candidates),
                    "candidate_50_count": 0,
                    "excluded_previously_promoted_count": len(excluded_candidates),
                }
            )
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

        relevant_top20 = _require_relevant_top3(reranked_for_selection, llm_scores, selected_count)
        if len(relevant_top20) < selected_count:
            partial_selection = (
                f"partial_high_relevance_selection:{len(relevant_top20)}/{selected_count}; "
                "not padding with weakly related papers"
            )
            daily_audit["fallbacks_used"].append(partial_selection)
            if selection_fallback:
                selection_fallback = f"{selection_fallback}; {partial_selection}"
            else:
                selection_fallback = partial_selection
        selected = select_papers_for_deep_read(relevant_top20, count=selected_count, llm_scores=llm_scores)
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
        card_reports: list[dict[str, Any]] = []
        deep_card_model_calls = 0
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
            report_path = folder / "audit-report.json"
            report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {
                "status": "failed", "errors": ["audit_report_missing"], "warnings": []
            }
            card_reports.append({
                "arxiv_id": record.arxiv_id,
                "title": record.title,
                "folder": str(folder),
                "audit": report,
            })
            analysis_path = folder / "paper_analysis.json"
            if analysis_path.exists():
                analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
                if analysis.get("status") == "one_shot_full_card":
                    deep_card_model_calls += 1
        write_json(output_dir / "card_quality.json", card_reports)

        actual_selected_count = len(selected)
        card_gate_passed = actual_selected_count > 0 and len(card_reports) == actual_selected_count and all(
            item["audit"].get("status") in {"pass", "warning"} for item in card_reports
        )
        if not card_gate_passed:
            daily_audit.update({
                "status": "card_quality_failed",
                "raw_arxiv_count": len(raw_candidates),
                "candidate_50_count": len(candidates),
                "excluded_previously_promoted_count": len(excluded_candidates),
                "top20_count": len(top20),
                "selected_count": len(selected),
                "deep_card_model_calls": deep_card_model_calls,
                "card_quality": card_reports,
                "pdf_success_count": sum(
                    1 for folder in paper_folders
                    if (folder / "metadata.json").exists()
                    and json.loads((folder / "metadata.json").read_text(encoding="utf-8")).get("download_status") == "downloaded"
                ),
                "card_success_count": sum(1 for item in card_reports if item["audit"].get("status") in {"pass", "warning"}),
                "zotero_upload_success_count": 0,
            })
            write_json(output_dir / "daily_audit.json", daily_audit)
            write_daily_report_markdown(output_dir, daily_audit, selected)
            write_daily_index(output_dir)
            return output_dir

        quick_look_paths: list[Path] = []
        quick_look_reports: list[dict[str, Any]] = []
        quick_look_model_calls = 0
        for record, card_report in zip(selected, card_reports):
            folder = Path(card_report["folder"])
            quick_look_path = folder / "paper-quick-look.md"
            try:
                quick_meta = generate_paper_quick_look_markdown(
                    record,
                    folder / "paper-card.md",
                    quick_look_path,
                    executor.openai_client,
                    llm_params,
                    max_input_chars=quick_look_input_chars,
                    max_output_tokens=quick_look_output_tokens,
                )
                quick_look_model_calls += 1 + (1 if quick_meta.get("repair_attempted") else 0)
                quick_look_reports.append({
                    "arxiv_id": record.arxiv_id,
                    "title": record.title,
                    "path": str(quick_look_path),
                    "audit": quick_meta["audit"],
                })
                quick_look_paths.append(quick_look_path)
            except Exception as exc:
                logger.error(f"Paper quick look failed for {record.title}: {exc}")
                quick_look_reports.append({
                    "arxiv_id": record.arxiv_id,
                    "title": record.title,
                    "path": str(quick_look_path),
                    "audit": {
                        "status": "fail",
                        "errors": [f"quick_look_failed:{type(exc).__name__}"],
                        "warnings": [],
                    },
                })

        write_json(output_dir / "quick-look-quality.json", quick_look_reports)
        quick_look_gate_passed = actual_selected_count > 0 and len(quick_look_reports) == actual_selected_count and all(
            item["audit"].get("status") == "pass" for item in quick_look_reports
        )
        if not quick_look_gate_passed:
            daily_audit.update({
                "status": "quick_look_quality_failed",
                "raw_arxiv_count": len(raw_candidates),
                "candidate_50_count": len(candidates),
                "excluded_previously_promoted_count": len(excluded_candidates),
                "top20_count": len(top20),
                "selected_count": len(selected),
                "deep_card_model_calls": deep_card_model_calls,
                "quick_look_model_calls": quick_look_model_calls,
                "card_quality": card_reports,
                "quick_look_quality": quick_look_reports,
                "pdf_success_count": sum(
                    1 for folder in paper_folders
                    if (folder / "metadata.json").exists()
                    and json.loads((folder / "metadata.json").read_text(encoding="utf-8")).get("download_status") == "downloaded"
                ),
                "card_success_count": len(card_reports),
                "zotero_upload_success_count": 0,
            })
            write_json(output_dir / "daily_audit.json", daily_audit)
            write_daily_report_markdown(output_dir, daily_audit, selected)
            write_daily_index(output_dir)
            return output_dir

        quote_meta: dict[str, Any] = {"status": "disabled", "quote": "", "model": None}
        if quote_enabled:
            try:
                quote_meta = generate_daily_quote(
                    output_dir / "daily-quote.json",
                    executor.openai_client,
                    llm_params,
                )
            except Exception as exc:
                logger.warning(f"Daily quote generation failed; continuing without quote: {exc}")
                quote_meta = {
                    "status": "failed",
                    "quote": "",
                    "model": llm_params.get("generation_kwargs", {}).get("model"),
                    "error": f"{type(exc).__name__}: {exc}",
                }
                write_json(output_dir / "daily-quote.json", quote_meta)

        public_base_url = os.getenv("DAILY_PIPELINE_PUBLIC_BASE_URL", "").strip()
        cloud_artifact_url = os.getenv("DAILY_PIPELINE_ARTIFACT_URL", "").strip()
        if public_base_url:
            card_pdf_links = [
                public_report_file_url(public_base_url, output_dir.name, f"paper-{index}-card.pdf")
                for index in range(1, len(paper_folders) + 1)
            ]
        elif cloud_artifact_url:
            card_pdf_links = [cloud_artifact_url] * len(paper_folders)
        else:
            card_pdf_links = [
                Path(folder / "文档分析.pdf").relative_to(output_dir).as_posix()
                for folder in paper_folders
            ]
        digest_meta = generate_three_card_digest_markdown(
            selected,
            quick_look_paths,
            output_dir / "wechat-digest.md",
            executor.openai_client,
            llm_params,
            max_input_chars=three_card_digest_input_chars,
            max_output_tokens=three_card_digest_output_tokens,
            report_date=run_date,
            raw_fetched_count=len(raw_candidates),
            quote=quote_meta.get("quote", ""),
            card_pdf_links=card_pdf_links,
        )
        digest_meta["quick_look_model_calls"] = quick_look_model_calls
        digest_meta["daily_quote_model_calls"] = 1 if quote_enabled else 0
        write_json(output_dir / "trend-analysis.json", digest_meta)

        zotero_uploads = []
        for record, folder in zip(selected, paper_folders):
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

        zotero_upload_success_count = sum(1 for item in zotero_uploads if item.get("status") == "uploaded")
        zotero_upload_partial_count = sum(1 for item in zotero_uploads if item.get("status") == "partial")
        zotero_upload_failure_count = sum(1 for item in zotero_uploads if item.get("status") == "failed")

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
                "status": "complete" if zotero_upload_success_count == len(selected) else "failed",
                "raw_arxiv_count": len(raw_candidates),
                "candidate_50_count": len(candidates),
                "excluded_previously_promoted_count": len(excluded_candidates),
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
                "deep_card_model_calls": deep_card_model_calls,
                "quick_look_model_calls": quick_look_model_calls,
                "daily_quote_model_calls": 1 if quote_enabled else 0,
                "three_card_digest_model_calls": 1,
                "card_quality": card_reports,
                "quick_look_quality": quick_look_reports,
                "daily_quote": quote_meta,
                "wechat_digest": digest_meta,
                "freshness_distribution": freshness_distribution(candidates),
                "top20_from_candidates": all(paper in candidates for paper in top20),
                "top3_from_top20": all(record.arxiv_id in {getattr(paper, "arxiv_id", None) for paper in top20} for record in selected),
                "pdf_success_count": pdf_success_count,
                "card_success_count": card_success_count,
                "zotero_upload_success_count": zotero_upload_success_count,
                "zotero_upload_partial_count": zotero_upload_partial_count,
                "zotero_upload_failure_count": zotero_upload_failure_count,
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
        if zotero_upload_success_count != len(selected):
            raise RuntimeError(
                "zotero_upload_incomplete: "
                f"{zotero_upload_success_count}/{len(selected)} selected papers uploaded; "
                f"failed={zotero_upload_failure_count}, partial={zotero_upload_partial_count}"
            )
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
    full_card_input_chars = _config_int(config, "daily_pipeline", "full_card_input_chars", 160_000)
    full_card_output_tokens = _config_int(config, "daily_pipeline", "full_card_output_tokens", 16_000)
    quick_look_input_chars = _config_int(config, "daily_pipeline", "quick_look_input_chars", 8_000)
    quick_look_output_tokens = _config_int(config, "daily_pipeline", "quick_look_output_tokens", 1_200)
    three_card_digest_input_chars = _config_int(config, "daily_pipeline", "three_card_digest_input_chars", 180_000)
    three_card_digest_output_tokens = _config_int(config, "daily_pipeline", "three_card_digest_output_tokens", 3_200)
    quote_enabled = _config_bool(config, "daily_radar", "quote_enabled", True)
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
            quick_look_input_chars=quick_look_input_chars,
            quick_look_output_tokens=quick_look_output_tokens,
            three_card_digest_input_chars=three_card_digest_input_chars,
            three_card_digest_output_tokens=three_card_digest_output_tokens,
            quote_enabled=quote_enabled,
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
