#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recommendation history tracker with cooldown for dropped stocks."""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class RecommendationHistory:
    """Tracks stock analysis history and manages cooldown for dropped stocks."""

    DEFAULT_DATA = {
        "cooldown_days": 2,
        "runs": [],
        "stock_last_analyzed": {},
        "dropped_stocks": {},
    }

    def __init__(self, history_path: str = "data/recommendation_history.json"):
        self.history_path = history_path
        self.data = self.load()

    def load(self) -> dict:
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key in self.DEFAULT_DATA:
                if key not in data:
                    data[key] = self.DEFAULT_DATA[key]
            return data
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return json.loads(json.dumps(self.DEFAULT_DATA))

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.history_path) or ".", exist_ok=True)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_last_run_symbols(self) -> List[str]:
        runs = self.data.get("runs", [])
        if not runs:
            return []
        return runs[-1].get("stocks_analyzed", [])

    def get_cooldown_symbols(self, current_date: str) -> List[str]:
        dropped = self.data.get("dropped_stocks", {})
        if not dropped:
            return []
        cooldown_days = self.data.get("cooldown_days", 2)
        try:
            cur = datetime.strptime(current_date, "%Y-%m-%d")
        except ValueError:
            return []
        result = []
        for symbol, drop_date_str in dropped.items():
            try:
                drop_date = datetime.strptime(drop_date_str, "%Y-%m-%d")
                if (cur - drop_date).days < cooldown_days:
                    result.append(symbol)
            except ValueError:
                continue
        return result

    def get_recent_symbols(self, n_days: int = 14) -> List[str]:
        runs = self.data.get("runs", [])
        if not runs:
            return []
        try:
            latest_date = datetime.strptime(runs[-1]["date"], "%Y-%m-%d")
        except (KeyError, ValueError, IndexError):
            return []
        cutoff = latest_date - timedelta(days=n_days)
        symbols = set()
        for run in runs:
            try:
                run_date = datetime.strptime(run["date"], "%Y-%m-%d")
                if run_date >= cutoff:
                    for s in run.get("stocks_analyzed", []):
                        symbols.add(s)
            except (KeyError, ValueError):
                continue
        return list(symbols)

    def record_run(self, date: str, stocks: List[dict], recommendations: dict) -> None:
        new_symbols = [s["symbol"] for s in stocks]
        previous_symbols = self.get_last_run_symbols()

        self.data["runs"].append({
            "date": date,
            "stocks_analyzed": new_symbols,
            "recommendations": recommendations,
        })

        for symbol in new_symbols:
            self.data["stock_last_analyzed"][symbol] = date

        if previous_symbols:
            dropped_set = set(previous_symbols) - set(new_symbols)
            for symbol in dropped_set:
                self.data["dropped_stocks"][symbol] = date

        for symbol in list(self.data.get("dropped_stocks", {}).keys()):
            if symbol in new_symbols:
                del self.data["dropped_stocks"][symbol]

        self.cleanup_old_runs()
        self.save()

    def cleanup_old_runs(self, keep_days: int = 30) -> None:
        try:
            latest_date = datetime.strptime(self.data["runs"][-1]["date"], "%Y-%m-%d")
        except (IndexError, KeyError, ValueError):
            return
        cutoff = latest_date - timedelta(days=keep_days)
        self.data["runs"] = [
            r for r in self.data["runs"]
            if self._parse_date_safe(r.get("date", "")) >= cutoff
        ]
        dropped = self.data.get("dropped_stocks", {})
        self.data["dropped_stocks"] = {
            k: v for k, v in dropped.items()
            if self._parse_date_safe(v) >= cutoff
        }

    @staticmethod
    def _parse_date_safe(date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.min
