"""
Bankroll growth projection for sports betting.

Answers: "How many compliant flat-stake bets to reach my goal bankroll?"
Shows three scenarios based on discipline and edge.

Usage:
    python tools/projection.py
    python tools/projection.py --bankroll 100 --goal 200
    python tools/projection.py --bankroll 100 --goal 200 --stake-pct 2 --strike-rate 50 --avg-odds 1.90

Output:
    tools/projection_report.md  (human-readable; link from context.md)
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

REPORT_PATH = Path(__file__).resolve().parent / "projection_report.md"

MILESTONE_BETS = (50, 100, 200, 300, 500)
# Upper bound on bet count per scenario (increase if your edge needs more bets to hit goal)
DEFAULT_MAX_BETS = 10_000


def expected_pnl_per_bet(stake: float, strike_rate: float, avg_odds: float) -> float:
    """Deterministic expected PnL for one bet (flat stake as fraction of bankroll)."""
    p_win = strike_rate / 100.0
    p_loss = (100.0 - strike_rate) / 100.0
    net_win = avg_odds - 1.0
    return stake * (p_win * net_win - p_loss * 1.0)


def simulate_growth(
    bankroll: float,
    goal: float,
    stake_pct: float,
    strike_rate: float,
    avg_odds: float,
    max_bets: int = DEFAULT_MAX_BETS,
) -> list[dict]:
    """Bet-by-bet growth using expected value per bet (deterministic)."""
    equity = bankroll
    history: list[dict] = [{"bet": 0, "equity": round(equity, 4)}]

    for i in range(1, max_bets + 1):
        stake = equity * (stake_pct / 100.0)
        pnl = expected_pnl_per_bet(stake, strike_rate, avg_odds)
        equity += pnl
        equity = round(equity, 4)
        history.append({"bet": i, "equity": equity})
        if equity >= goal:
            break
        if equity <= 0:
            break

    return history


def format_scenario(name: str, history: list[dict], goal: float) -> list[str]:
    """Format a single scenario into markdown lines (units only)."""
    final = history[-1]
    reached = final["equity"] >= goal
    bets_needed = final["bet"] if reached else None

    lines: list[str] = []
    if reached:
        lines.append(f"**{name}:** {bets_needed} bets to reach {goal:g}u")
    else:
        lines.append(
            f"**{name}:** Did not reach {goal:g}u in {final['bet']} bets "
            f"(final: {final['equity']:.2f}u)"
        )

    milestone_lines: list[str] = []
    for m in MILESTONE_BETS:
        if m < len(history):
            milestone_lines.append(f"| {m} | {history[m]['equity']:.2f}u |")

    if milestone_lines:
        lines.append("")
        lines.append("| Bet # | Bankroll (u) |")
        lines.append("|-------|--------------|")
        lines.extend(milestone_lines)
        if reached and bets_needed is not None and bets_needed not in MILESTONE_BETS:
            lines.append(f"| **{bets_needed}** | **{goal:g}u (goal)** |")

    return lines


def generate_report(
    bankroll: float,
    goal: float,
    stake_pct: float,
    strike_rate: float,
    avg_odds: float,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    scenarios = {
        "Disciplined (your stats)": {
            "strike_rate": strike_rate,
            "avg_odds": avg_odds,
        },
        "Sloppy (no edge, recreational)": {
            "strike_rate": 45.0,
            "avg_odds": 1.90,
        },
        "Degenerate (accumulators, chasing)": {
            "strike_rate": 35.0,
            "avg_odds": 2.50,
        },
    }

    lines = [
        "# Bankroll Growth Projection",
        "",
        f"Generated: {ts}",
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Starting bankroll | {bankroll:g}u |",
        f"| Goal bankroll | {goal:g}u |",
        f"| Stake per bet | {stake_pct}% of bankroll |",
        f"| Strike rate (your stats) | {strike_rate}% |",
        f"| Average decimal odds | {avg_odds:.2f} |",
        "",
        "## Scenarios",
        "",
        "Three paths from the same starting bankroll. Staking rule is identical; "
        "**strike rate and average odds** reflect behavior and edge.",
        "",
    ]

    for name, params in scenarios.items():
        history = simulate_growth(
            bankroll=bankroll,
            goal=goal,
            stake_pct=stake_pct,
            strike_rate=params["strike_rate"],
            avg_odds=params["avg_odds"],
        )
        scenario_lines = format_scenario(name, history, goal)
        lines.extend(scenario_lines)
        lines.append("")

    lines.extend(
        [
            "## What This Means",
            "",
            "**Disciplined** — Flat staking at your assumed strike rate and average odds. "
            "This is the compound path when process is stable: same stake fraction every bet, "
            "no tilting, no acca stacking. The number of bets to the goal is pure arithmetic "
            "on edge and stake size.",
            "",
            "**Sloppy** — Recreational baseline: 45% strike at 1.90. Typical slight "
            "underperformance vs breakeven; bankroll expectation drifts down unless you "
            "have real edge somewhere else. No disaster per bet, but no growth story.",
            "",
            "**Degenerate** — Accumulator and chasing profile: higher quoted average odds "
            "with a collapsed strike rate (35%). High odds do not rescue negative "
            "expectation when hit rate collapses; this is how rollercoaster graphs and "
            "bust-outs happen over enough bets.",
            "",
            "---",
            "",
            "*Updated automatically. Run: `python tools/projection.py`*",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bankroll growth projection (flat % staking, deterministic EV per bet)"
    )
    parser.add_argument("--bankroll", type=float, default=100.0, help="Starting bankroll (units)")
    parser.add_argument("--goal", type=float, default=200.0, help="Goal bankroll (units)")
    parser.add_argument("--stake-pct", type=float, default=2.0, help="Stake per bet (%% of bankroll)")
    parser.add_argument("--strike-rate", type=float, default=50.0, help="Strike rate (%%)")
    parser.add_argument("--avg-odds", type=float, default=1.90, help="Average decimal odds")
    args = parser.parse_args()

    report = generate_report(
        bankroll=args.bankroll,
        goal=args.goal,
        stake_pct=args.stake_pct,
        strike_rate=args.strike_rate,
        avg_odds=args.avg_odds,
    )

    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
