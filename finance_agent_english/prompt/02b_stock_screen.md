# Phase 2.5: Dynamic Stock Screening & Selection

## Macro Background (from Phase 2)

{{macro_analysis}}

---

## Task Objective

Based on the macro analysis above and current market conditions, search for and identify **15-20 US-listed stocks** that are the most important to analyze today. You must use web_search and web_fetch tools to find real market data.

### Recently Analyzed Stocks (Avoid Repeating)

The following stocks were analyzed recently and should be **avoided** unless no better alternatives exist:
{{cooldown_stocks}}

Recent coverage in the past 2 weeks: {{recent_coverage}}

### CRITICAL: Minimum Change Requirement

At least **3 stocks** in your final list must be **different** from the recently analyzed stocks above. Prioritize discovering new, timely opportunities over repeating familiar names.

---

## Sector Diversity Guidance

While stock selection should be driven by market performance, please maintain reasonable sector diversity across Technology, Financial, Consumer, and other sectors.

Do NOT select all tech stocks.

---

## Risk Screening Criteria (MANDATORY EXCLUSION)

You MUST exclude any stock that meets ANY of these conditions:
1. **Declined more than 8% in the past 5 trading days** — do not include
2. **Declined more than 15% in the past 20 trading days** — do not include
3. **Volume spike (>2x average) combined with price drop >5% in a single session** — do not include
4. **Company announced materially negative guidance, earnings miss, or regulatory action in the past 5 days** — do not include

Search for "US stock market biggest losers" and "stocks selling off" to build your exclusion list.

---

## Search Instructions

Use web_search and web_fetch to find:
1. "US stock market top performers today" / "best performing stocks this week"
2. "S&P 500 sector leaders performance" / "which sectors outperforming"
3. "US stock market biggest losers" / "stocks selling off today" (for exclusion)
4. "stocks with positive momentum catalyst" / "earnings beats this week"
5. "financial sector leaders" / "bank stocks performance"
6. "consumer staples outperformers" / "defensive stocks gains"

Cross-reference multiple sources. Do not rely on a single search result.

---

## Output Format (STRICT — Return ONLY this JSON)

Return a JSON array with 15-20 candidate stocks. Each entry must have this exact structure:

```json
[
  {
    "symbol": "NVDA",
    "name": "NVIDIA Corporation",
    "sector": "Technology",
    "reason": "AI chip demand acceleration, recent earnings beat expectations",
    "momentum": "Bullish",
    "pct_change_5d": "+3.2%",
    "pct_change_20d": "+8.1%",
    "data_confidence": {
      "level": "high",
      "details": "All data verified from Yahoo Finance and multiple market data sources",
      "uncertain_fields": []
    }
  }
]
```

Fields:
- `symbol`: Ticker symbol (e.g., "NVDA")
- `name`: Full company name
- `sector`: One of: Technology, Financial, Consumer, Healthcare, Energy, Industrial, Value
- `reason`: 1-2 sentence justification for why this stock is worth analyzing today
- `momentum`: One of "Bullish", "Neutral", "Bearish"
- `pct_change_5d`: 5-day price change as string with % sign (e.g., "+3.2%" or "-1.5%")
- `pct_change_20d`: 20-day price change as string with % sign
- `data_confidence`: Object describing confidence in this stock's data.
  - `level`: One of "high", "medium", "low". Overall confidence for this stock.
  - `details`: Free-text explanation of what was verified and what was estimated.
  - `uncertain_fields`: Array of objects for any fields with uncertainty. Each object:
    - `field`: The field name (e.g., "pct_change_5d", "momentum")
    - `credibility`: Source of the data or why it is uncertain
    - `risk`: Risk assessment of relying on this data (one of "LOW", "MEDIUM", "HIGH")
  If all data is verified, set `uncertain_fields` to an empty array `[]`.

**IMPORTANT**: Return ONLY the JSON array. No additional text before or after.

---

## Rules

1. All data must be obtained through search tools — no guessing or fabrication.
2. If you cannot find exact percentage changes, provide your best estimate based on search results and mark it as approximate.
3. Prioritize stocks with positive or neutral momentum over bearish stocks.
4. Ensure at least 3 candidates are NEW (not in the cooldown list above).
5. Maintain sector diversity as specified.
6. **All output must be 100% ENGLISH.**
7. **Search turns are limited.** If you run out of turns, output your best available JSON. Use the `data_confidence` field to annotate any unverified data with source credibility and risk of relying on it. Do not fabricate data.
