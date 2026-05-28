# 美股深度分析 Agent 项目

## 运行分析

```bash
python run_analysis.py
```

可选参数：
- `--temperature 0.1` — 基础 LLM 温度（默认 0.1）
- `--screen-temperature 0.4` — 股票筛选阶段温度（默认 0.4）
- `--cooldown-days 3` — 被剔除股票重新进入候选的天数（默认 3）

## 如何生成报告总结（给 AI / OpenClaw 的指令）

每次运行完成后，`output/` 目录会生成 4 个文件：

| 文件 | 大小 | 用途 |
|:---|:---|:---|
| `*_summary.json` | ~8-12 KB | **结构化摘要 JSON（首选）** |
| `*_summary.md` | ~2-3 KB | **LLM 生成的 Markdown 摘要（可读性强）** |
| `*.md` | ~80 KB | 完整 Markdown 报告 |
| `*.html` | ~200 KB | 完整 HTML 报告 |

### ✅ 推荐方式一：读取 summary JSON（最快，结构化数据）

```bash
ls -t output/US_Stock_Deep_Analysis_Report_*_summary.json | head -1
```

JSON 包含字段：
- `report_date` — 报告日期
- `macro_judgment` — 宏观判断（fed_stance, dollar, market）
- `macro_summary` — 宏观结论摘要（完整段落）
- `indicators` — 关键宏观指标（pce, core_pce, 10y_yield, 2y_yield, 30y_yield, dxy）
- `news_headlines` — 地缘政治头条（每条含 headline + impact）
- `fed_highlights` — 美联储关键事件（FOMC 投票、点阵图、领导层交接）
- `stocks` — 每只股票的结构化数据（symbol, name, current_price, market_cap, recommendation, recommendation_color, buy_range, stop_loss, risk_flag, risk_level）
- `live_url` — **可直接点击的 HTTP 链接**
- `stock_count` — 股票数量

### ✅ 推荐方式二：读取 summary Markdown（LLM 生成，可读性强）

```bash
ls -t output/US_Stock_Deep_Analysis_Report_*_summary.md | head -1
```

这是 LLM 根据 JSON 数据 + 模版生成的英文摘要，包含：
- Macro 环境判断（红绿灯）
- 🏦 Fed Policy Stance
- 📰 Geopolitical Headlines
- 📊 Key Macro Data
- 🔬 Macro Conclusion
- 🔥 Top 3 Picks（按推荐级别排序：green > yellow > red）
- 🔗 Full Report 链接

### 如何展示完整报告

1. **直接使用 `live_url`** — JSON 里的 `live_url` 字段是实时 HTTP 链接。后台有持续运行的 HTTP 服务器。
2. **关键数据直接列成表格** — summary JSON 的 `stocks` 数组已有结构化数据。
3. **摘要 Markdown 可直接展示** — `_summary.md` 是 LLM 生成的完整英文摘要，格式美观。

### 搜索最新报告

```bash
# 最新 summary JSON
ls -t output/US_Stock_Deep_Analysis_Report_*_summary.json | head -1

# 最新 summary Markdown
ls -t output/US_Stock_Deep_Analysis_Report_*_summary.md | head -1

# 最新完整报告
ls -t output/US_Stock_Deep_Analysis_Report_*.md | grep -v summary | head -1
```
