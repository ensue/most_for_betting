# Iron Rules

Seven rules. Non-negotiable. No exceptions. No "just this once."

## Axiom: A Lost Bet Is Dead

A bet that lost is a **closed thesis**. The result **invalidated** the idea. Placing the same selection again is a **new bet** — never a "continuation" or "doubling down." "Recovery" framing is a documented trap (chasing losses — treating the next bet as if it will undo the previous one).

There is no such thing as "getting my money back." You are placing a new bet with a new risk budget, and you must go through the full Rule 3 plan + Rule 5 cooldown first.

---

## 1. Pre-Bet Pause

Before placing any bet, open this workspace and talk to AI.
State the thesis. Describe the reasoning. Hear the response.
Minimum 60 seconds between "I like this bet" and "I place it."

**Why:** The compression of "I think" → "I feel" → "I know" happens fast enough to evade self-monitoring. The pause breaks the chain. Research shows even brief delays reduce impulsive betting significantly (Construal Level Theory, Trope & Liberman, 2010).

---

## 2. Max Stake Per Bet

| Phase | Rule |
|-------|------|
| First 200 bets | Flat staking: **____** units (___% of bankroll) per bet, every bet, no exceptions |
| After 200 compliant + calibrated | Quarter Kelly on trailing stats + Brier score validation |

The stake is **the same on every bet** during calibration. No "confidence-based" sizing. No "I'm more sure about this one." Flat. Every. Time.

### Bankroll Model

| Parameter | Value |
|-----------|-------|
| Declared bankroll | ______ (units / currency) |
| Unit size | ______ (1-3% of bankroll) |
| Stake per bet | 1 unit (flat during calibration) |
| Hard stop | If bankroll drops to 50% of starting value, STOP. Re-evaluate strategy before continuing. |

_Fill in during your first session with the AI partner._

**Why:** Escalation always starts with "just a bit more on this one." A fixed flat stake kills it at origin. Variable staking during calibration is emotional noise disguised as edge optimization.

---

## 3. Bet Plan Before Placing

Before placing the bet, tell AI:
- **Selection** (team/player/outcome)
- **Market** (1X2, over/under, handicap, etc.)
- **Odds** (decimal, from which bookmaker)
- **Stake** (must equal 1 unit during calibration)
- **Estimated probability** (your honest assessment, in %)
- **Edge calculation** = estimated probability − implied probability (must be positive)
- **Thesis** (one sentence: why this is a value bet)

AI records it. This becomes the immutable reference for post-settlement review.

### Edge Calculation (mandatory)

For every bet, the user must state their **estimated probability** and demonstrate **positive expected value**:

1. **Implied probability** = 1 / decimal_odds × 100
2. **Your estimated probability** = your honest assessment (%)
3. **Edge** = your_probability − implied_probability
4. **If edge ≤ 0:** this is NOT a value bet. The AI flags it. Place it anyway? Fine, but it's logged as a non-value bet and does not count toward compliant total.

**Example:** Arsenal to win at 2.10 odds. Implied probability = 47.6%. Your estimate = 55%. Edge = +7.4%. This is a value bet.

### Accumulator Rules

Accumulators are **not banned** but carry heavy friction:
- Calculate and display the **compounded bookmaker margin** across all legs
- Each leg must have a stated probability estimate and positive individual edge
- The combined edge must still be positive after margin compounding
- If any leg lacks an edge estimate → the acca is logged as a **recreational bet**, not a value bet
- Maximum 3 legs during calibration phase

**Pre-mortem (before locking plan):** Answer: "What is the scenario where this bet leads to me breaking rules — not just the loss, but what I do in the minutes after?" If you cannot articulate that cascade path, you are not seeing the full risk.

**Why:** A plan spoken out loud to another entity is harder to corrupt than a plan that exists only in your head. The edge calculation forces honest probability assessment instead of "I just have a feeling."

---

## 4. No Chasing

After a loss:
- **Do not** increase stake size on the next bet
- **Do not** place a bet specifically to "recover" the loss
- **Do not** switch to higher-odds markets or accumulators for bigger potential payouts
- **Do not** place more bets than your daily limit allows

Stake stays flat. Selection criteria stay the same. The loss is absorbed by the bankroll — that's what the bankroll is for.

