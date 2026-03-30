# Source of truth — bankroll, staking, and intervention math

Universal layout: **no hardcoded currency amounts in AI rules or `flow.md`**. Forks read their own `rules.md`; the public template stays anonymous.

## Priority (highest wins)

1. **`rules.md`** — human-readable authority for **phase**, **unit size**, **bankroll**, and how stake is defined. Always read this.
2. **`context.md`** — current bankroll state, updated after each session.
3. **`journal/bets/_summary.md`** — rolling stats (strike rate, ROI, CLV, Brier score).

## What the AI must do

- **Staking / Rule 2:** Read **`rules.md`** for flat stake amount. During calibration: 1 unit per bet, no exceptions. After 200 compliant bets: Quarter Kelly.
- **Intervention (damage report):** Use **only** figures from **journal entries**, **`context.md`**, and **`_summary.md`** — never invented round numbers. Placeholders in docs are `[UNITS_LOST]`, `[BANKROLL]`, `[N]` — never literal amounts in shared files.
- **Edge calculation:** Implied probability = 1/odds. Edge = user's estimate − implied. Must be positive for a value bet.
