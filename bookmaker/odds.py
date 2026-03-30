"""
Odds comparison and CLV tracking via The Odds API.

Fetches current odds for a given sport/event from multiple bookmakers.
Used for:
- Pre-bet odds comparison (find best available price)
- Closing line recording for CLV calculation after settlement
- Market overround calculation

The Odds API free tier: 500 requests/month.
Docs: https://the-odds-api.com/liveAPI/guides/v4/

Usage:
    python bookmaker/odds.py --sport soccer_epl
    python bookmaker/odds.py --sport soccer_epl --event "Arsenal v Chelsea"
    python bookmaker/odds.py --sport soccer_epl --markets h2h,totals
    python bookmaker/odds.py --remaining
    python bookmaker/odds.py --sports

Output:
    bookmaker/data/odds_snapshot.json
    bookmaker/data/odds_snapshot.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

try:
    import requests
except ImportError:
    print("Missing dependency: requests. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
ENV_PATH = ROOT / "vault" / "odds-api.env"

BASE_URL = "https://api.the-odds-api.com/v4"

POPULAR_SPORTS = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_uefa_champs_league",
    "basketball_nba",
    "basketball_euroleague",
    "tennis_atp_french_open",
    "americanfootball_nfl",
    "icehockey_nhl",
    "mma_mixed_martial_arts",
]


def load_api_key() -> str:
    key = os.environ.get("ODDS_API_KEY", "")
    if key:
        return key
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "ODDS_API_KEY":
                return v.strip().strip("\"'")
    return ""


def get_sports(api_key: str) -> list[dict]:
    resp = requests.get(
        f"{BASE_URL}/sports",
        params={"apiKey": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def get_odds(
    api_key: str,
    sport: str,
    regions: str = "uk,eu",
    markets: str = "h2h",
    odds_format: str = "decimal",
) -> tuple[list[dict], int]:
    resp = requests.get(
        f"{BASE_URL}/sports/{sport}/odds",
        params={
            "apiKey": api_key,
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
        },
        timeout=15,
    )
    resp.raise_for_status()
    remaining = int(resp.headers.get("x-requests-remaining", -1))
    return resp.json(), remaining


def calc_overround(outcomes: list[dict]) -> float:
    total = sum(1.0 / o["price"] for o in outcomes if o.get("price", 0) > 0)
    return round((total - 1.0) * 100, 2)


def calc_implied_prob(decimal_odds: float) -> float:
    if decimal_odds <= 0:
        return 0.0
    return round(1.0 / decimal_odds * 100, 2)


def filter_events(events: list[dict], query: str) -> list[dict]:
    q = query.lower()
    return [
        e for e in events
        if q in e.get("home_team", "").lower()
        or q in e.get("away_team", "").lower()
        or q in f"{e.get('home_team', '')} v {e.get('away_team', '')}".lower()
    ]


def generate_snapshot_md(events: list[dict], sport: str, remaining: int) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Odds Snapshot",
        "",
        f"**Sport:** {sport}  ",
        f"**Generated:** {ts}  ",
        f"**API requests remaining:** {remaining}",
        "",
    ]

    if not events:
        lines.append("No events found.")
        return "\n".join(lines)

    for event in events:
        home = event.get("home_team", "?")
        away = event.get("away_team", "?")
        commence = event.get("commence_time", "?")
        lines.append(f"## {home} vs {away}")
        lines.append(f"**Kickoff:** {commence}")
        lines.append("")

        for bookmaker_data in event.get("bookmakers", []):
            bk_name = bookmaker_data.get("title", "?")
            for market in bookmaker_data.get("markets", []):
                market_key = market.get("key", "?")
                outcomes = market.get("outcomes", [])
                overround = calc_overround(outcomes)

                lines.append(f"### {bk_name} — {market_key} (overround: {overround:.1f}%)")
                lines.append("")
                lines.append("| Selection | Odds | Implied Prob |")
                lines.append("|-----------|------|-------------|")
                for o in outcomes:
                    name = o.get("name", "?")
                    price = o.get("price", 0)
                    impl = calc_implied_prob(price)
                    lines.append(f"| {name} | {price:.2f} | {impl:.1f}% |")
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def find_best_odds(events: list[dict]) -> dict[str, dict]:
    """For each outcome across bookmakers, find the best available odds."""
    best: dict[str, dict] = {}
    for event in events:
        event_key = f"{event.get('home_team', '?')} vs {event.get('away_team', '?')}"
        for bk in event.get("bookmakers", []):
            bk_name = bk.get("title", "?")
            for market in bk.get("markets", []):
                for outcome in market.get("outcomes", []):
                    sel_key = f"{event_key} | {outcome['name']}"
                    price = outcome.get("price", 0)
                    if sel_key not in best or price > best[sel_key]["price"]:
                        best[sel_key] = {
                            "event": event_key,
                            "selection": outcome["name"],
                            "price": price,
                            "bookmaker": bk_name,
                            "market": market.get("key", "?"),
                        }
    return best


def _normalize_probs(outcomes: list[dict]) -> dict[str, float]:
    implied: dict[str, float] = {}
    total = 0.0
    for o in outcomes:
        price = float(o.get("price", 0) or 0)
        if price <= 0:
            continue
        p = 1.0 / price
        implied[o.get("name", "?")] = p
        total += p
    if total <= 0:
        return {}
    return {k: (v / total) for k, v in implied.items()}


def _quarter_kelly_fraction(decimal_odds: float, est_prob: float) -> float:
    """
    Quarter-Kelly bet fraction of bankroll.
    est_prob is a decimal probability in [0, 1].
    """
    b = decimal_odds - 1.0
    if b <= 0:
        return 0.0
    q = 1.0 - est_prob
    full_kelly = ((b * est_prob) - q) / b
    if full_kelly <= 0:
        return 0.0
    return full_kelly * 0.25


def generate_research_recommendations(
    events: list[dict],
    bankroll: float,
    max_stake_pct: float,
    min_edge_pct: float,
) -> list[dict]:
    """
    Build recommendations from market consensus:
    1) Remove bookmaker margin per market (normalize implied probs).
    2) Average normalized probabilities across bookmakers -> consensus fair probability.
    3) Score every offered price by EV, edge, and capped quarter-Kelly stake.
    """
    scored: list[dict] = []

    for event in events:
        event_key = f"{event.get('home_team', '?')} vs {event.get('away_team', '?')}"
        markets_grouped: dict[str, list[dict]] = {}

        for bk in event.get("bookmakers", []):
            for market in bk.get("markets", []):
                mk = market.get("key", "?")
                markets_grouped.setdefault(mk, []).append(
                    {
                        "bookmaker": bk.get("title", "?"),
                        "outcomes": market.get("outcomes", []),
                    }
                )

        for market_key, market_books in markets_grouped.items():
            # Consensus fair probability per selection.
            fair_prob_samples: dict[str, list[float]] = {}
            for mb in market_books:
                normalized = _normalize_probs(mb["outcomes"])
                for sel, prob in normalized.items():
                    fair_prob_samples.setdefault(sel, []).append(prob)
            if not fair_prob_samples:
                continue
            fair_probs = {sel: mean(vals) for sel, vals in fair_prob_samples.items() if vals}

            # Score all available offered prices against fair probs.
            for mb in market_books:
                bookmaker = mb["bookmaker"]
                for outcome in mb["outcomes"]:
                    selection = outcome.get("name", "?")
                    odds = float(outcome.get("price", 0) or 0)
                    if odds <= 1:
                        continue
                    est_prob = fair_probs.get(selection)
                    if est_prob is None:
                        continue
                    implied_prob = 1.0 / odds
                    edge_pct = (est_prob - implied_prob) * 100.0
                    ev_per_unit = (est_prob * (odds - 1.0)) - (1.0 - est_prob)
                    kelly_q = _quarter_kelly_fraction(odds, est_prob)
                    kelly_q = min(kelly_q, max_stake_pct / 100.0)
                    stake_units = bankroll * kelly_q

                    if edge_pct < min_edge_pct or ev_per_unit <= 0:
                        continue

                    scored.append(
                        {
                            "event": event_key,
                            "market": market_key,
                            "selection": selection,
                            "bookmaker": bookmaker,
                            "odds": odds,
                            "estimated_probability_pct": round(est_prob * 100.0, 2),
                            "implied_probability_pct": round(implied_prob * 100.0, 2),
                            "edge_pct": round(edge_pct, 2),
                            "ev_per_unit": round(ev_per_unit, 4),
                            "kelly_quarter_fraction_pct": round(kelly_q * 100.0, 2),
                            "recommended_stake_units": round(stake_units, 2),
                        }
                    )

    scored.sort(key=lambda x: (x["ev_per_unit"], x["edge_pct"], x["odds"]), reverse=True)
    return scored


def generate_research_md(
    recommendations: list[dict],
    sport: str,
    bankroll: float,
    max_stake_pct: float,
    min_edge_pct: float,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Market Research and Bet Recommendation",
        "",
        f"**Sport:** {sport}  ",
        f"**Generated:** {ts}  ",
        f"**Bankroll input:** {bankroll:.2f}u  ",
        f"**Stake cap:** {max_stake_pct:.2f}% bankroll  ",
        f"**Min edge filter:** {min_edge_pct:.2f}%",
        "",
        "Method: bookmaker-margin-adjusted market consensus probabilities + EV + capped quarter-Kelly sizing.",
        "",
    ]
    if not recommendations:
        lines.append("No positive-EV bets passed filters.")
        return "\n".join(lines)

    best = recommendations[0]
    lines.extend(
        [
            "## Optimal Bet (Current Snapshot)",
            "",
            f"- **Event:** {best['event']}",
            f"- **Market:** {best['market']}",
            f"- **Selection:** {best['selection']}",
            f"- **Bookmaker:** {best['bookmaker']}",
            f"- **Odds:** {best['odds']:.2f}",
            f"- **Estimated probability:** {best['estimated_probability_pct']:.2f}%",
            f"- **Implied probability:** {best['implied_probability_pct']:.2f}%",
            f"- **Edge:** {best['edge_pct']:.2f}%",
            f"- **EV per 1u stake:** {best['ev_per_unit']:+.4f}u",
            f"- **Recommended stake:** {best['recommended_stake_units']:.2f}u ({best['kelly_quarter_fraction_pct']:.2f}% bankroll)",
            "",
            "## Top 10 Positive-EV Candidates",
            "",
            "| Event | Market | Selection | Bookmaker | Odds | Est. p | Edge | EV/1u | Stake (u) |",
            "|-------|--------|-----------|-----------|------|--------|------|-------|-----------|",
        ]
    )
    for r in recommendations[:10]:
        lines.append(
            f"| {r['event']} | {r['market']} | {r['selection']} | {r['bookmaker']} | "
            f"{r['odds']:.2f} | {r['estimated_probability_pct']:.2f}% | {r['edge_pct']:.2f}% | "
            f"{r['ev_per_unit']:+.4f} | {r['recommended_stake_units']:.2f} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Odds comparison via The Odds API")
    parser.add_argument("--sport", type=str, default="soccer_epl", help="Sport key (e.g. soccer_epl)")
    parser.add_argument("--event", type=str, default=None, help="Filter by team/event name")
    parser.add_argument("--markets", type=str, default="h2h", help="Markets: h2h, totals, spreads (comma-separated)")
    parser.add_argument("--regions", type=str, default="uk,eu", help="Bookmaker regions (comma-separated)")
    parser.add_argument("--sports", action="store_true", help="List all available sports and exit")
    parser.add_argument("--remaining", action="store_true", help="Show remaining API requests and exit")
    parser.add_argument("--recommend", action="store_true", help="Run market research and output optimal bet recommendation")
    parser.add_argument("--bankroll", type=float, default=100.0, help="Bankroll in units for stake sizing")
    parser.add_argument("--max-stake-pct", type=float, default=2.0, help="Maximum stake as percent of bankroll")
    parser.add_argument("--min-edge-pct", type=float, default=0.5, help="Minimum edge (percentage points) to include")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print(
            "No API key found. Set ODDS_API_KEY environment variable or create vault/odds-api.env.\n"
            "Get a free key at https://the-odds-api.com/",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.sports:
        sports = get_sports(api_key)
        print(f"{'Key':<40} {'Group':<25} {'Title'}")
        print("-" * 90)
        for s in sorted(sports, key=lambda x: x.get("group", "")):
            if s.get("active"):
                print(f"{s['key']:<40} {s.get('group', ''):<25} {s.get('title', '')}")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    events, remaining = get_odds(
        api_key=api_key,
        sport=args.sport,
        regions=args.regions,
        markets=args.markets,
    )

    if args.remaining:
        print(f"API requests remaining this month: {remaining}")
        return

    if args.event:
        events = filter_events(events, args.event)

    snapshot_json = {
        "sport": args.sport,
        "markets": args.markets,
        "regions": args.regions,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "api_requests_remaining": remaining,
        "events": events,
    }

    json_path = DATA_DIR / "odds_snapshot.json"
    json_path.write_text(json.dumps(snapshot_json, indent=2, default=str), encoding="utf-8")

    md_content = generate_snapshot_md(events, args.sport, remaining)
    md_path = DATA_DIR / "odds_snapshot.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Found {len(events)} events for {args.sport}")
    if events:
        best = find_best_odds(events)
        print(f"\nBest odds across bookmakers:")
        for sel_key, info in sorted(best.items()):
            print(f"  {info['selection']:<25} {info['price']:.2f}  ({info['bookmaker']})")

    if args.recommend:
        recommendations = generate_research_recommendations(
            events=events,
            bankroll=args.bankroll,
            max_stake_pct=args.max_stake_pct,
            min_edge_pct=args.min_edge_pct,
        )
        research_json = {
            "sport": args.sport,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "bankroll": args.bankroll,
            "max_stake_pct": args.max_stake_pct,
            "min_edge_pct": args.min_edge_pct,
            "recommendations": recommendations,
            "optimal_bet": recommendations[0] if recommendations else None,
        }
        research_json_path = DATA_DIR / "research_recommendation.json"
        research_json_path.write_text(json.dumps(research_json, indent=2), encoding="utf-8")

        research_md = generate_research_md(
            recommendations=recommendations,
            sport=args.sport,
            bankroll=args.bankroll,
            max_stake_pct=args.max_stake_pct,
            min_edge_pct=args.min_edge_pct,
        )
        research_md_path = DATA_DIR / "research_recommendation.md"
        research_md_path.write_text(research_md, encoding="utf-8")

        if recommendations:
            top = recommendations[0]
            print("\nOptimal bet from current market snapshot:")
            print(
                f"  {top['event']} | {top['market']} | {top['selection']} @ {top['odds']:.2f} ({top['bookmaker']})"
            )
            print(
                f"  est p={top['estimated_probability_pct']:.2f}% | edge={top['edge_pct']:.2f}% | "
                f"EV/1u={top['ev_per_unit']:+.4f} | stake={top['recommended_stake_units']:.2f}u"
            )
        else:
            print("\nNo positive-EV recommendation found for this snapshot and filters.")
        print(f"Research JSON saved to {research_json_path}")
        print(f"Research report saved to {research_md_path}")

    print(f"\nAPI requests remaining: {remaining}")
    print(f"Snapshot saved to {json_path}")
    print(f"Report saved to {md_path}")


if __name__ == "__main__":
    main()
