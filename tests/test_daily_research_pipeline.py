import json
from types import SimpleNamespace

import pymupdf
import pytest

from zotero_arxiv_daily.daily_research_pipeline import (
    CARD_SECTIONS,
    QUICK_LOOK_FIELDS,
    SelectionRecord,
    _card_excerpt_for_quick_look,
    _require_relevant_top3,
    audit_paper_card,
    audit_paper_quick_look,
    audit_three_card_digest,
    build_one_shot_full_card_prompt,
    export_markdown_to_html,
    export_markdown_to_pdf,
    extract_source_bundle,
    filter_previously_promoted_candidates,
    generate_daily_quote,
    generate_one_shot_full_card_markdown,
    generate_paper_quick_look_markdown,
    generate_three_card_digest_markdown,
    generate_paper_card_markdown,
    canonical_arxiv_id,
    deduplicate_papers,
    normalize_yiduo_card_markdown,
    paper_identity_key,
    public_report_file_url,
    rank_candidates_with_llm,
    process_selected_paper,
    select_papers_for_deep_read,
    upload_selected_paper_to_zotero,
    validate_pdf,
    write_deep_analysis,
    write_candidates,
    write_daily_index,
    write_initial_analysis,
    write_selected_papers,
)


def test_zotero_attachment_response_extracts_key_from_success_list():
    from zotero_arxiv_daily.daily_research_pipeline import _zotero_attachment_key

    response = {"success": [{"key": "ABCD1234", "filename": "C:/tmp/original.pdf"}]}
    assert _zotero_attachment_key(response, "original.pdf") == "ABCD1234"


def test_zotero_object_key_supports_nested_data():
    from zotero_arxiv_daily.daily_research_pipeline import _zotero_object_key

    assert _zotero_object_key({"data": {"key": "COLL1234"}}) == "COLL1234"


def test_daily_zotero_collection_path_creates_daily_update_child():
    from zotero_arxiv_daily.daily_research_pipeline import (
        DAILY_ZOTERO_COLLECTION_PATH,
        _zotero_collection_key,
    )

    class StubZotero:
        def __init__(self):
            self._collections = [
                {"key": "ROOT1", "data": {"name": "一多科研", "parentCollection": False}}
            ]
            self.created_payloads = []

        def collections(self):
            return self._collections

        def everything(self, value):
            return value

        def create_collections(self, payloads):
            self.created_payloads.extend(payloads)
            self._collections.append(
                {
                    "key": "DAILY1",
                    "data": {
                        "name": payloads[0]["name"],
                        "parentCollection": payloads[0].get("parentCollection", False),
                    },
                }
            )
            return {"success": {"0": "DAILY1"}}

    zot = StubZotero()
    assert DAILY_ZOTERO_COLLECTION_PATH == ["一多科研", "每日更新"]
    assert _zotero_collection_key(zot, DAILY_ZOTERO_COLLECTION_PATH) == "DAILY1"
    assert zot.created_payloads == [{"name": "每日更新", "parentCollection": "ROOT1"}]


