from dataclasses import dataclass
from typing import Optional, TypeVar
from datetime import datetime
import re
import tiktoken
from openai import OpenAI
from loguru import logger
import json
RawPaperItem = TypeVar('RawPaperItem')


BRIEF_LABELS = {
    "一句话": "tldr",
    "为什么重要": "why_it_matters",
    "方法核心": "method_core",
    "实验证据": "evidence",
    "实验/证据": "evidence",
    "局限风险": "limitations",
    "局限": "limitations",
    "给你的启发": "research_inspiration",
}


def _extract_json_object(content: str) -> dict[str, str] | None:
    candidates = [content]
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.insert(0, fenced.group(1))
    loose = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if loose:
        candidates.append(loose.group(0))

    key_map = {
        "tldr": "tldr",
        "summary": "tldr",
        "一句话": "tldr",
        "why_it_matters": "why_it_matters",
        "为什么重要": "why_it_matters",
        "method_core": "method_core",
        "方法核心": "method_core",
        "evidence": "evidence",
        "实验证据": "evidence",
        "实验/证据": "evidence",
        "limitations": "limitations",
        "局限风险": "limitations",
        "局限": "limitations",
        "research_inspiration": "research_inspiration",
        "给你的启发": "research_inspiration",
    }
    for candidate in candidates:
        try:
            raw = json.loads(candidate)
        except Exception:
            continue
        if not isinstance(raw, dict):
            continue
        parsed = {field: "" for field in ["tldr", "why_it_matters", "method_core", "evidence", "limitations", "research_inspiration"]}
        for key, value in raw.items():
            field = key_map.get(str(key).strip())
            if field is not None and value is not None:
                parsed[field] = str(value).strip()
        if any(parsed.values()):
            return parsed
    return None


def _parse_research_brief(content: str) -> dict[str, str]:
    fields = ["why_it_matters", "method_core", "evidence", "limitations", "research_inspiration"]
    parsed = _parse_daily_analysis(content)
    return {field: parsed.get(field, "") for field in fields}


def _compact_summary(text: str, limit: int = 280) -> str:
    clean = re.sub(r"\s+", " ", text or "").strip()
    if len(clean) <= limit:
        return clean
    first_sentence = re.split(r"(?<=[.!?。！？])\s+", clean, maxsplit=1)[0]
    if 40 <= len(first_sentence) <= limit:
        return first_sentence
    return clean[: limit - 1].rstrip() + "…"


def _fallback_research_brief(summary: str, abstract: str) -> dict[str, str]:
    basis = _compact_summary(summary or abstract or "摘要信息不足，建议打开原文确认。")
    return {
        "why_it_matters": basis,
        "method_core": "模型没有稳定返回结构化方法字段；请优先核查模型/算法框架、输入数据、baseline 和消融实验。",
        "evidence": "模型没有稳定返回结构化实验证据；请打开原文确认数据集、benchmark、指标、代码和可复现资源。",
        "limitations": "模型没有稳定返回作者局限；先按数据覆盖、跨数据泛化、统计显著性和可复现性审查。",
        "research_inspiration": "如果这篇与你的研究画像相关，下一步交给一多科研生成 Paper Card 深读，再决定是否导入 Zotero。",
    }


def _parse_daily_analysis(content: str) -> dict[str, str]:
    fields = ["tldr", "why_it_matters", "method_core", "evidence", "limitations", "research_inspiration"]
    json_brief = _extract_json_object(content)
    if json_brief is not None:
        return {field: json_brief.get(field, "") for field in fields}

    brief = {field: "" for field in fields}
    current_field = None
    for raw_line in content.splitlines():
        line = raw_line.strip().lstrip("-*0123456789.、) ")
        if not line:
            continue
        matched = False
        for label, field in BRIEF_LABELS.items():
            if line.startswith(label):
                value = line[len(label):].lstrip("：: ").strip()
                brief[field] = value
                current_field = field
                matched = True
                break
        if not matched and current_field:
            brief[current_field] = (brief[current_field] + " " + line).strip()

    if not any(brief.values()):
        brief["tldr"] = content.strip()

    return brief


