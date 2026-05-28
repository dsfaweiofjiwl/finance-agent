# Phase 4: Compile Final Report

## Task Objective
Integrate analysis from previous phases into a complete US stock market deep analysis report according to specified format.

**⚠️ CRITICAL LANGUAGE REQUIREMENT: All output must be 100% ENGLISH ONLY. No Chinese characters, words, or phrases anywhere in your response. The entire final report must be in English.**

---

## Input Data

### Macro Data Collection (with brief interpretations per section) (from Phase 1)
{{macro_data}}

### Federal Reserve Policy Analysis (from Phase 2)
{{macro_analysis}}

### Stock Analysis List (from Phase 3)
See full stock analyses in Section V below.

{{stock_sector_summary}}

---

## Output Format Requirements (100% Strict Compliance, do not add or remove titles)

---

# 【US Stock Market Deep Analysis Report】

**Date**: {{today}}  
**Data Sources**: List main websites  
**Original Data Release Time**: Latest published official values used (note each data release date)

---

## 📑 Table of Contents

[box]
1. 🏦 US Macro Policy & Federal Reserve
2. 📰 Official News & Geopolitical Headlines
3. 📊 Key Macro Data & Policy Signals
4. 🔬 Macro Conclusion Summary
5. 📈 S&P 500, Nasdaq 100 and Related ETF Indices
6. 💎 Alternative Asset Watch (Oil, Gold, BTC)
7. 🔍 Individual Stock Analysis (10 Stocks)
8. 💼 General Recommendations for Investors
[/box]

---

# I. 🏦 US Macro Policy & Federal Reserve

**⚠️ MANDATORY: Do NOT skip or merge this section. It must contain BOTH macro policy AND Fed analysis.**

(Merge and copy the macro policy overview from macro_analysis AND the Federal Reserve speeches/meetings content from macro_analysis. Include: FOMC rate decision, Fed Chair speech quotes, dot plot summary, leadership transition updates, and investment direction implications. Do NOT leave a stub saying "content merged elsewhere" — write the full content here. Do NOT add numbering to subheadings — use plain `##` titles only.)

---

# II. 📰 Official News & Geopolitical Headlines

## 🔴 Top Geopolitical Headlines

(Copy the detailed geopolitical narratives from macro_analysis. Keep the paragraph format — NOT a table. 2-3 stories, each with bold headline + 3-4 sentence analysis covering what happened, market impact, and what to watch next.)

## 🗞️ Latest Official News & Corporate Announcements

(Copy the corporate news table from macro_analysis. Columns: Time | Source | Event | Affected.)

## 🎓 Wall Street & Institutional Commentary

(Copy analyst quotes and views from macro_analysis.)

## 🧭 Week Ahead — Key Events to Watch

(Copy the week ahead table from macro_analysis. Columns: Date | Event | Why It Matters. 5-7 items.)

---

# III. 📊 Key Macro Data & Policy Signals
(Place macro_data content here EXCEPT the "Alternative Assets" section and "Macro Conclusion Summary" — stop before "## 4. Alternative Assets". Include all inflation, employment, and rates tables with their interpretations.)

---

# IV. 🔬 Macro Conclusion Summary
(Place ONLY the "Macro Conclusion Summary" content from macro_data here — the logical chain table and judgment summary. Do NOT include the macro_data sub-heading "## Macro Conclusion Summary" — the Section IV heading above replaces it.)

---

# V. 📈 S&P 500, Nasdaq 100 and Related ETF Indices
(Extract index levels from macro_data, organize into following format)

| Index/ETF | Latest Value | 5-Day Change |
|:----------|:----------|:----------|
| S&P 500 | {{sp500_value}} | (wrap in [up] or [down]) |
| Nasdaq 100 | {{ndx_value}} | (wrap in [up] or [down]) |

**Index Analysis & ETF Recommendations**: (Brief analysis of index positioning, main ETF investment direction, and impact on weighted stocks — combine into one concise paragraph)

---

## 💎 Alternative Asset Watch

(Copy the "## 4. Alternative Assets" section from macro_data here — Oil, Gold, BTC tables with their analysis. Keep the existing data and format from Phase 1. Do NOT create new tables from scratch — use the data already collected.)

---

