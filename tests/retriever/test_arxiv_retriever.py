"""Tests for ArxivRetriever."""

import time
from datetime import datetime, timezone
from types import SimpleNamespace

import feedparser
import pytest

from zotero_arxiv_daily.retriever.arxiv_retriever import ArxivRetriever, _run_with_hard_timeout
import zotero_arxiv_daily.retriever.arxiv_retriever as arxiv_retriever


def _sleep_and_return(value: str, delay_seconds: float) -> str:
    time.sleep(delay_seconds)
    return value


def _raise_runtime_error() -> None:
    raise RuntimeError("boom")


def test_arxiv_retriever(config, mock_feedparser, monkeypatch):
    from omegaconf import open_dict

    with open_dict(config):
        config.source.arxiv.include_cross_list = False
        config.source.arxiv.use_rss_metadata = False
        config.source.arxiv.domain_keywords = None
        config.source.arxiv.method_keywords = None

    monkeypatch.setattr("zotero_arxiv_daily.retriever.base.sleep", lambda _: None)

    # The RSS fixture gives us paper IDs.  After feedparser, the code calls
    # arxiv.Client().results(search) which makes real HTTP requests.  We mock
    # the arxiv Client so the test stays offline.
    new_entries = [
        e for e in mock_feedparser.entries
        if e.get("arxiv_announce_type", "new") == "new"
    ]
    paper_ids = [e.id.removeprefix("oai:arXiv.org:") for e in new_entries]

    # Build fake ArxivResult-like objects matching each RSS entry
    fake_results = []
    for entry in new_entries:
        pid = entry.id.removeprefix("oai:arXiv.org:")
        fake_results.append(SimpleNamespace(
            title=entry.title,
            authors=[SimpleNamespace(name="Test Author")],
            summary="Test abstract",
            pdf_url=f"https://arxiv.org/pdf/{pid}",
            entry_id=f"https://arxiv.org/abs/{pid}",
            source_url=lambda pid=pid: f"https://arxiv.org/e-print/{pid}",
        ))

    class FakeClient:
        def __init__(self, **kw):
            pass
        def results(self, search):
            return iter(fake_results)

    monkeypatch.setattr(arxiv_retriever.arxiv, "Client", FakeClient)

    # Skip file downloads in convert_to_paper
    monkeypatch.setattr(arxiv_retriever, "extract_text_from_html", lambda paper: None)
    monkeypatch.setattr(arxiv_retriever, "extract_text_from_pdf", lambda paper: None)
    monkeypatch.setattr(arxiv_retriever, "extract_text_from_tar", lambda paper: None)

    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()

    assert len(papers) == len(new_entries)
    assert set(p.title for p in papers) == set(e.title for e in new_entries)


def test_arxiv_retriever_rss_metadata_fast_path(config, mock_feedparser, monkeypatch):
    from omegaconf import open_dict

    with open_dict(config):
        config.source.arxiv.include_cross_list = False
        config.source.arxiv.use_rss_metadata = True
        config.source.arxiv.domain_keywords = None
        config.source.arxiv.method_keywords = None

    monkeypatch.setattr("zotero_arxiv_daily.retriever.base.sleep", lambda _: None)
    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()

    new_entries = [
        e for e in mock_feedparser.entries
        if e.get("arxiv_announce_type", "new") == "new"
    ]
    assert len(papers) == len(new_entries)
    assert set(p.title for p in papers) == set(e.title for e in new_entries)
    assert all(p.full_text is None for p in papers)


