import json
from types import SimpleNamespace

import pymupdf

from zotero_arxiv_daily.daily_research_pipeline import (
    CARD_SECTIONS,
    QUICK_LOOK_FIELDS,
    SelectionRecord,
    _card_excerpt_for_quick_look,
    audit_paper_card,
    export_markdown_to_pdf,
    extract_source_bundle,
    filter_previously_promoted_candidates,
    generate_daily_quote,
    generate_one_shot_full_card_markdown,
    generate_paper_quick_look_markdown,
    generate_three_card_digest_markdown,
    generate_paper_card_markdown,
    rank_candidates_with_llm,
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


def test_filter_previously_promoted_candidates_excludes_history_and_zotero_titles():
    promoted = make_sample_paper(title="Previously Selected", score=9.0)
    promoted.arxiv_id = "2601.00001"
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
    assert scores["Best Match"]["total"] == 74.0

    selected = select_papers_for_deep_read(ranked, count=3, llm_scores=scores)
    assert [paper.title for paper in selected] == ["Best Match", "Method", "Trend"]
    assert [paper.role for paper in selected] == ["best_match", "method_inspiration", "trend_signal"]


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
    sections = {
        key: (
            f"[Analysis] [Paper: PDF p. 1] {key} content."
            if key == "13 批判性分析"
            else f"[Hypothesis] [Paper: PDF p. 1] {key} content."
            if key == "16 研究想法"
            else f"[Paper: PDF p. 1] {key} content."
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
    markdown = "\n\n".join(
        [
            "> Source coverage: Full paper\n> Extraction confidence: High\n> Locator mode: page-grounded\n> Primary analytical lens: methods\n> Secondary analytical lens: None\n> Context verification: Paper-only\n> Card completeness: Complete relative to supplied source",
                *[
                    f"## {section}\n\n"
                    + ("[Analysis] " if section == "13 批判性分析" else "")
                    + ("[Hypothesis] " if section == "16 研究想法" else "")
                    + f"[Paper: PDF p. 1] {section} content."
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


def test_three_card_digest_requires_exact_date_and_all_titles(tmp_path):
    papers = [
        SelectionRecord(
            source="arxiv", title=f"Paper {index}", authors=["A"], abstract="Abstract",
            url=f"https://arxiv.org/abs/2601.0000{index}",
            pdf_url=f"https://arxiv.org/pdf/2601.0000{index}",
            published_date="2026-09-14",
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
            "方法逻辑", "主要结果", "真正贡献", "与你研究方向的关系",
            "局限性", "是否值得精读",
        ]
    )
    digest = "# 一多科研｜每日论文速递\n\n**2026-09-15**\n\n早上好，一多。\n\n> quote\n\n"
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
