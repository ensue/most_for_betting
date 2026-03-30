"""
Monte Carlo sports betting simulation.

Runs N random bet sequences to show the RANGE of possible outcomes,
not just the expected value. Answers questions like:
- "What's the probability I reach 200u from 100u?"
- "What's the worst realistic drawdown I should prepare for?"
- "How much variance should I expect even when betting with edge?"

Default parameters come from `journal/bets/bet_stats.json` when you have
compliant settled bets; otherwise the report states clearly that scenario
defaults are used (not measured edge).

Usage:
    python tools/monte_carlo.py
    python tools/monte_carlo.py --bankroll 100 --goal 200 --bets 500 --sims 5000
    python tools/monte_carlo.py --bankroll 100 --goal 200 --stake-pct 2 --strike-rate 50 --avg-odds 1.90
    python tools/monte_carlo.py --ignore-stats-file

Output:
    tools/monte_carlo_report.md
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPORT_PATH = Path(__file__).resolve().parent / "monte_carlo_report.md"
STATS_PATH = Path(__file__).resolve().parent.parent / "journal" / "bets" / "bet_stats.json"
STATS_FILE_REL = "journal/bets/bet_stats.json"

DEFAULT_STRIKE_RATE = 50.0
DEFAULT_AVG_NET_WIN = 0.90
MIN_SAMPLE_BETS_FOR_CONFIDENCE = 30

STREAK_EXAMPLE_LEN = 8
STREAK_PROB_MC_TRIALS = 30_000


@dataclass
class SimResult:
    final_equity: float
    max_drawdown_pct: float
    peak_equity: float
    reached_goal: bool
    longest_losing_streak: int
    bet_count: int


@dataclass(frozen=True)
class ResolvedParams:
    """Strike rate / net win inputs for the simulation after merging file + CLI."""

    strike_rate: float
    avg_net_win: float
    wins: int
    losses: int
    source_kind: str
    cli_override: bool


def load_bet_stats_from_file(path: Path) -> tuple[int, int, float, float]:
    if not path.exists():
        return 0, 0, 0.0, 0.0
    data = json.loads(path.read_text(encoding="utf-8"))
    ct = data.get("compliant_trades", {})
    return (
        int(ct.get("wins", 0)),
        int(ct.get("losses", 0)),
        float(ct.get("sum_net_wins", 0.0)),
        float(ct.get("sum_losses_abs", 0.0)),
    )


def resolve_monte_carlo_params(
    stats_path: Path,
    ignore_stats_file: bool,
    cli_strike_rate: float | None,
    cli_avg_net_win: float | None,
) -> ResolvedParams:
    wins, losses, sum_net_wins, sum_losses_abs = 0, 0, 0.0, 0.0
    if not ignore_stats_file:
        wins, losses, sum_net_wins, sum_losses_abs = load_bet_stats_from_file(stats_path)

    n = wins + losses
    measured = n > 0 and not ignore_stats_file

    if measured:
        strike_rate = wins / n * 100
        avg_net_win = (sum_net_wins / wins) if wins > 0 else DEFAULT_AVG_NET_WIN
        source_kind = "measured"
    else:
        strike_rate = DEFAULT_STRIKE_RATE
        avg_net_win = DEFAULT_AVG_NET_WIN
        if ignore_stats_file:
            source_kind = "defaults_ignore_file"
        else:
            source_kind = "defaults_no_compliant_bets"

    cli_override = cli_strike_rate is not None or cli_avg_net_win is not None
    if cli_strike_rate is not None:
        strike_rate = float(cli_strike_rate)
    if cli_avg_net_win is not None:
        avg_net_win = float(cli_avg_net_win)

    if cli_override:
        if measured and source_kind == "measured":
            source_kind = "measured_cli_override"
        else:
            source_kind = "defaults_cli_override"

    return ResolvedParams(
        strike_rate=strike_rate,
        avg_net_win=avg_net_win,
        wins=wins,
        losses=losses,
        source_kind=source_kind,
        cli_override=cli_override,
    )


def _net_win_std(avg_net_win: float) -> float:
    return max(0.03, avg_net_win * 0.12)


def simulate_one(
    bankroll: float,
    goal: float,
    stake_pct: float,
    strike_rate: float,
    avg_net_win: float,
    net_win_std: float,
    num_bets: int,
) -> SimResult:
    equity = bankroll
    peak = bankroll
    max_dd_pct = 0.0
    reached_goal = False
    losing_streak = 0
    longest_losing = 0

    for _ in range(num_bets):
        stake = equity * (stake_pct / 100.0)
        if random.random() * 100 < strike_rate:
            net_r = max(0.01, random.gauss(avg_net_win, net_win_std))
            equity += stake * net_r
            losing_streak = 0
        else:
            equity -= stake
            losing_streak += 1
            longest_losing = max(longest_losing, losing_streak)

        if equity <= 0:
            equity = 0.0
            break

        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd_pct:
            max_dd_pct = dd

        if equity >= goal and not reached_goal:
            reached_goal = True

    return SimResult(
        final_equity=round(equity, 2),
        max_drawdown_pct=round(max_dd_pct, 1),
        peak_equity=round(peak, 2),
        reached_goal=reached_goal,
        longest_losing_streak=longest_losing,
        bet_count=num_bets,
    )


def run_simulation(
    bankroll: float,
    goal: float,
    stake_pct: float,
    strike_rate: float,
    avg_net_win: float,
    num_bets: int = 100,
    num_sims: int = 5000,
    seed: int | None = None,
) -> list[SimResult]:
    net_win_std = _net_win_std(avg_net_win)
    if seed is not None:
        random.seed(seed)
    return [
        simulate_one(
            bankroll,
            goal,
            stake_pct,
            strike_rate,
            avg_net_win,
            net_win_std,
            num_bets,
        )
        for _ in range(num_sims)
    ]


def percentile(values: list[float], pct: float) -> float:
    s = sorted(values)
    idx = int(len(s) * pct / 100)
    idx = min(idx, len(s) - 1)
    return s[idx]


def estimate_prob_at_least_one_loss_streak(
    num_bets: int,
    streak_len: int,
    strike_rate_pct: float,
    rng: random.Random,
    trials: int = STREAK_PROB_MC_TRIALS,
) -> float:
    """Monte Carlo estimate: P(at least one run of `streak_len` consecutive losses) in `num_bets` i.i.d. bets."""
    p_loss = (100.0 - strike_rate_pct) / 100.0
    hits = 0
    for _ in range(trials):
        cur = 0
        max_streak = 0
        for _ in range(num_bets):
            if rng.random() < p_loss:
                cur += 1
                max_streak = max(max_streak, cur)
            else:
                cur = 0
        if max_streak >= streak_len:
            hits += 1
    return hits / trials * 100.0


def _data_source_section(resolved: ResolvedParams) -> list[str]:
    n = resolved.wins + resolved.losses
    lines: list[str] = [
        "## Data source",
        "",
    ]
    sk = resolved.source_kind
    if sk == "measured":
        lines.append(
            f"**Measured** from `{STATS_FILE_REL}`: **{n}** compliant settled bets "
            f"(**{resolved.wins}** W / **{resolved.losses}** L). Strike rate and average net win on wins come from counts and stored sums."
        )
        if n < MIN_SAMPLE_BETS_FOR_CONFIDENCE:
            lines.append(
                f"**Low sample:** {n} < **{MIN_SAMPLE_BETS_FOR_CONFIDENCE}** — treat headline percentages as **very noisy**."
            )
    elif sk == "measured_cli_override":
        lines.append(
            f"**Baseline from file:** **{n}** compliant settled bets (**{resolved.wins}** W / **{resolved.losses}** L). "
            "**CLI overrides** changed strike rate and/or average net win — see Parameters below."
        )
    elif sk == "defaults_ignore_file":
        lines.append(
            "**Scenario defaults** (`--ignore-stats-file`). **Not** your measured edge."
        )
    elif sk in ("defaults_cli_override",):
        lines.append(
            "**Scenario defaults** with **CLI overrides** — still not measured edge unless your numbers match the story you intend to test."
        )
    else:
        lines.append(
            f"**No compliant sample** in `{STATS_FILE_REL}` (wins + losses = 0). "
            "The Parameters below are **illustrative defaults** only. They do **not** reflect recent rule breaks, cascades, or unlogged bets. "
            f"Update `{STATS_FILE_REL}` when compliant bets settle."
        )
    lines.extend(["", "---", ""])
    return lines


def generate_report(
    bankroll: float,
    goal: float,
    stake_pct: float,
    resolved: ResolvedParams,
    num_bets: int,
    num_sims: int,
    results: list[SimResult],
    streak_example_seed: int,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    strike_rate = resolved.strike_rate
    avg_net_win = resolved.avg_net_win
    avg_decimal_odds = avg_net_win + 1.0

    finals = [r.final_equity for r in results]
    drawdowns = [r.max_drawdown_pct for r in results]
    streaks = [r.longest_losing_streak for r in results]
    goal_reached = sum(1 for r in results if r.reached_goal)
    blown = sum(1 for r in results if r.final_equity <= 0)

    median_final = percentile(finals, 50)
    p10_final = percentile(finals, 10)
    p90_final = percentile(finals, 90)
    p5_final = percentile(finals, 5)
    p95_final = percentile(finals, 95)
    worst_final = min(finals)
    best_final = max(finals)
    avg_final = sum(finals) / len(finals)

    median_dd = percentile(drawdowns, 50)
    p90_dd = percentile(drawdowns, 90)
    p95_dd = percentile(drawdowns, 95)
    worst_dd = max(drawdowns)

    median_streak = percentile(streaks, 50)
    p90_streak = percentile(streaks, 90)
    worst_streak = max(streaks)

    streak_rng = random.Random(streak_example_seed)
    streak_example_pct = estimate_prob_at_least_one_loss_streak(
        num_bets, STREAK_EXAMPLE_LEN, strike_rate, streak_rng
    )

    lines = [
        "# Monte Carlo Betting Simulation",
        "",
        f"Generated: {ts}  ",
        f"Simulations: {num_sims:,} random paths of {num_bets} bets each",
        "",
        *_data_source_section(resolved),
        "## Parameters",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Starting bankroll | {bankroll:.2f} u |",
        f"| Goal bankroll | {goal:.2f} u |",
        f"| Stake per bet | {stake_pct}% of bankroll |",
        f"| Strike rate | {strike_rate:.2f}% |",
        f"| Avg net return on wins | {avg_net_win:.2f} u per unit staked (~decimal odds {avg_decimal_odds:.2f}; std: {_net_win_std(avg_net_win):.3f}) |",
        f"| Loss | full stake lost (−1 u per unit staked) |",
        f"| Bets simulated | {num_bets} |",
        "",
        "## Probability of Reaching Goal",
        "",
        f"**{goal_reached / len(results) * 100:.1f}%** chance of reaching **{goal:.0f} u** within {num_bets} bets.",
        "",
        f"({goal_reached:,} out of {num_sims:,} simulations)",
        "",
        "## Final Bankroll Distribution (units)",
        "",
        "| Percentile | Bankroll |",
        "|------------|----------|",
        f"| Worst case | {worst_final:.2f} u |",
        f"| 5th (bad luck) | {p5_final:.2f} u |",
        f"| 10th | {p10_final:.2f} u |",
        f"| **50th (median)** | **{median_final:.2f} u** |",
        f"| Average | {avg_final:.2f} u |",
        f"| 90th | {p90_final:.2f} u |",
        f"| 95th (good luck) | {p95_final:.2f} u |",
        f"| Best case | {best_final:.2f} u |",
        "",
        f"Bankrolls ruined (equity ≤ 0 u): **{blown}** ({blown/len(results)*100:.1f}%)",
        "",
        "## Drawdown Risk",
        "",
        "Max drawdown from peak bankroll across each simulation:",
        "",
        "| Metric | Drawdown |",
        "|--------|----------|",
        f"| Median max drawdown | {median_dd:.1f}% |",
        f"| 90th percentile | {p90_dd:.1f}% |",
        f"| 95th percentile | {p95_dd:.1f}% |",
        f"| Worst observed | {worst_dd:.1f}% |",
        "",
        "**Translation:** Even betting with edge, expect your bankroll to drop",
        f"~{median_dd:.0f}% from its peak at some point. In unlucky runs, up to {p95_dd:.0f}%.",
        "This is normal variance, not a signal to change process.",
        "",
        "## Losing streaks (simulation vs. independent-outcome math)",
        "",
        "Long losing streaks are **normal** at any strike rate below 100%. The table below is from the **same** Monte Carlo paths (stake compounding, wins/losses as simulated). It describes how long a dry spell can get when bankroll and stake size move together.",
        "",
        "| Metric | Consecutive losses |",
        "|--------|--------------------|",
        f"| Median longest streak | {int(median_streak)} |",
        f"| 90th percentile | {int(p90_streak)} |",
        f"| Worst observed | {worst_streak} |",
        "",
        f"**Independent-outcome context:** At **{strike_rate:.0f}%** strike rate with **{avg_decimal_odds:.2f}** average decimal odds, "
        f"a **{STREAK_EXAMPLE_LEN}**-bet losing streak (losses only; odds do not change i.i.d. loss probability) has approximately **{streak_example_pct:.1f}%** probability "
        f"of occurring **at least once** over **{num_bets}** bets (estimated with {STREAK_PROB_MC_TRIALS:,} sequence draws; seed {streak_example_seed}).",
        "",
        f"**Translation:** You WILL hit {int(median_streak)}-loss streaks routinely in the simulation. "
        f"Occasionally {int(p90_streak)} in a row. That says nothing about edge — it is probability. "
        "The rules exist so you do not treat variance as proof the model is broken.",
        "",
        "---",
        "",
        f"*Inputs: `{STATS_FILE_REL}` (compliant bets). Optional CLI overrides. "
        "`--ignore-stats-file` forces scenario defaults.*",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Monte Carlo sports betting simulation")
    parser.add_argument("--bankroll", type=float, default=100, help="Starting bankroll (units)")
    parser.add_argument("--goal", type=float, default=200, help="Goal bankroll (units)")
    parser.add_argument("--stake-pct", type=float, default=2, help="Stake per bet as %% of bankroll")
    parser.add_argument(
        "--strike-rate",
        type=float,
        default=None,
        help="Override strike rate (%%); omit to use bet_stats.json or scenario defaults",
    )
    avg_group = parser.add_mutually_exclusive_group()
    avg_group.add_argument(
        "--avg-r",
        type=float,
        default=None,
        help="Override average net return on wins (decimal_odds − 1); omit to use bet_stats.json or defaults",
    )
    avg_group.add_argument(
        "--avg-odds",
        type=float,
        default=None,
        help="Override average decimal odds on wins; net return = avg_odds − 1",
    )
    parser.add_argument(
        "--ignore-stats-file",
        action="store_true",
        help="Do not read journal/bets/bet_stats.json; use scenario defaults (unless CLI overrides)",
    )
    parser.add_argument("--bets", type=int, default=100, help="Bets per simulation path")
    parser.add_argument("--sims", type=int, default=5000, help="Number of simulations")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (for reproducibility)")
    args = parser.parse_args()

    cli_avg_net: float | None = None
    if args.avg_odds is not None:
        cli_avg_net = float(args.avg_odds) - 1.0
    elif args.avg_r is not None:
        cli_avg_net = float(args.avg_r)

    resolved = resolve_monte_carlo_params(
        STATS_PATH,
        args.ignore_stats_file,
        args.strike_rate,
        cli_avg_net,
    )

    print(f"Running {args.sims:,} simulations of {args.bets} bets each...")
    results = run_simulation(
        bankroll=args.bankroll,
        goal=args.goal,
        stake_pct=args.stake_pct,
        strike_rate=resolved.strike_rate,
        avg_net_win=resolved.avg_net_win,
        num_bets=args.bets,
        num_sims=args.sims,
        seed=args.seed,
    )

    streak_seed = args.seed if args.seed is not None else 42

    report = generate_report(
        bankroll=args.bankroll,
        goal=args.goal,
        stake_pct=args.stake_pct,
        resolved=resolved,
        num_bets=args.bets,
        num_sims=args.sims,
        results=results,
        streak_example_seed=streak_seed,
    )

    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
