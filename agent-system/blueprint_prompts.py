TRADING_STRATEGY_PROMPT = """
You are an expert quantitative trader and MQL5/PineScript developer.
Design a precise, actionable trading strategy spec for:
- Asset Class: {asset_class}
- Timeframe: {timeframe}
- Strategy Style: {strategy_style}

Include:
1. Technical Indicators & Parameter Settings
2. Exact Long/Short Entry Conditions
3. Stop Loss, Take Profit, and Trailing Stop Rules (Fixed Pip/ATR based)
4. Risk Management Rules (Position sizing & max daily drawdown limit)
5. Execution Pseudocode / Rule Set
"""

ARBITRAGE_PROMPT = """
You are an e-commerce automation and web scraping engineer.
Design an operational arbitrage specification for:
- Source Platform: {source_platform}
- Target Platform: {target_platform}
- Product Category: {category}

Include:
1. Data Extraction Strategy (API vs Web Scraping parameters)
2. Margin & Profitability Logic (Handling platform fees, shipping, taxes)
3. Dynamic Pricing Engine Rules (Threshold triggers for price updates)
4. Inventory Sync Logic & Error Handling (Stock stockout prevention)
5. Automation Execution Pipeline Pseudocode
"""

LEADGEN_PROMPT = """
You are a B2B growth marketer and copywriting strategist.
Build a high-converting B2B lead generation & cold outreach engine for:
- Target Niche: {target_niche}
- Location: {location}
- Offer Summary: {offer_summary}

Include:
1. Prospect Identification & Data Scraping Parameters
2. Cold Email Campaign Sequence (Subject line, Hook, Value Prop, CTA)
3. Follow-up Email Variants (Value-add angle, Urgency angle)
4. Objection Handling Framework
5. Response Handling & CRM Automation Flow
"""