**Why:** Chasing losses is the single highest-damage behavioral pattern in sports betting. It converts a controlled 1-unit loss into a multi-unit cascade. Loss aversion (Kahneman & Tversky) means losses feel ~2× more painful than equivalent gains — the brain demands recovery, and that demand produces the worst bets of your career.

---

## 5. Cooldown After Loss

After a losing bet, return to this workspace before any new bet.
AI logs it. Then — and only then — consider the next bet.

**Minimum cooldown times:**

| Event | Minimum wait |
|-------|-------------|
| Single loss (plan followed) | **30 minutes** from bet settlement |
| Loss with any rule violation | **2 hours** |
| 3 consecutive losses in one session | **Session ends. Mandatory.** |
| 5+ units lost in one day | **24 hours** |

The AI tracks cooldown based on **logged timestamps**, not user self-report. If you appear before cooldown expires, the AI engages with mood, analysis, and journal — **not** with new bet ideas or stake sizing.

**Why:** Serial betting after losses is a consistent value-destruction pattern. Each subsequent bet is less analytical and more compulsive. The cooldown breaks the revenge cycle. Even brief delays improve decision quality (Meichenbaum stress inoculation, 1985).

---

## 6. Daily Bet Limit

During calibration (first 200 compliant bets), maximum **____** bets per day.

This prevents:
- **Overtrading** the bankroll (more bets ≠ more profit when edge is small)
- **Decision fatigue** degrading selection quality
- **Dopamine-seeking** disguised as "finding value"

If you've placed your daily limit and see "one more great bet" — it will still be there tomorrow. Markets don't disappear.

_Fill in during your first session. Recommended: 3-5 bets per day maximum during calibration._

**Why:** Profitable sports bettors typically place 1-5 bets per day. More than that almost always means selection criteria have loosened, not that more value was found.

---

## 7. System Accountability

This system (Cursor + AI partner) has a **real monthly cost**. Budget for it explicitly.

The AI must demonstrably contribute to betting results. This means:
- **Preventing losses** from undisciplined bets (interventions, pattern catches, cooldown enforcement)
- **Maintaining compliance** (verification rate, streak length)
- **Reducing cascade frequency** (the most expensive failure mode)
- **Improving calibration** over time (Brier score trending downward)

**Primary metrics (process, not P/L):**
- CLV (Closing Line Value) — are you consistently getting better odds than the market closes at?
- Calibration accuracy (Brier score) — are your probability estimates honest and improving?
- Compliance rate — what % of bets follow the full Rule 3 plan?
- Streak length — consecutive compliant bets without a rule violation

**P/L is informational context, not the measure of system value.** A month with 3% ROI and perfect compliance is a successful month. A month with 10% ROI from undisciplined lucky accumulators is a failing month — the ROI will revert, the habits won't.

---

## Post-Bet Verification (mandatory procedure)

After a **pre-bet consultation** and **after you place the bet at the bookmaker**, you complete the loop:

1. Tell AI: "Bet placed — verify."
2. State: selection, odds you actually got, actual stake, bookmaker used.
3. AI compares to the **locked plan** recorded in `journal/bets/` for that bet (selection, odds range, stake, market).
4. AI responds with **PASS** or **MISMATCH** and a short checklist:
   - Selection matches plan
   - Odds within reasonable range of plan (allow minor line movement)
   - Stake matches flat unit (no oversizing)
   - Market type matches plan
   - No extra legs added (accumulator creep)

If **MISMATCH**: do not rationalize. Log what happened.

**Why:** Execution drift is subtle — "I got slightly different odds" becomes "I added one more leg" becomes "I put 3 units on because I'm sure." Verification makes drift visible immediately.

---

## Bet Settlement — Recording Outcomes

When a bet settles (win or loss):

1. Tell AI: "Bet settled — [selection] [won/lost]."
2. AI updates `journal/bets/` entry with:
   - **Result** (W / L / void / partial)
   - **P/L in units** (+0.9u for a win at 1.90, -1.0u for a loss)
   - **Closing odds** (if available — for CLV calculation)
   - **Compliance tag** (PASS / FAIL + which rules)
   - **Compliant bet #N / 200** (toward Kelly unlock)
3. AI updates `journal/bets/_summary.md` statistics (strike rate, ROI, CLV, etc.)
4. AI updates `context.md` with current bankroll state

If loss → cooldown rules (Rule 5) apply immediately.