def test_arxiv_retriever_keyword_search(config, monkeypatch):
    from omegaconf import open_dict

    captured = {}
    fake_results = [
        SimpleNamespace(
            title="Single-cell Foundation Model Paper",
            authors=[SimpleNamespace(name="Test Author")],
            summary="A paper about single-cell foundation models.",
            pdf_url="https://arxiv.org/pdf/2601.00001",
            entry_id="https://arxiv.org/abs/2601.00001",
            source_url=lambda: "https://arxiv.org/e-print/2601.00001",
        )
    ]

    class FakeClient:
        def __init__(self, **kw):
            captured["client_kwargs"] = kw

        def results(self, search):
            captured["query"] = search.query
            captured["max_results"] = search.max_results
            captured["sort_by"] = search.sort_by
            captured["sort_order"] = search.sort_order
            return iter(fake_results)

    with open_dict(config):
        config.source.arxiv.keywords = ["single-cell foundation model", "spatial transcriptomics"]
        config.source.arxiv.domain_keywords = None
        config.source.arxiv.method_keywords = None
        config.source.arxiv.keyword_query_max_results = 7
        config.source.arxiv.category = ["cs.LG", "q-bio.GN"]
        config.source.arxiv.extract_full_text = False

    monkeypatch.setattr(arxiv_retriever.arxiv, "Client", FakeClient)
    monkeypatch.setattr("zotero_arxiv_daily.retriever.base.sleep", lambda _: None)
    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()

    assert len(papers) == 1
    assert papers[0].title == "Single-cell Foundation Model Paper"
    assert 'all:"single-cell foundation model"' in captured["query"]
    assert 'all:"spatial transcriptomics"' in captured["query"]
    assert "cat:cs.LG" in captured["query"]
    assert "cat:q-bio.GN" in captured["query"]
    assert captured["max_results"] == 7
    assert captured["client_kwargs"]["page_size"] == 7
    assert captured["sort_by"] == arxiv_retriever.arxiv.SortCriterion.SubmittedDate
    assert captured["sort_order"] == arxiv_retriever.arxiv.SortOrder.Descending


def test_arxiv_retriever_strict_groups_query_and_ranks(config, monkeypatch):
    from omegaconf import open_dict

    captured = {}
    published = datetime.now(timezone.utc)
    fake_results = [
        SimpleNamespace(
            title="Spatial Transcriptomics with Deep Learning",
            authors=[SimpleNamespace(name="Test Author")],
            summary="We learn spatial domains from spatial transcriptomics data.",
            published=published,
            updated=published,
            categories=["q-bio.GN"],
            pdf_url="https://arxiv.org/pdf/2601.00003",
            entry_id="https://arxiv.org/abs/2601.00003",
            source_url=lambda: "https://arxiv.org/e-print/2601.00003",
        )
    ]

    class FakeClient:
        def __init__(self, **kw):
            captured["client_kwargs"] = kw

        def results(self, search):
            captured.setdefault("queries", []).append(search.query)
            captured["max_results"] = search.max_results
            return iter(fake_results)

    with open_dict(config):
        config.source.arxiv.domain_keywords = ["spatial transcriptomics"]
        config.source.arxiv.method_keywords = ["deep learning"]
        config.source.arxiv.task_keywords = ["spatial domain"]
        config.source.arxiv.keyword_query_max_results = 100
        config.source.arxiv.retrieval_result_limit = 1
        config.source.arxiv.freshness_hours = 48
        config.source.arxiv.freshness_fallback_hours = 168
        config.source.arxiv.category = ["q-bio.GN"]
        config.source.arxiv.extract_full_text = False

    monkeypatch.setattr(arxiv_retriever.arxiv, "Client", FakeClient)
    monkeypatch.setattr("zotero_arxiv_daily.retriever.base.sleep", lambda _: None)
    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()

    assert len(papers) == 1
    assert papers[0].title == "Spatial Transcriptomics with Deep Learning"
    query = captured["queries"][0]
    assert "cat:q-bio.GN" not in query
    assert "submittedDate:[" in query
    assert 'all:"spatial transcriptomics"' in query
    assert "deep learning" not in query
    assert captured["max_results"] == 100
    assert papers[0].published_date == published.isoformat()
    assert papers[0].matched_terms["domain"] == ["spatial transcriptomics"]
    assert papers[0].matched_terms["method"] == ["deep learning"]
    assert papers[0].score == 14
    assert papers[0].freshness_label == "latest_48h"


