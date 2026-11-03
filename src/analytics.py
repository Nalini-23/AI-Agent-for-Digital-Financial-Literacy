"""
Analytics module – tracks topic usage, language usage, scam checks,
and thumbs-up/down feedback. All stored in a lightweight JSON file.
Thread-safe with a file lock via a simple in-memory dict (single-process).
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock

_LOCK = Lock()
_DB_PATH = Path(os.getenv("ANALYTICS_PATH", "./data/analytics.json"))


def _load() -> dict:
    if _DB_PATH.exists():
        try:
            with open(_DB_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "topics": {},
        "languages": {},
        "scam_checks": 0,
        "scam_risk_levels": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "feedback": {"thumbs_up": 0, "thumbs_down": 0},
        "total_queries": 0,
        "sessions": 0,
        "known_sessions": [],
    }


def _save(db: dict) -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def record_query(topic: str | None, language: str, session_id: str) -> None:
    with _LOCK:
        db = _load()
        db["total_queries"] = db.get("total_queries", 0) + 1
        t = topic or "General"
        db["topics"][t] = db["topics"].get(t, 0) + 1
        db["languages"][language] = db["languages"].get(language, 0) + 1
        known = db.get("known_sessions", [])
        if session_id not in known:
            known.append(session_id)
            db["known_sessions"] = known[-500:]   # cap at 500
            db["sessions"] = db.get("sessions", 0) + 1
        _save(db)


def record_scam_check(risk_level: str) -> None:
    with _LOCK:
        db = _load()
        db["scam_checks"] = db.get("scam_checks", 0) + 1
        rl = risk_level if risk_level in ("HIGH", "MEDIUM", "LOW") else "LOW"
        db.setdefault("scam_risk_levels", {"HIGH": 0, "MEDIUM": 0, "LOW": 0})
        db["scam_risk_levels"][rl] = db["scam_risk_levels"].get(rl, 0) + 1
        _save(db)


def record_feedback(sentiment: str) -> None:
    """sentiment: 'up' or 'down'"""
    with _LOCK:
        db = _load()
        fb = db.setdefault("feedback", {"thumbs_up": 0, "thumbs_down": 0})
        if sentiment == "up":
            fb["thumbs_up"] = fb.get("thumbs_up", 0) + 1
        else:
            fb["thumbs_down"] = fb.get("thumbs_down", 0) + 1
        _save(db)


def get_stats() -> dict:
    with _LOCK:
        db = _load()
    topics = db.get("topics", {})
    languages = db.get("languages", {})
    feedback = db.get("feedback", {"thumbs_up": 0, "thumbs_down": 0})
    scam_rl = db.get("scam_risk_levels", {"HIGH": 0, "MEDIUM": 0, "LOW": 0})

    total_fb = feedback.get("thumbs_up", 0) + feedback.get("thumbs_down", 0)
    satisfaction = round(
        feedback.get("thumbs_up", 0) / total_fb * 100, 1
    ) if total_fb else 0

    return {
        "total_queries": db.get("total_queries", 0),
        "total_sessions": db.get("sessions", 0),
        "scam_checks": db.get("scam_checks", 0),
        "topics": dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)),
        "languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
        "feedback": {**feedback, "satisfaction_pct": satisfaction},
        "scam_risk_levels": scam_rl,
    }
