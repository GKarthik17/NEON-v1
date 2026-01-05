def format_summary(summary: dict) -> list[str]:
    """
    Format a daily summary into clean, human-readable lines.
    Presentation only.
    """
    lines = []

    lines.append(f"DATE: {summary['date']}")

    exec_min = summary["execution"]["total_sec"] // 60
    exec_sessions = summary["execution"]["sessions"]
    lines.append(f"EXECUTION: {exec_min} min ({exec_sessions} sessions)")

    done = summary["tasks"]["completed"]
    failed = summary["tasks"]["failed"]
    ratio = summary["tasks"]["success_ratio"]
    ratio_txt = f"{int(ratio * 100)}%" if ratio is not None else "N/A"
    lines.append(f"TASKS: {done} done / {failed} failed ({ratio_txt})")

    lines.append(f"AVOIDANCE: {summary['states']['avoidance_count']}")

    rec_min = summary["states"]["recovery_total_sec"] // 60
    lines.append(f"RECOVERY: {rec_min} min")

    if summary["passive"]:
        lines.append("PASSIVE:")
        for k, v in summary["passive"].items():
            lines.append(f"  {k}: {v:+.2f}")

    return lines


def format_trends(trends: dict) -> list[str]:
    """
    Format trend labels into clean output.
    """
    lines = ["TRENDS (last 3 days vs previous 3)"]

    for key, value in trends.items():
        label = key.replace("_trend", "").replace("_", " ").title()
        lines.append(f"{label}: {value}")

    return lines
