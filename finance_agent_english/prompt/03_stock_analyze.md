# Phase 3: Individual Stock Analysis

**Today: {{today}}.** Use the latest available trading day's close for prices. If today is a weekday and markets are open, the latest close is yesterday's. If today is Monday, the latest close is last Friday's. Do NOT fabricate a same-day closing price. News should be the latest available.

## Macro Background (from Phase 2)

{{macro_analysis}}

---

## Data Confidence from Screening Phase

{{data_confidence_note}}

---

## Task Objective
Conduct complete fundamental + technical analysis for **{{stock_name}} ({{stock_symbol}})**.

**⚠️ CRITICAL LANGUAGE REQUIREMENT: All output must be 100% ENGLISH ONLY. No Chinese characters, words, or phrases anywhere in your response.**

### Risk Pre-Screening Context
This stock has passed initial risk screening. However, if during your analysis you discover ANY of the following, you MUST set Trading Recommendation to "Not Recommended" and explicitly state the risk factor:

- Stock has declined more than 8% in the past 5 trading days
- Stock has declined more than 15% in the past 20 trading days
- Stock shows volume spike (>2x average) combined with price drop >5% in a single session
- Stock has broken below key support levels with no nearby support
- Company has announced materially negative guidance, earnings miss, or regulatory action in the past 5 days

DO NOT output a risk verification table showing PASS/FAIL for each item. Only mention a risk factor if it actually triggered. If all checks pass, simply say nothing.

### Mandatory Data Points (Missing None is Allowed)
- Company Profile (2-3 sentences: what the company does, key business segments, competitive position. Include shareholder structure summary — institutional %, key holders, capital return posture)
- Current price (latest close)
- Market capitalization
- P/E (TTM), Dividend Yield, 52-Week Range (search for each, mark [Data Not Available] if missing)
- Price trend description
- Volume situation
- Support & resistance analysis, calculate buy range and stop loss
- 30-day trend forecast (drivers + risks)
- Trading recommendation

---

## Output Format (Strict Compliance — BE CONCISE)

### {{stock_index}}. {{stock_name}} ({{stock_symbol}})

- **Current Price**: $XXX (latest close with date noted)
- **Market Cap**: $XXX
- **Company Profile**: (2-3 sentences: what the company does, key business segments, competitive position. Then 1 sentence on shareholder structure — institutional %, key holders, buyback/dividend posture.)
- **Daily K-Line Chart**: [Yahoo Finance Chart](https://finance.yahoo.com/quote/{{stock_symbol}}/chart/)
- **Price Trend**: (1-2 sentences)
- **Volume**: (1 sentence)
- **Support & Resistance Analysis**:
  - **Buy Range**: **$XXX-$XXX**
  - **Stop-Loss**: **$XXX**
  - *Dynamic estimates, adjust in real-time with latest market conditions*
- **30-Day Trend Forecast**: (Concise, 3-5 bullet points combining drivers, risks, and overall judgment)
- **Trading Recommendation**: Priority Buy / Wait for Pullback / Not Recommended

---

## Rules (Mandatory Enforcement)

1. **All data must be obtained through search**, guessing and fabrication is prohibited.
2. If data cannot be found after search, mark `[Data Not Available]`, do not force analysis.
3. Yahoo Finance chart link must be correct and clickable.
4. Buy range and stop loss must be calculated according to rules, clearly provide specific prices.
5. **PRICE FORMAT RULE: Always place dollar sign BEFORE the number**:
   - ✅ Correct: `$195-$202`, `$189`
   - ❌ Wrong: `195-202$`, `189$`, `$260-265$`
