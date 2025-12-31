from core.task import Task, PassiveTask, TaskType, TaskStatus


class TaskManager:
    def __init__(self, logger):
        self.logger = logger
        self.tasks = {}
        self.passive_tasks = {}
        self.active_task_id = None
        self._id_counter = 1

    def _next_id(self):
        tid = self._id_counter
        self._id_counter += 1
        return tid

    def add_active_task(self, name, duration):
        task_id = self._next_id()
        task = Task(task_id, name, TaskType.ACTIVE, duration)
        self.tasks[task_id] = task
        self.logger.info(f"Active task added: {task_id} - {name}")
        return task_id

    def add_passive_task(self, name):
        task_id = self._next_id()
        task = PassiveTask(task_id, name)
        self.passive_tasks[task_id] = task
        self.logger.info(f"Passive task added: {task_id} - {name}")
        return task_id

    def activate_task(self, task_id):
        if self.active_task_id is not None:
            self.logger.warning("Another task is already active")
            return False

        task = self.tasks.get(task_id)
        if not task:
            self.logger.error("Task not found")
            return False

        task.start()
        self.active_task_id = task_id
        self.logger.info(f"Task {task_id} activated")
        return True

    def complete_active_task(self):
        if self.active_task_id is None:
            return False

        task = self.tasks[self.active_task_id]
        task.complete()
        self.logger.info(f"Task {task.id} completed")
        self.active_task_id = None
        return True

    def fail_active_task(self):
        if self.active_task_id is None:
            return False

        task = self.tasks[self.active_task_id]
        task.fail()
        self.logger.info(f"Task {task.id} failed")
        self.active_task_id = None
        return True

    def update_passive(self, task_id, delta):
        task = self.passive_tasks.get(task_id)
        if not task:
            self.logger.error("Passive task not found")
            return False

        task.update_signal(delta)
        self.logger.info(
            f"Passive task {task_id} updated, score={task.compliance_score}"
        )
        return True

    def tick(self, time_tracker):
        facts = {}

        facts["active_task_running"] = self.active_task_id is not None
        facts["silence_seconds"] = time_tracker.seconds_since_input()
        facts["task_inactivity_seconds"] = time_tracker.seconds_since_task_activity()
        facts["passive_summary"] = {
            t.name: t.compliance_score
            for t in self.passive_tasks.values()
        }

        facts["tasks_completed"] = sum(
            1 for t in self.tasks.values() if t.status.name == "DONE"
        )

        facts["tasks_failed"] = sum(
            1 for t in self.tasks.values() if t.status.name == "FAILED"
        )


        return facts

    def export_state(self):
        return {
            "active_task_id": self.active_task_id,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "type": t.type.name,
                    "status": t.status.name,
                    "duration": t.duration,
                    "created_at": t.created_at.isoformat(),
                    "started_at": t.started_at.isoformat() if t.started_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None
                }
                for t in self.tasks.values()
            ],
            "passive_tasks": [
                {
                    "id": p.id,
                    "name": p.name,
                    "compliance_score": p.compliance_score
                }
                for p in self.passive_tasks.values()
            ]
        }

    def restore_state(self, data):
        from core.task import Task, PassiveTask, TaskType, TaskStatus
        from datetime import datetime

        self.tasks.clear()
        self.passive_tasks.clear()

        for t in data.get("tasks", []):
            task = Task(
                t["id"],
                t["name"],
                TaskType[t["type"]],
                t["duration"]
            )
            task.status = TaskStatus[t["status"]]
            task.created_at = datetime.fromisoformat(t["created_at"])
            task.started_at = datetime.fromisoformat(t["started_at"]) if t["started_at"] else None
            task.completed_at = datetime.fromisoformat(t["completed_at"]) if t["completed_at"] else None
            self.tasks[task.id] = task

        for p in data.get("passive_tasks", []):
            passive = PassiveTask(p["id"], p["name"])
            passive.compliance_score = p["compliance_score"]
            self.passive_tasks[passive.id] = passive

        self.active_task_id = data.get("active_task_id")
        self.logger.info("TaskManager state restored")

    def list_tasks(self):
        """
        Returns a snapshot of all tasks (active + passive)
        """
        active_tasks = []
        passive_tasks = []

        for task in self.tasks.values():
            active_tasks.append({
                "id": task.id,
                "name": task.name,
                "type": task.type.name,
                "status": task.status.name,
                "duration": task.duration
            })

        for task in self.passive_tasks.values():
            passive_tasks.append({
                "id": task.id,
                "name": task.name,
                "compliance_score": task.compliance_score
            })

        return active_tasks, passive_tasks