# VI. 🔍 Individual Stock Analysis
Selected US Stocks and Buy/Sell Points

{% for stock in stock_analyses %}

**🏢 Company Profile**
(Write 2-3 sentences summarizing this company based on the Phase 3 analysis below: what it does, key business segments, competitive position. Include shareholder structure summary and the Yahoo Finance K-line chart link from Phase 3.)

**📋 Quick Summary**

| Metric | Value |
|:---|---:|
| 💰 Current Price | (extract from analysis below) |
| 🏢 Market Cap | (extract from analysis below) |
| 📊 P/E (TTM) | (extract from analysis below) |
| 💵 Dividend Yield | (extract from analysis below) |
| 📈 52-Week Range | (extract from analysis below) |
| 🟢 Buy Range | (extract from analysis below) |
| 🔴 Stop-Loss | (extract from analysis below) |
| ⚡ Recommendation | [badge:green]Priority Buy[/badge] / [badge:yellow]Wait[/badge] / [badge:red]Not Recommended[/badge] |

**📊 Support & Resistance Levels**

| Level | Price | Signal / Rationale |
|:---|---:|:---|
| 🔴 Major Resistance | (extract) | (extract) |
| 🟡 Minor Resistance | (extract) | (extract) |
| 🟢 Minor Support | (extract) | (extract) |
| 🔵 Major Support | (extract) | (extract) |

**🔮 30-Day Outlook**

| 🟢 Bullish Drivers | 🔴 Bearish Risks |
|:---|:---|
| (extract) | (extract) |
| (extract) | (extract) |
| (extract) | (extract) |

**Overall Bias:** [badge:green]Bullish[/badge] / [badge:yellow]Range-bound[/badge] / [badge:red]Bearish[/badge]

---

**📝 Detailed Analysis**
(Summarize the key analytical points from Phase 3 below in your own words. Cover: price trend, volume dynamics, key catalysts. Do NOT repeat the data points already captured in the tables above. Keep it concise — 2-3 sentences per stock.)

---

*Reference data from Phase 3 (use for table extraction — do NOT output verbatim):*

{{stock}}
{% endfor %}

---

# VII. 💼 General Recommendations for Investors

## 📌 Executive Summary

