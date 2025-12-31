import time


class TimeTracker:
    def __init__(self):
        now = time.monotonic()
        self.start_time = now
        self.last_input_time = now
        self.last_task_activity_time = now

    def mark_input(self):
        self.last_input_time = time.monotonic()

    def mark_task_activity(self):
        self.last_task_activity_time = time.monotonic()

    def seconds_since_input(self):
        return time.monotonic() - self.last_input_time

    def seconds_since_task_activity(self):
        return time.monotonic() - self.last_task_activity_time
