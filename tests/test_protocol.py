"""Tests for zotero_arxiv_daily.protocol: Paper.generate_tldr, Paper.generate_affiliations."""

import pytest

from tests.canned_responses import make_sample_paper, make_stub_openai_client


@pytest.fixture()
def llm_params():
    return {
        "api_mode": "chat_completion",
        "language": "English",
        "generation_kwargs": {"model": "gpt-4o-mini", "max_tokens": 16384},
    }


# ---------------------------------------------------------------------------
# generate_tldr
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("api_mode", ["chat_completion", "response"])
def test_tldr_returns_response(llm_params, api_mode):
    llm_params["api_mode"] = api_mode
    client = make_stub_openai_client()
    paper = make_sample_paper()
    result = paper.generate_tldr(client, llm_params)
    assert result == "Hello! How can I assist you today?"
    assert paper.tldr == result


def test_tldr_without_abstract_or_fulltext(llm_params):
    client = make_stub_openai_client()
    paper = make_sample_paper(abstract="", full_text=None)
    result = paper.generate_tldr(client, llm_params)
    assert "Failed to generate TLDR" in result


def test_tldr_falls_back_to_abstract_on_error(llm_params):
    paper = make_sample_paper()

    # Client whose create() raises
    from types import SimpleNamespace

    broken_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kw: (_ for _ in ()).throw(RuntimeError("API down")))
        )
    )
    result = paper.generate_tldr(broken_client, llm_params)
    assert result == paper.abstract


def test_tldr_truncates_long_prompt(llm_params):
    client = make_stub_openai_client()
    paper = make_sample_paper(full_text="word " * 10000)
    result = paper.generate_tldr(client, llm_params)
    assert result is not None


def test_response_mode_maps_max_tokens(llm_params):
    from types import SimpleNamespace

    received_kwargs = {}

    def create_response(**kwargs):
        received_kwargs.update(kwargs)
        return SimpleNamespace(output_text="Summary")

    client = SimpleNamespace(
        responses=SimpleNamespace(create=create_response),
    )
    llm_params["api_mode"] = "response"
    paper = make_sample_paper()

    assert paper.generate_tldr(client, llm_params) == "Summary"
    assert received_kwargs["max_output_tokens"] == 16384
    assert "max_tokens" not in received_kwargs


def test_invalid_api_mode_falls_back_to_abstract(llm_params):
    llm_params["api_mode"] = "invalid"
    paper = make_sample_paper()

    assert paper.generate_tldr(make_stub_openai_client(), llm_params) == paper.abstract


# ---------------------------------------------------------------------------
# generate_research_brief
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("api_mode", ["chat_completion", "response"])
def test_research_brief_returns_structured_fields(llm_params, api_mode):
    llm_params["api_mode"] = api_mode
    client = make_stub_openai_client()
    paper = make_sample_paper()
    result = paper.generate_research_brief(client, llm_params)
    assert result["why_it_matters"] == "It is relevant to single-cell modeling."
    assert result["method_core"] == "A graph attention model."
    assert result["research_inspiration"] == "Try the representation on spatial transcriptomics."
    assert paper.research_brief == result


def test_research_brief_falls_back_on_error(llm_params):
    from types import SimpleNamespace

    broken_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kw: (_ for _ in ()).throw(RuntimeError("boom")))
        )
    )
    paper = make_sample_paper(tldr="Short summary")
    result = paper.generate_research_brief(broken_client, llm_params)
    assert result["why_it_matters"] == "Short summary"
    assert "模型没有稳定返回结构化方法字段" in result["method_core"]


@pytest.mark.parametrize("api_mode", ["chat_completion", "response"])
def test_daily_analysis_sets_tldr_and_structured_brief(llm_params, api_mode):
    llm_params["api_mode"] = api_mode
    client = make_stub_openai_client()
    paper = make_sample_paper()
    result = paper.generate_daily_analysis(client, llm_params)
    assert result["tldr"] == "A concise daily summary."
    assert paper.tldr == "A concise daily summary."
    assert paper.research_brief["method_core"] == "A graph attention model."


def test_daily_analysis_fallback_does_not_call_extra_llm(llm_params):
    from types import SimpleNamespace

    calls = {"n": 0}

    def fail_once(**kwargs):
        calls["n"] += 1
        raise RuntimeError("boom")

    broken_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fail_once)
        )
    )
    paper = make_sample_paper()
    result = paper.generate_daily_analysis(broken_client, llm_params)
    assert calls["n"] == 1
    assert result["tldr"] == paper.abstract
    assert "模型没有稳定返回结构化方法字段" in paper.research_brief["method_core"]


def test_daily_analysis_fills_fallback_for_unstructured_response(llm_params):
    from types import SimpleNamespace

    def create_unstructured(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="This paper proposes a useful but unstructured summary."),
                )
            ]
        )

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create_unstructured)
        )
    )
    paper = make_sample_paper()
    result = paper.generate_daily_analysis(client, llm_params)

    assert result["tldr"] == "This paper proposes a useful but unstructured summary."
    assert paper.research_brief["why_it_matters"] == result["tldr"]
    assert "模型没有稳定返回结构化方法字段" in paper.research_brief["method_core"]
    assert all(paper.research_brief.values())


def test_daily_analysis_compacts_long_unstructured_response(llm_params):
    from types import SimpleNamespace

    long_summary = (
        "This paper proposes a first useful idea. "
        "It then continues with a very long abstract-like response that should not flood WeChat. " * 20
    )

    def create_unstructured(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=long_summary),
                )
            ]
        )

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create_unstructured)
        )
    )
    paper = make_sample_paper()
    result = paper.generate_daily_analysis(client, llm_params)

    assert result["tldr"] == "This paper proposes a first useful idea."
    assert paper.research_brief["why_it_matters"] == result["tldr"]


# ---------------------------------------------------------------------------
# generate_affiliations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("api_mode", ["chat_completion", "response"])
def test_affiliations_returns_parsed_list(llm_params, api_mode):
    llm_params["api_mode"] = api_mode
    client = make_stub_openai_client()
    paper = make_sample_paper()
    result = paper.generate_affiliations(client, llm_params)
    assert isinstance(result, list)
    assert "TsingHua University" in result
    assert "Peking University" in result


def test_affiliations_none_without_fulltext(llm_params):
    client = make_stub_openai_client()
    paper = make_sample_paper(full_text=None)
    result = paper.generate_affiliations(client, llm_params)
    assert result is None


def test_affiliations_deduplicates(llm_params):
    """The stub returns two distinct affiliations, so no dedup needed.
    But confirm the set() dedup in the code doesn't break anything.
    """
    client = make_stub_openai_client()
    paper = make_sample_paper()
    result = paper.generate_affiliations(client, llm_params)
    assert len(result) == len(set(result))


def test_affiliations_malformed_llm_output(llm_params):
    """LLM returns affiliations without JSON brackets. Should fall back gracefully."""
    from types import SimpleNamespace

    def create_no_brackets(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="TsingHua University, Peking University"),
                )
            ]
        )

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create_no_brackets)
        )
    )
    paper = make_sample_paper()
    result = paper.generate_affiliations(client, llm_params)
    # re.search for [...] will fail -> AttributeError -> caught -> returns None
    assert result is None


def test_affiliations_error_returns_none(llm_params):
    from types import SimpleNamespace

    broken_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kw: (_ for _ in ()).throw(RuntimeError("boom")))
        )
    )
    paper = make_sample_paper()
    result = paper.generate_affiliations(broken_client, llm_params)
    assert result is None
    assert paper.affiliations is None