def test_zotero_quota_error_creates_link_note(monkeypatch, tmp_path):
    from zotero_arxiv_daily import daily_research_pipeline as pipeline

    class StubZotero:
        def __init__(self, *_args):
            self.created_payloads = []

        def everything(self, value):
            return value

        def items(self, **_kwargs):
            return []

        def item_template(self, item_type, **_kwargs):
            if item_type == "preprint":
                return {"itemType": "preprint"}
            if item_type == "note":
                return {"itemType": "note"}
            return {"itemType": item_type}

        def create_items(self, payloads):
            self.created_payloads.extend(payloads)
            if payloads[0].get("itemType") == "note":
                return {"success": {"0": "NOTE1234"}}
            return {"success": {"0": "ITEM1234"}}

    def raise_quota(*_args, **_kwargs):
        raise RuntimeError("RequestEntityTooLargeError: Code: 413 Response: File would exceed quota (301.8 > 300)")

    stub = StubZotero()
    monkeypatch.setattr(pipeline.zotero, "Zotero", lambda *_args: stub)
    monkeypatch.setattr(pipeline, "_zotero_collection_key", lambda *_args: None)
    monkeypatch.setattr(pipeline, "_upload_zotero_attachment", raise_quota)

    (tmp_path / "original.pdf").write_bytes(b"%PDF-1.4\n")
    (tmp_path / "文档分析.pdf").write_bytes(b"%PDF-1.4\n")
    record = SelectionRecord(
        source="arxiv",
        title="Spatial Transcriptomics Paper",
        authors=["A Researcher"],
        abstract="summary",
        url="https://arxiv.org/abs/2601.00001",
        pdf_url="https://arxiv.org/pdf/2601.00001",
        score=9.0,
        role="best_match",
        scoring={},
        selection_reason="reason",
        arxiv_id="2601.00001",
    )
    config = SimpleNamespace(zotero=SimpleNamespace(user_id="1", api_key="key"))

    result = upload_selected_paper_to_zotero(
        config,
        record,
        tmp_path,
        "2026-09-17",
        links={
            "original_pdf": "https://example.test/original.pdf",
            "card_pdf": "https://example.test/card.pdf",
            "card_markdown": "https://example.test/card.md",
            "quick_look": "https://example.test/quick.md",
        },
    )

    assert result["status"] == "linked"
    assert result["item_key"] == "ITEM1234"
    assert result["link_note_key"] == "NOTE1234"
    assert result["zotero_storage_quota_fallback"] is True
    note_payload = [item for item in stub.created_payloads if item.get("itemType") == "note"][0]
    assert note_payload["parentItem"] == "ITEM1234"
    assert "https://example.test/card.pdf" in note_payload["note"]
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


def test_filter_previously_promoted_candidates_excludes_history_and_zotero_titles():
    promoted = make_sample_paper(title="Previously Selected", score=9.0)
    promoted.arxiv_id = "2601.00001v2"
    in_zotero = make_sample_paper(title="Already In Zotero", score=8.0)
    in_zotero.arxiv_id = "2601.00002"
    fresh = make_sample_paper(title="Fresh Relevant Paper", score=7.0)
    fresh.arxiv_id = "2601.00003"

    filtered, excluded = filter_previously_promoted_candidates(
        [promoted, in_zotero, fresh],
        excluded_arxiv_ids={"2601.00001"},
        zotero_title_fingerprints={"already in zotero"},
    )

    assert [paper.arxiv_id for paper in filtered] == ["2601.00003"]
    assert [item["reason"] for item in excluded] == ["previously_selected_or_uploaded", "already_in_zotero_by_title"]


def test_arxiv_identity_deduplicates_versioned_ids():
    first = make_sample_paper(title="Same Paper", score=9.0)
    first.arxiv_id = "2609.14970v1"
    second = make_sample_paper(title="Same Paper", score=8.0)
    second.arxiv_id = "2609.14970"
    distinct = make_sample_paper(title="Distinct Paper", score=7.0)
    distinct.arxiv_id = "2609.14971v2"

    deduped = deduplicate_papers([first, second, distinct])

    assert canonical_arxiv_id("https://arxiv.org/abs/2609.14970v1") == "2609.14970"
    assert [paper.arxiv_id for paper in deduped] == ["2609.14970v1", "2609.14971v2"]


