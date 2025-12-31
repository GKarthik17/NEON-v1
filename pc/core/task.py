from enum import Enum, auto
from datetime import datetime


class TaskType(Enum):
    ACTIVE = auto()
    PASSIVE = auto()


class TaskStatus(Enum):
    PENDING = auto()
    ACTIVE = auto()
    DONE = auto()
    FAILED = auto()


class Task:
    def __init__(self, task_id, name, task_type, duration=None):
        self.id = task_id
        self.name = name
        self.type = task_type
        self.duration = duration          # minutes (ACTIVE only)
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None

    def start(self):
        self.status = TaskStatus.ACTIVE
        self.started_at = datetime.now()

    def complete(self):
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()

    def fail(self):
        self.status = TaskStatus.FAILED

class PassiveTask:
    def __init__(self, task_id, name):
        self.id = task_id
        self.name = name
        self.type = TaskType.PASSIVE
        self.compliance_score = 0.0   # -1.0 to +1.0
        self.last_updated = None

    def update_signal(self, score_delta):
        """
        score_delta: small value like +0.1, -0.2
        """
        self.compliance_score = max(-1.0, min(1.0, self.compliance_score + score_delta))
        self.last_updated = datetime.now()
