from datetime import datetime
from types import SimpleNamespace

from zotero_arxiv_daily.protocol import CorpusPaper, Paper
from zotero_arxiv_daily.research_state import (
    ResearchRadarState,
    candidate_embedding_records,
    corpus_embedding_records,
    embedding_rerank_candidates,
    ensure_embeddings,
)


def test_embedding_cache_reuses_existing_vectors(tmp_path):
    state = ResearchRadarState(tmp_path / "radar.sqlite")
    calls = []

    class FakeEmbeddings:
        def create(self, input, model):
            calls.append(list(input))
            data = []
            for text in input:
                value = float(len(text) % 10 + 1)
                data.append(SimpleNamespace(embedding=[value, 0.0, 0.0]))
            return SimpleNamespace(data=data)

    client = SimpleNamespace(embeddings=FakeEmbeddings())
    records = [
        ("a", "Title: A\nAbstract: spatial transcriptomics", "hash-a", {"title": "A"}),
        ("b", "Title: B\nAbstract: graph neural network", "hash-b", {"title": "B"}),
    ]

    vectors, audit = ensure_embeddings(
        state,
        records,
        entity_type="candidate",
        model="text-embedding-v4",
        openai_client=client,
        batch_size=10,
    )
    assert vectors.shape == (2, 3)
    assert audit == {"cache_hit_count": 0, "api_create_count": 2}

    vectors, audit = ensure_embeddings(
        state,
        records,
        entity_type="candidate",
        model="text-embedding-v4",
        openai_client=client,
        batch_size=10,
    )
    assert vectors.shape == (2, 3)
    assert audit == {"cache_hit_count": 2, "api_create_count": 0}
    assert len(calls) == 1
    state.close()


def test_embedding_rerank_records_zotero_evidence():
    papers = [
        Paper(
            source="arxiv",
            title="Spatial Transcriptomics Foundation Model",
            authors=[],
            abstract="A foundation model for spatial transcriptomics.",
            url="https://arxiv.org/abs/2601.1",
            pdf_url="https://arxiv.org/pdf/2601.1",
        ),
        Paper(
            source="arxiv",
            title="Unrelated Vision Paper",
            authors=[],
            abstract="A generic vision paper.",
            url="https://arxiv.org/abs/2601.2",
            pdf_url="https://arxiv.org/pdf/2601.2",
        ),
    ]
    papers[0].arxiv_id = "2601.1"
    papers[0].freshness_label = "latest_48h"
    papers[0].matched_terms = {"domain": ["spatial transcriptomics"], "method": ["foundation model"], "task": []}
    papers[1].arxiv_id = "2601.2"
    papers[1].freshness_label = "backfill"
    papers[1].matched_terms = {"domain": [], "method": [], "task": []}
    corpus = [
        CorpusPaper(
            title="My Spatial Transcriptomics Paper",
            abstract="spatial transcriptomics foundation model",
            added_date=datetime(2026, 1, 1),
            paths=["一多科研/单细胞转录组"],
        )
    ]

    ranked, records = embedding_rerank_candidates(
        papers,
        corpus,
        candidate_vectors=__import__("numpy").array([[1.0, 0.0], [0.0, 1.0]]),
        corpus_vectors=__import__("numpy").array([[1.0, 0.0]]),
    )

    assert ranked[0].arxiv_id == "2601.1"
    assert ranked[0].embedding_rank == 1
    assert ranked[0].matched_zotero_items[0]["title"] == "My Spatial Transcriptomics Paper"
    assert records[0].score_breakdown["domain_keyword_score"] > 0


def test_embedding_record_builders_are_stable():
    paper = Paper("arxiv", "A", [], "B", "https://arxiv.org/abs/1")
    paper.arxiv_id = "1"
    corpus = [CorpusPaper("C", "D", datetime(2026, 1, 1), ["x"])]
    assert candidate_embedding_records([paper], "text-embedding-v4")[0][0] == "1"
    assert len(corpus_embedding_records(corpus, "text-embedding-v4")[0][0]) == 64


def test_state_returns_previously_promoted_ids_and_zotero_titles(tmp_path):
    state = ResearchRadarState(tmp_path / "radar.sqlite")
    state.conn.execute(
        "INSERT INTO daily_selections(run_date, arxiv_id, selection_json) VALUES(?,?,?)",
        ("2026-09-14", "2601.00001", "{}"),
    )
    state.conn.execute(
        "INSERT INTO zotero_uploads(run_date, arxiv_id, upload_json) VALUES(?,?,?)",
        ("2026-09-13", "2601.00002", '{"status":"uploaded"}'),
    )
    state.conn.execute(
        "INSERT INTO daily_selections(run_date, arxiv_id, selection_json) VALUES(?,?,?)",
        ("2026-09-15", "2601.00003", "{}"),
    )
    state.conn.execute(
        "INSERT INTO zotero_uploads(run_date, arxiv_id, upload_json) VALUES(?,?,?)",
        ("2026-09-14", "2601.00004", '{"status":"failed"}'),
    )
    corpus = [CorpusPaper("Already In Zotero", "abstract", datetime(2026, 1, 1), ["一多科研"])]
    state.upsert_zotero_items(corpus, "text-embedding-v4")

    assert state.previously_selected_or_uploaded_arxiv_ids(before_date="2026-09-15") == {"2601.00002"}
    assert "already in zotero" in state.zotero_title_fingerprints()
    state.close()
