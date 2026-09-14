from __future__ import annotations

from collections import Counter
from html import escape
import math
import random
import re

from omegaconf import DictConfig
import requests

from .protocol import Paper


WARM_FALLBACK_QUOTES = [
    "真正有用的积累，不是每天都很猛，而是每天都没有完全断线。",
    "今天不用一下子读懂所有东西，先把一个关键问题看清楚就很好。",
    "科研里最可靠的进步，常常来自一次更具体的问题和一次更诚实的复盘。",
    "把复杂问题拆小一点，答案就会慢慢露出形状。",
]

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "using", "based", "towards",
    "into", "via", "are", "our", "new", "study", "model", "models", "data", "analysis",
    "paper", "method", "learning", "deep", "single",
}

WEATHER_CODES = {
    0: "晴",
    1: "大部晴朗",
    2: "局部多云",
    3: "阴",
    45: "有雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "毛毛雨",
    55: "较强毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "阵雨",
    81: "较强阵雨",
    82: "强阵雨",
    95: "雷雨",
}

KNOWN_WEATHER_LOCATIONS = {
    "harbin": ("哈尔滨", 45.75, 126.65),
    "哈尔滨": ("哈尔滨", 45.75, 126.65),
}


framework = """
<!DOCTYPE HTML>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: Arial, "Microsoft YaHei", sans-serif; line-height: 1.62; color: #263238; }
    .radar-wrap { max-width: 760px; margin: 0 auto; }
    .hero { border: 1px solid #d7e3e5; border-radius: 8px; padding: 18px; background: #f6fbfb; }
    .section { margin-top: 18px; }
    .section h2 { font-size: 18px; margin: 0 0 8px; color: #102a43; }
    .paper { border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin: 12px 0; background: #ffffff; }
    .paper-title { font-size: 17px; font-weight: 700; color: #102a43; }
    .meta { font-size: 13px; color: #607d8b; margin: 6px 0; }
    .label { font-weight: 700; color: #29434e; }
    .button { display: inline-block; text-decoration: none; font-size: 13px; font-weight: 700; color: #fff; background: #2f6f73; padding: 7px 12px; border-radius: 4px; }
    ul { margin-top: 6px; padding-left: 20px; }
  </style>
</head>
<body>
<div class="radar-wrap">
__CONTENT__
</div>
</body>
</html>
"""


def _safe(value: object) -> str:
    return escape("" if value is None else str(value))


def _md_safe(value: object) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _author_text(p: Paper) -> str:
    author_list = [a for a in p.authors]
    if len(author_list) <= 5:
        return ", ".join(author_list)
    return ", ".join(author_list[:3] + ["..."] + author_list[-2:])


def _affiliation_text(p: Paper) -> str:
    if p.affiliations is None:
        return "Unknown Affiliation"
    affiliations = p.affiliations[:5]
    text = ", ".join(affiliations)
    if len(p.affiliations) > 5:
        text += ", ..."
    return text


def _format_open_meteo_weather(city_name: str, latitude: float, longitude: float) -> str:
    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
        timeout=20,
    )
    weather_response.raise_for_status()
    current = weather_response.json()["current"]
    condition = WEATHER_CODES.get(int(current.get("weather_code", -1)), "天气状态未知")
    temperature = round(float(current["temperature_2m"]))
    feels_like = round(float(current["apparent_temperature"]))
    humidity = round(float(current["relative_humidity_2m"]))
    wind = round(float(current["wind_speed_10m"]))
    return f"{city_name}: {condition}, {temperature}°C, 体感 {feels_like}°C, 湿度 {humidity}%, 风速 {wind} km/h"


def _fetch_open_meteo_weather(city: str) -> str:
    known = KNOWN_WEATHER_LOCATIONS.get(str(city).strip().lower()) or KNOWN_WEATHER_LOCATIONS.get(str(city).strip())
    if known is not None:
        city_name, latitude, longitude = known
        return _format_open_meteo_weather(city_name, latitude, longitude)

    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "zh", "format": "json"},
        timeout=20,
    )
    geo_response.raise_for_status()
    location = geo_response.json()["results"][0]
    return _format_open_meteo_weather(
        location.get("name", city),
        location["latitude"],
        location["longitude"],
    )


def _fetch_weather(config: DictConfig | None) -> str:
    radar = (config or {}).get("daily_radar", {}) if config is not None else {}
    city = radar.get("weather_city", "Harbin")
    try:
        response = requests.get(
            f"https://wttr.in/{city}",
            params={"format": "%l: %C, %t, feels like %f, humidity %h, wind %w", "lang": "zh-cn"},
            timeout=12,
        )
        response.raise_for_status()
        text = response.text.strip()
        return text if text else f"{city} 天气暂时没有返回"
    except Exception:
        pass

    try:
        return _fetch_open_meteo_weather(city)
    except Exception:
        return f"{city} 天气暂时获取失败，出门前看一眼实时天气。"


