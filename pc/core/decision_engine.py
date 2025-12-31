class DecisionEngine:
    def __init__(self, logger):
        self.logger = logger
        self.escalation_level = 0

    def evaluate(self, facts, current_state=None):
        # ---- thresholds (tune later) ----
        EXECUTION_GRACE = 90
        TASK_SELECT_LIMIT = 600
        TASK_IDLE_LIMIT = 900

        # Recovery policy
        MIN_RECOVERY_TIME = 30 * 60   # 30 minutes

        # Burnout policy
        BURNOUT_EXEC_TIME = 3 * 60 * 60
        BURNOUT_TASKS_DONE = 3
        NEGATIVE_PASSIVE_LIMIT = -0.5

        # Read facts
        execution_time = facts.get("execution_duration", 0)
        total_exec = facts.get("total_execution_time", 0)
        recovery_time = facts.get("recovery_duration", 0)

        active = facts.get("active_task_running", False)
        task_idle = facts.get("task_inactivity_seconds", 0)
        tasks_done = facts.get("tasks_completed", 0)
        passive = facts.get("passive_summary", {})

        # -------------------------------
        # RECOVERY STATE: protected zone
        # -------------------------------
        if current_state == "RECOVERY":
            # Exit rule: minimum time satisfied
            if recovery_time >= MIN_RECOVERY_TIME:
                return "RECOVERY_COMPLETE"
            return "CONTINUE"

        # -------------------------------
        # EXECUTION: grace period
        # -------------------------------
        if execution_time < EXECUTION_GRACE:
            return "CONTINUE"

        # -------------------------------
        # Burnout (earned)
        # -------------------------------
        negative_passive = sum(1 for v in passive.values() if v < NEGATIVE_PASSIVE_LIMIT)
        if (
            total_exec > BURNOUT_EXEC_TIME
            and tasks_done >= BURNOUT_TASKS_DONE
            and negative_passive >= 1
        ):
            return "BURNOUT"

        # -------------------------------
        # Avoidance
        # -------------------------------
        if not active and execution_time > TASK_SELECT_LIMIT:
            return "AVOIDANCE"

        if active and task_idle > TASK_IDLE_LIMIT:
            return "AVOIDANCE"

        return "CONTINUE"



