# US Stock Market Financial Data Source Documentation

**Last Updated:** 2026-04-23  
**Document Version:** v2.2

---

## 📋 Overview

This document is an **authoritative data source manual**, recording verified and available financial data sources and access methods. If you find excellent new websites, or if a website is no longer available, please modify it.

**Analysis report output format reference:** `config/meigu2.md`

---

## 📋 Data Collection Objectives

### 1. Macro Policy Data

| Category | Specific Content |
|-----|---------|
| **Major Economy Macro Policies** | US, China, EU, Japan and other major economies policies |
| **Central Bank Financial Data** | Federal Reserve, ECB, PBoC interest rates and policies |
| **Official News** | Official releases from governments, central banks, regulators |
| **Financial Institution Reports** | Goldman Sachs, Morgan Stanley, JPMorgan and other investment bank reports |
| **Listed Company Information** | Earnings reports, public statements, guidance |

---

### 2. Analysis Objectives

| Objective | Description |
|-----|------|
| **US Index Impact** | S&P 500, Nasdaq, Dow Jones analysis |
| **ETF Fund Analysis** | Major ETF capital flows and performance |
| **Weight Stock Impact** | Magnificent Seven and other heavyweight stock analysis |
| **Trading Recommendations** | Buy/sell recommendations based on news flow |
| **Top Ten Stocks Buy Points** | The ten most important stocks and entry/exit points |

---

## 🌐 Recommended Data Sources — Please retrieve from at least 6 authoritative sources

### 1. Federal Reserve (federalreserve.gov) ⭐⭐⭐⭐⭐

**Available Content:**
- ✅ FOMC 2026 committee member list
- ✅ Complete monetary policy framework
- ✅ Future meeting calendar
- ✅ Monetary policy tool details
- ✅ Recent Postings latest release summaries
- ✅ FEDS Notes research papers
- ✅ Beige Book, discount rate meeting minutes
- ✅ Enforcement action announcements, board meeting notices

**Best For:** Official Fed policy, monetary policy, research reports

---

### 2. Bureau of Labor Statistics (BLS, bls.gov) ⭐⭐⭐⭐⭐

**Available Content:**
- ✅ CPI/PPI/NFP latest official data
- ✅ Historical data series
- ✅ Original news releases

**Best For:** Official employment and inflation data

---

### 3. Yahoo Finance (finance.yahoo.com) ⭐⭐⭐⭐⭐

**Available Content:**
- ✅ Latest stock prices, market cap, volume
- ✅ Historical K-line data
- ✅ Earnings calendar

**Best For:** Individual stock market data

---

### 4. CNBC (cnbc.com) ⭐⭐⭐⭐

**Available Content:**
- ✅ Real-time financial news
- ✅ Analyst ratings
- ✅ Market dynamics

**Best For:** Latest market news

---

### 5. Reuters (reuters.com) ⭐⭐⭐⭐⭐

**Available Content:**
- ✅ Authoritative financial news
- ✅ Company announcements
- ✅ Macro data reporting

**Best For:** Authoritative news cross-verification

---

### 6. Trading Economics (tradingeconomics.com) ⭐⭐⭐⭐

**Available Content:**
- ✅ Latest economic data summaries
- ✅ Global macroeconomic news

**Best For:** Global economic data summary cross-verification

---

## Usage Instructions

When generating analysis reports:
1. Select at least 12 authoritative sources from this manual to obtain data
2. Each key data point must be cross-verified with at least two sources
3. Output the final report according to the format specified in `config/meigu2.md`
4. Save reports to: `output/` directory

## Version History

| Version | Date | Update Content |
|-----|------|---------|
| v1.0 | Unknown | Original version |
| v2.0 | 2026-04-16 | Comprehensive reorganization, added multiple website test results |
| v2.1 | 2026-04-17 | Added API access method description |
| v2.2 | 2026-04-23 | Migrated to self-built Python agent framework |