def _fetch_quote(config: DictConfig | None) -> str:
    radar = (config or {}).get("daily_radar", {}) if config is not None else {}
    if not bool(radar.get("quote_enabled", True)):
        return random.choice(WARM_FALLBACK_QUOTES)
    try:
        response = requests.get(
            "https://v1.hitokoto.cn/",
            params={"c": "d", "encode": "json"},
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        quote = str(data.get("hitokoto", "")).strip()
        if quote:
            return quote
    except Exception:
        pass
    return random.choice(WARM_FALLBACK_QUOTES)


def _keyword_trends(papers: list[Paper], limit: int = 3) -> list[str]:
    text = " ".join([f"{p.title} {p.abstract}" for p in papers])
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", text)]
    counts = Counter(w for w in words if w not in STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def _trend_sentences(papers: list[Paper]) -> list[str]:
    keywords = _keyword_trends(papers)
    if not keywords:
        return ["今天候选论文较少，先把重点论文读透，比追数量更重要。"]
    sentences = []
    if len(keywords) >= 1:
        sentences.append(f"{keywords[0]} 是今天最明显的信号，建议留意它和你现有单细胞/空间组学问题的连接。")
    if len(keywords) >= 2:
        sentences.append(f"{keywords[1]} 相关论文值得横向比较，重点看数据集、baseline 和跨数据泛化是否扎实。")
    if len(keywords) >= 3:
        sentences.append(f"{keywords[2]} 方向可能有噪音，先看实验设计和可复现资源，再决定是否深读。")
    return sentences


def get_stars(score: float):
    full_star = '<span class="full-star">⭐</span>'
    half_star = '<span class="half-star">⭐</span>'
    low = 6
    high = 8
    if score <= low:
        return ''
    if score >= high:
        return full_star * 5
    interval = (high - low) / 10
    star_num = math.ceil((score - low) / interval)
    full_star_num = int(star_num / 2)
    half_star_num = star_num - full_star_num * 2
    return '<div class="star-wrapper">' + full_star * full_star_num + half_star * half_star_num + '</div>'


def get_empty_html(config: DictConfig | None = None):
    weather = _safe(_fetch_weather(config))
    quote = _safe(_fetch_quote(config))
    content = f"""
    <div class="hero">
      <strong>早上好，一多。</strong><br>
      {weather}<br><br>
      今天这句话送你：{quote}<br><br>
      今天没有筛到足够相关的新论文。也挺好，留一点空白，把昨天没读完的东西收束一下。
    </div>
    """
    return content


def get_empty_markdown(config: DictConfig | None = None) -> str:
    weather = _md_safe(_fetch_weather(config))
    quote = _md_safe(_fetch_quote(config))
    return "\n\n".join(
        [
            "**早上好，一多。**",
            weather,
            f"今天这句话送你：\n> {quote}",
            "今天没有筛到足够相关的新论文。也挺好，留一点空白，把昨天没读完的东西收束一下。",
        ]
    )


def get_block_html(title: str, authors: str, rate: str, tldr: str, pdf_url: str, affiliations: str = None, brief: dict[str, str] | None = None):
    brief = brief or {}
    return f"""
    <div class="paper">
      <div class="paper-title">{_safe(title)}</div>
      <div class="meta">{_safe(authors)}<br><i>{_safe(affiliations)}</i></div>
      <div><span class="label">相关度：</span>{_safe(rate)}</div>
      <div><span class="label">一句话：</span>{_safe(tldr)}</div>
      <div><span class="label">为什么重要：</span>{_safe(brief.get("why_it_matters", ""))}</div>
      <div><span class="label">方法核心：</span>{_safe(brief.get("method_core", ""))}</div>
      <div><span class="label">实验/证据：</span>{_safe(brief.get("evidence", ""))}</div>
      <div><span class="label">局限：</span>{_safe(brief.get("limitations", ""))}</div>
      <div><span class="label">给你的启发：</span>{_safe(brief.get("research_inspiration", ""))}</div>
      <p><a class="button" href="{_safe(pdf_url)}">PDF / 原文</a></p>
    </div>
    """


def get_block_markdown(index: int, title: str, authors: str, rate: str, tldr: str, pdf_url: str, affiliations: str = None, brief: dict[str, str] | None = None):
    brief = brief or {}
    lines = [
        f"### {index}. {_md_safe(title)}",
        f"- 相关度：{_md_safe(rate)}",
        f"- 作者：{_md_safe(authors)}",
        f"- 机构：{_md_safe(affiliations)}",
        f"- 一句话：{_md_safe(tldr)}",
        f"- 为什么重要：{_md_safe(brief.get('why_it_matters', ''))}",
        f"- 方法核心：{_md_safe(brief.get('method_core', ''))}",
        f"- 实验/证据：{_md_safe(brief.get('evidence', ''))}",
        f"- 局限：{_md_safe(brief.get('limitations', ''))}",
        f"- 给你的启发：{_md_safe(brief.get('research_inspiration', ''))}",
    ]
    if pdf_url:
        lines.append(f"- [PDF / 原文]({pdf_url})")
    return "\n".join(lines)


def render_email(papers: list[Paper], config: DictConfig | None = None) -> str:
    if len(papers) == 0:
        return framework.replace("__CONTENT__", get_empty_html(config))

    weather = _safe(_fetch_weather(config))
    quote = _safe(_fetch_quote(config))
    trend_items = "".join(f"<li>{_safe(item)}</li>" for item in _trend_sentences(papers))
    top_paper = papers[0]
    deep_reason = (
        top_paper.research_brief or {}
    ).get("research_inspiration") or top_paper.tldr or "它和你的研究画像最接近，适合作为今天的深读入口。"

    parts = [
        f"""
        <div class="hero">
          <strong>早上好，一多。</strong><br>
          {weather}<br><br>
          今天这句话送你：{quote}<br><br>
          我今天替你扫了一轮新论文，先把最值得看的内容放在前面。今天筛出 <strong>{len(papers)}</strong> 篇重点论文，建议先看趋势，再挑一篇深读。
        </div>
        <div class="section">
          <h2>今日趋势</h2>
          <ul>{trend_items}</ul>
        </div>
        <div class="section">
          <h2>重点论文</h2>
        </div>
        """
    ]

    for p in papers:
        rate = round(p.score, 1) if p.score is not None else "Unknown"
        parts.append(
            get_block_html(
                p.title,
                _author_text(p),
                str(rate),
                p.tldr or p.abstract,
                p.pdf_url or p.url,
                _affiliation_text(p),
                p.research_brief,
            )
        )

    parts.append(
        f"""
        <div class="section">
          <h2>今日深读建议</h2>
          <p>优先深读：<strong>{_safe(top_paper.title)}</strong></p>
          <p>{_safe(deep_reason)}</p>
          <p>下一步可以让“一多科研”对这篇走 Paper Card：下载 PDF、生成 evidence-grounded 分析卡，再决定是否导入 Zotero。</p>
        </div>
        """
    )
    return framework.replace("__CONTENT__", "\n".join(parts))


def render_markdown(papers: list[Paper], config: DictConfig | None = None) -> str:
    if len(papers) == 0:
        return get_empty_markdown(config)

    weather = _md_safe(_fetch_weather(config))
    quote = _md_safe(_fetch_quote(config))
    trends = "\n".join(f"- {_md_safe(item)}" for item in _trend_sentences(papers))
    top_paper = papers[0]
    deep_reason = (
        top_paper.research_brief or {}
    ).get("research_inspiration") or top_paper.tldr or "它和你的研究画像最接近，适合作为今天的深读入口。"

    parts = [
        "**早上好，一多。**",
        weather,
        f"今天这句话送你：\n> {quote}",
        f"我今天替你扫了一轮新论文，先把最值得看的内容放在前面。今天筛出 **{len(papers)}** 篇重点论文，建议先看趋势，再挑一篇深读。",
        f"## 今日趋势\n{trends}",
        "## 重点论文",
    ]

    for index, p in enumerate(papers, start=1):
        rate = round(p.score, 1) if p.score is not None else "Unknown"
        parts.append(
            get_block_markdown(
                index,
                p.title,
                _author_text(p),
                str(rate),
                p.tldr or p.abstract,
                p.pdf_url or p.url,
                _affiliation_text(p),
                p.research_brief,
            )
        )

    parts.append(
        "\n".join(
            [
                "## 今日深读建议",
                f"优先深读：**{_md_safe(top_paper.title)}**",
                _md_safe(deep_reason),
                "下一步可以让“一多科研”对这篇走 Paper Card：下载 PDF、生成 evidence-grounded 分析卡，再决定是否导入 Zotero。",
            ]
        )
    )
    return "\n\n".join(parts)