def test_arxiv_retriever_strict_groups_prefers_newer_candidates_before_score(config, monkeypatch):
    from omegaconf import open_dict

    new_date = datetime(2026, 9, 14, tzinfo=timezone.utc)
    old_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    fake_results = [
        SimpleNamespace(
            title="Spatial Transcriptomics Foundation Model Graph Transformer",
            authors=[SimpleNamespace(name="Old Author")],
            summary="A foundation model graph transformer embedding method for spatial transcriptomics.",
            published=old_date,
            updated=old_date,
            categories=["q-bio.GN"],
            pdf_url="https://arxiv.org/pdf/2501.00001",
            entry_id="https://arxiv.org/abs/2501.00001",
            source_url=lambda: "https://arxiv.org/e-print/2501.00001",
        ),
        SimpleNamespace(
            title="Spatial Transcriptomics with Graph Learning",
            authors=[SimpleNamespace(name="New Author")],
            summary="A graph learning method for spatial transcriptomics.",
            published=new_date,
            updated=new_date,
            categories=["q-bio.GN"],
            pdf_url="https://arxiv.org/pdf/2609.00001",
            entry_id="https://arxiv.org/abs/2609.00001",
            source_url=lambda: "https://arxiv.org/e-print/2609.00001",
        ),
    ]

    class FakeClient:
        def __init__(self, **kw):
            pass

        def results(self, search):
            return iter(fake_results)

    with open_dict(config):
        config.source.arxiv.domain_keywords = ["spatial transcriptomics"]
        config.source.arxiv.method_keywords = ["graph learning", "foundation model", "graph transformer", "embedding"]
        config.source.arxiv.task_keywords = []
        config.source.arxiv.keyword_query_max_results = 100
        config.source.arxiv.retrieval_result_limit = 2
        config.source.arxiv.strict_rss_first = False
        config.source.arxiv.strict_html_fallback_enabled = False
        config.source.arxiv.category = ["q-bio.GN"]
        config.source.arxiv.extract_full_text = False

    monkeypatch.setattr(arxiv_retriever.arxiv, "Client", FakeClient)
    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()

    assert [paper.arxiv_id for paper in papers] == ["2609.00001", "2501.00001"]


def test_arxiv_retriever_recent_category_rss_fallback_keeps_recent_candidates(config, monkeypatch):
    from omegaconf import open_dict

    class FakeClient:
        def __init__(self, **kw):
            pass

        def results(self, search):
            raise arxiv_retriever.arxiv.HTTPError("url", 1, 429)

    now = time.time()
    feed_entries = [
        {
            "title": "Spatial Transcriptomics with Graph Learning",
            "summary": "A graph neural network for spatial transcriptomics.",
            "authors": [{"name": "Test Author"}],
            "link": "https://arxiv.org/abs/2601.00004",
            "id": "oai:arXiv.org:2601.00004",
            "published_parsed": time.gmtime(now),
            "arxiv_announce_type": "new",
        },
        {
            "title": "Spatial Transcriptomics without the Required Method",
            "summary": "A spatial transcriptomics study without machine learning.",
            "authors": [{"name": "Other Author"}],
            "link": "https://arxiv.org/abs/2601.00005",
            "id": "oai:arXiv.org:2601.00005",
            "published_parsed": time.gmtime(now),
            "arxiv_announce_type": "new",
        },
        {
            "title": "Old Spatial Transcriptomics Graph Learning Paper",
            "summary": "An old graph learning paper.",
            "authors": [{"name": "Old Author"}],
            "link": "https://arxiv.org/abs/2601.00006",
            "id": "oai:arXiv.org:2601.00006",
            "published_parsed": time.gmtime(now - 10 * 24 * 3600),
            "arxiv_announce_type": "new",
        },
    ]

    with open_dict(config):
        config.source.arxiv.domain_keywords = ["spatial transcriptomics"]
        config.source.arxiv.method_keywords = ["graph learning"]
        config.source.arxiv.task_keywords = []
        config.source.arxiv.keyword_query_max_results = 20
        config.source.arxiv.retrieval_result_limit = 20
        config.source.arxiv.freshness_hours = 48
        config.source.arxiv.freshness_fallback_hours = 168
        config.source.arxiv.category = ["q-bio.GN"]
        config.source.arxiv.keyword_fallback_to_rss = True
        config.source.arxiv.extract_full_text = False

    monkeypatch.setattr(arxiv_retriever.arxiv, "Client", FakeClient)
    monkeypatch.setattr(retriever := ArxivRetriever(config), "_retrieve_recent_topic_html", lambda *_: [])
    monkeypatch.setattr(
        arxiv_retriever.feedparser,
        "parse",
        lambda _: SimpleNamespace(feed=SimpleNamespace(title="q-bio.GN updates on arXiv.org"), entries=feed_entries),
    )
    papers = retriever.retrieve_papers()

    assert len(papers) == 3
    assert papers[0].title == "Spatial Transcriptomics with Graph Learning"
    assert papers[0].source == "arxiv"
    assert papers[0].categories == []
    assert papers[1].title == "Spatial Transcriptomics without the Required Method"
    assert papers[2].title == "Old Spatial Transcriptomics Graph Learning Paper"
    assert [paper.freshness_label for paper in papers] == [
        "latest_48h",
        "latest_48h",
        "recent_30d",
    ]