(Write 3-4 sentences synthesizing this week's macro stance + stock analysis into an actionable takeaway. Answer: given everything above, what should an investor DO this week? Reference the Fed stance, key macro data, geopolitical backdrop, and the dominant recommendation pattern across the 10 stocks. Do NOT repeat the macro conclusion from Section IV — this is about portfolio action, not macro diagnosis.)

---

## 🧠 This Week's Tactical Plan

1. **(Specific action)**: (Which sector or stock to act on this week. Entry zone, target signal, or trigger condition. Reference specific prices from the stock picks.)
2. **(Specific action)**: (What to reduce, avoid, or wait on this week. Why — macro catalyst or technical overextension. Name specific names.)
3. **(Specific action)**: (A concrete entry plan: "If [STOCK] pulls back to $[PRICE], start a position with stop at $[PRICE]." Reference the best risk/reward setup from this week's picks.)
4. **(Risk to watch)**: (The single most consequential near-term catalyst — data release, Fed event, geopolitical milestone. What signal to monitor and how it changes the plan.)

---

## 🎯 Position Allocation

<!-- 👇 INSTRUCTIONS FOR LLM ONLY - DO NOT OUTPUT IN FINAL REPORT 👇
Final Position Allocation = Integrated result of Phase 1 Macro Judgment + Phase 3 Stock Analysis

1. Macro input: Reference Macro Conclusion Summary (inflation trend/Fed policy stance/Treasuries/DXY/index positioning judgment)
2. Stock input: Combine fundamental and technical analysis conclusions from 10 individual stocks
3. Dynamically adjust, DO NOT USE FIXED DEFAULT VALUES!
4. Each sector allocation rationale must cite BOTH macro data AND stock analysis conclusions
5. Adjustment reference logic:
   - Inflation hotter than expected + Fed hawkish → Reduce growth stocks, increase defensives and cash
   - Inflation cooling + Fed turning dovish → Can moderately increase growth stock allocation
   - Employment data weakening + rising recession risk → Increase defensive sectors, reduce cyclicals
   - Dollar Index strengthening persistently → Be cautious on commodities and emerging markets
   👆 INSTRUCTIONS FOR LLM ONLY - DO NOT OUTPUT IN FINAL REPORT -->

| Investment Direction | Position Ratio | Rationale |
|:------|:------:|:-------|
| AI/Tech Leaders | [bar:tech:XX] | (2-3 sentences. Cite rate environment, Fed stance, and specific tech stocks from this week's picks.) |
| Financial Leaders | [bar:finance:XX] | (2-3 sentences. Cite yield curve shape, NIM outlook, and specific financial stocks analyzed.) |
| Consumer/Defensive | [bar:defensive:XX] | (2-3 sentences. Cite inflation level, consumer strength, and specific defensive stocks analyzed.) |
| Energy/Value | [bar:value:XX] | (2-3 sentences. Cite oil supply dynamics, valuation spreads, and specific energy stocks analyzed.) |
| Alternative Assets (Oil, Gold, BTC) | [bar:alt:XX] | (2-3 sentences. Cite oil supply risk, gold as inflation hedge, BTC risk appetite correlation.) |
| Cash / Dry Powder | [bar:cash:XX] | (2-3 sentences. Cite market uncertainty, index levels vs. moving averages, pullback optionality.) |

(Position Ratio column: only the [bar:category:XX] markup — do NOT add a separate "XX%" text. The bar renders the percentage visually. Ensure all bars sum to 100.)

---

## ⚠️ Risk Disclosure

(List 4-5 current risks ordered by probability × impact. Title color = priority. At most 2 [down]HIGH[/down] items. Tie each risk to a specific catalyst — no generic labels.)

[down]**(HIGH) Risk Title**[/down]: (1 sentence — likely + damaging. What triggers it, what it impacts.)

[warn]**(MEDIUM) Risk Title**[/warn]: (1 sentence — either likely OR damaging, not both.)

[up]**(LOW) Risk Title**[/up]: (1 sentence — tail risk, low probability or low impact.)

---

*Report Generation Time: {{current_time}} GMT+8*  
*This analysis is generated based on public data, for internal investment research discussion reference only, does not constitute any investment advice or trading decision basis.*

---

## Rules

1. Strictly maintain title hierarchy, do not add or remove titles.
2. Directly use content already generated in previous phases, place in correct positions as-is, no need to regenerate.
3. Do not repeat content, do not repeat analysis.
4. Keep original formatting and tables unchanged.
5. **⚠️ NEVER skip Section I (Macro Policy & Fed) or the 🔴 Top Geopolitical Headlines subsection. These are MANDATORY.**
6. **PRICE FORMAT RULE: Always place dollar sign BEFORE the number**:
   - Correct: `$195-$202`, `$189`
   - Wrong: `195-202$`, `189$`, `$260-265$`
7. **COLOR MARKER RULES**:
   - Wrap ALL positive changes/deltas in `[up]...[/up]` (renders as green text): `[up]+1.2%[/up]`
   - Wrap ALL negative changes/deltas in `[down]...[/down]` (renders as red text): `[down]-0.8%[/down]`
   - Use `[badge:green]Label[/badge]` for Priority Buy, `[badge:yellow]Label[/badge]` for Wait/Caution, `[badge:red]Label[/badge]` for Avoid/Not Recommended
   - In Section VII Risk Disclosure: `[down] **(HIGH) Title**[/down]` = red title, `[warn]**(MEDIUM) Title**[/warn]` = amber title, `[up]**(LOW) Title**[/up]` = green title.
8. **BAR CHART RULE**: In the Position Allocation table, replace `XX` in `[bar:category:XX]` with the midpoint percentage number (e.g., `[bar:tech:35]` for a 30-40% range). Available categories: `tech`, `finance`, `defensive`, `value`, `alt`, `cash`
9. **STOCK SECTIONS REQUIRED**: Each stock MUST have these sections in order: 🏢 Company Profile → 📋 Quick Summary table → 📊 Support & Resistance table → 🔮 30-Day Outlook table → 📝 Detailed Analysis. Do NOT skip any of these.
10. **NO DUPLICATION**: Tables extract data from Phase 3 analysis. The 📝 Detailed Analysis section summarizes the narrative in your own words. Do NOT copy-paste the raw Phase 3 text verbatim after the tables.
