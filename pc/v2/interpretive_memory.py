from datetime import date, timedelta
from v2.aggregators import aggregate_daily


class InterpretiveMemory:
    """
    Read-only interpretive layer over daily summaries.
    No decisions. No control. No mutation.
    """

    def __init__(self):
        self._summaries = {}

    def refresh(self):
        """
        Reload summaries from events.
        Safe to call anytime.
        """
        self._summaries = aggregate_daily()

    # ---------- BASIC ACCESS ----------

    def get_day(self, day: str):
        """
        Get summary for a specific YYYY-MM-DD.
        """
        return self._summaries.get(day)

    def get_today(self):
        return self.get_day(date.today().isoformat())

    # ---------- WINDOWED SUMMARIES ----------

    def get_window(self, days: int):
        """
        Return summaries for last N days (including today).
        """
        end = date.today()
        start = end - timedelta(days=days - 1)

        window = []
        for d in range(days):
            day = (start + timedelta(days=d)).isoformat()
            if day in self._summaries:
                window.append(self._summaries[day])

        return window

    def last_3_days(self):
        return self.get_window(3)

    def last_7_days(self):
        return self.get_window(7)

    # ---------- DERIVED INSIGHTS (NO JUDGMENT) ----------

    def execution_totals(self, days: int):
        """
        Total execution seconds over last N days.
        """
        return sum(
            s["execution"]["total_sec"]
            for s in self.get_window(days)
        )

    def avoidance_count(self, days: int):
        return sum(
            s["states"]["avoidance_count"]
            for s in self.get_window(days)
        )

    def burnout_count(self, days: int):
        return sum(
            s["states"]["burnout_count"]
            for s in self.get_window(days)
        )

    def avg_recovery_time(self, days: int):
        durations = [
            s["states"]["recovery_total_sec"]
            for s in self.get_window(days)
            if s["states"]["recovery_total_sec"] > 0
        ]
        if not durations:
            return None
        return int(sum(durations) / len(durations))
