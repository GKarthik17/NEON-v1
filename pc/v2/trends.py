from typing import List, Dict, Optional


def _avg(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def _trend_count(recent: int, baseline: int) -> str:
    if recent >= baseline + 1:
        return "increasing"
    if recent <= baseline - 1:
        return "decreasing"
    return "stable"


def _trend_duration(recent_avg: Optional[float], baseline_avg: Optional[float]) -> str:
    if baseline_avg is None or baseline_avg == 0 or recent_avg is None:
        return "insufficient_data"

    if recent_avg >= baseline_avg * 1.2:
        return "increasing"
    if recent_avg <= baseline_avg * 0.8:
        return "decreasing"
    return "stable"


def _trend_ratio(recent_avg: Optional[float], baseline_avg: Optional[float]) -> str:
    if recent_avg is None or baseline_avg is None:
        return "insufficient_data"

    if recent_avg >= baseline_avg + 0.10:
        return "increasing"
    if recent_avg <= baseline_avg - 0.10:
        return "decreasing"
    return "stable"


def compute_trends(recent: List[Dict], baseline: List[Dict]) -> Dict[str, str]:
    """
    Compute trend labels comparing recent (last 3 days)
    against baseline (previous 3 days).
    """

    # ---------- Guard ----------
    if len(recent) < 2 or len(baseline) < 2:
        return {
            "execution_trend": "insufficient_data",
            "avoidance_trend": "insufficient_data",
            "burnout_trend": "insufficient_data",
            "recovery_trend": "insufficient_data",
            "task_success_trend": "insufficient_data",
        }

    # ---------- EXECUTION ----------
    exec_recent = _avg([d["execution"]["total_sec"] for d in recent])
    exec_base = _avg([d["execution"]["total_sec"] for d in baseline])
    execution_trend = _trend_duration(exec_recent, exec_base)

    # ---------- AVOIDANCE ----------
    avoid_recent = sum(d["states"]["avoidance_count"] for d in recent)
    avoid_base = sum(d["states"]["avoidance_count"] for d in baseline)
    avoidance_trend = _trend_count(avoid_recent, avoid_base)

    # ---------- BURNOUT ----------
    burn_recent = sum(d["states"]["burnout_count"] for d in recent)
    burn_base = sum(d["states"]["burnout_count"] for d in baseline)
    burnout_trend = _trend_count(burn_recent, burn_base)

    # ---------- RECOVERY ----------
    rec_recent_avg = _avg([
        d["states"]["recovery_total_sec"]
        for d in recent
        if d["states"]["recovery_total_sec"] > 0
    ])
    rec_base_avg = _avg([
        d["states"]["recovery_total_sec"]
        for d in baseline
        if d["states"]["recovery_total_sec"] > 0
    ])
    recovery_trend = _trend_duration(rec_recent_avg, rec_base_avg)

    # ---------- TASK SUCCESS ----------
    succ_recent_avg = _avg([
        d["tasks"]["success_ratio"]
        for d in recent
        if d["tasks"]["success_ratio"] is not None
    ])
    succ_base_avg = _avg([
        d["tasks"]["success_ratio"]
        for d in baseline
        if d["tasks"]["success_ratio"] is not None
    ])
    task_success_trend = _trend_ratio(succ_recent_avg, succ_base_avg)

    return {
        "execution_trend": execution_trend,
        "avoidance_trend": avoidance_trend,
        "burnout_trend": burnout_trend,
        "recovery_trend": recovery_trend,
        "task_success_trend": task_success_trend,
    }
