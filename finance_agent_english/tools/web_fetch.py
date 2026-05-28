#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Fetch Tool - Fetch webpage content and extract text information
Used to obtain complete data from authoritative sources
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional


def web_fetch(url: str, max_length: int = 16000) -> str:
    """
    Fetch webpage content and extract text.

    Args:
        url: The webpage URL to fetch
        max_length: Maximum text length to return, default 16000 characters

    Returns:
        Extracted text content
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # Correct encoding detection

        # 使用BeautifulSoup提取文本
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除script、style等标签
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # 获取文本
        text = soup.get_text(separator='\n', strip=True)

        # 清理空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        # 截断
        if len(text) > max_length:
            text = text[:max_length] + f"\n\n[Truncated: Content exceeds {max_length} characters, has been truncated]"

        return f"=== Web content: {url} ===\n\n{text}"

    except Exception as e:
        return f"Failed to fetch webpage: {str(e)}"


# 工具定义（供注册使用）
TOOL_DEFINITION = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "Webpage URL to fetch content from, e.g. 'https://www.federalreserve.gov/newsevents/pressreleases/monetary20260318a.htm'",
        },
        "max_length": {
            "type": "integer",
            "description": "Maximum text length to return, default 16000",
            "default": 16000,
        },
    },
    "required": ["url"],
}
