from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Any

from loguru import logger
from omegaconf import DictConfig
import pymupdf
import requests

from .executor import Executor
from .protocol import Paper


CARD_SECTIONS = [
    "01 文献定位",
    "02 研究问题",
    "03 背景路线",
    "04 领域痛点",
    "05 核心 insight",
    "06 方法结构",
    "07 关键公式/建模假设",
    "08 实验设计",
    "09 证据链：实验 -> 结论",
    "10 主要结论",
    "11 边界和局限",
    "12 作者明确承认的限制",
    "13 我的批判性分析",
    "14 对你研究方向的连接",
    "15 相关知识连接",
    "16 可验证的新 idea",
]


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


def generate_paper_card_markdown(paper: SelectionRecord, analysis: dict[str, Any], output_path: str | Path) -> str:
    refs = ", ".join(str(ref) for ref in analysis.get("page_refs", [])) or "source_bundle"
    section_values = {
        "01 文献定位": analysis.get("bibliographic_position", ""),
        "02 研究问题": analysis.get("research_question", ""),
        "03 背景路线": analysis.get("background_route", ""),
        "04 领域痛点": analysis.get("pain_point", ""),
        "05 核心 insight": analysis.get("core_insight", ""),
        "06 方法结构": analysis.get("method_logic", ""),
        "07 关键公式/建模假设": "Not fully assessable before formula-aware extraction.",
        "08 实验设计": analysis.get("experiments", ""),
        "09 证据链：实验 -> 结论": analysis.get("evidence_chain", ""),
        "10 主要结论": analysis.get("core_insight", ""),
        "11 边界和局限": analysis.get("limitations", ""),
        "12 作者明确承认的限制": "Not fully assessable before full card synthesis.",
        "13 我的批判性分析": "This scaffold must be replaced or enriched by Huoshen chunk-grounded analysis before final use.",
        "14 对你研究方向的连接": analysis.get("connection_to_user_research", ""),
        "15 相关知识连接": "Not fully assessable before external context check.",
        "16 可验证的新 idea": "\n".join(f"- {idea}" for idea in analysis.get("testable_ideas", [])) or "Not assessable from supplied material.",
    }
    lines = [f"# {paper.title}", "", f"- Source: {paper.source}", f"- URL: {paper.url}", f"- PDF: {paper.pdf_url or 'missing'}", ""]
    for section in CARD_SECTIONS:
        lines.extend([f"## {section}", "", section_values.get(section, "Not assessable from supplied material."), "", f"Source refs: {refs}", ""])
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
        if card.count("Source refs:") < 5:
            warnings.append("fewer_than_5_source_refs")
        if "scaffold must be replaced" in card:
            warnings.append("scaffold_card_needs_llm_enrichment")

    status = "failed" if errors else ("warning" if warnings else "pass")
    report = {"status": status, "errors": errors, "warnings": warnings}
    write_json(folder / "audit-report.json", report)
    return report


def export_markdown_to_pdf(markdown_path: str | Path, pdf_path: str | Path) -> None:
    markdown_path = Path(markdown_path)
    pdf_path = Path(pdf_path)
    text = markdown_path.read_text(encoding="utf-8")
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    margin = 50
    rect = pymupdf.Rect(margin, margin, 545, 792)
    overflow = page.insert_textbox(rect, text[:3500], fontsize=10, fontname="helv", align=0)
    remaining = text[3500:]
    while remaining or overflow < 0:
        page = doc.new_page(width=595, height=842)
        chunk = remaining[:3500] if remaining else ""
        page.insert_textbox(rect, chunk, fontsize=10, fontname="helv", align=0)
        remaining = remaining[3500:]
        overflow = 0
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


def process_selected_paper(record: SelectionRecord, output_dir: str | Path, index: int) -> Path:
    folder = paper_folder(output_dir, index, record.title)
    folder.mkdir(parents=True, exist_ok=True)
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
    analysis = write_initial_analysis(record, bundle, folder / "paper_analysis.json")
    generate_paper_card_markdown(record, analysis, folder / "paper-card.md")
    export_markdown_to_pdf(folder / "paper-card.md", folder / "文档分析.pdf")
    audit_paper_card(folder)
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
    for index, record in enumerate(selected, start=1):
        process_selected_paper(record, output_dir, index)
    write_daily_index(output_dir)
    return output_dir
