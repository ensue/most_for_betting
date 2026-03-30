# MOST — Vibe Betting

**Mental Operating System for Betting** — an AI partner that lives in your IDE for **research, probability estimation, and accountability**.

You bet with your analysis, your bookmaker, your edge. MOST is the layer between your research and your execution: it helps you **structure research**, **compare fair probability to market-implied odds**, **tracks your bets**, **monitors your patterns over time**, and deploys **research-backed psychological tools** at the exact moment your brain tries to override your plan.

> **Vibe Betting** = data first, opinions when you ask, accountability always.

---

## The Problem This Solves

You know what value betting is. You understand bankroll management, implied probability, and why accumulators are -EV. The failure is never the knowledge — it's what happens between the analysis and the execution, and especially what happens in the 10 minutes after a losing bet.

MOST doesn't try to make you a better analyst. It's built for the gap between knowing and doing.

---

## What MOST Does

**Research & probability** — The workspace is a **research lab**, not only a journal. You (and the AI) gather sources, state uncertainty, and produce **fair probability estimates** (point or range) to compare with **implied probability** from odds. Substantive analysis is logged under `research/` (see `research/TEMPLATE.md`). Outcomes feed **Brier score** and calibration in `journal/bets/_summary.md`.

**Odds comparison** — Fetch live odds from 100+ bookmakers via [The Odds API](https://the-odds-api.com/). Compare prices, find best value, and record closing odds for CLV tracking.

**Structured plan-and-verify loop** — State your bet plan (selection, odds, stake, probability estimate, edge calculation, thesis). Lock it. Place at the bookmaker. Report back. The AI compares what you placed to what you planned — PASS or MISMATCH. Not approval — verification.

**Psychological toolkit** — Not generic advice. Research-backed behavioral interventions deployed at trigger moments:

| Tool | What it does | When it fires |
|------|-------------|--------------|
| **Pre-mortem** (Klein, 2007) | "Describe the scenario where this bet leads to you breaking rules" | Before every plan lock |
| **AVE firewall** (Marlatt & Gordon, 1985) | Contains first violation before it cascades into chasing | Between rule break #1 and #2 |
| **Implementation intentions** (Gollwitzer, 1999) | Pre-committed if-then responses to triggers | When trigger pattern matches |
| **Urge surfing** (Marlatt, 1985) | 15-minute structured observation of the betting urge | When activation language detected |
| **Cognitive defusion** (Hayes, 2004) | Separates you from the rationalization ("this can't lose") | When sure-thing language appears |
| **Affect labeling** (Lieberman, 2007) | One-word emotion naming reduces amygdala ~30% | When user is clearly activated |
| **Behavioral chain analysis** (Linehan, 1993) | Maps full vulnerability-to-consequence sequence | After every rule violation |
| **Decision fatigue budget** (Baumeister, 1998) | Counts decisions per session, flags degradation | At 5 and 8 decisions |

**Chapter narratives** — Live trajectory analysis that predicts danger before it arrives. The AI opens with where you're heading, not "how are you feeling?"

**Pattern memory** — Your `profile.md` accumulates behavioral patterns over time. The AI remembers what you forget — not sports patterns, but *your* patterns.

**XP progression** — Gamified discipline tracking. Every compliant bet, every verification, every resisted chasing urge earns XP. Every violation costs. Visible in every response.

**Journal without the cringe** — Bets, mood, reflections, patterns. Structured markdown, not essays. The AI writes it for you from the conversation.

**Growth math** — Monte Carlo (5,000 paths) + deterministic projection. Context for variance and goals, not a lecture.

---

## Seven Rules (template — you customize)

1. **Pre-bet pause** — open workspace, state thesis, hear response
2. **Max stake per bet** — flat staking during calibration, no exceptions
3. **Bet plan before placing** — selection, odds, stake, probability, edge calculation, thesis
4. **No chasing** — stakes don't increase after losses, no revenge bets, no recovery accumulators
5. **Cooldown after loss** — minimum time gaps before next bet
6. **Daily bet limit** — maximum N bets per day during calibration
7. **System accountability** — measured by process quality (CLV, calibration, compliance), not short-term P/L

---

## What Makes This Different

| Other tools | MOST |
|-------------|------|
| Manual bet tracking spreadsheets | AI-powered accountability with pattern detection |
| Generic "don't chase" advice | Research-backed intervention at the exact trigger moment |
| Post-mortem only | Live trajectory prediction + post-mortem |
| Rules as text | Rules enforced through structured verification loop |
| Journal as chore | Journal written for you from conversation |
| Willpower-based | Engineering-based (friction, commitment devices, pre-commitment) |
| P/L as success metric | CLV + calibration + compliance as success metrics |

---

## Who It's For

- You understand value betting and probability — execution and headspace are the hard part
- You've tried discipline before and it worked... until it didn't
- You want **memory + structure** without another app that nags you
- You use **Cursor** and want one workspace that feels like your command deck

---

## Quick Start

```bash
git clone https://github.com/ensue/most_for_betting.git
cd most_for_betting
pip install -r bookmaker/requirements.txt
```

Optionally set up odds API access:
```bash
cp vault/odds-api.env.example vault/odds-api.env
# Edit vault/odds-api.env with your API key from https://the-odds-api.com/
```

Open the folder in **Cursor**. The `.cursor/rules/betting-partner.mdc` tells the AI how MOST works — odds checking, plan verification, pattern detection, psychological interventions.

Optional — growth simulation:
```bash
python tools/monte_carlo.py
python tools/projection.py
```

See [`SETUP.md`](SETUP.md) for full setup and configuration.

---

## Layout

```
.cursor/rules/betting-partner.mdc  <- AI operating manual (Cursor loads automatically)
context.md                         <- rolling state — AI reads first every session
rules.md                           <- your rules (template — customize)
profile.md                         <- behavioral patterns (builds over time)
system/
  flow.md                          <- deterministic processing pipeline
  progression.md                   <- XP system design
  progression_state.json           <- current XP/level
bookmaker/
  odds.py                          <- The Odds API -> odds comparison + CLV
  README.md                        <- how to set up odds API access
research/                          <- structured thesis + fair probability vs market
  TEMPLATE.md                      <- one format for research notes
journal/
  bets/                            <- bet plans + outcomes
  chapters/                        <- live trajectory + postmortems
  reflections/                     <- analysis, notes, implementation intentions
  mood/                            <- energy / headspace (AI logs implicitly)
  patterns/                        <- behavioral patterns + chain analyses
  slips/                           <- bet slip screenshots
tools/
  monte_carlo.py                   <- 5K path simulation
  projection.py                    <- deterministic compound growth
  progression.py                   <- XP calculator
vault/                             <- API keys (gitignored)
```

---

## Key Metrics

| Metric | What it measures | Why it matters |
|--------|-----------------|----------------|
| **CLV** (Closing Line Value) | Did you get better odds than the closing line? | Single strongest predictor of long-term profitability |
| **Brier Score** | Are your probability estimates calibrated? | Honest estimation = sustainable edge |
| **Strike Rate** | What % of bets win? | Context alongside average odds |
| **ROI** | Profit / total staked | The bottom line (but meaningless under ~500 bets) |
| **Compliance Rate** | What % of bets follow the full plan? | Process quality = edge sustainability |

---

## Philosophy

MOST is not "AI that picks winners for you." You research. You estimate probabilities. MOST is the layer that **structures that research**, **surfaces edge vs the market**, and is the accountability layer: it remembers your patterns when you forget them, deploys psychological tools when your brain is trying to override your plan, and makes the concrete cost of breaking rules viscerally clear — using your own numbers, your own history, your own words from when you were thinking clearly.

The vibe: your future self and your AI partner are looking at the same facts. Not the story you half-remember at 1 AM after three losing bets.

---

## License

[MIT](LICENSE)
