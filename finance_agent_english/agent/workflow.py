#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow - 分步执行架构
流程：
1. 阶段一：收集宏观数据（所有必填数据填完才进下一步）
2. 阶段二：基于完整宏观数据做宏观分析
2.5. 阶段二.5：动态选股 + 风险筛选
3. 阶段三：逐个收集股票数据 + 逐个分析
4. 阶段四：整合所有内容生成最终报告
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.llm_client import LLMClient
from agent.tool_registry import ToolRegistry
from agent.history_tracker import RecommendationHistory
from agent.stock_selector import StockSelector

from tools.web_search import web_search, TOOL_DEFINITION as SEARCH_TOOL
from tools.web_fetch import web_fetch, TOOL_DEFINITION as FETCH_TOOL


class FinanceAnalysisWorkflow:
    """US Stock Analysis Workflow - Phased Execution Version"""

    # Fallback stock list: Tech×4 / Financial×2 / Consumer×3 / Value×1
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

    def __init__(self, llm_client: LLMClient, config_dir: str = "config", prompt_dir: str = "prompt"):
        self.llm = llm_client
        self.config_dir = config_dir
        self.prompt_dir = prompt_dir

        # 初始化工具注册器
        self.tools = ToolRegistry()
        self._register_tools()

        # 初始化历史追踪和选股器
        self.history = RecommendationHistory()
        self.stock_selector = StockSelector()
        self.current_stock_list: List[Dict[str, str]] = []

    def _register_tools(self) -> None:
        """注册所有可用工具"""
        self.tools.register(
            name="web_search",
            description="Search the web for the latest financial information, data, and news. Used to find macroeconomic data, latest stock prices, and news events.",
            parameters=SEARCH_TOOL,
            func=web_search,
        )
        self.tools.register(
            name="web_fetch",
            description="Get the full text content of a specified webpage, extracting detailed data from authoritative sources.",
            parameters=FETCH_TOOL,
            func=web_fetch,
        )

    def _format_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """格式化工具调用结果为文本"""
        name = tool_call.get("function", {}).get("name")
        args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
        result = self.tools.execute(name, **args)
        return f"\nTool call result [{name}]:\n{result}\n"

    def _read_prompt_template(self, filename: str) -> str:
        """读取prompt模板"""
        path = os.path.join(self.prompt_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """简单模板渲染"""
        result = template
        for key, value in context.items():
            result = result.replace("{{" + key + "}}", str(value))
        return result

    CHECKPOINT_DIR = "data/checkpoints"

    def _save_checkpoint(self, name: str, data: Any) -> None:
        """保存阶段性 checkpoint"""
        os.makedirs(self.CHECKPOINT_DIR, exist_ok=True)
        path = os.path.join(self.CHECKPOINT_DIR, f"{name}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"data": data, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False)
        print(f"   [Save]  Checkpoint saved: {name}")

    def _load_checkpoint(self, name: str, default=None) -> Any:
        """加载阶段性 checkpoint，不存在或已过期返回 default"""
        path = os.path.join(self.CHECKPOINT_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 过期检查：非今天的 checkpoint 视为无效
            saved_date = data.get("timestamp", "")[:10]
            today = datetime.now().strftime("%Y-%m-%d")
            if saved_date == today:
                return data["data"]
            else:
                print(f"   [Trash]   Checkpoint expired ({saved_date}), re-running {name}")
                os.remove(path)
        return default

    def _run_llm_with_tools(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.1,
        max_turns: int = 15,
        checkpoint_name: Optional[str] = None,
    ) -> str:
        """运行LLM+工具调用循环，直到得到最终回答"""
        # 从 checkpoint 恢复消息历史
        turn_start = 0
        if checkpoint_name:
            cp = self._load_checkpoint(checkpoint_name, default=None)
            if cp is not None and isinstance(cp, dict):
                saved_messages = cp.get("messages")
                saved_turn = cp.get("turn", 0)
                if saved_messages and saved_turn < max_turns:
                    messages = saved_messages
                    turn_start = saved_turn
                    print(f"        [Resume]   Resuming LLM conversation from turn {saved_turn}/{max_turns}")

        import requests
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

        for turn in range(turn_start, max_turns):
            url = f"{self.llm.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.llm.api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": self.llm.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": self.llm.max_tokens,
                "tools": self.tools.get_openai_tools(),
                "tool_choice": "auto",
            }

            response = session.post(url, headers=headers, json=data, timeout=600, proxies=None)
            response.raise_for_status()
            result = response.json()
            choice = result["choices"][0]
            message = choice["message"]

            # 检查是否有工具调用
            if "tool_calls" in message and message["tool_calls"]:
                # Append assistant message once before tool results
                messages.append(message)

                # 并行执行所有工具调用
                def run_one_tool(tc: Dict[str, Any]) -> Tuple[str, str, str]:
                    name = tc["function"]["name"]
                    args = json.loads(tc["function"].get("arguments", "{}"))
                    short_desc = f"{name}({args.get('query', args.get('url', '?'))[:60]})"
                    print(f"   [Tool]  {short_desc}...", end="", flush=True)
                    result_text = self._format_tool_call(tc)
                    print(f" done")
                    return tc["id"], name, result_text

                with ThreadPoolExecutor(max_workers=5) as pool:
                    futures = {pool.submit(run_one_tool, tc): tc for tc in message["tool_calls"]}
                    for future in as_completed(futures):
                        tc_id, name, content = future.result()
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc_id,
                            "name": name,
                            "content": content,
                        })

                # 每轮只保存一次 checkpoint（工具全部执行完后）
                if checkpoint_name:
                    self._save_checkpoint(checkpoint_name, {
                        "messages": messages,
                        "turn": turn + 1,
                    })


                # 到达最后一轮时强制收尾
                if turn == max_turns - 1:
                    print(f"   ⏰ 达到轮次上限 ({max_turns})，强制输出最终结果")
                    force_msg = (
                        "TIME LIMIT REACHED. You have used all available search turns. "
                        "Output your best available data now using the specified JSON format. "
                        "For any data points you could not fully verify, set the "
                        "data_confidence field per stock to indicate what was estimated, "
                        "the credibility of the source, and risk of relying on that data. "
                        "Do NOT call any more tools."
                    )
                    messages.append({"role": "user", "content": force_msg})
                    data["messages"] = messages
                    data["tool_choice"] = "none"
                    response = session.post(url, headers=headers, json=data, timeout=600, proxies=None)
                    response.raise_for_status()
                    result = response.json()
                    choice = result["choices"][0]
                    return choice["message"]["content"].strip()

                continue

            # 没有工具调用，返回最终回答
            if checkpoint_name:
                path = os.path.join(self.CHECKPOINT_DIR, f"{checkpoint_name}.json")
                if os.path.exists(path):
                    os.remove(path)
            return message["content"].strip()

        # 不应到达此处，兜底
        raise RuntimeError(f"Unreachable: exceeded max_turns {max_turns}")

    def _collect_macro_data(self, system_prompts: List[str], temperature: float) -> str:
        """Phase 1: Collect macroeconomic data"""
        print("\n[Data]  Phase 1: Collecting macroeconomic data")
        template = self._read_prompt_template("01_macro_collect.md")
        today = datetime.now().strftime("%B %d, %Y")
        template = template.replace("{{today}}", today)

        messages = []
        for sp in system_prompts:
            messages.append({"role": "system", "content": sp})
        messages.append({"role": "user", "content": template})

        result = self._run_llm_with_tools(messages, temperature, max_turns=25)
        print("   [OK]  Macro data collection complete")
        return result

    def _analyze_macro(self, system_prompts: List[str], macro_data: str, temperature: float) -> str:
        """Phase 2: Macro analysis"""
        print("\n[Data]  Phase 2: Macroeconomic analysis")
        template = self._read_prompt_template("02_macro_analyze.md")
        prompt = self._render_template(template, {"macro_data": macro_data})

        messages = []
        for sp in system_prompts:
            messages.append({"role": "system", "content": sp})
        messages.append({"role": "user", "content": prompt})

        result = self._run_llm_with_tools(messages, temperature, max_turns=20)
        print("   [OK]  Macro analysis complete")
        return result

    def _screen_stocks(
        self,
        system_prompts: List[str],
        macro_analysis: str,
        screen_temperature: float = 0.4,
        extra_cooldown: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """Phase 2.5: Dynamic stock screening and selection"""
        print("\n[Screen]  Phase 2.5: Screening and selecting stocks for analysis")

        current_date = datetime.now().strftime("%Y-%m-%d")
        cooldown_symbols = self.history.get_cooldown_symbols(current_date)
        if extra_cooldown:
            cooldown_symbols = list(set(cooldown_symbols + extra_cooldown))
        last_run_symbols = self.history.get_last_run_symbols()
        recent_symbols = self.history.get_recent_symbols(n_days=14)

        template = self._read_prompt_template("02b_stock_screen.md")
        prompt = self._render_template(template, {
            "macro_analysis": macro_analysis,
            "cooldown_stocks": ", ".join(cooldown_symbols) if cooldown_symbols else "None",
            "recent_coverage": ", ".join(recent_symbols) if recent_symbols else "No recent coverage",
        })

        messages = []
        for sp in system_prompts:
            messages.append({"role": "system", "content": sp})
        messages.append({"role": "user", "content": prompt})

        result = self._run_llm_with_tools(messages, temperature=screen_temperature, max_turns=25, checkpoint_name="phase25_screening")

        candidates = self.stock_selector.parse_llm_json(result)

        if not candidates:
            print("   [WARN]   WARNING: Failed to parse stock candidates from LLM, using fallback list")
            candidates = [
                {"symbol": s["symbol"], "name": s["name"], "sector": "Unknown",
                 "momentum": "Neutral", "pct_change_5d": "0%", "pct_change_20d": "0%"}
                for s in self.FALLBACK_STOCKS
            ]

        selected = self.stock_selector.select(
            candidates, cooldown_symbols, last_run_symbols, target_count=10
        )

        if len(selected) < 5:
            print(f"   [WARN]   WARNING: Only {len(selected)} stocks after screening, supplementing with fallback")
            selected = self.stock_selector._supplement_with_fallback(
                selected, cooldown_symbols, target_count=10
            )

        stock_list = []
        for s in selected:
            entry = {"symbol": s["symbol"], "name": s["name"]}
            if "data_confidence" in s:
                entry["data_confidence"] = s["data_confidence"]
            stock_list.append(entry)

        print(f"   [OK]  Selected {len(stock_list)} stocks: {', '.join(s['symbol'] for s in stock_list)}")
        if last_run_symbols:
            new_count = sum(1 for s in stock_list if s["symbol"] not in set(last_run_symbols))
            print(f"   [Data]  New stocks in this run: {new_count} (minimum required: 3)")

        return stock_list, candidates

    def _prerotate_stocks(self, last_run_symbols: List[str], cooldown_symbols: List[str]) -> List[str]:
        """
        Parallel real-time price check on last run's stocks.
        Find the 3 worst performers and add them to the cooldown list.
        """
        if not last_run_symbols:
            return list(cooldown_symbols)

        to_check = [s for s in last_run_symbols if s not in set(cooldown_symbols)]
        if len(to_check) <= 3:
            return list(cooldown_symbols)

        import re

        def check_one(symbol: str) -> tuple:
            try:
                result = self.tools.execute(
                    "web_search",
                    query=f"{symbol} stock price change today percentage",
                    num_results=3,
                )
                text = result.lower()
                # Try matching "down/fell/declined X%" or "up/rose/gained X%" or standalone "+/-X%"
                m = re.search(r'(?:down|fell|declined|dropped|decreased)\s+([\d.]+)%', text)
                if m:
                    return symbol, -float(m.group(1))
                m = re.search(r'(?:up|rose|gained|increased|climbed)\s+([\d.]+)%', text)
                if m:
                    return symbol, float(m.group(1))
                m = re.search(r'([+-])\s*([\d.]+)%', text)
                if m:
                    sign = -1 if m.group(1) == '-' else 1
                    return symbol, sign * float(m.group(2))
                # Check for "down" / "fell" mentions without exact number
                if re.search(r'\b(down|fell|drop|decline)\b', text):
                    return symbol, -0.5  # small negative signal
                if re.search(r'\b(up|rose|gain|climb)\b', text):
                    return symbol, 0.5   # small positive signal
            except Exception:
                pass
            return symbol, None

        print("   [Pre-rotate] Checking last run stocks for today's performance...")
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(check_one, to_check))

        with_data = [(s, p) for s, p in results if p is not None]
        if len(with_data) < 3:
            print(f"   [Pre-rotate] Only {len(with_data)} with price data, skipping rotation")
            return list(cooldown_symbols)

        with_data.sort(key=lambda x: x[1])
        worst_three = with_data[:3]
        updated = set(cooldown_symbols)
        for sym, pct in worst_three:
            updated.add(sym)
            print(f"   [Pre-rotate] {sym} ({pct:+.1f}%) -> cooldown (2 days)")
        print(f"   [Pre-rotate] {len(cooldown_symbols)} existing + {len(worst_three)} new = {len(updated)} in cooldown")
        return list(updated)

    def _pick_new_stocks(
        self,
        stock_list: List[Dict[str, str]],
        llm_candidates: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """
        Identify new additions and put them first in the analysis order.
        New = not in last_run_symbols. Sorted by pct_change_5d descending.
        """
        last_symbols = set(self.history.get_last_run_symbols())
        if not last_symbols:
            return stock_list

        candidates_map = {c["symbol"]: c for c in llm_candidates if "pct_change_5d" in c}

        carryover = []
        new_stocks = []
        for s in stock_list:
            if s["symbol"] in last_symbols:
                carryover.append(s)
            else:
                new_stocks.append(s)

        scored = []
        for s in new_stocks:
            c = candidates_map.get(s["symbol"])
            if c:
                pct = StockSelector._parse_pct(c.get("pct_change_5d", "0%"))
                scored.append((pct, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_new = [s for _, s in scored]

        result = top_new + carryover
        if top_new:
            print(f"   [Pick-new] Priority stocks (new additions): {', '.join(s['symbol'] for s in top_new)}")
        return result[:10]

    def _analyze_single_stock(
        self,
        system_prompts: List[str],
        macro_analysis: str,
        stock: Dict[str, str],
        index: int,
        temperature: float,
        total_stocks: int = 10,
    ) -> str:
        """Phase 3: Analyze single stock"""
        symbol = stock["symbol"]
        name = stock["name"]
        print(f"\n[Data]  Phase 3: Analyzing stock {index}/{total_stocks} - {name} ({symbol})")

        template = self._read_prompt_template("03_stock_analyze.md")
        context = {
            "macro_analysis": macro_analysis,
            "stock_name": name,
            "stock_symbol": symbol,
            "stock_index": index,
            "today": datetime.now().strftime("%B %d, %Y"),
        }

        # 注入数据可信度备注（如选股阶段标注了低/中置信度）
        data_conf = stock.get("data_confidence")
        if data_conf and isinstance(data_conf, dict):
            conf_level = data_conf.get("level", "high")
            uncertain_fields = data_conf.get("uncertain_fields", [])
            if conf_level != "high" or uncertain_fields:
                details = data_conf.get("details", "")
                parts = [f"[Data Confidence: {conf_level.upper()}]"]
                if details:
                    parts.append(details)
                if uncertain_fields:
                    parts.append("Uncertain fields:")
                    for uf in uncertain_fields:
                        field = uf.get("field", "?")
                        cred = uf.get("credibility", "No source info")
                        risk = uf.get("risk", "Unknown")
                        parts.append(f"- {field}: source='{cred}', risk={risk}")
                context["data_confidence_note"] = "\n".join(parts)
            else:
                context["data_confidence_note"] = ""
        else:
            context["data_confidence_note"] = ""

        prompt = self._render_template(template, context)

        messages = []
        for sp in system_prompts:
            messages.append({"role": "system", "content": sp})
        messages.append({"role": "user", "content": prompt})

        result = self._run_llm_with_tools(messages, temperature, max_turns=20, checkpoint_name=f"phase3_stock_{symbol}")
        print(f"   [OK]  {name} analysis complete")
        return result

    @staticmethod
    def _extract_recommendation(analysis_text: str, symbol: str) -> str:
        """Extract trading recommendation from stock analysis text"""
        for line in analysis_text.split('\n'):
            lower = line.lower()
            if 'trading recommendation' in lower or 'recommendation' in lower:
                if 'Priority Buy' in line:
                    return 'Priority Buy'
                elif 'Not Recommended' in line:
                    return 'Not Recommended'
                elif 'Wait for Pullback' in line:
                    return 'Wait for Pullback'
        return 'Unclear'

    def _build_sector_summary(self) -> str:
        """Build dynamic sector summary from current stock list"""
        sector_map = {
            "NVDA": "Technology", "AAPL": "Technology", "MSFT": "Technology", "AMD": "Technology",
            "JPM": "Financial", "BAC": "Financial",
            "COST": "Consumer", "KO": "Consumer", "V": "Consumer",
            "BRK.B": "Value",
        }
        sector_groups: Dict[str, List[str]] = {}
        for stock in self.current_stock_list:
            sector = sector_map.get(stock["symbol"], "Other")
            sector_groups.setdefault(sector, []).append(stock["symbol"])

        lines = ["\nSector Summary of Selected Stocks:"]
        for sector, symbols in sector_groups.items():
            lines.append(f"- {sector}: {', '.join(symbols)}")
        return '\n'.join(lines)

    def _compile_final_report(
        self,
        system_prompts: List[str],
        macro_data: str,
        macro_analysis: str,
        stock_analyses: List[str],
        temperature: float,
    ) -> str:
        """Phase 4: Compile final report"""
        print("\n[Data]  Phase 4: Compiling final report")

        # Extract S&P 500 and Nasdaq 100 values (simple search from macro_data)
        sp500_value = ""
        ndx_value = ""
        for line in macro_data.split('\n'):
            if 'S&P 500' in line and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    sp500_value = parts[2]
            if 'Nasdaq 100' in line and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    ndx_value = parts[2]

        template = self._read_prompt_template("04_final_compile.md")
        today = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%B %d, %Y %H:%M")

        stock_sector_summary = self._build_sector_summary()

        # Render template, handle stock block loop
        prompt = template
        prompt = prompt.replace("{{macro_data}}", macro_data)
        prompt = prompt.replace("{{macro_analysis}}", macro_analysis)
        prompt = prompt.replace("{{sp500_value}}", sp500_value)
        prompt = prompt.replace("{{ndx_value}}", ndx_value)
        prompt = prompt.replace("{{today}}", today)
        prompt = prompt.replace("{{current_time}}", current_time)
        prompt = prompt.replace("{{stock_sector_summary}}", stock_sector_summary)

        # Handle stock loop
        if "{% for stock in stock_analyses %}" in prompt:
            # Find start and end of stock loop
            lines = prompt.split('\n')
            new_lines = []
            in_loop = False
            loop_content = []
            for line in lines:
                if "{% for stock in stock_analyses %}" in line:
                    in_loop = True
                    continue
                if "{% endfor %}" in line:
                    in_loop = False
                    # Concatenate all stock analyses
                    for stock in stock_analyses:
                        for ll in loop_content:
                            new_lines.append(ll.replace("{{stock}}", stock))
                    continue
                if in_loop:
                    loop_content.append(line)
                else:
                    new_lines.append(line)
            prompt = '\n'.join(new_lines)

        messages = []
        for sp in system_prompts:
            messages.append({"role": "system", "content": sp})
        messages.append({"role": "user", "content": prompt})

        # Final step doesn't need tools, direct LLM integration
        result = self.llm.complete(system_prompts, prompt, temperature)
        print("   [OK]  Final report generation complete")
        return result

    def run(
        self,
        output_dir: str = "output",
        temperature: float = 0.1,
        screen_temperature: float = 0.4,
        cooldown_days: int = 2,
        max_turns: int = 40,
    ) -> Tuple[str, str]:
        """Run complete phased analysis workflow"""

        # Apply cooldown_days setting
        self.history.data["cooldown_days"] = cooldown_days

        from agent.prompt_builder import PromptBuilder
        builder = PromptBuilder(self.config_dir)
        system_prompts = builder.build_system_prompts()

        print("=" * 60)
        print("[Rocket]  Starting US Stock Deep Analysis Workflow (Phased Execution)")
        print(f"[Time]  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        print(f"[Config]  Loaded layered configuration:")
        print(f"   - IDENTITY: {len(system_prompts[0])} chars")
        print(f"   - SOUL: {len(system_prompts[1])} chars")
        print(f"   - Finance: {len(system_prompts[2])} chars")
        print()
        print(f"[Target]  Stock list will be determined dynamically after macro analysis")
        print(f"   Cooldown: {cooldown_days} days for dropped stocks")
        print(f"   Screen temperature: {screen_temperature}")
        print()

        # ========== 断点续跑：检查已有 checkpoint ==========

        # Phase 1: Collect macro data
        macro_data = self._load_checkpoint("phase1_complete")
        if macro_data is not None:
            print("   [Resume]   Resuming from checkpoint: Phase 1 (macro data)")
        else:
            macro_data = self._collect_macro_data(system_prompts, temperature)
            self._save_checkpoint("phase1_complete", macro_data)

        missing = macro_data.count("[Data Not Available]")
        if missing > 0:
            print(f"   [WARN]   {missing} instances of [Data Not Available] in macro data, continuing analysis (no fabrication)")

        # Phase 2: Macro analysis
        macro_analysis = self._load_checkpoint("phase2_complete")
        if macro_analysis is not None:
            print("   [Resume]   Resuming from checkpoint: Phase 2 (macro analysis)")
        else:
            macro_analysis = self._analyze_macro(system_prompts, macro_data, temperature)
            self._save_checkpoint("phase2_complete", macro_analysis)

        # Phase 2.5: Dynamic stock screening
        stock_list = self._load_checkpoint("phase25_complete")
        if stock_list is not None:
            print("   [Resume]   Resuming from checkpoint: Phase 2.5 (screening + rotation complete)")
            candidates = []
        else:
            # Step A: Pre-rotate — find 3 worst from last run, add to cooldown
            last_run_symbols = self.history.get_last_run_symbols()
            current_cooldown = self.history.get_cooldown_symbols(datetime.now().strftime("%Y-%m-%d"))
            extra_cooldown = self._prerotate_stocks(last_run_symbols, current_cooldown)

            # Step B: LLM screens stocks (avoids cooldown including prerotated)
            stock_list, candidates = self._screen_stocks(
                system_prompts, macro_analysis, screen_temperature,
                extra_cooldown=extra_cooldown,
            )
            self._save_checkpoint("phase25_screen_result", stock_list)

            # Step C: pick 3 best new additions, put them first
            stock_list = self._pick_new_stocks(stock_list, candidates)
            self._save_checkpoint("phase25_complete", stock_list)

        self.current_stock_list = stock_list
        total_stocks = len(stock_list)
        print(f"\n[Target]  Final analysis target: {total_stocks} stocks - " +
              ", ".join(s["symbol"] for s in stock_list))

        # Phase 3: Analyze each selected stock (parallel with 2 workers)
        cp3 = self._load_checkpoint("phase3_progress", default={})
        stock_analyses = cp3.get("analyses", [])
        recommendations = cp3.get("recommendations", {})

        # 补齐到 total_stocks 长度（首次或部分完成时）
        if len(stock_analyses) < total_stocks:
            stock_analyses += [None] * (total_stocks - len(stock_analyses))

        remaining = [i + 1 for i in range(total_stocks) if stock_analyses[i] is None]
        completed_count = total_stocks - len(remaining)

        if completed_count > 0:
            print(f"   [Resume]   Resuming from checkpoint: Phase 3 ({completed_count}/{total_stocks} stocks done)")

        def analyze_stock(i: int, stock: Dict[str, str]) -> Tuple[int, str, str]:
            analysis = self._analyze_single_stock(
                system_prompts, macro_analysis, stock, i, temperature, total_stocks
            )
            rec = self._extract_recommendation(analysis, stock["symbol"])
            return i, analysis, rec

        if remaining:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(analyze_stock, i, stock_list[i - 1]): i
                    for i in remaining
                }
                for future in as_completed(futures):
                    i, analysis, rec = future.result()
                    stock_analyses[i - 1] = analysis
                    recommendations[stock_list[i - 1]["symbol"]] = rec
                    # 每完成一只增量保存 checkpoint
                    self._save_checkpoint("phase3_progress", {
                        "analyses": stock_analyses,
                        "recommendations": recommendations,
                    })



        # Phase 4: Compile final report (lighter system prompts — no tools needed)
        compile_system_prompts = builder.build_compile_system_prompts()
        final_report = self._compile_final_report(
            compile_system_prompts, macro_data, macro_analysis, stock_analyses, temperature
        )

        # Record this run in history
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.history.record_run(current_date, stock_list, recommendations)
        print(f"   [OK]  Run recorded in history ({len(stock_list)} stocks, cooldown={cooldown_days} days)")

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"US_Stock_Deep_Analysis_Report_{timestamp}.md"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_report)

        # Generate HTML version for web viewing
        from web_renderer import save_html_report, get_http_url
        html_path = save_html_report(final_report, output_dir, timestamp)
        html_url = get_http_url(html_path)

        # Report completion
        print(f"\n============================================================")
        print(f"[OK]  Full workflow complete!")
        print(f"[File]  Markdown report: {output_path}")
        print(f"[Link]  View in browser: {html_url}")
        print(f"[Tip]  To serve report: python open_report.py --latest")
        print(f"============================================================")

        return final_report, output_path