def test_arxiv_retriever_html_fallback_parses_recent_matching_result(config, monkeypatch):
    from omegaconf import open_dict

    html = """
    <html><body><ol>
      <li class="arxiv-result">
        <p class="title is-5 mathjax">Spatial Transcriptomics with Graph Learning</p>
        <p class="list-title"><a href="https://arxiv.org/abs/2609.00007">arXiv:2609.00007</a></p>
        <p class="abstract mathjax">Abstract: We use graph learning to analyze spatial transcriptomics.</p>
        <p class="is-size-7">Submitted 15 September, 2026; originally announced September 2026.</p>
        <p class="authors">Authors: <a href="/search/?searchtype=author&amp;query=Test%2C+A">Test Author</a></p>
      </li>
      <li class="arxiv-result">
        <p class="title is-5 mathjax">Spatial Transcriptomics without Machine Learning</p>
        <p class="list-title"><a href="https://arxiv.org/abs/2609.00008">arXiv:2609.00008</a></p>
        <p class="abstract mathjax">Abstract: We study spatial transcriptomics data.</p>
        <p class="is-size-7">Submitted 15 September, 2026; originally announced September 2026.</p>
      </li>
    </ol></body></html>
    """

    class FakeResponse:
        content = html.encode("utf-8")

        def raise_for_status(self):
            return None

    with open_dict(config):
        config.source.arxiv.category = ["q-bio.GN"]

    monkeypatch.setattr(arxiv_retriever.requests, "get", lambda *args, **kwargs: FakeResponse())
    retriever = ArxivRetriever(config)
    papers = retriever._retrieve_strict_keyword_html(
        ["spatial transcriptomics"], ["graph learning"], [], 48, 50
    )

    assert len(papers) == 1
    assert papers[0]["id"] == "oai:arXiv.org:2609.00007"
    assert papers[0]["retrieval_source"] == "html"
    assert papers[0]["authors"] == [{"name": "Test Author"}]
    assert "Less" not in papers[0]["summary"]