def test_llm_ranking_uses_title_abstract_and_selects_distinct_roles():
    papers = [
        make_sample_paper(title="Best Match", abstract="single-cell foundation model", score=9.0),
        make_sample_paper(title="Method", abstract="new graph method", score=8.0),
        make_sample_paper(title="Trend", abstract="spatial trend", score=7.0),
    ]
    payload = {
        "rankings": [
            {"paper_index": 1, "relevance_to_user": 10, "method_novelty": 4, "evidence_quality": 8, "transferability": 9, "trend_value": 4, "resource_value": 5, "reason": "最贴合研究画像", "risk": "摘要证据有限"},
            {"paper_index": 2, "relevance_to_user": 5, "method_novelty": 10, "evidence_quality": 7, "transferability": 8, "trend_value": 6, "resource_value": 8, "reason": "方法启发强", "risk": "需核查实验"},
            {"paper_index": 3, "relevance_to_user": 6, "method_novelty": 7, "evidence_quality": 6, "transferability": 5, "trend_value": 10, "resource_value": 3, "reason": "代表趋势", "risk": "主题较宽"},
        ]
    }
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="模型判断如下：\n```json\n" + json.dumps(payload["rankings"], ensure_ascii=False) + "\n```"))]
    )
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return fake_response
    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    ranked, scores = rank_candidates_with_llm(
        papers,
        fake_client,
        {"generation_kwargs": {"model": "qwen3.8-max", "max_tokens": 1500}, "research_profile": "single-cell"},
    )
    prompt = calls[0]["messages"][1]["content"]
    assert "Title: Best Match" in prompt
    assert "Abstract: single-cell foundation model" in prompt
    assert "全文摘录" not in prompt
    assert ranked[0].title == "Best Match"
    assert scores[paper_identity_key(papers[0])]["total"] == 74.0

    selected = select_papers_for_deep_read(ranked, count=3, llm_scores=scores)
    assert [paper.title for paper in selected] == ["Best Match", "Method", "Trend"]
    assert [paper.role for paper in selected] == ["best_match", "method_inspiration", "trend_signal"]


def test_selection_prioritizes_direct_research_anchors_over_generic_methods():
    papers = [
        make_sample_paper(title="RAGCell", abstract="retrieval augmented generation for single-cell analysis", score=90.0),
        make_sample_paper(title="Spatial Omics Model", abstract="spatial transcriptomics representation learning", score=85.0),
        make_sample_paper(title="Knowledge Single Cell", abstract="knowledge enhanced single-cell foundation model", score=82.0),
        make_sample_paper(title="Generic Transport", abstract="quantile transport for time series forecasting", score=95.0),
    ]
    llm_scores = {
        "RAGCell": {"relevance_to_user": 9, "method_novelty": 7, "evidence_quality": 7, "transferability": 8, "trend_value": 8, "resource_value": 6, "total": 80, "reason": "single-cell direct", "risk": "limited"},
        "Spatial Omics Model": {"relevance_to_user": 9, "method_novelty": 8, "evidence_quality": 7, "transferability": 8, "trend_value": 8, "resource_value": 5, "total": 79, "reason": "spatial direct", "risk": "limited"},
        "Knowledge Single Cell": {"relevance_to_user": 8, "method_novelty": 8, "evidence_quality": 7, "transferability": 7, "trend_value": 8, "resource_value": 5, "total": 77, "reason": "single-cell direct", "risk": "limited"},
        "Generic Transport": {"relevance_to_user": 4, "method_novelty": 10, "evidence_quality": 8, "transferability": 8, "trend_value": 8, "resource_value": 6, "total": 88, "reason": "generic method", "risk": "domain gap"},
    }

    selected = select_papers_for_deep_read(papers, count=3, llm_scores=llm_scores)

    assert [paper.title for paper in selected] == ["RAGCell", "Spatial Omics Model", "Knowledge Single Cell"]


def test_relevance_gate_allows_partial_without_padding_weak_papers():
    papers = [
        make_sample_paper(title="Spatial Direct", abstract="spatial transcriptomics graph transformer", score=90.0),
        make_sample_paper(title="Single Cell Direct", abstract="single-cell foundation model", score=85.0),
        make_sample_paper(title="Generic Method", abstract="generic video diffusion transformer", score=95.0),
    ]
    llm_scores = {
        "Spatial Direct": {"relevance_to_user": 10, "total": 90},
        "Single Cell Direct": {"relevance_to_user": 10, "total": 88},
        "Generic Method": {"relevance_to_user": 2, "total": 75},
    }

    relevant = _require_relevant_top3(papers, llm_scores, count=3)

    assert [paper.title for paper in relevant] == ["Spatial Direct", "Single Cell Direct"]


