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

    def tick(self):
        """
        Called periodically (or on FSM EXECUTION entry)
        Returns factual signals only.
        """
        facts = {}

        if self.active_task_id:
            facts["active_task_running"] = True
        else:
            facts["active_task_running"] = False

        facts["passive_summary"] = {
            t.name: t.compliance_score
            for t in self.passive_tasks.values()
        }

        return facts
