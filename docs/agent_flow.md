# Agent Flow Spec

## Pipeline

```text
[User Query]
   -> [Intent Parser]
   -> [Data Fetchers: Market / News / Filings / On-chain / ETF]
   -> [Normalizer + Deduper]
   -> [Importance Scoring]
   -> [Summarizer + Interpreter]
   -> [Final Report + Q&A Memory]
```

## Pseudo Logic

1. Parse query
2. Resolve target assets: default = ETH, BMNR
3. Pull data for the requested window (default 24h)
4. Score each event/item
5. Keep top-ranked items
6. Generate:
   - quick brief (<= 10 bullets)
   - deep dive (narrative + scenario)
7. Save context for follow-up questions

## Scoring Example

`score = 0.35*impact + 0.25*credibility + 0.2*timeliness + 0.2*market_reaction`

- impact: price/volume move magnitude
- credibility: source trust tier
- timeliness: recency
- market_reaction: correlated move confirmation

## Q&A Memory

- store fields:
  - `last_assets`
  - `last_time_window`
  - `last_report_type`
  - `open_questions`

- follow-up handling:
  - "그럼 BMNR은?" -> inherits last_time_window
  - "일주일 기준으로 다시" -> overrides time window