def test_relevance_gate_rejects_zero_direct_candidates():
    papers = [
        make_sample_paper(title="Generic Method", abstract="generic video diffusion transformer", score=95.0),
    ]
    llm_scores = {"Generic Method": {"relevance_to_user": 2, "total": 75}}

    with pytest.raises(RuntimeError, match="no_relevant_candidates"):
        _require_relevant_top3(papers, llm_scores, count=3)


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
    exported_text = "\n".join(page.get_text() for page in pymupdf.open(tmp_path / "文档分析.pdf"))
    exported_text = " ".join(exported_text.replace("\u00a0", " ").split())
    assert "01 基本信息" in exported_text
    assert "02 一句话总结" in exported_text

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
    rich_cn = (
        "这段内容用中文解释论文逻辑：作者先界定单细胞表示学习中的核心问题，再把方法模块、"
        "实验对照、结论边界和可迁移启发连接起来，便于研究者复盘为什么这样设计以及哪些地方能借鉴。"
    )
    sections = {
        key: (
            f"[Analysis] [Paper] [Paper: PDF p. 1] {key} {rich_cn}"
            if key == "13 批判性分析"
            else f"[Hypothesis] [Paper] [Paper: PDF p. 1] {key} {rich_cn}"
            if key == "16 研究想法"
            else f"[Paper] [Paper: PDF p. 1] {key} {rich_cn}"
        )
        for key in CARD_SECTIONS
    }
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
    assert (tmp_path / "paper-card.html").exists()
    exported_text = "\n".join(page.get_text() for page in pymupdf.open(tmp_path / "文档分析.pdf"))
    exported_text = " ".join(exported_text.replace("\u00a0", " ").split())
    assert "01 基本信息" in exported_text
    assert "16 研究想法" in exported_text
    report = audit_paper_card(tmp_path)
    assert report["status"] == "pass"
    assert report["errors"] == []


def test_one_shot_full_card_streaming_passes_audit(tmp_path):
    pdf_path = tmp_path / "original.pdf"
    make_pdf(pdf_path)
    bundle = extract_source_bundle(pdf_path, tmp_path / "source_bundle.json")
    paper = SelectionRecord(
        source="arxiv",
        title="A Streaming Full Card Paper",
        authors=["A", "B"],
        abstract="This paper introduces a method for single-cell representation learning.",
        url="https://arxiv.org/abs/2601.00004",
        pdf_url="https://arxiv.org/pdf/2601.00004",
        score=9.0,
        role="best_match",
        scoring={"total": 9.0},
        selection_reason="Highly relevant.",
    )
    rich_cn = (
        "这段内容用中文解释论文逻辑：研究问题、方法模块、实验证据和结论边界之间形成清晰链条，"
        "能够帮助用户判断这篇论文是否值得精读，以及哪些设计可以迁移到空间转录组和多组学研究。"
    )
    markdown = "\n\n".join(
        [
            "> Source coverage: Full paper\n> Extraction confidence: High\n> Locator mode: page-grounded\n> Primary analytical lens: methods\n> Secondary analytical lens: None\n> Context verification: Paper-only\n> Card completeness: Complete relative to supplied source",
                *[
                    f"## {section}\n\n"
                    + ("[Analysis] " if section == "13 批判性分析" else "")
                    + ("[Hypothesis] " if section == "16 研究想法" else "")
                    + f"[Paper] [Paper: PDF p. 1] {section} {rich_cn}"
                    for section in CARD_SECTIONS
                ],
        ]
    )
    chunks = [
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=markdown[:100]))]),
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=markdown[100:]))]),
    ]
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: iter(chunks)))
    )
    llm_params = {"generation_kwargs": {"model": "qwen3.8-max", "max_tokens": 1000}, "language": "Chinese"}

    analysis = generate_one_shot_full_card_markdown(
        paper,
        bundle,
        tmp_path / "paper-card.md",
        fake_client,
        llm_params,
        max_input_chars=20000,
        max_output_tokens=1000,
    )
    assert analysis["status"] == "one_shot_full_card"
    assert (tmp_path / "paper-card.md").read_text(encoding="utf-8") == markdown

    export_markdown_to_pdf(tmp_path / "paper-card.md", tmp_path / "文档分析.pdf")
    report = audit_paper_card(tmp_path)
    assert report["status"] == "pass"
    assert report["errors"] == []


