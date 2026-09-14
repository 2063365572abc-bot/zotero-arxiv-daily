"""Tests for zotero_arxiv_daily.construct_email: daily research radar rendering."""

import zotero_arxiv_daily.construct_email as construct_email
from zotero_arxiv_daily.construct_email import render_email, render_markdown, get_stars, get_block_html, get_empty_html
from tests.canned_responses import make_sample_paper


def test_render_email_with_papers(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    papers = [make_sample_paper(score=7.5, tldr="A great paper.", affiliations=["MIT"])]
    papers[0].research_brief = {
        "why_it_matters": "Useful for single-cell.",
        "method_core": "Graph attention.",
        "evidence": "Public benchmarks.",
        "limitations": "Small validation.",
        "research_inspiration": "Try it on spatial data.",
    }
    html = render_email(papers)
    assert "Sample Paper Title" in html
    assert "A great paper." in html
    assert "MIT" in html
    assert "早上好，一多" in html
    assert "今日趋势" in html
    assert "Useful for single-cell" in html
    assert "今日深读建议" in html


def test_render_email_empty_list(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    html = render_email([])
    assert "今天没有筛到足够相关的新论文" in html


def test_fetch_weather_falls_back_to_open_meteo(monkeypatch):
    class Response:
        def __init__(self, payload=None, text="", fail=False):
            self._payload = payload
            self.text = text
            self.fail = fail

        def raise_for_status(self):
            if self.fail:
                raise RuntimeError("down")

        def json(self):
            return self._payload

    def fake_get(url, **kwargs):
        if "wttr.in" in url:
            return Response(fail=True)
        if "geocoding-api.open-meteo.com" in url:
            return Response({"results": [{"name": "Harbin", "latitude": 45.75, "longitude": 126.63}]})
        if "api.open-meteo.com" in url:
            return Response(
                {
                    "current": {
                        "temperature_2m": 12.4,
                        "apparent_temperature": 10.2,
                        "relative_humidity_2m": 61,
                        "wind_speed_10m": 9.6,
                        "weather_code": 3,
                    }
                }
            )
        raise AssertionError(url)

    monkeypatch.setattr(construct_email.requests, "get", fake_get)

    weather = construct_email._fetch_weather(None)

    assert "Harbin: 阴" in weather
    assert "12°C" in weather
    assert "体感 10°C" in weather


def test_render_markdown_for_wechat(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    papers = [make_sample_paper(score=7.5, tldr="A great paper.", affiliations=["MIT"])]
    papers[0].research_brief = {
        "why_it_matters": "Useful for single-cell.",
        "method_core": "Graph attention.",
        "evidence": "Public benchmarks.",
        "limitations": "Small validation.",
        "research_inspiration": "Try it on spatial data.",
    }

    markdown = render_markdown(papers)

    assert "**早上好，一多。**" in markdown
    assert "## 今日趋势" in markdown
    assert "### 1. Sample Paper Title" in markdown
    assert "- [PDF / 原文](" in markdown
    assert "Useful for single-cell" in markdown
    assert "<div" not in markdown
    assert "<table" not in markdown


def test_render_email_author_truncation(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    authors = [f"Author {i}" for i in range(10)]
    paper = make_sample_paper(authors=authors, score=7.0, tldr="ok")
    html = render_email([paper])
    assert "Author 0" in html
    assert "Author 1" in html
    assert "Author 2" in html
    assert "..." in html
    assert "Author 8" in html
    assert "Author 9" in html
    # Middle authors should be truncated
    assert "Author 5" not in html


def test_render_email_affiliation_truncation(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    affiliations = [f"Uni {i}" for i in range(8)]
    paper = make_sample_paper(affiliations=affiliations, score=7.0, tldr="ok")
    html = render_email([paper])
    assert "Uni 0" in html
    assert "Uni 4" in html
    assert "..." in html
    assert "Uni 7" not in html


def test_render_email_no_affiliations(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    paper = make_sample_paper(affiliations=None, score=7.0, tldr="ok")
    html = render_email([paper])
    assert "Unknown Affiliation" in html


def test_get_stars_low_score():
    assert get_stars(5.0) == ""
    assert get_stars(6.0) == ""


def test_get_stars_high_score():
    stars = get_stars(8.0)
    assert stars.count("full-star") == 5


def test_get_stars_mid_score():
    stars = get_stars(7.0)
    assert "star" in stars
    assert stars.count("full-star") + stars.count("half-star") > 0


def test_get_block_html_contains_all_fields():
    html = get_block_html(
        "Title",
        "Auth",
        "3.5",
        "Summary",
        "http://pdf.url",
        "MIT",
        {"why_it_matters": "Important", "method_core": "Core"},
    )
    assert "Title" in html
    assert "Auth" in html
    assert "3.5" in html
    assert "Summary" in html
    assert "http://pdf.url" in html
    assert "MIT" in html
    assert "Important" in html


def test_get_empty_html(monkeypatch):
    monkeypatch.setattr(construct_email, "_fetch_weather", lambda config=None: "Harbin: Sunny, 19C")
    monkeypatch.setattr(construct_email, "_fetch_quote", lambda config=None: "Keep the thread alive.")
    html = get_empty_html()
    assert "今天没有筛到足够相关的新论文" in html
