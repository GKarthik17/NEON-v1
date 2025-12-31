class DecisionEngine:
    def __init__(self, logger):
        self.logger = logger
        self.escalation_level = 0

    def evaluate(self, facts):
        """
        facts come from TaskManager.tick()
        """
        # --- Time thresholds (seconds) ---
        EXECUTION_GRACE = 90          # setup time
        TASK_SELECT_LIMIT = 600       # 10 min
        TASK_IDLE_LIMIT = 900         # 15 min

        execution_time = facts.get("execution_duration", 0)
        silence = facts.get("silence_seconds", 0)
        task_idle = facts.get("task_inactivity_seconds", 0)
        active = facts.get("active_task_running", False)

        # 1. Grace period: do nothing
        if execution_time < EXECUTION_GRACE:
            return "CONTINUE"

        # 2. No active task after grace → possible avoidance
        if not active and execution_time > TASK_SELECT_LIMIT:
            return "AVOIDANCE"

        # 3. Active task but stalled too long → avoidance
        if active and task_idle > TASK_IDLE_LIMIT:
            return "AVOIDANCE"

        # 4. Burnout logic comes later (not yet)
        return "CONTINUE"