def test_card_inventory_coverage_gaps_are_warnings_not_blockers(tmp_path):
    pdf_path = tmp_path / "original.pdf"
    make_pdf(pdf_path)
    source_bundle = {
        "page_count": 2,
        "extraction": {"total_characters": 2000},
        "evidence_inventory": {
            "figures": [{"id": "Figure 1"}, {"id": "Figure 8"}],
            "tables": [],
            "equations": [{"id": "Equation 1"}, {"id": "Equation 23"}],
        },
    }
    (tmp_path / "source_bundle.json").write_text(json.dumps(source_bundle), encoding="utf-8")
    markdown = "\n\n".join(
        [
            "> Source coverage: Full paper\n"
            "> Extraction confidence: High\n"
            "> Locator mode: page-grounded\n"
            "> Primary analytical lens: methods\n"
            "> Secondary analytical lens: None\n"
            "> Context verification: Paper-only\n"
            "> Card completeness: Complete relative to supplied source",
            *[
                f"## {section}\n\n"
                + ("[Analysis] " if section == "13 批判性分析" else "")
                + ("[Hypothesis] " if section == "16 研究想法" else "")
                + "[Paper] [Paper: PDF p. 1] Figure 1 and Equation 1 are central evidence."
                for section in CARD_SECTIONS
            ],
        ]
    )
    (tmp_path / "paper-card.md").write_text(markdown, encoding="utf-8")

    report = audit_paper_card(tmp_path)

    assert report["status"] == "warning"
    assert report["errors"] == []
    assert any("figures_not_covered" in warning for warning in report["warnings"])
    assert any("equations_not_covered" in warning for warning in report["warnings"])


def test_full_card_prompt_requires_yiduo_chinese_provenance_style(tmp_path):
    paper = SelectionRecord(
        source="arxiv",
        title="Prompt Test Paper",
        authors=["A"],
        abstract="A paper about spatial transcriptomics and graph representation learning.",
        url="https://arxiv.org/abs/2601.00005",
        pdf_url="https://arxiv.org/pdf/2601.00005",
        score=9.0,
        role="best_match",
        scoring={},
        selection_reason="test",
        arxiv_id="2601.00005",
    )
    bundle = {
        "source_text": "[PDF p. 1]\nThis is a short source page.",
        "pages": [{"page": 1, "text": "This is a short source page."}],
        "evidence_inventory": {"figures": [], "tables": [], "equations": []},
    }

    prompt = build_one_shot_full_card_prompt(paper, bundle, max_input_chars=5000, require_full_source=False)

    assert "一多科研" in prompt
    assert "中文科研笔记为主体" in prompt
    assert "[Paper] [Paper: PDF p. 1]" in prompt
    assert "01 用表格：Field | Value | Source" in prompt


def test_yiduo_card_normalization_adds_missing_provenance_labels():
    markdown = (
        "## 01 基本信息\n\n"
        "事实来自论文。[Paper: PDF p. 1]\n\n"
        "## 16 研究想法\n\n"
        "- idea from limitation [Paper: PDF p. 2]"
    )

    normalized = normalize_yiduo_card_markdown(markdown)

    assert "[Paper] [Paper: PDF p. 1]" in normalized
    assert "[Paper] [Paper: PDF p. 2]" in normalized
    assert "[Hypothesis]" in normalized


