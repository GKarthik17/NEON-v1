class DecisionEngine:
    def __init__(self, logger):
        self.logger = logger
        self.escalation_level = 0

    def evaluate(self, facts):
        """
        facts come from TaskManager.tick()
        """
        if facts.get("active_task_running") is False:
            return "AVOIDANCE"

        # Passive signals influence later versions
        return "CONTINUE"
