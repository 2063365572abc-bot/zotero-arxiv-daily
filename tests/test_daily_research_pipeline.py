import json
from types import SimpleNamespace

import pymupdf

from zotero_arxiv_daily.daily_research_pipeline import (
    CARD_SECTIONS,
    SelectionRecord,
    audit_paper_card,
    export_markdown_to_pdf,
    extract_source_bundle,
    generate_paper_card_markdown,
    process_selected_paper,
    select_papers_for_deep_read,
    validate_pdf,
    write_deep_analysis,
    write_candidates,
    write_daily_index,
    write_initial_analysis,
    write_selected_papers,
)
from tests.canned_responses import make_sample_paper


def make_pdf(path):
    doc = pymupdf.open()
    text = (
        "This paper studies single-cell foundation models, perturbation prediction, "
        "multi-omics integration, methods, experiments, evidence, and limitations. "
    )
    for page_index in range(120):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {page_index + 1}\n" + text * 35, fontsize=10)
    doc.save(path)


def test_write_candidates_and_selected_papers(tmp_path):
    papers = [
        make_sample_paper(title="Paper A", score=9.0),
        make_sample_paper(title="Paper B", score=8.0),
        make_sample_paper(title="Paper C", score=7.0),
        make_sample_paper(title="Paper D", score=6.0),
    ]

    candidates_path = write_candidates(papers, tmp_path, limit=3)
    selected = select_papers_for_deep_read(papers, count=3)
    selected_path = write_selected_papers(selected, tmp_path)

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    selected_payload = json.loads(selected_path.read_text(encoding="utf-8"))
    assert len(candidates) == 3
    assert [item["role"] for item in selected_payload] == ["best_match", "method_inspiration", "trend_signal"]
    assert selected_payload[0]["title"] == "Paper A"


def test_pdf_bundle_card_audit_and_export(tmp_path):
    pdf_path = tmp_path / "original.pdf"
    make_pdf(pdf_path)
    ok, reason = validate_pdf(pdf_path)
    assert ok, reason

    bundle = extract_source_bundle(pdf_path, tmp_path / "source_bundle.json")
    assert bundle["page_count"] == 120
    assert len(bundle["pages"][0]["text"]) > 100

    paper = SelectionRecord(
        source="arxiv",
        title="A Real Test Paper",
        authors=["A", "B"],
        abstract="This paper introduces a method for single-cell representation learning.",
        url="https://arxiv.org/abs/2601.00001",
        pdf_url="https://arxiv.org/pdf/2601.00001",
        score=9.0,
        role="best_match",
        scoring={"total": 9.0},
        selection_reason="Highly relevant.",
    )
    analysis = write_initial_analysis(paper, bundle, tmp_path / "paper_analysis.json")
    markdown = generate_paper_card_markdown(paper, analysis, tmp_path / "paper-card.md")
    for section in CARD_SECTIONS:
        assert f"## {section}" in markdown

    export_markdown_to_pdf(tmp_path / "paper-card.md", tmp_path / "文档分析.pdf")
    ok, reason = validate_pdf(tmp_path / "文档分析.pdf", min_bytes=0)
    assert ok, reason

    report = audit_paper_card(tmp_path)
    assert report["status"] == "warning"
    assert "scaffold_card_needs_llm_enrichment" in report["warnings"]


def test_llm_enriched_card_passes_audit(tmp_path):
    pdf_path = tmp_path / "original.pdf"
    make_pdf(pdf_path)
    bundle = extract_source_bundle(pdf_path, tmp_path / "source_bundle.json")
    paper = SelectionRecord(
        source="arxiv",
        title="A Real LLM Paper",
        authors=["A", "B"],
        abstract="This paper introduces a method for single-cell representation learning.",
        url="https://arxiv.org/abs/2601.00003",
        pdf_url="https://arxiv.org/pdf/2601.00003",
        score=9.0,
        role="best_match",
        scoring={"total": 9.0},
        selection_reason="Highly relevant.",
    )
    sections = {key: f"[Paper: PDF p. 1] {key} content." for key in CARD_SECTIONS}
    payload = {
        "source_coverage": "Full paper",
        "extraction_confidence": "High",
        "locator_mode": "page-grounded",
        "primary_lens": "methods",
        "secondary_lens": "None",
        "context_verification": "Paper-only",
        "card_completeness": "Complete relative to supplied source",
        "sections": sections,
        "quality_notes": [],
    }
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload, ensure_ascii=False)))]
    )
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: fake_response))
    )
    llm_params = {"api_mode": "chat_completion", "generation_kwargs": {"model": "gpt-5.5", "max_tokens": 700}, "language": "Chinese"}

    analysis = write_deep_analysis(paper, bundle, tmp_path / "paper_analysis.json", fake_client, llm_params)
    markdown = generate_paper_card_markdown(paper, analysis, tmp_path / "paper-card.md")
    assert "Analysis status: llm_enriched" in markdown

    export_markdown_to_pdf(tmp_path / "paper-card.md", tmp_path / "文档分析.pdf")
    report = audit_paper_card(tmp_path)
    assert report == {"status": "pass", "errors": [], "warnings": []}


def test_process_selected_paper_records_download_failure(tmp_path, monkeypatch):
    def fake_download(pdf_url, output_pdf, timeout=60):
        return {
            "pdf_url": pdf_url,
            "download_status": "failed",
            "failure_reason": "missing_pdf_url",
            "sha256": None,
            "bytes": 0,
        }

    monkeypatch.setattr("zotero_arxiv_daily.daily_research_pipeline.download_pdf", fake_download)
    record = SelectionRecord(
        source="arxiv",
        title="No PDF Paper",
        authors=[],
        abstract="No PDF.",
        url="https://arxiv.org/abs/2601.00002",
        pdf_url=None,
        score=1.0,
        role="trend_signal",
        scoring={},
        selection_reason="Testing failure.",
    )

    folder = process_selected_paper(record, tmp_path, 1)
    metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    audit = json.loads((folder / "audit-report.json").read_text(encoding="utf-8"))

    assert metadata["download_status"] == "failed"
    assert audit["status"] == "failed"
    assert not (folder / "paper-card.md").exists()


def test_write_daily_index(tmp_path):
    paper_dir = tmp_path / "paper-1" / "Paper"
    paper_dir.mkdir(parents=True)
    (tmp_path / "candidates.json").write_text("[{}]", encoding="utf-8")
    (tmp_path / "selected_papers.json").write_text("[{}]", encoding="utf-8")
    (paper_dir / "metadata.json").write_text('{"title":"Paper","failure_reason":null}', encoding="utf-8")
    (paper_dir / "audit-report.json").write_text('{"status":"warning"}', encoding="utf-8")

    index_path = write_daily_index(tmp_path)
    payload = json.loads(index_path.read_text(encoding="utf-8"))

    assert payload["candidate_count"] == 1
    assert payload["selected_count"] == 1
    assert payload["papers"][0]["status"] == "completed"
