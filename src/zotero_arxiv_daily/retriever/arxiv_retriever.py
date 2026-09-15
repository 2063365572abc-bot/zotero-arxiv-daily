from .base import BaseRetriever, register_retriever
import arxiv
from arxiv import Result as ArxivResult
from ..protocol import Paper
from ..utils import extract_markdown_from_pdf, extract_tex_code_from_tar
from tempfile import TemporaryDirectory
import feedparser
from tqdm import tqdm
import multiprocessing
import os
from queue import Empty
from time import sleep
from typing import Any, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from loguru import logger
import requests
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
from lxml import html as lxml_html

T = TypeVar("T")

DOWNLOAD_TIMEOUT = (10, 60)
PDF_EXTRACT_TIMEOUT = 180
TAR_EXTRACT_TIMEOUT = 180


def _download_file(url: str, path: str) -> None:
    with requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:
        response.raise_for_status()
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)


def _run_in_subprocess(
    result_queue: Any,
    func: Callable[..., T | None],
    args: tuple[Any, ...],
) -> None:
    try:
        result_queue.put(("ok", func(*args)))
    except Exception as exc:
        result_queue.put(("error", f"{type(exc).__name__}: {exc}"))


def _run_with_hard_timeout(
    func: Callable[..., T | None],
    args: tuple[Any, ...],
    *,
    timeout: float,
    operation: str,
    paper_title: str,
) -> T | None:
    start_methods = multiprocessing.get_all_start_methods()
    if "fork" not in start_methods:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            future.cancel()
            logger.warning(f"{operation} timed out for {paper_title} after {timeout} seconds")
            return None
        except Exception as exc:
            logger.warning(f"{operation} failed for {paper_title}: {type(exc).__name__}: {exc}")
            return None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    context = multiprocessing.get_context("fork")
    result_queue = context.Queue()
    process = context.Process(target=_run_in_subprocess, args=(result_queue, func, args))
    process.start()

    try:
        status, payload = result_queue.get(timeout=timeout)
    except Empty:
        if process.is_alive():
            process.kill()
        process.join(5)
        result_queue.close()
        result_queue.join_thread()
        logger.warning(f"{operation} timed out for {paper_title} after {timeout} seconds")
        return None

    process.join(5)
    result_queue.close()
    result_queue.join_thread()

    if status == "ok":
        return payload

    logger.warning(f"{operation} failed for {paper_title}: {payload}")
    return None


def _extract_text_from_pdf_worker(pdf_url: str) -> str:
    with TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "paper.pdf")
        _download_file(pdf_url, path)
        return extract_markdown_from_pdf(path)


def _extract_text_from_html_worker(html_url: str) -> str | None:
    import trafilatura

    downloaded = trafilatura.fetch_url(html_url)
    if downloaded is None:
        raise ValueError(f"Failed to download HTML from {html_url}")
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not text:
        raise ValueError(f"No text extracted from {html_url}")
    return text


def _extract_text_from_tar_worker(source_url: str, paper_id: str, paper_title: str | None = None) -> str | None:
    with TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "paper.tar.gz")
        _download_file(source_url, path)
        file_contents = extract_tex_code_from_tar(path, paper_id, paper_title=paper_title)
        if not file_contents or "all" not in file_contents:
            raise ValueError("Main tex file not found.")
        return file_contents["all"]


