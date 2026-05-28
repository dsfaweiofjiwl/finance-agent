#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Client - Wrapper for LLM API calls with prompt caching support
"""

import json
import hashlib
import os
import time
from typing import List, Dict, Any, Optional
import requests
from dataclasses import dataclass


@dataclass
class CachedPrompt:
    """Cached prompt information"""
    cache_key: str
    content: str
    tokens: int
    created_at: float


class LLMClient:
    """
    Generic LLM client supporting OpenAI-compatible APIs
    Built-in prompt caching optimization to reduce token costs
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        context_window: int = 256000,
        max_tokens: int = 32000,
        enable_prompt_caching: bool = True,
        min_content_tokens: int = 1024,
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.context_window = context_window
        self.max_tokens = max_tokens
        self.enable_prompt_caching = enable_prompt_caching
        self.min_content_tokens = min_content_tokens

        # 缓存目录
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompt_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, content: str) -> str:
        """生成缓存key"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def _estimate_tokens(self, text: str) -> int:
        """粗略估算token数 ~ 1 token ≈ 4字符"""
        return len(text) // 4

    def build_messages(
        self,
        system_prompts: List[str],
        user_query: str,
    ) -> List[Dict[str, Any]]:
        """
        构建消息列表，合并多个system prompt
        支持prompt缓存（OpenAI格式）
        """
        messages = []

        # 合并所有system prompt
        full_system = "\n\n".join(p.strip() for p in system_prompts if p.strip())
        messages.append({"role": "system", "content": full_system})

        # 用户查询
        messages.append({"role": "user", "content": user_query})

        return messages

    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.1,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """调用LLM chat API"""

        # 确保路径正确拼接
        if self.base_url.endswith('/'):
            url = f"{self.base_url}chat/completions"
        else:
            url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_tokens,
            "stream": stream,
        }

        # 如果API支持prompt缓存，这里可以扩展
        # 目前火山方舟已经兼容openai格式，缓存由provider处理

        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        session.trust_env = False
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        response = session.post(url, headers=headers, json=data, timeout=600, proxies=None)
        response.raise_for_status()
        return response.json()

    def complete(
        self,
        system_prompts: List[str],
        user_query: str,
        temperature: float = 0.1,
    ) -> str:
        """完整的补全：合并system prompts + user query，返回文本"""

        messages = self.build_messages(system_prompts, user_query)
        result = self.chat(messages, temperature=temperature)

        if "choices" not in result or not result["choices"]:
            raise ValueError(f"Unexpected response: {result}")

        return result["choices"][0]["message"]["content"].strip()

    def get_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """获取token使用情况"""
        usage = response.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }
