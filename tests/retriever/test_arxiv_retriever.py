"""Tests for ArxivRetriever."""

import time
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