def test_markdown_html_export_preserves_card_tables_and_quotes(tmp_path):
    markdown = tmp_path / "paper-card.md"
    html_path = tmp_path / "paper-card.html"
    markdown.write_text(
        "# 测试卡片\n\n"
        "> Source coverage: Full paper\n\n"
        "## 01 基本信息\n\n"
        "| Field | Value | Source |\n"
        "| --- | --- | --- |\n"
        "| Title | 测试论文 | [Paper] [Paper: PDF p. 1] |\n\n"
        "## 02 一句话总结\n\n"
        "[Paper] [Paper: PDF p. 1] 这是一段中文说明。\n",
        encoding="utf-8",
    )

    export_markdown_to_html(markdown, html_path)
    html_text = html_path.read_text(encoding="utf-8")

    assert "<blockquote>" in html_text
    assert "<table>" in html_text
    assert "Noto Sans CJK SC" in html_text
    assert "测试论文" in html_text


def test_three_card_digest_requires_exact_date_and_all_titles(tmp_path):
    papers = [
        SelectionRecord(
            source="arxiv", title=f"Paper {index}", authors=["A"], abstract="Abstract",
            url=f"https://arxiv.org/abs/2601.0000{index}",
            pdf_url=f"https://arxiv.org/pdf/2601.0000{index}",
            published_date="2026-09-14T12:00:00+08:00" if index == 1 else "2026-09-14",
            score=1.0,
            role="best_match", scoring={}, selection_reason="test", arxiv_id=f"2601.0000{index}",
        )
        for index in range(1, 4)
    ]
    card = "\n\n".join(
        [
            "> Source coverage: Full paper\n> Extraction confidence: High\n> Locator mode: page-grounded\n"
            "> Primary analytical lens: methods\n> Secondary analytical lens: None\n"
            "> Context verification: Paper-only\n> Card completeness: Complete relative to supplied source",
            *[f"## {section}\n\n[Paper: PDF p. 1] [Analysis] [Hypothesis] content" for section in CARD_SECTIONS],
        ]
    )
    quick_fields = "\n".join(
        f"**{field}**\ncontent"
        for field in [
            "标题与发布时间", "作者和机构", "研究背景", "核心假设或问题",
            "发表状态", "方法逻辑", "主要结果", "真正贡献", "与你研究方向的关系",
            "局限性", "是否值得精读",
        ]
    )
    digest = "# 每日速看\n\n**2026-09-15**\n\n早上好，一多。\n\n> quote\n\n"
    digest += "## 今日主线\ntrend\n\n"
    for index in range(1, 4):
        digest += (
            f"# {index:02d}｜Paper {index}\n\n"
            f"**发布时间 · 来源**\n2026-09-14 · arXiv\n\n"
            f"> **速读判断**：This paper has a clear methodological signal.\n\n"
            f"{quick_fields}\n\n"
            f"[原文 PDF](https://arxiv.org/pdf/2601.0000{index}) · "
            f"[下载 Paper Card](paper-{index}.pdf)\n\n"
        )
    digest += "## 今日精读顺序\n01 → 02 → 03。今日首次从 arXiv 抓取 50 篇候选论文，最终精选 3 篇。"
    fake_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=digest))])
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: fake_response))
    )
    for index in range(1, 4):
        (tmp_path / f"card-{index}.md").write_text(card.replace("Paper 1", f"Paper {index}"), encoding="utf-8")
    result = generate_three_card_digest_markdown(
        papers,
        [tmp_path / "card-1.md", tmp_path / "card-2.md", tmp_path / "card-3.md"],
        tmp_path / "wechat-digest.md",
        fake_client,
        {"generation_kwargs": {"model": "qwen3.8-max", "max_tokens": 100}},
        report_date="2026-09-15",
        raw_fetched_count=50,
        quote="quote",
        card_pdf_links=["paper-1.pdf", "paper-2.pdf", "paper-3.pdf"],
    )
    assert result["audit"]["status"] == "pass"


