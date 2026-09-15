from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import sqlite3
from typing import Any

from loguru import logger
import numpy as np
from openai import OpenAI

from .protocol import CorpusPaper, Paper


@dataclass
class MatchedZoteroItem:
    title: str
    similarity: float
    added_date: str
    paths: list[str]


@dataclass
class RadarRankingRecord:
    arxiv_id: str | None
    title: str
    url: str
    pdf_url: str | None
    published_date: str | None
    freshness_label: str
    embedding_score: float
    final_score: float
    score_breakdown: dict[str, float]
    matched_zotero_items: list[dict[str, Any]]
    matched_terms: dict[str, list[str]] | None


class ResearchRadarState:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS arxiv_papers (
                arxiv_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT NOT NULL,
                url TEXT NOT NULL,
                pdf_url TEXT,
                published_date TEXT,
                updated_date TEXT,
                metadata_json TEXT NOT NULL,
                seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS zotero_items (
                item_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT NOT NULL,
                added_date TEXT NOT NULL,
                paths_json TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                synced_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS embeddings (
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                model TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                embedding_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (entity_type, entity_id, model)
            );
            CREATE TABLE IF NOT EXISTS daily_runs (
                run_date TEXT PRIMARY KEY,
                metadata_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS daily_rankings (
                run_date TEXT NOT NULL,
                arxiv_id TEXT NOT NULL,
                ranking_json TEXT NOT NULL,
                PRIMARY KEY (run_date, arxiv_id)
            );
            CREATE TABLE IF NOT EXISTS daily_selections (
                run_date TEXT NOT NULL,
                arxiv_id TEXT NOT NULL,
                selection_json TEXT NOT NULL,
                PRIMARY KEY (run_date, arxiv_id)
            );
            CREATE TABLE IF NOT EXISTS zotero_uploads (
                run_date TEXT NOT NULL,
                arxiv_id TEXT NOT NULL,
                upload_json TEXT NOT NULL,
                PRIMARY KEY (run_date, arxiv_id)
            );
            """
        )
        self.conn.commit()

    @staticmethod
    def normalized_text(title: str, abstract: str, extra: str = "") -> str:
        return "\n".join(
            part.strip()
            for part in [
                f"Title: {title or ''}",
                f"Abstract: {abstract or ''}",
                extra.strip(),
            ]
            if part.strip()
        )

    @staticmethod
    def text_hash(text: str, model: str) -> str:
        return sha256(f"{model}\n{text}".encode("utf-8")).hexdigest()

    @staticmethod
    def zotero_id(item: CorpusPaper) -> str:
        basis = json.dumps(
            {
                "title": item.title,
                "abstract": item.abstract,
                "added_date": item.added_date.isoformat(),
                "paths": item.paths,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return sha256(basis.encode("utf-8")).hexdigest()

    @staticmethod
    def arxiv_id(paper: Paper) -> str:
        arxiv_id = getattr(paper, "arxiv_id", None)
        if arxiv_id:
            return str(arxiv_id)
        return sha256((paper.url or paper.title).encode("utf-8")).hexdigest()

    def upsert_zotero_items(self, corpus: list[CorpusPaper], model: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        for item in corpus:
            text = self.normalized_text(item.title, item.abstract, "Collections: " + "; ".join(item.paths))
            rows.append(
                (
                    self.zotero_id(item),
                    item.title,
                    item.abstract,
                    item.added_date.isoformat(),
                    json.dumps(item.paths, ensure_ascii=False),
                    self.text_hash(text, model),
                    now,
                )
            )
        self.conn.executemany(
            """
            INSERT INTO zotero_items(item_id,title,abstract,added_date,paths_json,text_hash,synced_at)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(item_id) DO UPDATE SET
              title=excluded.title,
              abstract=excluded.abstract,
              added_date=excluded.added_date,
              paths_json=excluded.paths_json,
              text_hash=excluded.text_hash,
              synced_at=excluded.synced_at
            """,
            rows,
        )
        self.conn.commit()

    def upsert_arxiv_papers(self, papers: list[Paper]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        for paper in papers:
            metadata = {
                "authors": paper.authors,
                "categories": getattr(paper, "categories", []),
                "freshness_label": getattr(paper, "freshness_label", "unknown"),
                "retrieval_source": getattr(paper, "retrieval_source", "unknown"),
                "matched_terms": getattr(paper, "matched_terms", None),
            }
            rows.append(
                (
                    self.arxiv_id(paper),
                    paper.title,
                    paper.abstract,
                    paper.url,
                    paper.pdf_url,
                    getattr(paper, "published_date", None),
                    getattr(paper, "updated_date", None),
                    json.dumps(metadata, ensure_ascii=False),
                    now,
                )
            )
        self.conn.executemany(
            """
            INSERT INTO arxiv_papers(arxiv_id,title,abstract,url,pdf_url,published_date,updated_date,metadata_json,seen_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            ON CONFLICT(arxiv_id) DO UPDATE SET
              title=excluded.title,
              abstract=excluded.abstract,
              url=excluded.url,
              pdf_url=excluded.pdf_url,
              published_date=excluded.published_date,
              updated_date=excluded.updated_date,
              metadata_json=excluded.metadata_json,
              seen_at=excluded.seen_at
            """,
            rows,
        )
        self.conn.commit()

    def get_embedding(self, entity_type: str, entity_id: str, model: str, text_hash: str) -> list[float] | None:
        row = self.conn.execute(
            """
            SELECT embedding_json FROM embeddings
            WHERE entity_type=? AND entity_id=? AND model=? AND text_hash=?
            """,
            (entity_type, entity_id, model, text_hash),
        ).fetchone()
        if row is None:
            return None
        return [float(value) for value in json.loads(row["embedding_json"])]

    def set_embedding(
        self,
        entity_type: str,
        entity_id: str,
        model: str,
        text_hash: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO embeddings(entity_type,entity_id,model,text_hash,embedding_json,metadata_json,updated_at)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(entity_type, entity_id, model) DO UPDATE SET
              text_hash=excluded.text_hash,
              embedding_json=excluded.embedding_json,
              metadata_json=excluded.metadata_json,
              updated_at=excluded.updated_at
            """,
            (
                entity_type,
                entity_id,
                model,
                text_hash,
                json.dumps(embedding),
                json.dumps(metadata or {}, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    def embedding_audit(self, model: str) -> dict[str, int | str]:
        rows = self.conn.execute(
            "SELECT entity_type, COUNT(*) AS count FROM embeddings WHERE model=? GROUP BY entity_type",
            (model,),
        ).fetchall()
        counts = {row["entity_type"]: int(row["count"]) for row in rows}
        return {
            "embedding_model": model,
            "zotero_embedding_count": counts.get("zotero", 0),
            "candidate_embedding_count": counts.get("candidate", 0),
        }

    def previously_selected_or_uploaded_arxiv_ids(self, before_date: str | None = None) -> set[str]:
        """Return arXiv IDs that have already been promoted beyond the candidate pool."""
        selected_query = "SELECT arxiv_id FROM daily_selections"
        upload_query = "SELECT arxiv_id FROM zotero_uploads"
        params: tuple[str, ...] = ()
        if before_date is not None:
            selected_query += " WHERE run_date < ?"
            upload_query += " WHERE run_date < ?"
            params = (before_date,)
        rows = self.conn.execute(f"{selected_query} UNION {upload_query}", params * 2).fetchall()
        return {str(row["arxiv_id"]) for row in rows if row["arxiv_id"]}

    def zotero_title_fingerprints(self) -> set[str]:
        rows = self.conn.execute("SELECT title FROM zotero_items").fetchall()
        return {_title_fingerprint(str(row["title"])) for row in rows if row["title"]}


def _title_fingerprint(title: str) -> str:
    return " ".join(title.casefold().split())


def _create_embeddings(
    texts: list[str],
    openai_client: OpenAI,
    model: str,
    batch_size: int,
) -> list[list[float]]:
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = openai_client.embeddings.create(input=batch, model=model)
        embeddings.extend([list(item.embedding) for item in response.data])
    return embeddings


def ensure_embeddings(
    state: ResearchRadarState,
    records: list[tuple[str, str, str, dict[str, Any]]],
    *,
    entity_type: str,
    model: str,
    openai_client: OpenAI,
    batch_size: int = 10,
) -> tuple[np.ndarray, dict[str, int]]:
    cached_or_none: list[list[float] | None] = []
    missing: list[tuple[int, str, str, str, dict[str, Any]]] = []
    for index, (entity_id, text, text_hash, metadata) in enumerate(records):
        cached = state.get_embedding(entity_type, entity_id, model, text_hash)
        cached_or_none.append(cached)
        if cached is None:
            missing.append((index, entity_id, text, text_hash, metadata))

    if missing:
        logger.info(f"Embedding {len(missing)} {entity_type} records with {model}")
        created = _create_embeddings([item[2] for item in missing], openai_client, model, batch_size)
        for (index, entity_id, _text, text_hash, metadata), embedding in zip(missing, created):
            state.set_embedding(entity_type, entity_id, model, text_hash, embedding, metadata)
            cached_or_none[index] = embedding
        state.conn.commit()

    vectors = [embedding for embedding in cached_or_none if embedding is not None]
    if len(vectors) != len(records):
        raise ValueError(f"Missing embeddings after creation: {len(records) - len(vectors)}")
    return np.array(vectors, dtype=float), {"cache_hit_count": len(records) - len(missing), "api_create_count": len(missing)}


def corpus_embedding_records(corpus: list[CorpusPaper], model: str) -> list[tuple[str, str, str, dict[str, Any]]]:
    records = []
    for item in corpus:
        item_id = ResearchRadarState.zotero_id(item)
        text = ResearchRadarState.normalized_text(
            item.title,
            item.abstract,
            "Collections: " + "; ".join(item.paths),
        )
        records.append(
            (
                item_id,
                text,
                ResearchRadarState.text_hash(text, model),
                {
                    "title": item.title,
                    "added_date": item.added_date.isoformat(),
                    "paths": item.paths,
                },
            )
        )
    return records


def candidate_embedding_records(papers: list[Paper], model: str) -> list[tuple[str, str, str, dict[str, Any]]]:
    records = []
    for paper in papers:
        paper_id = ResearchRadarState.arxiv_id(paper)
        text = ResearchRadarState.normalized_text(paper.title, paper.abstract)
        records.append(
            (
                paper_id,
                text,
                ResearchRadarState.text_hash(text, model),
                {
                    "title": paper.title,
                    "url": paper.url,
                    "published_date": getattr(paper, "published_date", None),
                },
            )
        )
    return records


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def _keyword_score(matched_terms: dict[str, list[str]] | None, key: str) -> float:
    terms = (matched_terms or {}).get(key, [])
    return min(1.0, len(terms) / 3)


def _freshness_score(label: str) -> float:
    return {
        "latest_48h": 1.0,
        "recent_7d": 0.8,
        "recent_30d": 0.55,
        "backfill": 0.2,
    }.get(label, 0.0)


def _paper_type_boost(paper: Paper) -> float:
    text = f"{paper.title}\n{paper.abstract}".lower()
    signals = [
        "foundation model",
        "benchmark",
        "representation",
        "cross-modal",
        "multimodal",
        "graph neural",
        "transformer",
        "contrastive",
    ]
    return 1.0 if any(signal in text for signal in signals) else 0.0


def embedding_rerank_candidates(
    papers: list[Paper],
    corpus: list[CorpusPaper],
    candidate_vectors: np.ndarray,
    corpus_vectors: np.ndarray,
    *,
    top_k_matches: int = 5,
) -> tuple[list[Paper], list[RadarRankingRecord]]:
    if not papers or not corpus:
        return [], []
    sim = _normalize(candidate_vectors).dot(_normalize(corpus_vectors).T)
    corpus_order = sorted(range(len(corpus)), key=lambda idx: corpus[idx].added_date, reverse=True)
    time_weights = 1 / (1 + np.log10(np.arange(len(corpus_order)) + 1))
    time_weights = time_weights / time_weights.sum()
    original_weights = np.zeros(len(corpus))
    for order_idx, corpus_idx in enumerate(corpus_order):
        original_weights[corpus_idx] = time_weights[order_idx]

    recent_indices = corpus_order[: min(10, len(corpus_order))]
    ranking_records: list[RadarRankingRecord] = []
    for paper_index, paper in enumerate(papers):
        weighted_similarity = float((sim[paper_index] * original_weights).sum())
        recent_similarity = float(sim[paper_index, recent_indices].mean()) if recent_indices else weighted_similarity
        matched_terms = getattr(paper, "matched_terms", None)
        freshness_label = getattr(paper, "freshness_label", "unknown")
        breakdown = {
            "zotero_topk_similarity": weighted_similarity,
            "recent_profile_similarity": recent_similarity,
            "domain_keyword_score": _keyword_score(matched_terms, "domain"),
            "method_keyword_score": _keyword_score(matched_terms, "method"),
            "freshness_score": _freshness_score(freshness_label),
            "paper_type_boost": _paper_type_boost(paper),
        }
        final_score = (
            0.45 * breakdown["zotero_topk_similarity"]
            + 0.20 * breakdown["recent_profile_similarity"]
            + 0.15 * breakdown["domain_keyword_score"]
            + 0.10 * breakdown["method_keyword_score"]
            + 0.05 * breakdown["freshness_score"]
            + 0.05 * breakdown["paper_type_boost"]
        )
        top_indices = list(np.argsort(sim[paper_index])[::-1][:top_k_matches])
        matched = [
            asdict(
                MatchedZoteroItem(
                    title=corpus[idx].title,
                    similarity=round(float(sim[paper_index, idx]), 6),
                    added_date=corpus[idx].added_date.isoformat(),
                    paths=corpus[idx].paths,
                )
            )
            for idx in top_indices
        ]
        paper.score = round(final_score * 100, 4)
        paper.embedding_score = round(weighted_similarity, 6)
        paper.score_breakdown = {key: round(value, 6) for key, value in breakdown.items()}
        paper.matched_zotero_items = matched
        paper.embedding_rank = 0
        ranking_records.append(
            RadarRankingRecord(
                arxiv_id=getattr(paper, "arxiv_id", None),
                title=paper.title,
                url=paper.url,
                pdf_url=paper.pdf_url,
                published_date=getattr(paper, "published_date", None),
                freshness_label=freshness_label,
                embedding_score=round(weighted_similarity, 6),
                final_score=paper.score,
                score_breakdown=paper.score_breakdown,
                matched_zotero_items=matched,
                matched_terms=matched_terms,
            )
        )

    ranked_pairs = sorted(zip(papers, ranking_records), key=lambda pair: pair[0].score or 0, reverse=True)
    ranked_papers = []
    ranked_records = []
    for rank, (paper, record) in enumerate(ranked_pairs, start=1):
        paper.embedding_rank = rank
        ranked_papers.append(paper)
        ranked_records.append(record)
    return ranked_papers, ranked_records
