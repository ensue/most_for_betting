# Betting Command Center — Current Context

Last updated: ___

## Quick Status

| Metric | Value |
|--------|-------|
| Pending bets | 0 |
| Today's bets | 0 / ___ daily limit |
| Compliance streak | 0 |
| Phase | Calibration (first 200 bets, flat staking) |
| Mental state | Not assessed |
| Last session | N/A — system initialized |

## Progression

| Metric | Value |
|--------|-------|
| Total XP | See `system/progression_state.json` |
| Level | See `system/progression_state.json` |
| Session XP breakdown | `tools/progression_report.md` |

## Bankroll

- **Starting bankroll:** ___
- **Current bankroll:** ___
- **Unit size:** ___ (___% of starting bankroll)
- **Units P/L (lifetime):** ___
- **Units P/L (this chapter):** ___

## Key Metrics (rolling)

| Metric | Value |
|--------|-------|
| Total bets | 0 |
| Strike rate | — |
| Average odds | — |
| ROI | — |
| CLV (rolling avg) | — |
| Brier score | — |
| Compliant bets toward Kelly | 0 / 200 |

## Staking Model

- **Current:** Flat staking — 1 unit per bet
- **Transition at:** 200 compliant bets with Brier score < 0.25
- **Target model:** Quarter Kelly on trailing 200-bet statistics

## Active Concerns

None — fresh start.

## Recent Activity

System initialized. No betting activity yet.

## Session Notes

_Updated by AI after each betting conversation._

## Growth Models

| Tool | Report | Regenerate |
|------|--------|------------|
| Projection (deterministic) | `tools/projection_report.md` | `python tools/projection.py` |
| Monte Carlo (5K sims) | `tools/monte_carlo_report.md` | `python tools/monte_carlo.py` |

_Run the tools after setting your parameters in `rules.md` to see projections._

## Reminders for AI

- Read `profile.md` when warning signs appear
- Read sphere summaries in `journal/*/` for deeper context
- First 200 bets: flat staking — do NOT skip to Kelly early
- Watch for: chasing, accumulator binges, in-play impulse, late-night betting, overconfidence after wins
- User prefers structured/visual logs over narrative text
- Workspace-first rule: all betting decisions originate from this workspace
- The rules in `rules.md` are non-negotiable — verify compliance every conversation
- After each settled bet: update stats if changed materially
- Continuously capture notable info from conversations — don't ask, just log
