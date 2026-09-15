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

    def _retrieve_raw_papers(self) -> list[ArxivResult]:
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
