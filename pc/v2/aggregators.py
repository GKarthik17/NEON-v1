import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


EVENTS_FILE = Path(__file__).parent / "events.jsonl"


def _date_from_ts(ts: str) -> str:
    """
    Extract UTC date (YYYY-MM-DD) from ISO-8601 timestamp.
    """
    return datetime.fromisoformat(ts.replace("Z", "")).date().isoformat()


def aggregate_daily(events_file: Path = EVENTS_FILE) -> dict:
    """
    Aggregate events into daily summaries.

    Returns:
        dict[str, dict] -> date -> summary
    """
    summaries = {}

    if not events_file.exists():
        return summaries

    # Initialize day containers lazily
    def new_day(date):
        return {
            "date": date,
            "execution": {
                "total_sec": 0,
                "sessions": 0
            },
            "tasks": {
                "created": 0,
                "started": 0,
                "completed": 0,
                "failed": 0,
                "success_ratio": None
            },
            "states": {
                "avoidance_count": 0,
                "burnout_count": 0,
                "recovery_total_sec": 0
            },
            "passive": defaultdict(float)
        }

    with open(events_file, "r", encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            date = _date_from_ts(event["ts"])

            if date not in summaries:
                summaries[date] = new_day(date)

            s = summaries[date]
            etype = event["type"]
            data = event.get("data", {})

            # -------- EXECUTION --------
            if etype == "EXECUTION_START":
                s["execution"]["sessions"] += 1

            elif etype == "EXECUTION_END":
                s["execution"]["total_sec"] += int(data.get("duration_sec", 0))

            # -------- TASKS --------
            elif etype == "TASK_CREATED":
                s["tasks"]["created"] += 1

            elif etype == "TASK_STARTED":
                s["tasks"]["started"] += 1

            elif etype == "TASK_COMPLETED":
                s["tasks"]["completed"] += 1

            elif etype == "TASK_FAILED":
                s["tasks"]["failed"] += 1

            # -------- STATES --------
            elif etype == "AVOIDANCE_ENTERED":
                s["states"]["avoidance_count"] += 1

            elif etype == "BURNOUT_ENTERED":
                s["states"]["burnout_count"] += 1

            elif etype == "RECOVERY_END":
                s["states"]["recovery_total_sec"] += int(data.get("duration_sec", 0))

            # -------- PASSIVE --------
            elif etype == "PASSIVE_UPDATE":
                signal = data.get("signal")
                delta = float(data.get("delta", 0))
                if signal:
                    s["passive"][signal] += delta

    # Finalize ratios
    for s in summaries.values():
        completed = s["tasks"]["completed"]
        failed = s["tasks"]["failed"]
        denom = completed + failed
        s["tasks"]["success_ratio"] = (
            round(completed / denom, 2) if denom > 0 else None
        )
        s["passive"] = dict(s["passive"])  # freeze defaultdict

    return summaries