def test_digest_audit_allows_partial_high_relevance_selection():
    papers = [
        SelectionRecord(
            source="arxiv", title=f"Paper {index}", authors=["A"], abstract="Abstract",
            url=f"https://arxiv.org/abs/2601.0000{index}",
            pdf_url=f"https://arxiv.org/pdf/2601.0000{index}",
            published_date="2026-09-14",
            score=1.0,
            role="best_match", scoring={}, selection_reason="test", arxiv_id=f"2601.0000{index}",
        )
        for index in range(1, 3)
    ]
    quick_fields = "\n".join(f"**{field}**\ncontent" for field in QUICK_LOOK_FIELDS)
    digest = (
        "# 每日速看\n\n**2026-09-15**\n\n早上好，一多。\n\n"
        "## 今日主线\n今日首次从 arXiv 抓取 50 篇候选论文，最终精选 2 篇。\n\n"
        "# 01｜Paper 1\n\n**发布时间 · 来源**\n2026-09-14 · arXiv\n\n"
        "> **速读判断**：content\n\n"
        f"{quick_fields}\n\n"
        "[原文 PDF](https://arxiv.org/pdf/2601.00001) · [下载 Paper Card](paper-1.pdf)\n\n"
        "# 02｜Paper 2\n\n**发布时间 · 来源**\n2026-09-14 · arXiv\n\n"
        "> **速读判断**：content\n\n"
        f"{quick_fields}\n\n"
        "[原文 PDF](https://arxiv.org/pdf/2601.00002) · [下载 Paper Card](paper-2.pdf)\n\n"
        "## 今日精读顺序\n01 → 02。先读空间转录组方法论文，再读单细胞基础模型论文；今天只有两篇达到高相关标准，不硬凑第三篇。"
    )

    audit = audit_three_card_digest(
        digest,
        papers,
        report_date="2026-09-15",
        raw_fetched_count=50,
        card_pdf_links=["paper-1.pdf", "paper-2.pdf"],
    )

    assert audit["status"] == "pass"


def test_wechat_readability_audit_rejects_formula_markup():
    paper = SelectionRecord(
        source="arxiv",
        title="Formula Heavy Paper",
        authors=["Author"],
        abstract="Abstract",
        url="https://arxiv.org/abs/2601.00001",
        pdf_url="https://arxiv.org/pdf/2601.00001",
        published_date="2026-09-14",
        score=1.0,
        role="best_match",
        scoring={},
        selection_reason="test",
        arxiv_id="2601.00001",
    )
    quick = (
        "## Formula Heavy Paper\n\n"
        "**标题与发布时间**\nFormula Heavy Paper（2026-09-14）\n\n"
        "**作者和机构**\nAuthor\n\n"
        "**研究背景**\ncontent\n\n"
        "**核心假设或问题**\ncontent\n\n"
        "**方法逻辑**\nuses `z_i = x_i` and <sub>con</sub>\n\n"
        "**主要结果**\ncontent\n\n"
        "**真正贡献**\ncontent\n\n"
        "**与你研究方向的关系**\ncontent\n\n"
        "**局限性**\ncontent\n\n"
        "**是否值得精读**\ncontent\n\n"
        "https://arxiv.org/pdf/2601.00001"
    )

    quick_audit = audit_paper_quick_look(quick, paper)
    digest_audit = audit_three_card_digest(
        "# 每日速看\n\n**2026-09-15**\n\n## 今日主线\n"
        "今日首次从 arXiv 抓取 50 篇候选论文，最终精选 3 篇。\n\n"
        "# 01｜Formula Heavy Paper\n\n**2026-09-14 · arXiv**\n\n"
        "> **速读判断**：uses `z_i` and <sub>con</sub>\n\n"
        + "\n".join(f"**{field}**\ncontent" for field in QUICK_LOOK_FIELDS)
        + "\n\n[原文 PDF](https://arxiv.org/pdf/2601.00001) · [下载 Paper Card](paper-1.pdf)\n\n"
        "## 今日精读顺序\n01 → 02 → 03。排序完整。",
        [paper, paper, paper],
        report_date="2026-09-15",
        raw_fetched_count=50,
        card_pdf_links=["paper-1.pdf", "paper-1.pdf", "paper-1.pdf"],
    )

    assert quick_audit["status"] == "fail"
    assert "quick_look_contains_formula_markup" in quick_audit["errors"]
    assert "quick_look_contains_html_tag" in quick_audit["errors"]
    assert digest_audit["status"] == "fail"
    assert "digest_contains_formula_markup" in digest_audit["errors"]
    assert "digest_contains_html_tag" in digest_audit["errors"]


