# MOST Betting — First-Time Setup

## Prerequisites

- [Cursor IDE](https://cursor.sh) with an AI-enabled subscription
- Python 3.10+
- A sports betting account at any bookmaker (the system tracks bets manually — no bookmaker API required)

## Step 1 — Clone and open

```bash
git clone https://github.com/ensue/prediction-market.git
cd prediction-market
```

Open the folder as a workspace in Cursor IDE.

## Step 2 — Install Python dependencies

```bash
pip install -r bookmaker/requirements.txt
```

## Step 3 — Set up odds API (optional but recommended)

The Odds API provides live odds from 100+ bookmakers for odds comparison and CLV tracking.

1. Get a free API key at [the-odds-api.com](https://the-odds-api.com/) (500 requests/month on free tier)
2. Copy the example env file and add your key:

```bash
cp vault/odds-api.env.example vault/odds-api.env
```

3. Edit `vault/odds-api.env` with your actual API key

Test it:
```bash
python bookmaker/odds.py --sports          # list available sports
python bookmaker/odds.py --sport soccer_epl  # fetch EPL odds
```

**Without an API key:** The system works fine. You manually provide odds from your bookmaker. The odds API adds value comparison and automated CLV tracking.

## Step 4 — Start your first session

Open a conversation in Cursor. The AI will:
1. Run the Monte Carlo simulation
2. Read your current state files
3. Present a status block
4. Guide you through initial configuration

In this first session, you'll agree on:

| Parameter | Description | Example |
|---|---|---|
| Declared bankroll | Total amount committed to betting | 500 units / £500 |
| Unit size | Fixed stake per bet (1-3% of bankroll) | 1 unit = £5 |
| Daily bet limit | Max bets per day during calibration | 3-5 bets |
| Primary sports | Which sports/leagues you bet on | EPL, La Liga |
| Goal | Target bankroll | 1000 units |

The AI fills in `rules.md` and `context.md` with your numbers and generates growth projections.

## Step 5 — Build your profile

`profile.md` starts blank. The AI builds it from conversations over time — your patterns, triggers, cognitive style, what works and what doesn't. You can also fill in the core facts section yourself during the first session.

Be honest. This file exists so the AI can catch your patterns, not judge you.

## Step 6 — Initialize your own git branch

The template ships on `main`. For your personal use:

```bash
git checkout -b develop
git add .
git commit -m "Personal MOST Betting setup"
```

## What happens next

- **Before every bet:** open Cursor, talk to the AI, state your plan with edge calculation
- **After placing a bet:** tell the AI "bet placed — verify" with the actual details
- **When a bet settles:** tell the AI the result for tracking
- **After every session:** the AI updates your journal, context, and summaries automatically
- **After 200 compliant bets with proven calibration:** the system transitions from flat staking to Quarter Kelly

## File structure

```
├── .cursor/rules/betting-partner.mdc  ← AI operating manual
├── context.md                         ← AI loads first every session
├── rules.md                           ← your iron rules
├── profile.md                         ← psychological profile (AI builds over time)
├── bookmaker/
│   ├── odds.py                        ← The Odds API integration
│   └── data/                          ← odds snapshots (gitignored)
├── journal/
│   ├── bets/                          ← bet plans + outcomes
│   ├── reflections/                   ← sports analysis, research notes
│   ├── mood/                          ← emotional state tracking
│   ├── patterns/                      ← behavioral pattern observations
│   └── slips/                         ← bet slip screenshots
├── tools/
│   ├── monte_carlo.py                 ← probability simulation
│   ├── projection.py                  ← deterministic growth model
│   └── progression.py                 ← XP calculator
├── vault/                             ← API keys (gitignored)
└── ideas/                             ← future experiments
```

## Betting workflow

```
1. Research → Form thesis → Estimate probability
2. Open Cursor → State plan to AI → Edge calculation
3. AI verifies rules → Pre-mortem → Lock plan
4. Place bet at bookmaker → Report back → AI verifies execution
5. Bet settles → Report result → AI logs and updates stats
6. Repeat (within daily limit)
```

The AI handles all journaling, pattern tracking, XP, and context updates. Your job is to research, estimate probabilities honestly, and follow the process.
