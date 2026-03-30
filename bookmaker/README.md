# Bookmaker — Odds & CLV Tracking

## Odds comparison

`odds.py` fetches live odds from 100+ bookmakers via [The Odds API](https://the-odds-api.com/).

**Free tier:** 500 requests/month — enough for a few checks per day.

### Setup

1. Get an API key at [the-odds-api.com](https://the-odds-api.com/)
2. Create `vault/odds-api.env`:
   ```
   ODDS_API_KEY=your_key_here
   ```

### Usage

```bash
python bookmaker/odds.py --sports                          # list all sports
python bookmaker/odds.py --sport soccer_epl                # EPL odds
python bookmaker/odds.py --sport soccer_epl --event "Arsenal"  # filter by team
python bookmaker/odds.py --sport soccer_epl --markets h2h,totals  # multiple markets
python bookmaker/odds.py --remaining                       # check API quota
python bookmaker/odds.py --sport soccer_epl --recommend --bankroll 100 --max-stake-pct 2
```

### Outputs (`bookmaker/data/`)

| File | Purpose |
|------|---------|
| `odds_snapshot.json` | Raw odds data from API |
| `odds_snapshot.md` | Human-readable odds comparison with overround |
| `research_recommendation.json` | EV/edge-scored candidate bets + optimal bet |
| `research_recommendation.md` | Human-readable research report with recommended stake |

### Research + optimal bet recommendation

`--recommend` runs a market-research pass directly from bookmaker prices:
- Removes overround per bookmaker market
- Builds consensus fair probabilities from all available books
- Scores each offered outcome by edge and expected value
- Calculates capped quarter-Kelly stake sizing
- Returns a single **optimal bet** plus top candidates

This is an evidence-based recommendation from market data, not a certainty guarantee.

### CLV (Closing Line Value) tracking

CLV is the single strongest predictor of long-term betting profitability. It measures whether you consistently get better odds than the closing line.

**Workflow:**
1. Before placing a bet: check odds with `odds.py`, record in your bet plan
2. After the event starts (market closes): check closing odds
3. CLV = (odds_taken / closing_odds) − 1
4. Positive CLV over 500+ bets = strong evidence of genuine edge

The AI tracks CLV in `journal/bets/_summary.md` and flags trends.

### Without an API key

The system works without an API key. You manually provide odds from your bookmaker when discussing bets with the AI. The API adds:
- Cross-bookmaker comparison (find best price)
- Automated overround calculation
- Closing line tracking for CLV

## Bet entry

Unlike exchange trading, bookmaker bets are logged **manually through conversation**:

1. Tell the AI your bet plan (selection, odds, stake, thesis, probability, edge)
2. AI locks the plan in `journal/bets/`
3. Place the bet at your bookmaker
4. Tell the AI what you actually placed
5. AI verifies PASS/MISMATCH

This manual loop is intentional — it creates friction between impulse and execution.