def test_public_report_file_url_quotes_filename():
    assert (
        public_report_file_url(
            "https://raw.githubusercontent.com/u/r/reports/public/daily/",
            "2026-09-16",
            "paper-1-card.pdf",
        )
        == "https://raw.githubusercontent.com/u/r/reports/public/daily/2026-09-16/paper-1-card.pdf"
    )


def test_paper_quick_look_is_card_only_and_audited(tmp_path):
    paper = SelectionRecord(
        source="arxiv",
        title="Card-grounded paper",
        authors=["Author"],
        abstract="Abstract",
        url="https://arxiv.org/abs/2601.00001",
        pdf_url="https://arxiv.org/pdf/2601.00001",
        published_date="2026-09-14",
        score=1.0,
        role="best_match",
        scoring={},
        selection_reason="test",
        arxiv_id="2601.00001",
    )
    card = "\n".join(["## 01 基本信息", "**作者**: Author", "**机构**: Test Lab"])
    quick = (
        "## Card-grounded paper\n\n"
        "**标题与发布时间**\nCard-grounded paper（2026-09-14）\n\n"
        "**作者和机构**\nAuthor；Test Lab\n\n"
        + "\n\n".join(f"**{field}**\nCard content" for field in QUICK_LOOK_FIELDS)
        + "\n\n**原文 PDF**：https://arxiv.org/pdf/2601.00001"
    )
    fake_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=quick))])
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: fake_response))
    )
    card_path = tmp_path / "paper-card.md"
    card_path.write_text(card, encoding="utf-8")
    result = generate_paper_quick_look_markdown(
        paper,
        card_path,
        tmp_path / "paper-quick-look.md",
        fake_client,
        {"generation_kwargs": {"model": "qwen3.8-max", "max_tokens": 100}},
    )
    assert result["status"] == "paper_quick_look"
    assert result["audit"]["status"] == "pass"
    assert (tmp_path / "paper-quick-look.md").exists()


def test_quick_look_excerpt_uses_relevant_card_sections():
    card = "\n\n".join(
        [
            "## 01 基本信息\nkeep metadata",
            "## 03 研究问题\nkeep question",
            "## 09 关键公式与符号\ndrop formula details",
            "## 10 实验设计与证据链\nkeep evidence",
            "## 15 与既有知识的连接\nkeep relation",
            "## 16 研究想法\ndrop future ideas",
        ]
    )
    excerpt = _card_excerpt_for_quick_look(card, max_chars=10_000)
    assert "keep metadata" in excerpt
    assert "keep question" in excerpt
    assert "keep evidence" in excerpt
    assert "keep relation" in excerpt
    assert "drop formula details" not in excerpt
    assert "drop future ideas" not in excerpt


def test_daily_quote_writes_one_model_generated_sentence(tmp_path):
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="把复杂的问题拆开，答案会开始出现。"))]
    )
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: fake_response))
    )
    result = generate_daily_quote(
        tmp_path / "daily-quote.json",
        fake_client,
        {"generation_kwargs": {"model": "qwen3.8-max", "max_tokens": 100}},
    )
    assert result["status"] == "generated"
    assert result["quote"] == "把复杂的问题拆开，答案会开始出现。"


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
