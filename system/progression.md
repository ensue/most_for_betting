# MOST Betting Progression System

This system tracks quality betting progress in a tangible way.
It rewards discipline, analysis quality, and process hygiene.
It does not reward random short-term P/L noise.

## Philosophy

- Process quality is the core signal.
- Rule compliance has highest weight.
- P/L is informational context, not primary XP driver.
- Calibration accuracy is a key skill metric.
- Exceptional learning and exceptional discipline get extra credit.

## XP Categories

### 1) Compliance XP (highest weight)

- Pre-bet pause respected and plan discussed: +20 XP
- Bet plan completeness:
  - Selection present: +5 XP
  - Odds recorded: +5 XP
  - Estimated probability stated: +8 XP
  - Edge calculation shown: +10 XP
  - Thesis present (one sentence): +5 XP
- Post-bet verification performed: +20 XP
- Cooldown respected after a loss (when applicable): +15 XP
- Daily bet limit honored: +10 XP

### 2) Analysis Quality XP

Scored from 0 to 40 per meaningful bet review:

- Edge clarity (probability estimate vs implied, explicit edge): 0-10
- Research depth (stats cited, form considered, context): 0-8
- Scenario quality (if/then branches, what invalidates the thesis): 0-8
- Calibration honesty (probability not inflated to justify bet): 0-8
- Coherence (clean, falsifiable reasoning, no hand-waving): 0-6

### 3) Behavior XP

- Honest state reporting (mood/energy/fatigue): +8 XP
- Session stop discipline when yellow/red risk state: +12 XP
- Accumulator resistance (chose singles over acca when tempted): +15 XP
- In-play resistance (declined live bet impulse): +10 XP
- Daily limit honored after seeing "one more good bet": +10 XP

## Penalties

- Chasing after loss (increased stake or rapid re-bet): -50 XP
- New bet without pre-bet pause: -40 XP
- Accumulator placed without edge calculation on each leg: -40 XP
- In-play impulse bet (no pre-game analysis): -35 XP
- Stake exceeding flat unit during calibration: -60 XP
- Bet placed during cooldown period: -50 XP
- Daily limit exceeded: -30 XP

## Coach Adjustment Lane (bounded)

The coach may apply a small bounded adjustment:

- `coach_adjustment_xp` in range [-15, +15] per session
- Use positive adjustment for:
  - Novel high-quality self-correction
  - Unusually honest probability recalibration
  - Repeated discipline under emotional pressure
  - Excellent CLV on a bet (evidence of genuine edge)
- Use negative adjustment for soft but visible process drift not captured by hard rules.
- Every adjustment must include a short reason in the report.

## Level Curve

Non-linear progression (harder over time):

- Level 1: 0 XP
- Level 2: 120 XP
- Level 3: 280 XP
- Level 4: 480 XP
- Level 5: 730 XP
- Level 6: 1,030 XP
- Level 7: 1,380 XP
- Level 8: 1,780 XP
- Level 9: 2,230 XP
- Level 10: 2,730 XP

Above level 10, each new level requires +550 XP.

## Titles and Milestones

- Level 1-2: Initiate
- Level 3-4: Structured Bettor
- Level 5-6: Process Guardian
- Level 7-8: Edge Hunter
- Level 9-10: Discipline Architect
- Level 11+: System Executor

## Weekly Missions (process-first)

- 3 complete bet plans with full edge calculation
- 2 post-bet verifications
- 0 chasing violations
- At least 1 session ended intentionally due to fatigue/risk state
- Record closing odds on at least 2 settled bets (CLV tracking)

Each completed mission: +25 XP.

## Data Sources

Primary:
- `journal/bets/_summary.md`
- `journal/bets/bet_stats.json`
- `context.md`

Outputs:
- `system/progression_state.json`
- `tools/progression_report.md`

## Operating Notes

- This is a quality tracking system, not betting permission.
- XP should reflect repeatable behavior, not luck.
- If scoring feels noisy, tighten evidence thresholds before changing weights.
- **AI accountability:** The Cursor partner must **update** `progression_state.json` on substantive sessions — **not** leave totals frozen while `journal/` records incidents. Run `tools/progression.py` for baseline scoring, then **append manual penalty/bonus lines** when hard penalties apply.
