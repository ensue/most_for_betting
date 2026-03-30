"""
MOST betting progression scoring.

Process-first scoring: compliance, analysis quality, and execution hygiene.
P/L is context only (not a primary XP source).

Reads:
  - context.md — session signals
  - journal/bets/_summary.md — betting stats and compliance

Data root `bookmaker/data/` exists for bookmaker exports; this scorer does not read JSON there.

Usage:
    python tools/progression.py                  # normal run (idempotent per day)
    python tools/progression.py --force           # skip same-day guard
    python tools/progression.py --coach -10       # apply bounded coach adjustment
    python tools/progression.py --dry-run         # preview without writing files
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM_DIR = ROOT / "system"
JOURNAL_BETS_SUMMARY = ROOT / "journal" / "bets" / "_summary.md"
CONTEXT_PATH = ROOT / "context.md"

STATE_PATH = SYSTEM_DIR / "progression_state.json"
REPORT_PATH = Path(__file__).resolve().parent / "progression_report.md"

LEVEL_THRESHOLDS = [0, 120, 280, 480, 730, 1030, 1380, 1780, 2230, 2730]
LEVEL_TITLES = [
    "Initiate",
    "Initiate",
    "Structured Bettor",
    "Structured Bettor",
    "Process Guardian",
    "Process Guardian",
    "Edge Hunter",
    "Edge Hunter",
    "Discipline Architect",
    "Discipline Architect",
]


@dataclass
class ScoreEvent:
    key: str
    xp: int
    reason: str


def read_json(path: Path, default: dict | list) -> dict | list:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_int(pattern: str, text: str, default: int = 0) -> int:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return default
    try:
        return int(m.group(1))
    except ValueError:
        return default


def current_level(total_xp: int) -> int:
    if total_xp < 0:
        return 1
    if total_xp < LEVEL_THRESHOLDS[-1]:
        for i in range(len(LEVEL_THRESHOLDS) - 1):
            if LEVEL_THRESHOLDS[i] <= total_xp < LEVEL_THRESHOLDS[i + 1]:
                return i + 1
        return len(LEVEL_THRESHOLDS)
    extra = total_xp - LEVEL_THRESHOLDS[-1]
    return 10 + (extra // 550)


def next_level_threshold(level: int) -> int:
    if level < 10:
        return LEVEL_THRESHOLDS[level]
    return LEVEL_THRESHOLDS[-1] + (level - 9) * 550


def title_for_level(level: int) -> str:
    if level <= len(LEVEL_TITLES):
        return LEVEL_TITLES[level - 1]
    return "System Executor"


def clamp(n: int, low: int, high: int) -> int:
    return max(low, min(high, n))


def compute_analysis_xp(context_text: str, bets_summary_text: str) -> tuple[int, str]:
    """0–40 XP from edge / probability / research / scenario language."""
    score = 0
    reasons: list[str] = []
    lower = (context_text + "\n" + bets_summary_text).lower()

    if re.search(r"\bedge\b|\+ev|expected value|value bet", lower):
        score += 10
        reasons.append("edge/value language")
    if re.search(r"probability|implied prob|implied odds|brier|calibrat", lower):
        score += 8
        reasons.append("probability/calibration language")
    if re.search(r"stat|form|xg|model|research|sample|injury|lineup", lower):
        score += 8
        reasons.append("research/stats context")
    if "if " in lower and "then" in lower:
        score += 5
        reasons.append("scenario branching (if/then)")
    if re.search(r"invalidat|falsif|thesis|contradict|what changes", lower):
        score += 5
        reasons.append("thesis invalidation / falsifiability")
    if re.search(r"closing line|clv|sharp|closing odds", lower):
        score += 4
        reasons.append("CLV / market efficiency language")

    score = clamp(score, 0, 40)
    reason = ", ".join(reasons) if reasons else "no strong analysis signals in context/summary"
    return score, reason


def _has_pre_bet_pause(context_lower: str) -> bool:
    if "pre-bet" in context_lower or "pre bet" in context_lower:
        return True
    if "plan" in context_lower:
        return True
    return False


def _bet_plan_field_count(context_lower: str) -> int:
    n = 0
    if re.search(r"\bselection\b|\bpick\b|\bbacking\b|\blean\b|\bmarket\b", context_lower):
        n += 1
    if re.search(r"\bodds\b|@\s*[\d.]+|decimal odds", context_lower):
        n += 1
    if re.search(r"\bprobability\b|implied prob|estimated prob|p\(\s*win", context_lower):
        n += 1
    if re.search(r"\bedge\b|\+ev|expected value|ev\b", context_lower):
        n += 1
    if re.search(r"\bthesis\b|\bbecause\b|reasoning|invalidat", context_lower):
        n += 1
    return n


def _has_post_bet_verification(combined_lower: str) -> bool:
    has_v = "verify" in combined_lower or "verification" in combined_lower
    has_pass = "pass" in combined_lower
    return has_v and has_pass


def _has_cooldown_respected(combined_lower: str) -> bool:
    if "cooldown" in combined_lower or "cool down" in combined_lower or "cooling off" in combined_lower:
        return True
    if "wait" in combined_lower and ("loss" in combined_lower or "lost" in combined_lower):
        return True
    return False


def _has_daily_limit_honored(combined_lower: str) -> bool:
    if "daily limit" not in combined_lower and "daily bet" not in combined_lower:
        return False
    if re.search(r"daily (?:bet )?limit.*(?:honored|respected|within|under|compliant|not exceeded)", combined_lower):
        return True
    if "under the limit" in combined_lower or "within limit" in combined_lower or "stayed within" in combined_lower:
        return True
    return False


def _has_accumulator_resistance(combined_lower: str) -> bool:
    acca = bool(re.search(r"accumulator|acca\b|parlay|multi\b", combined_lower))
    if not acca:
        return False
    resist = bool(
        re.search(
            r"resist|declined|avoided|skipped|no acca|singles only|single bet|"
            r"chose single|stuck to single|not (?:the )?(?:acca|parlay)",
            combined_lower,
        )
    )
    return resist


def _has_inplay_resistance(combined_lower: str) -> bool:
    live = bool(re.search(r"in-play|in play|live bet|live betting|in-play impulse", combined_lower))
    if not live:
        return False
    resist = bool(re.search(r"declined|resist|skipped|no live|avoided live|passed on live", combined_lower))
    return resist


def _has_session_stop_discipline(combined_lower: str) -> bool:
    risk = bool(re.search(r"risk state|yellow|red (?:risk|state)|stop session|end session|session stop", combined_lower))
    if not risk:
        return False
    stop = bool(re.search(r"stopped|ended|closed (?:the )?app|walked away|shut down", combined_lower))
    return stop


def _has_honest_state_reporting(combined_lower: str) -> bool:
    return bool(re.search(r"\bmood\b|fatigue|tired|sleep|energy|stress|anxious|irritable", combined_lower))


def _has_betting_activity_logged(bets_summary_text: str) -> bool:
    t = bets_summary_text
    n = extract_int(r"\*\*Total (?:bets|trades)\*\*\s*[—:]\s*(\d+)", t, default=0)
    if n > 0:
        return True
    n2 = extract_int(r"Total (?:bets|trades)\s*[:—]\s*(\d+)", t, default=0)
    if n2 > 0:
        return True
    if re.search(r"No (?:trades|bets) recorded|_No trades", t, flags=re.IGNORECASE):
        return False
    if re.search(r"recent closed|last 10|bet log|settled", t, flags=re.IGNORECASE) and re.search(
        r"@\s*[\d.]+|\d+\.\d+\s*stake|units?\b", t, flags=re.IGNORECASE
    ):
        return True
    return False


def score_session(
    context_text: str,
    bets_summary_text: str,
    coach_adjustment: int,
) -> list[ScoreEvent]:
    events: list[ScoreEvent] = []
    combined = context_text + "\n" + bets_summary_text
    combined_lower = combined.lower()
    context_lower = context_text.lower()

    if _has_pre_bet_pause(context_lower):
        events.append(ScoreEvent("pre_bet_pause", 20, "pre-bet or plan discussion detected in context"))

    plan_fields = _bet_plan_field_count(context_lower)
    if plan_fields >= 5:
        events.append(ScoreEvent("bet_plan_completeness", 25, "selection, odds, probability, edge, thesis signals present"))
    elif plan_fields >= 2:
        events.append(ScoreEvent("bet_plan_completeness", 12, "partial plan structure present"))

    if _has_post_bet_verification(combined_lower):
        events.append(ScoreEvent("post_bet_verification", 20, "verification language with PASS noted"))

    if _has_cooldown_respected(combined_lower):
        events.append(ScoreEvent("cooldown_respected", 15, "cooldown / post-loss wait language detected"))

    if _has_daily_limit_honored(combined_lower):
        events.append(ScoreEvent("daily_limit_honored", 10, "daily limit compliance language detected"))

    if _has_accumulator_resistance(combined_lower):
        events.append(ScoreEvent("accumulator_resistance", 15, "accumulator / parlay temptation resisted"))

    if _has_inplay_resistance(combined_lower):
        events.append(ScoreEvent("inplay_resistance", 10, "in-play / live impulse declined"))

    if _has_session_stop_discipline(combined_lower):
        events.append(ScoreEvent("session_stop_discipline", 12, "session stop tied to risk state"))

    if _has_honest_state_reporting(combined_lower):
        events.append(ScoreEvent("honest_state_reporting", 8, "mood / fatigue / state language present"))

    if _has_betting_activity_logged(bets_summary_text):
        events.append(ScoreEvent("activity_logged", 5, "betting activity data present in summary"))

    analysis_xp, analysis_reason = compute_analysis_xp(context_text, bets_summary_text)
    events.append(ScoreEvent("analysis_quality", analysis_xp, analysis_reason))

    coach_adjustment = clamp(coach_adjustment, -15, 15)
    if coach_adjustment != 0:
        direction = "bonus" if coach_adjustment > 0 else "penalty"
        events.append(
            ScoreEvent("coach_adjustment", coach_adjustment, f"{direction} applied within bounded coach lane")
        )

    return events


def summarize_scores(events: list[ScoreEvent]) -> tuple[int, float, float]:
    total_xp = sum(e.xp for e in events)

    compliance_keys = {
        "pre_bet_pause",
        "bet_plan_completeness",
        "post_bet_verification",
        "cooldown_respected",
        "daily_limit_honored",
        "accumulator_resistance",
        "inplay_resistance",
        "session_stop_discipline",
        "honest_state_reporting",
        "activity_logged",
    }
    analysis_keys = {"analysis_quality"}

    compliance_xp = sum(e.xp for e in events if e.key in compliance_keys)
    analysis_xp = sum(e.xp for e in events if e.key in analysis_keys)

    discipline_score = float(clamp(compliance_xp, 0, 100))
    analysis_score = float(clamp(analysis_xp * 2, 0, 100))
    return total_xp, discipline_score, analysis_score


def generate_report(
    ts: str,
    events: list[ScoreEvent],
    earned_xp: int,
    total_xp: int,
    level: int,
    title: str,
    xp_to_next: int,
    discipline_score: float,
    analysis_score: float,
) -> str:
    lines = [
        "# MOST Betting Progression Report",
        "",
        f"Generated: {ts}",
        "",
        "## Session XP",
        "",
        f"**Earned this run** — {earned_xp} XP",
        "",
        "| Event | XP | Reason |",
        "|------|---:|--------|",
    ]
    for event in events:
        lines.append(f"| {event.key} | {event.xp:+d} | {event.reason} |")

    lines.extend(
        [
            "",
            "## Progress",
            "",
            f"**Total XP** — {total_xp}",
            f"**Level** — {level} ({title})",
            f"**XP to next level** — {xp_to_next}",
            f"**Discipline score** — {discipline_score:.0f}/100",
            f"**Analysis score** — {analysis_score:.0f}/100",
            "",
            "## Notes",
            "",
            "- P/L is informational context only; process quality drives XP.",
            "- Coach adjustment lane is bounded at +/-15 XP per run.",
            "",
            "*Run: `python tools/progression.py` after material session updates.*",
        ]
    )
    return "\n".join(lines)


def _context_hash(context_text: str) -> str:
    return hashlib.sha256(context_text.encode("utf-8")).hexdigest()[:16]


def _already_scored_today(history: list[dict], today_date: str, ctx_hash: str) -> bool:
    for entry in reversed(history):
        ts = entry.get("timestamp", "")
        if ts[:10] == today_date and entry.get("context_hash") == ctx_hash:
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="MOST betting progression scoring")
    parser.add_argument("--force", action="store_true", help="Skip same-day idempotency guard")
    parser.add_argument("--coach", type=int, default=0, metavar="N", help="Coach adjustment XP (bounded -15..+15)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    cli = parser.parse_args()

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    today_date = now.strftime("%Y-%m-%d")

    context_text = read_text(CONTEXT_PATH)
    bets_summary_text = read_text(JOURNAL_BETS_SUMMARY)
    state = read_json(STATE_PATH, {})
    if not isinstance(state, dict):
        state = {}

    ctx_hash = _context_hash(context_text)
    history = state.get("history", [])
    if not isinstance(history, list):
        history = []

    if not cli.force and _already_scored_today(history, today_date, ctx_hash):
        print(f"Already scored today ({today_date}) with unchanged context. Use --force to override.")
        return

    coach_adjustment = clamp(cli.coach, -15, 15)
    events = score_session(
        context_text=context_text,
        bets_summary_text=bets_summary_text,
        coach_adjustment=coach_adjustment,
    )

    earned_xp, discipline_score, analysis_score = summarize_scores(events)
    previous_total = int(state.get("total_xp", 0))
    total_xp = max(0, previous_total + earned_xp)
    level = current_level(total_xp)
    next_threshold = next_level_threshold(level)
    xp_to_next = max(0, next_threshold - total_xp)
    title = title_for_level(level)

    old_discipline = float(state.get("discipline_score", 0.0))
    old_analysis = float(state.get("analysis_score", 0.0))
    blended_discipline = round(old_discipline * 0.7 + discipline_score * 0.3, 1)
    blended_analysis = round(old_analysis * 0.7 + analysis_score * 0.3, 1)

    streak_src = bets_summary_text
    history.append(
        {
            "timestamp": now.isoformat(),
            "earned_xp": earned_xp,
            "events": [{"key": e.key, "xp": e.xp, "reason": e.reason} for e in events],
            "discipline_score": discipline_score,
            "analysis_score": analysis_score,
            "balance_total": None,
            "context_hash": ctx_hash,
        }
    )
    history = history[-50:]

    new_state = {
        "schema_version": 1,
        "updated_at": now.isoformat(),
        "total_xp": total_xp,
        "level": level,
        "title": title,
        "xp_to_next_level": xp_to_next,
        "discipline_score": blended_discipline,
        "analysis_score": blended_analysis,
        "compliance_streak": int(
            extract_int(r"\*\*Current streak\*\*\s*[—:]\s*(\d+)", streak_src, default=0)
        ),
        "missions": state.get(
            "missions",
            {"window": "weekly", "completed_this_window": [], "last_reset": None},
        ),
        "badges": state.get("badges", []),
        "history": history,
    }

    report = generate_report(
        ts=ts,
        events=events,
        earned_xp=earned_xp,
        total_xp=total_xp,
        level=level,
        title=title,
        xp_to_next=xp_to_next,
        discipline_score=blended_discipline,
        analysis_score=blended_analysis,
    )

    if cli.dry_run:
        print("--- DRY RUN (no files written) ---")
        print(report)
        print(f"\nWould set total_xp={total_xp}, level={level} ({title})")
        return

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(new_state, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Progression state updated: {STATE_PATH}")
    print(f"Progression report saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()
