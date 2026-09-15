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


def _selection_scoring(paper: Paper, role: str) -> dict[str, Any]:
    base_score = float(paper.score or 0.0)
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


def select_papers_for_deep_read(papers: list[Paper], count: int = 3) -> list[SelectionRecord]:
    roles = ["best_match", "method_inspiration", "trend_signal"]
    ranked = sorted(papers, key=lambda paper: paper.score if paper.score is not None else -1, reverse=True)
    selected = []
    for index, paper in enumerate(ranked[:count]):
        role = roles[index] if index < len(roles) else "best_match"
        scoring = _selection_scoring(paper, role)
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
                    f"Selected as {role}; embedding score={paper.score:.3f}."
                    if paper.score is not None
                    else f"Selected as {role}; LLM scoring still required."
                ),
            )
        )
    return selected


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


def _page_texts_for_llm(bundle: dict[str, Any], max_chars: int = 16000) -> tuple[str, list[str]]:
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
        snippet = text[:1800]
        block = f"[Paper: PDF p. {page_no}]\n{snippet}"
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining < 500:
                break
            block = block[:remaining]
        chunks.append(block)
        refs.append(f"[Paper: PDF p. {page_no}]")
        total += len(block)
        if total >= max_chars:
            break
    return "\n\n".join(chunks), refs or ["source_bundle"]


def _json_from_llm_content(content: str) -> dict[str, Any]:
    candidates = [content]
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.insert(0, fenced.group(1))
    loose = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if loose:
        candidates.append(loose.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("LLM did not return a JSON object")


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
    logger.info(f"Calling Huoshen LLM for Paper Card: {paper.title}")
    lang = llm_params.get("language", "Chinese")
    user_profile = llm_params.get("research_profile") or (
        "single-cell foundation models, spatial transcriptomics, graph neural networks, "
        "multi-omics, biomedical AI, perturbation prediction, and cell-state representation"
    )
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))
    generation_kwargs["max_tokens"] = max(int(generation_kwargs.get("max_tokens") or 0), 2800)
    card_llm_params = {**llm_params, "generation_kwargs": generation_kwargs}
    section_contract = "\n".join(f"- {section}: JSON key `{key}`" for section, key in CARD_SECTION_MAP.items())
    prompt = f"""
You are implementing the user's 一多科研 Paper Card workflow.

Write in {lang}. Preserve English technical terms, model names, datasets, metrics, and equations.
Be rigorous and source-grounded. Do not hype the paper. Do not invent evidence.
Every substantive paper-derived claim must include a source pointer like [Paper: PDF p. 3].
If a section is not supported by the supplied source excerpt, write "Not assessable from supplied material."
Author-stated limitations and your own criticism must be separated.
Research ideas must be hypotheses, not novelty claims, and must include validation plus possible failure modes.
Keep each section concise: 1 short paragraph or a compact Markdown table.

User research profile:
{user_profile}

Return only valid JSON with this shape:
{{
  "source_coverage": "Full paper or Partial paper",
  "extraction_confidence": "High or Mixed or Low",
  "locator_mode": "page-grounded",
  "primary_lens": "methods/discovery/resource/clinical/materials/review",
  "secondary_lens": "None or one lens",
  "context_verification": "Paper-only",
  "card_completeness": "Complete relative to supplied source or Partial",
  "sections": {{
{section_contract}
  }},
  "quality_notes": ["short notes"]
}}

Paper metadata:
Title: {paper.title}
Source: {paper.source}
URL: {paper.url}
PDF URL: {paper.pdf_url or "missing"}
Authors: {", ".join(paper.authors[:12])}
Abstract: {paper.abstract}
Selection role: {paper.role}
Selection reason: {paper.selection_reason}

Supplied PDF excerpts:
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
    sections = _normalise_card_sections(payload.get("sections", {}))
    missing_sections = [section for section, body in sections.items() if "Not assessable from supplied material" in body]
    logger.info(f"Huoshen LLM Paper Card JSON received: {paper.title}")
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
        logger.warning(f"Failed to generate Huoshen Paper Card analysis for {paper.title}: {exc}")
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
    margin = 50
    rect = pymupdf.Rect(margin, margin, 545, 792)
    remaining = text
    while remaining:
        page = doc.new_page(width=595, height=842)
        chunk = remaining[:2400]
        page.insert_textbox(rect, chunk, fontsize=9.5, fontname="china-s", align=0)
        remaining = remaining[2400:]
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


def run_daily_file_pipeline(config: DictConfig) -> Path:
    output_root = _config_get(config, "daily_pipeline", "output_dir", "outputs/daily")
    candidate_count = _config_int(config, "daily_pipeline", "candidate_count", 20)
    selected_count = _config_int(config, "daily_pipeline", "selected_count", 3)
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

    reranked = executor.reranker.rerank(candidates, corpus)
    selected = select_papers_for_deep_read(reranked, count=selected_count)
    write_selected_papers(selected, output_dir)
    llm_params = OmegaConf.to_container(config.llm, resolve=True) if hasattr(config, "llm") else None
    for index, record in enumerate(selected, start=1):
        process_selected_paper(record, output_dir, index, executor.openai_client, llm_params)
    write_daily_index(output_dir)
    return output_dir
