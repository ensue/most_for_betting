# Continuous AI partner — infrastructure vision

Status: **idea / not implemented**. Describes what a 24/7 or near-24/7 monitoring layer could look like if you outgrow manual Cursor sessions.

## Goals

- **Fresh odds truth:** current odds and line movements available without manual API calls.
- **Lean context:** summaries and alerts, not raw firehoses into the LLM.
- **Fail fast:** if APIs or jobs break, you know immediately — no silent staleness.
- **Separation of concerns:** deterministic odds ingestion vs. interpretive AI — never mix "facts" and "opinions" in one opaque blob.

## Layer 1 — Data plane (no LLM)

| Component | Role |
|-----------|------|
| **Scheduler** | Cron, Windows Task Scheduler, or systemd timer — runs at configured intervals. |
| **Odds ingest worker** | Same logic as `bookmaker/odds.py` (The Odds API): current odds for tracked events. Writes JSON + `odds_snapshot.md`. |
| **Line movement tracker** | Compare current snapshot to previous; emit `line_movements.jsonl` or small `delta.md` (odds shortened, odds drifted, new markets). |
| **CLV calculator** | When events kick off, record closing odds. Compute CLV for all tracked bets automatically. |
| **Retention** | Rotate raw files daily/weekly; keep aggregates longer. |

LLM never calls the bookmaker API directly in this design — only reads **already materialized** files.

## Layer 2 — Summary plane (still mostly deterministic)

| Artifact | Purpose |
|----------|---------|
| `rolling_summary.md` | 30-50 lines: pending bets, pending results, bankroll trajectory, upcoming events with tracked odds. |
| `stats.json` | Strike rate, CLV, Brier score, streak — fed from settled bet log. |
| **Alert rules** | e.g. "odds shortened significantly on a tracked selection", "daily limit approaching", "line moved against user's position" — flag before any AI reads the file. |

Optional: tiny rule engine (Python) — no ML required.

## Layer 3 — AI plane (interpretation)

| Mode | When |
|------|------|
| **On-demand (current)** | Cursor + `context.md` + `odds_snapshot.md` after manual odds check. |
| **Scheduled digest** | Local LLM or API generates a 1-page brief from `rolling_summary.md` + `delta.md` only — not full history. |
| **Interrupt** | Only on alert conditions (Telegram, email, desktop notification) to avoid notification fatigue. |

**Context budget:** LLM input should be `context.md` + `rolling_summary.md` + last `delta.md` + active `journal/bets/*-plan.md` — not entire odds history.

## Incremental path (recommended)

1. **Now:** manual `python bookmaker/odds.py` + Cursor bet planning.
2. **Next:** Task Scheduler runs odds.py every 15-30 min for tracked events; optional `delta.md`.
3. **Later:** alert rules + optional local digest model + auto CLV on event kickoff.