def _request_llm(openai_client: OpenAI, llm_params: dict, messages: list[dict]) -> str:
    api_mode = llm_params.get("api_mode", "chat_completion")
    generation_kwargs = dict(llm_params.get("generation_kwargs", {}))

    if api_mode == "chat_completion":
        response = openai_client.chat.completions.create(
            messages=messages,
            **generation_kwargs,
        )
        return response.choices[0].message.content

    if api_mode == "response":
        max_tokens = generation_kwargs.pop("max_tokens", None)
        if max_tokens is not None and "max_output_tokens" not in generation_kwargs:
            generation_kwargs["max_output_tokens"] = max_tokens
        generation_kwargs.setdefault("max_output_tokens", 1200)
        response = openai_client.responses.create(
            input=messages,
            **generation_kwargs,
        )
        return response.output_text

    raise ValueError(
        f"Unsupported llm.api_mode: {api_mode}. "
        "Expected 'chat_completion' or 'response'."
    )


@dataclass
class Paper:
    source: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    pdf_url: Optional[str] = None
    full_text: Optional[str] = None
    tldr: Optional[str] = None
    affiliations: Optional[list[str]] = None
    score: Optional[float] = None
    research_brief: Optional[dict[str, str]] = None

    def _generate_tldr_with_llm(self, openai_client:OpenAI,llm_params:dict) -> str:
        lang = llm_params.get('language', 'English')
        prompt = f"Given the following information of a paper, generate a one-sentence TLDR summary in {lang}:\n\n"
        if self.title:
            prompt += f"Title:\n {self.title}\n\n"

        if self.abstract:
            prompt += f"Abstract: {self.abstract}\n\n"

        if self.full_text:
            prompt += f"Preview of main content:\n {self.full_text}\n\n"

        if not self.full_text and not self.abstract:
            logger.warning(f"Neither full text nor abstract is provided for {self.url}")
            return "Failed to generate TLDR. Neither full text nor abstract is provided"
        
        # use gpt-4o tokenizer for estimation
        enc = tiktoken.encoding_for_model("gpt-4o")
        prompt_tokens = enc.encode(prompt)
        prompt_tokens = prompt_tokens[:4000]  # truncate to 4000 tokens
        prompt = enc.decode(prompt_tokens)
        
        tldr = _request_llm(
            openai_client,
            llm_params,
            [
                {
                    "role": "system",
                    "content": f"You are an assistant who perfectly summarizes scientific paper, and gives the core idea of the paper to the user. Your answer should be in {lang}.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return tldr
    
    def generate_tldr(self, openai_client:OpenAI,llm_params:dict) -> str:
        try:
            tldr = self._generate_tldr_with_llm(openai_client,llm_params)
            self.tldr = tldr
            return tldr
        except Exception as e:
            logger.warning(f"Failed to generate tldr of {self.url}: {e}")
            tldr = self.abstract
            self.tldr = tldr
            return tldr

    def _generate_research_brief_with_llm(self, openai_client: OpenAI, llm_params: dict) -> dict[str, str]:
        lang = llm_params.get("language", "Chinese")
        user_profile = llm_params.get(
            "research_profile",
            "single-cell foundation models, spatial transcriptomics, graph neural networks, multi-omics, and biomedical AI",
        )
        prompt = f"""
You are a warm but rigorous research advisor. Analyze this new preprint for a researcher whose interests are:
{user_profile}

Write in {lang}. Preserve technical terms, dataset names, model names, and metrics in English when appropriate.
Do not hype the paper. Judge what it actually contributes.

Return only valid JSON. Do not wrap it in Markdown. Use exactly these keys:
why_it_matters, method_core, evidence, limitations, research_inspiration

Each value must be one concise Chinese sentence. If the abstract lacks evidence, say what to verify in the paper instead of inventing results.

Paper:
Title: {self.title}
Source: {self.source}
Authors: {", ".join(self.authors[:8])}
Abstract: {self.abstract}
Preview: {(self.full_text or "")[:3000]}
"""
        enc = tiktoken.encoding_for_model("gpt-4o")
        prompt = enc.decode(enc.encode(prompt)[:5000])
        content = _request_llm(
            openai_client,
            llm_params,
            [
                {
                    "role": "system",
                    "content": "You produce source-bounded, practical research analysis and return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return _parse_research_brief(content)

    def generate_research_brief(self, openai_client: OpenAI, llm_params: dict) -> dict[str, str]:
        try:
            brief = self._generate_research_brief_with_llm(openai_client, llm_params)
            if not any(brief.values()):
                brief = _fallback_research_brief(self.tldr or self.abstract, self.abstract)
        except Exception as e:
            logger.warning(f"Failed to generate research brief of {self.url}: {e}")
            brief = _fallback_research_brief(self.tldr or self.abstract, self.abstract)
        self.research_brief = brief
        return brief

    def _generate_daily_analysis_with_llm(self, openai_client: OpenAI, llm_params: dict) -> dict[str, str]:
        lang = llm_params.get("language", "Chinese")
        user_profile = llm_params.get(
            "research_profile",
            "single-cell foundation models, spatial transcriptomics, graph neural networks, multi-omics, and biomedical AI",
        )
        prompt = f"""
You are a warm but rigorous research advisor. Analyze this new preprint for a researcher whose interests are:
{user_profile}

Write in {lang}. Preserve technical terms, dataset names, model names, and metrics in English when appropriate.
Do not hype the paper. Judge what it actually contributes.

Return only valid JSON. Do not wrap it in Markdown. Use exactly these keys:
tldr, why_it_matters, method_core, evidence, limitations, research_inspiration

Each value must be one concise Chinese sentence. If the abstract lacks evidence, say what to verify in the paper instead of inventing results.

Paper:
Title: {self.title}
Source: {self.source}
Authors: {", ".join(self.authors[:8])}
Abstract: {self.abstract[:2500]}
Preview: {(self.full_text or "")[:1200]}
"""
        enc = tiktoken.encoding_for_model("gpt-4o")
        prompt = enc.decode(enc.encode(prompt)[:2800])
        content = _request_llm(
            openai_client,
            llm_params,
            [
                {
                    "role": "system",
                    "content": "You produce source-bounded, practical research analysis and return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return _parse_daily_analysis(content)

    def generate_daily_analysis(self, openai_client: OpenAI, llm_params: dict) -> dict[str, str]:
        try:
            analysis = self._generate_daily_analysis_with_llm(openai_client, llm_params)
            self.tldr = analysis.get("tldr") or self.abstract
            self.research_brief = {
                "why_it_matters": analysis.get("why_it_matters", ""),
                "method_core": analysis.get("method_core", ""),
                "evidence": analysis.get("evidence", ""),
                "limitations": analysis.get("limitations", ""),
                "research_inspiration": analysis.get("research_inspiration", ""),
            }
            if not any(self.research_brief.values()):
                self.tldr = _compact_summary(self.tldr or self.abstract)
                self.research_brief = _fallback_research_brief(self.tldr, self.abstract)
                analysis = {"tldr": self.tldr, **self.research_brief}
            return analysis
        except Exception as e:
            logger.warning(f"Failed to generate daily analysis of {self.url}: {e}")
            self.tldr = self.abstract
            self.research_brief = _fallback_research_brief(self.abstract, self.abstract)
            return {"tldr": self.tldr, **self.research_brief}

    def _generate_affiliations_with_llm(self, openai_client:OpenAI,llm_params:dict) -> Optional[list[str]]:
        if self.full_text is not None:
            prompt = f"Given the beginning of a paper, extract the affiliations of the authors in a python list format, which is sorted by the author order. If there is no affiliation found, return an empty list '[]':\n\n{self.full_text}"
            # use gpt-4o tokenizer for estimation
            enc = tiktoken.encoding_for_model("gpt-4o")
            prompt_tokens = enc.encode(prompt)
            prompt_tokens = prompt_tokens[:2000]  # truncate to 2000 tokens
            prompt = enc.decode(prompt_tokens)
            affiliations = _request_llm(
                openai_client,
                llm_params,
                [
                    {
                        "role": "system",
                        "content": "You are an assistant who perfectly extracts affiliations of authors from a paper. You should return a python list of affiliations sorted by the author order, like [\"TsingHua University\",\"Peking University\"]. If an affiliation is consisted of multi-level affiliations, like 'Department of Computer Science, TsingHua University', you should return the top-level affiliation 'TsingHua University' only. Do not contain duplicated affiliations. If there is no affiliation found, you should return an empty list [ ]. You should only return the final list of affiliations, and do not return any intermediate results.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            affiliations = re.search(r'\[.*?\]', affiliations, flags=re.DOTALL).group(0)
            affiliations = json.loads(affiliations)
            affiliations = list(set(affiliations))
            affiliations = [str(a) for a in affiliations]

            return affiliations
    
    def generate_affiliations(self, openai_client:OpenAI,llm_params:dict) -> Optional[list[str]]:
        try:
            affiliations = self._generate_affiliations_with_llm(openai_client,llm_params)
            self.affiliations = affiliations
            return affiliations
        except Exception as e:
            logger.warning(f"Failed to generate affiliations of {self.url}: {e}")
            self.affiliations = None
            return None
@dataclass
class CorpusPaper:
    title: str
    abstract: str
    added_date: datetime
    paths: list[str]
