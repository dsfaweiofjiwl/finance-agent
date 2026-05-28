#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stock selector with cooldown, risk filtering, and sector balance enforcement."""

import json
import re
from typing import List, Dict, Optional


class StockSelector:
    """Programmatic stock candidate filtering — enforces constraints the LLM cannot reliably enforce."""

    SECTOR_MAP = {
        "Technology": ["Technology", "Tech", "Software", "Semiconductor", "Hardware", "Information Technology"],
        "Financial": ["Financial", "Banking", "Insurance", "Fintech", "Financials"],
        "Consumer": ["Consumer Staples", "Consumer Defensive", "Retail", "Consumer Cyclical", "Consumer Discretionary", "Consumer"],
        "Healthcare": ["Healthcare", "Pharma", "Biotech", "Medical", "Health Care"],
        "Energy": ["Energy", "Oil & Gas", "Utilities", "Utility"],
        "Industrial": ["Industrial", "Manufacturing", "Aerospace", "Transportation", "Industrials"],
        "Value": ["Value", "Conglomerate"],
    }

    FALLBACK_STOCKS = [
        {"name": "NVIDIA", "symbol": "NVDA"},
        {"name": "Apple", "symbol": "AAPL"},
        {"name": "Microsoft", "symbol": "MSFT"},
        {"name": "Advanced Micro Devices", "symbol": "AMD"},
        {"name": "JPMorgan Chase", "symbol": "JPM"},
        {"name": "Bank of America", "symbol": "BAC"},
        {"name": "Costco Wholesale", "symbol": "COST"},
        {"name": "Coca-Cola", "symbol": "KO"},
        {"name": "Visa", "symbol": "V"},
        {"name": "Berkshire Hathaway B", "symbol": "BRK.B"},
    ]

    def normalize_sector(self, raw_sector: str) -> str:
        raw_lower = raw_sector.lower()
        for canonical, aliases in self.SECTOR_MAP.items():
            for alias in aliases:
                if alias.lower() == raw_lower:
                    return canonical
        return "Other"

    def filter_cooldown(self, candidates: List[dict], cooldown_symbols: List[str]) -> List[dict]:
        cooldown_set = set(cooldown_symbols)
        return [c for c in candidates if c.get("symbol", "") not in cooldown_set]

    def filter_risk(self, candidates: List[dict]) -> List[dict]:
        result = []
        for c in candidates:
            pct_5d = self._parse_pct(c.get("pct_change_5d", "0%"))
            pct_20d = self._parse_pct(c.get("pct_change_20d", "0%"))
            momentum = c.get("momentum", "").lower()

            # 检查数据可信度：低置信数据不用于风险过滤
            data_confidence = c.get("data_confidence")
            if isinstance(data_confidence, dict):
                conf_level = data_confidence.get("level", "high")
            else:
                conf_level = "high"

            if conf_level == "low":
                result.append(c)
                continue

            if pct_5d < -8:
                continue
            if pct_20d < -15:
                continue
            if momentum == "bearish" and pct_5d < -5:
                continue
            result.append(c)
        return result

    def ensure_min_changes(
        self,
        candidates: List[dict],
        last_run_symbols: List[str],
        target_count: int = 10,
        min_changes: int = 3,
    ) -> List[dict]:
        if not last_run_symbols:
            return candidates[:target_count]

        last_set = set(last_run_symbols)
        new_candidates = [c for c in candidates if c.get("symbol", "") not in last_set]
        carry_over = [c for c in candidates if c.get("symbol", "") in last_set]

        new_count = len(new_candidates)
        if new_count >= min_changes:
            selected = new_candidates[:]
            remaining = target_count - len(selected)
            if remaining > 0:
                selected.extend(carry_over[:remaining])
            return selected[:target_count]
        else:
            print(f"   WARNING: Only {new_count} new candidates (need {min_changes}), including all new ones")
            selected = new_candidates[:]
            remaining = target_count - len(selected)
            if remaining > 0:
                selected.extend(carry_over[:remaining])
            return selected[:target_count]

    def _cap_tech_stocks(self, candidates: List[dict], max_tech: int = 7) -> List[dict]:
        """Ensure no more than max_tech stocks are Technology sector."""
        for c in candidates:
            c["sector_normalized"] = self.normalize_sector(c.get("sector", ""))

        tech_count = sum(1 for c in candidates if c["sector_normalized"] == "Technology")
        if tech_count <= max_tech:
            for c in candidates:
                c.pop("sector_normalized", None)
            return candidates

        tech_stocks = [c for c in candidates if c["sector_normalized"] == "Technology"]
        other_stocks = [c for c in candidates if c["sector_normalized"] != "Technology"]

        tech_stocks.sort(key=lambda c: self._parse_pct(c.get("pct_change_5d", "0%")), reverse=True)
        kept_tech = tech_stocks[:max_tech]

        result = kept_tech + other_stocks
        for c in result:
            c.pop("sector_normalized", None)
        return result

    def select(
        self,
        candidates: List[dict],
        cooldown_symbols: List[str],
        last_run_symbols: List[str],
        target_count: int = 10,
    ) -> List[dict]:
        filtered = self.filter_cooldown(candidates, cooldown_symbols)
        filtered = self.filter_risk(filtered)
        filtered = self.ensure_min_changes(filtered, last_run_symbols, target_count, min_changes=3)
        if len(filtered) < 5:
            filtered = self._supplement_with_fallback(filtered, cooldown_symbols, target_count)
        return filtered

    def _supplement_with_fallback(
        self, selected: List[dict], cooldown_symbols: List[str], target_count: int
    ) -> List[dict]:
        cooldown_set = set(cooldown_symbols)
        selected_symbols = {s["symbol"] for s in selected}
        for fb in self.FALLBACK_STOCKS:
            if len(selected) >= target_count:
                break
            sym = fb["symbol"]
            if sym not in selected_symbols and sym not in cooldown_set:
                selected.append({
                    "symbol": sym,
                    "name": fb["name"],
                    "sector": "Unknown",
                    "momentum": "Neutral",
                    "pct_change_5d": "0%",
                    "pct_change_20d": "0%",
                })
                selected_symbols.add(sym)
        return selected

    def parse_llm_json(self, response_text: str) -> List[dict]:
        text = response_text.strip()
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

        fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fence_match:
            try:
                result = json.loads(fence_match.group(1).strip())
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                pass

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end > start:
            try:
                result = json.loads(text[start:end + 1])
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                pass

        print("   WARNING: Failed to parse JSON from LLM stock screening response")
        return []

    @staticmethod
    def _parse_pct(s: str) -> float:
        try:
            return float(s.strip().replace("%", "").replace("+", ""))
        except (ValueError, AttributeError):
            return 0.0
