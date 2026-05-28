#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Search Tool - 搜索最新财经信息
支持多种免费/付费搜索后端：

1. **SerperDev** (推荐免费): 1000次/月免费配额，足够个人使用
   https://serper.dev/ - 获取 API KEY

2. **Brave Search** (免费): 20次/分钟，无需API KEY？不对，需要key，但免费额度够
   https://brave.com/search/api/

3. **Bing Search** (免费): 微软给每月1000次免费

4. **Google Custom Search** (需要API KEY)

设置环境变量选择后端：
- SEARCH_BACKEND=serper  (默认推荐)
- SEARCH_BACKEND=brave
- SEARCH_BACKEND=bing
- SEARCH_BACKEND=google
"""

import os
import requests
from typing import List, Dict, Any, Optional


def format_results(items: List[Dict[str, Any]], query: str) -> str:
    """格式化搜索结果"""
    if not items:
        return f"No results found for query: {query}"

    results = []
    results.append(f"Search results: {query}\n")

    for i, item in enumerate(items, 1):
        title = item.get("title", "No title")
        link = item.get("link", item.get("url", "No link"))
        snippet = item.get("snippet", item.get("description", "No snippet"))
        results.append(f"{i}. **{title}**\n   URL: {link}\n   {snippet}\n")

    return "\n".join(results)


def search_serper(query: str, num_results: int = 10) -> str:
    """SerperDev 搜索 - 免费1000次/月"""
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return "[Error] SERPER_API_KEY environment variable not set. Please go to https://serper.dev/ to register for a free key."

    url = "https://google.serper.dev/search"
    payload = {
        "q": query,
        "num": min(num_results, 10),
    }
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 提取organic结果
        organic = data.get("organic", [])
        items = []
        for result in organic:
            items.append({
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
            })

        return format_results(items[:num_results], query)

    except Exception as e:
        return f"SerperDev search error: {str(e)}"


def search_brave(query: str, num_results: int = 10) -> str:
    """Brave Search - 免费API"""
    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        return "[Error] BRAVE_API_KEY environment variable not set. Please go to https://brave.com/search/api/ to apply."

    url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        "q": query,
        "count": min(num_results, 20),
    }
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("web", {}).get("results", [])
        items = []
        for result in results:
            items.append({
                "title": result.get("title"),
                "link": result.get("url"),
                "snippet": result.get("description"),
            })

        return format_results(items[:num_results], query)

    except Exception as e:
        return f"Brave search error: {str(e)}"


def search_bing(query: str, num_results: int = 10) -> str:
    """Bing Search - 微软每月1000次免费"""
    api_key = os.environ.get("BING_API_KEY", "")
    if not api_key:
        return "[Error] BING_API_KEY environment variable not set."

    url = "https://api.bing.microsoft.com/v7.0/search"
    params = {
        "q": query,
        "count": min(num_results, 10),
        "responseFilter": "Webpages",
    }
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        pages = data.get("webPages", {}).get("value", [])
        items = []
        for page in pages:
            items.append({
                "title": page.get("name"),
                "link": page.get("url"),
                "snippet": page.get("snippet"),
            })

        return format_results(items[:num_results], query)

    except Exception as e:
        return f"Bing search error: {str(e)}"


def search_google(query: str, num_results: int = 10) -> str:
    """Google Custom Search"""
    api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        return "[Error] GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables not set."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": min(num_results, 10),
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        results = []
        for item in items:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            })

        return format_results(results[:num_results], query)

    except Exception as e:
        return f"Google search error: {str(e)}"


def search_exa(query: str, num_results: int = 10) -> str:
    """Exa AI Search - 专门给AI设计的搜索，你OpenClaw用的就是这个"""
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return "[Error] EXA_API_KEY environment variable not set. Exa is the search service currently used by your OpenClaw."

    url = "https://api.exa.ai/search"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "numResults": min(num_results, 10),
        "contents": True,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        items = []
        for result in results:
            items.append({
                "title": result.get("title"),
                "link": result.get("url"),
                "snippet": result.get("summary") or result.get("text", "")[:200],
            })

        return format_results(items[:num_results], query)

    except Exception as e:
        return f"Exa search error: {str(e)}"


def web_search(query: str, num_results: int = 10) -> str:
    """
    Search the web for the latest information.

    Args:
        query: Search keywords, e.g. 'Fed latest rate decision 2026', 'NVDA latest closing price'
        num_results: Number of results to return, default 10

    Returns:
        Formatted search results
    """
    backend = os.environ.get("SEARCH_BACKEND", "serper").lower()

    if backend == "serper":
        return search_serper(query, num_results)
    elif backend == "brave":
        return search_brave(query, num_results)
    elif backend == "bing":
        return search_bing(query, num_results)
    elif backend == "google":
        return search_google(query, num_results)
    elif backend == "exa":
        return search_exa(query, num_results)
    else:
        return f"[Error] Unknown search backend: {backend}. Supported: serper, brave, bing, google, exa"


# Tool definition (for registration)
TOOL_DEFINITION = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search keywords, e.g. 'Fed latest rate decision 2026', 'NVDA latest closing price'",
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return, default 10",
            "default": 10,
        },
    },
    "required": ["query"],
}