def test_arxiv_retriever_html_fallback_uses_original_arxiv_month_for_revised_old_papers(config, monkeypatch):
    from omegaconf import open_dict

    html = """
    <html><body><ol>
      <li class="arxiv-result">
        <p class="title is-5 mathjax">Spatial Transcriptomics with Graph Learning</p>
        <p class="list-title"><a href="https://arxiv.org/abs/2411.00007">arXiv:2411.00007</a></p>
        <p class="abstract mathjax">Abstract: We use graph learning to analyze spatial transcriptomics.</p>
        <p class="is-size-7">Submitted 15 September, 2026; originally announced November 2024.</p>
      </li>
    </ol></body></html>
    """

    class FakeResponse:
        content = html.encode("utf-8")

        def raise_for_status(self):
            return None

    with open_dict(config):
        config.source.arxiv.category = ["q-bio.GN"]

    monkeypatch.setattr(arxiv_retriever.requests, "get", lambda *args, **kwargs: FakeResponse())
    retriever = ArxivRetriever(config)
    papers = retriever._retrieve_strict_keyword_html(
        ["spatial transcriptomics"], ["graph learning"], [], 720, 50
    )

    assert papers == []


@pytest.mark.parametrize("status_code", [429, 503])
def test_arxiv_retriever_keyword_search_falls_back_to_rss_on_api_error(config, monkeypatch, status_code):
    from omegaconf import open_dict

    class FakeClient:
        def __init__(self, **kw):
            pass

        def results(self, search):
            raise arxiv_retriever.arxiv.HTTPError("url", 1, status_code)

    feed_entries = [
        {
            "title": "Spatial Transcriptomics with Robust Graph Models",
            "summary": "A new method for spatial transcriptomics analysis.",
            "authors": [{"name": "Test Author"}],
            "link": "https://arxiv.org/abs/2601.00001",
            "id": "oai:arXiv.org:2601.00001",
            "arxiv_announce_type": "new",
        },
        {
            "title": "Unrelated Optimization Paper",
            "summary": "A paper about optimizers.",
            "authors": [{"name": "Other Author"}],
            "link": "https://arxiv.org/abs/2601.00002",
            "id": "oai:arXiv.org:2601.00002",
            "arxiv_announce_type": "new",
        },
    ]

    with open_dict(config):
        config.source.arxiv.keywords = ["spatial transcriptomics"]
        config.source.arxiv.domain_keywords = None
        config.source.arxiv.method_keywords = None
        config.source.arxiv.keyword_query_max_results = 3
        config.source.arxiv.keyword_fallback_to_rss = True
        config.source.arxiv.category = ["cs.LG"]
        config.source.arxiv.extract_full_text = False

    monkeypatch.setattr(arxiv_retriever.arxiv, "Client", FakeClient)
    monkeypatch.setattr(
        arxiv_retriever.feedparser,
        "parse",
        lambda _: SimpleNamespace(feed=SimpleNamespace(title="cs.LG updates on arXiv.org"), entries=feed_entries),
    )
    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()

    assert len(papers) == 1
    assert papers[0].title == "Spatial Transcriptomics with Robust Graph Models"
    assert papers[0].pdf_url == "https://arxiv.org/pdf/2601.00001"


def test_run_with_hard_timeout_returns_value():
    result = _run_with_hard_timeout(
        _sleep_and_return, ("done", 0.01), timeout=1, operation="test op", paper_title="paper"
    )
    assert result == "done"


def test_run_with_hard_timeout_returns_none_on_timeout(monkeypatch):
    warnings: list[str] = []
    monkeypatch.setattr(arxiv_retriever, "logger", SimpleNamespace(warning=warnings.append))
    result = _run_with_hard_timeout(
        _sleep_and_return, ("done", 1.0), timeout=0.01, operation="test op", paper_title="paper"
    )
    assert result is None
    assert "timed out" in warnings[0]


def test_run_with_hard_timeout_returns_none_on_failure(monkeypatch):
    warnings: list[str] = []
    monkeypatch.setattr(arxiv_retriever, "logger", SimpleNamespace(warning=warnings.append))
    result = _run_with_hard_timeout(
        _raise_runtime_error, (), timeout=1, operation="test op", paper_title="paper"
    )
    assert result is None
    assert "boom" in warnings[0]