@register_retriever("arxiv")
class ArxivRetriever(BaseRetriever):
    def __init__(self, config):
        super().__init__(config)
        if self.config.source.arxiv.category is None and not self.config.source.arxiv.get("keywords"):
            raise ValueError("category must be specified for arxiv.")

    def _keyword_groups(self) -> tuple[list[str], list[str], list[str]]:
        domain = list(self.config.source.arxiv.get("domain_keywords") or [])
        method = list(self.config.source.arxiv.get("method_keywords") or [])
        task = list(self.config.source.arxiv.get("task_keywords") or [])
        return (
            [str(value).strip() for value in domain if str(value).strip()],
            [str(value).strip() for value in method if str(value).strip()],
            [str(value).strip() for value in task if str(value).strip()],
        )

    def _uses_strict_keyword_groups(self) -> bool:
        domain, method, _ = self._keyword_groups()
        return bool(domain and method)

    def retrieve_papers(self) -> list[Paper]:
        """Convert and deterministically rank the strict keyword candidate pool."""
        raw_papers = self._retrieve_raw_papers()
        papers = []
        for raw_paper in raw_papers:
            try:
                paper = self.convert_to_paper(raw_paper)
            except Exception as exc:
                logger.warning(f"Skipping paper {getattr(raw_paper, 'title', raw_paper)}: {exc}")
                continue
            if paper is None:
                continue
            self._attach_metadata(paper, raw_paper)
            papers.append(paper)

        if not self._uses_strict_keyword_groups():
            if self.max_candidate_num is not None:
                papers = papers[: self.max_candidate_num]
            return papers

        for paper in papers:
            paper.score = self._deterministic_retrieval_score(paper)
        papers.sort(
            key=lambda paper: (
                getattr(paper, "freshness_bucket", 0),
                paper.score if paper.score is not None else -1,
                getattr(paper, "published_date", ""),
            ),
            reverse=True,
        )
        limit = int(self.config.source.arxiv.get("retrieval_result_limit") or 20)
        return papers[:limit]

    def _retrieve_raw_papers(self) -> list[ArxivResult]:
        if self._uses_strict_keyword_groups():
            return self._retrieve_strict_keyword_papers()
        keywords = self.config.source.arxiv.get("keywords") or []
        if keywords:
            max_results = int(self.config.source.arxiv.get("keyword_query_max_results") or self.max_candidate_num or 20)
            client = arxiv.Client(num_retries=1, delay_seconds=3, page_size=max_results)
            query = self._build_keyword_query(list(keywords))
            logger.info(f"Retrieving arXiv papers by keyword query: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            try:
                return list(client.results(search))
            except arxiv.HTTPError as exc:
                if exc.status in {429, 503} and self.config.source.arxiv.get("keyword_fallback_to_rss", True):
                    logger.warning(
                        f"arXiv keyword API returned {exc.status}; falling back to category RSS with local keyword filtering."
                    )
                    return self._retrieve_keyword_rss_fallback(list(keywords), max_results)
                raise

        client = arxiv.Client(num_retries=10, delay_seconds=10)
        query = '+'.join(self.config.source.arxiv.category)
        include_cross_list = self.config.source.arxiv.get("include_cross_list", False)
        # Get the latest paper from arxiv rss feed
        feed = feedparser.parse(f"https://rss.arxiv.org/atom/{query}")
        if 'Feed error for query' in feed.feed.title:
            raise Exception(f"Invalid ARXIV_QUERY: {query}.")
        raw_papers = []
        allowed_announce_types = {"new", "cross"} if include_cross_list else {"new"}
        feed_entries = [
            i for i in feed.entries
            if i.get("arxiv_announce_type", "new") in allowed_announce_types
        ]
        if self.config.executor.debug:
            feed_entries = feed_entries[: self.debug_paper_limit]
        if self.retriever_config.get("use_rss_metadata", True):
            return feed_entries

        all_paper_ids = [
            i.id.removeprefix("oai:arXiv.org:")
            for i in feed_entries
        ]

        # Get full information of each paper from arxiv api
        bar = tqdm(total=len(all_paper_ids))
        max_batch_retries = 5
        batch_retry_delay = 30
        for i in range(0, len(all_paper_ids), 20):
            search = arxiv.Search(id_list=all_paper_ids[i:i + 20])
            for attempt in range(max_batch_retries):
                try:
                    batch = list(client.results(search))
                    bar.update(len(batch))
                    raw_papers.extend(batch)
                    break
                except arxiv.HTTPError as exc:
                    if exc.status == 429 and attempt < max_batch_retries - 1:
                        wait = batch_retry_delay * (attempt + 1)
                        logger.warning(f"arXiv API 429 on batch {i // 20}, retry {attempt + 1}/{max_batch_retries} in {wait}s")
                        sleep(wait)
                    else:
                        raise
            if i + 20 < len(all_paper_ids):
                sleep(3)
        bar.close()

        return raw_papers

    def _retrieve_strict_keyword_papers(self) -> list[ArxivResult | dict[str, Any]]:
        domain, method, task = self._keyword_groups()
        limit = int(self.config.source.arxiv.get("retrieval_result_limit") or 20)
        max_results = int(self.config.source.arxiv.get("keyword_query_max_results") or 100)
        primary_hours = int(self.config.source.arxiv.get("freshness_hours") or 48)
        fallback_hours = int(self.config.source.arxiv.get("freshness_fallback_hours") or 168)
        monthly_hours = int(self.config.source.arxiv.get("freshness_month_hours") or 720)
        results: list[ArxivResult | dict[str, Any]] = []
        seen_ids: set[str] = set()

        def add_matches(batch: list[ArxivResult | dict[str, Any]]) -> None:
            for item in batch:
                item_id = self._raw_id(item)
                if item_id and item_id in seen_ids:
                    continue
                if item_id:
                    seen_ids.add(item_id)
                if self._matches_keyword_groups(item, domain, method):
                    results.append(item)

        if self.config.source.arxiv.get("strict_rss_first", True):
            for hours in self._ordered_freshness_windows(primary_hours, fallback_hours, monthly_hours):
                add_matches(self._retrieve_strict_keyword_rss(domain, method, task, hours))
                if len(results) >= limit:
                    return results[:limit]

        if self.config.source.arxiv.get("strict_html_fallback_enabled", True):
            backfill_hours = int(self.config.source.arxiv.get("retrieval_backfill_hours") or 720)
            html_limit = int(self.config.source.arxiv.get("html_fallback_result_limit") or 50)
            add_matches(self._retrieve_strict_keyword_html(domain, method, task, backfill_hours, html_limit))
            if len(results) >= limit:
                return results[:limit]

        # The API is a last resort. A single failed request disables the rest of
        # the API window for this run, preventing a 429 from turning into a burst
        # of retries. RSS and HTML already provide the title/abstract metadata.
        client = arxiv.Client(num_retries=1, delay_seconds=3, page_size=max_results)
        api_hours = (
            self._ordered_freshness_windows(primary_hours, fallback_hours, monthly_hours)
            if not self.config.source.arxiv.get("strict_rss_first", True)
            else (monthly_hours,)
        )
        for hours in api_hours:
            query = self._build_grouped_keyword_query(domain, method, task, hours)
            logger.info(f"Retrieving strict arXiv keyword query: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            try:
                batch = list(client.results(search))
            except arxiv.HTTPError as exc:
                if exc.status in {429, 503} and self.config.source.arxiv.get("keyword_fallback_to_rss", True):
                    logger.warning(f"arXiv keyword API returned {exc.status}; skipping further API requests for this run.")
                    break
                raise
            add_matches(batch)
            if len(results) >= limit:
                break
        logger.info(f"Strict arXiv retrieval produced {len(results)} domain+method candidates.")
        return results[:limit]

    @staticmethod
    def _ordered_freshness_windows(*hours_values: int) -> tuple[int, ...]:
        ordered: list[int] = []
        for hours in hours_values:
            if hours > 0 and hours not in ordered:
                ordered.append(hours)
        return tuple(ordered)

    def _retrieve_keyword_rss_fallback(self, keywords: list[str], max_results: int) -> list[dict[str, Any]]:
        categories = self.config.source.arxiv.category
        if not categories:
            raise ValueError("source.arxiv.category is required for keyword RSS fallback.")

        query = '+'.join(categories)
        include_cross_list = self.config.source.arxiv.get("include_cross_list", False)
        feed = feedparser.parse(f"https://rss.arxiv.org/atom/{query}")
        if 'Feed error for query' in feed.feed.title:
            raise Exception(f"Invalid ARXIV_QUERY: {query}.")

        allowed_announce_types = {"new", "cross"} if include_cross_list else {"new"}
        normalized_keywords = [str(keyword).strip().lower() for keyword in keywords if str(keyword).strip()]
        matched_entries = []
        for entry in feed.entries:
            if entry.get("arxiv_announce_type", "new") not in allowed_announce_types:
                continue
            searchable_text = f"{entry.get('title', '')}\n{entry.get('summary', '')}".lower()
            if any(keyword in searchable_text for keyword in normalized_keywords):
                matched_entries.append(entry)
            if len(matched_entries) >= max_results:
                break

        logger.info(f"Keyword RSS fallback matched {len(matched_entries)} arXiv papers.")
        return matched_entries

    def _retrieve_strict_keyword_rss(
        self,
        domain: list[str],
        method: list[str],
        task: list[str],
        freshness_hours: int,
    ) -> list[dict[str, Any]]:
        categories = self.config.source.arxiv.category
        if not categories:
            raise ValueError("source.arxiv.category is required for keyword RSS fallback.")
        limit = int(self.config.source.arxiv.get("keyword_query_max_results") or 100)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=freshness_hours)
        include_cross_list = self.config.source.arxiv.get("include_cross_list", False)
        allowed = {"new", "cross"} if include_cross_list else {"new"}
        matches = []
        seen_ids: set[str] = set()
        for category in categories:
            feed = feedparser.parse(f"https://rss.arxiv.org/atom/{category}")
            if "Feed error for query" in feed.feed.title:
                raise ValueError(f"Invalid ARXIV_QUERY: {category}.")
            for entry in feed.entries:
                if entry.get("arxiv_announce_type", "new") not in allowed:
                    continue
                published = self._raw_datetime(entry)
                if published is None or published < cutoff:
                    continue
                item_id = self._raw_id(entry)
                if item_id in seen_ids:
                    continue
                if self._matches_keyword_groups(entry, domain, method):
                    entry["retrieval_source"] = "rss"
                    matches.append(entry)
                    seen_ids.add(item_id)
                if len(matches) >= limit:
                    return matches
        logger.info(f"Strict keyword RSS fallback matched {len(matches)} papers in {freshness_hours}h.")
        return matches

    def _retrieve_strict_keyword_html(
        self,
        domain: list[str],
        method: list[str],
        task: list[str],
        freshness_hours: int,
        max_results: int,
    ) -> list[dict[str, Any]]:
        """Use arXiv's human search page as a rate-limit-safe metadata fallback."""
        categories = self.config.source.arxiv.category or []
        category_query = " OR ".join(f"cat:{category}" for category in categories)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=freshness_hours)
        matches: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for domain_term in domain:
            escaped_term = domain_term.replace('"', '\\"')
            query = f'"{escaped_term}"'
            if category_query:
                query = f"{query} AND ({category_query})"
            try:
                response = requests.get(
                    "https://arxiv.org/search/",
                    params={
                        "query": query,
                        "searchtype": "all",
                        "abstracts": "show",
                        "order": "-announced_date_first",
                        "size": min(max_results, 200),
                    },
                    headers={"User-Agent": "zotero-arxiv-daily/1.0 (research metadata retrieval)"},
                    timeout=DOWNLOAD_TIMEOUT,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                logger.warning(f"arXiv HTML search fallback failed for {domain_term}: {type(exc).__name__}: {exc}")
                continue

            root = lxml_html.fromstring(response.content)
            result_nodes = root.xpath('//li[contains(concat(" ", normalize-space(@class), " "), " arxiv-result ")]')
            for node in result_nodes:
                title = self._html_node_text(node, "title")
                abstract = self._html_abstract_text(node)
                abs_url = ""
                paper_id = ""
                for link in node.xpath('.//a[@href]'):
                    found = re.search(r"arxiv\.org/abs/([^/?#]+)", link.get("href", ""))
                    if found:
                        paper_id = found.group(1)
                        abs_url = f"https://arxiv.org/abs/{paper_id}"
                        break
                published = self._html_submitted_datetime(node)
                if not paper_id or paper_id in seen_ids or not title or published is None or published < cutoff:
                    continue
                raw = {
                    "title": title,
                    "summary": abstract,
                    "authors": [{"name": name} for name in self._html_authors(node)],
                    "link": abs_url,
                    "id": f"oai:arXiv.org:{paper_id}",
                    "published": published.isoformat(),
                    "updated": published.isoformat(),
                    "tags": [],
                    "arxiv_announce_type": "new",
                    "retrieval_source": "html",
                }
                if self._matches_keyword_groups(raw, domain, method):
                    matches.append(raw)
                    seen_ids.add(paper_id)
                if len(matches) >= max_results:
                    return matches
        logger.info(f"Strict keyword HTML fallback matched {len(matches)} papers in {freshness_hours}h.")
        return matches

    @staticmethod
    def _html_node_text(node: Any, class_name: str) -> str:
        nodes = node.xpath(f'.//*[contains(concat(" ", normalize-space(@class), " "), " {class_name} ")]')
        return re.sub(r"\s+", " ", " ".join(item.text_content() for item in nodes)).strip()

    @classmethod
    def _html_abstract_text(cls, node: Any) -> str:
        nodes = node.xpath('.//*[contains(concat(" ", normalize-space(@class), " "), " abstract ")]')
        if not nodes:
            return ""
        full_nodes = nodes[0].xpath('.//*[contains(concat(" ", normalize-space(@class), " "), " abstract-full ")]')
        source = full_nodes[0] if full_nodes else nodes[0]
        text = re.sub(r"\s+", " ", source.text_content()).strip()
        text = re.sub(r"\s+[^\w\s]*\s*(?:More|Less)\s*$", "", text, flags=re.IGNORECASE)
        return re.sub(r"^Abstract:\s*", "", text, flags=re.IGNORECASE)

    @classmethod
    def _html_submitted_datetime(cls, node: Any) -> datetime | None:
        text = re.sub(r"\s+", " ", node.text_content()).strip()
        match = re.search(r"Submitted\s+(\d{1,2}\s+[A-Za-z]+,\s+\d{4})", text)
        if not match:
            return None
        try:
            return datetime.strptime(match.group(1), "%d %B, %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    @staticmethod
    def _html_authors(node: Any) -> list[str]:
        names = []
        for link in node.xpath('.//a[contains(@href, "searchtype=author")]'):
            name = re.sub(r"\s+", " ", link.text_content()).strip()
            if name and name not in names:
                names.append(name)
        return names

    def _build_keyword_query(self, keywords: list[str]) -> str:
        keyword_terms = []
        for keyword in keywords:
            keyword = str(keyword).strip()
            if not keyword:
                continue
            escaped = keyword.replace('"', '\\"')
            keyword_terms.append(f'all:"{escaped}"')
        if not keyword_terms:
            raise ValueError("source.arxiv.keywords must contain at least one non-empty keyword.")

        query = "(" + " OR ".join(keyword_terms) + ")"
        categories = self.config.source.arxiv.category
        if categories:
            category_terms = [f"cat:{category}" for category in categories]
            query = query + " AND (" + " OR ".join(category_terms) + ")"
        return query

    def _build_grouped_keyword_query(
        self, domain: list[str], method: list[str], task: list[str], freshness_hours: int
    ) -> str:
        def field_terms(values: list[str]) -> str:
            parts = []
            for value in values:
                escaped = value.replace('"', '\\"')
                parts.append(f'(ti:"{escaped}" OR abs:"{escaped}")')
            return "(" + " OR ".join(parts) + ")"

        query = f"{field_terms(domain)} AND {field_terms(method)}"
        categories = self.config.source.arxiv.category
        if categories:
            query = query + " AND (" + " OR ".join(f"cat:{category}" for category in categories) + ")"
        now = datetime.now(timezone.utc)
        start = (now - timedelta(hours=freshness_hours)).strftime("%Y%m%d%H%M")
        end = (now + timedelta(minutes=5)).strftime("%Y%m%d%H%M")
        return f"{query} AND submittedDate:[{start} TO {end}]"

    @staticmethod
    def _raw_id(raw_paper: ArxivResult | dict[str, Any]) -> str:
        if isinstance(raw_paper, dict):
            return str(raw_paper.get("id", "")).removeprefix("oai:arXiv.org:")
        return str(getattr(raw_paper, "entry_id", "")).rstrip("/").rsplit("/", 1)[-1]

    @staticmethod
    def _parse_datetime_value(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if hasattr(value, "tm_year"):
            return datetime(value.tm_year, value.tm_mon, value.tm_mday, value.tm_hour, value.tm_min, value.tm_sec, tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                return None
        return None

    @classmethod
    def _raw_datetime(cls, raw_paper: ArxivResult | dict[str, Any], field: str = "published") -> datetime | None:
        if isinstance(raw_paper, dict):
            value = raw_paper.get(f"{field}_parsed") or raw_paper.get(field)
        else:
            value = getattr(raw_paper, field, None)
        return cls._parse_datetime_value(value)

    @staticmethod
    def _raw_text(raw_paper: ArxivResult | dict[str, Any]) -> str:
        if isinstance(raw_paper, dict):
            return f"{raw_paper.get('title', '')}\n{raw_paper.get('summary', '')}".lower()
        return f"{getattr(raw_paper, 'title', '')}\n{getattr(raw_paper, 'summary', '')}".lower()

    def _matches_keyword_groups(self, raw_paper: ArxivResult | dict[str, Any], domain: list[str], method: list[str]) -> bool:
        text = self._raw_text(raw_paper)
        return any(term.lower() in text for term in domain) and any(term.lower() in text for term in method)

    def _deterministic_retrieval_score(self, paper: Paper) -> float:
        domain, method, task = self._keyword_groups()
        title = paper.title.lower()
        abstract = paper.abstract.lower()
        combined = f"{title}\n{abstract}"
        score = 0.0
        score += 6 if any(term.lower() in title for term in domain) else 3
        score += 4 if any(term.lower() in title for term in method) else 2
        score += 2 if any(term.lower() in combined for term in task) else 0
        score += getattr(paper, "freshness_bucket", 0) * 0.5
        return score

    def _freshness_metadata(self, published: datetime | None) -> tuple[int, str]:
        if published is None:
            return 0, "unknown"
        now = datetime.now(timezone.utc)
        age_hours = (now - published).total_seconds() / 3600
        primary_hours = int(self.config.source.arxiv.get("freshness_hours") or 48)
        fallback_hours = int(self.config.source.arxiv.get("freshness_fallback_hours") or 168)
        monthly_hours = int(self.config.source.arxiv.get("freshness_month_hours") or 720)
        if age_hours <= primary_hours:
            return 4, "latest_48h"
        if age_hours <= fallback_hours:
            return 3, "recent_7d"
        if age_hours <= monthly_hours:
            return 2, "recent_30d"
        return 1, "backfill"

    def _attach_metadata(self, paper: Paper, raw_paper: ArxivResult | dict[str, Any]) -> None:
        published = self._raw_datetime(raw_paper)
        paper.arxiv_id = self._raw_id(raw_paper)
        paper.published_date = published.isoformat() if published else None
        updated = self._raw_datetime(raw_paper, "updated") or published
        paper.updated_date = updated.isoformat() if updated else None
        paper.categories = [str(category) for category in (raw_paper.get("tags", []) if isinstance(raw_paper, dict) else getattr(raw_paper, "categories", []))]
        paper.retrieval_freshness_hours = int(self.config.source.arxiv.get("freshness_hours") or 48)
        paper.freshness_bucket, paper.freshness_label = self._freshness_metadata(published)
        paper.matched_terms = {
            "domain": [term for term in self._keyword_groups()[0] if term.lower() in f"{paper.title}\n{paper.abstract}".lower()],
            "method": [term for term in self._keyword_groups()[1] if term.lower() in f"{paper.title}\n{paper.abstract}".lower()],
            "task": [term for term in self._keyword_groups()[2] if term.lower() in f"{paper.title}\n{paper.abstract}".lower()],
        }
        paper.retrieval_source = raw_paper.get("retrieval_source", "api") if isinstance(raw_paper, dict) else "api"

    def convert_to_paper(self, raw_paper: ArxivResult | dict[str, Any]) -> Paper:
        if isinstance(raw_paper, dict) or (hasattr(raw_paper, "get") and not hasattr(raw_paper, "pdf_url")):
            title = raw_paper["title"]
            authors = []
            for author in raw_paper.get("authors", []):
                name = author.get("name", "")
                authors.extend([a.strip() for a in name.split(",") if a.strip()])
            abstract = raw_paper.get("summary", "")
            abstract = re.sub(r"^arXiv:\S+\s+Announce Type:\s+\S+\s+Abstract:\s*", "", abstract, flags=re.DOTALL)
            url = raw_paper.get("link")
            paper_id = raw_paper.get("id", "").removeprefix("oai:arXiv.org:")
            pdf_url = f"https://arxiv.org/pdf/{paper_id}" if paper_id else url
            return Paper(
                source=self.name,
                title=title,
                authors=authors,
                abstract=abstract,
                url=url,
                pdf_url=pdf_url,
                full_text=None,
            )

        title = raw_paper.title
        authors = [a.name for a in raw_paper.authors]
        abstract = raw_paper.summary
        pdf_url = raw_paper.pdf_url
        full_text = None
        if self.retriever_config.get("extract_full_text", False):
            full_text = extract_text_from_tar(raw_paper)
            if full_text is None:
                full_text = extract_text_from_html(raw_paper)
            if full_text is None:
                full_text = extract_text_from_pdf(raw_paper)
        return Paper(
            source=self.name,
            title=title,
            authors=authors,
            abstract=abstract,
            url=raw_paper.entry_id,
            pdf_url=pdf_url,
            full_text=full_text,
        )


def extract_text_from_html(paper: ArxivResult) -> str | None:
    html_url = paper.entry_id.replace("/abs/", "/html/")
    try:
        return _extract_text_from_html_worker(html_url)
    except Exception as exc:
        logger.warning(f"HTML extraction failed for {paper.title}: {exc}")
        return None


def extract_text_from_pdf(paper: ArxivResult) -> str | None:
    if paper.pdf_url is None:
        logger.warning(f"No PDF URL available for {paper.title}")
        return None
    return _run_with_hard_timeout(
        _extract_text_from_pdf_worker,
        (paper.pdf_url,),
        timeout=PDF_EXTRACT_TIMEOUT,
        operation="PDF extraction",
        paper_title=paper.title,
    )


def extract_text_from_tar(paper: ArxivResult) -> str | None:
    source_url = paper.source_url()
    if source_url is None:
        logger.warning(f"No source URL available for {paper.title}")
        return None
    return _run_with_hard_timeout(
        _extract_text_from_tar_worker,
        (source_url, paper.entry_id, paper.title),
        timeout=TAR_EXTRACT_TIMEOUT,
        operation="Tar extraction",
        paper_title=paper.title,
    )
