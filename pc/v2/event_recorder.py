import json
import os
from datetime import datetime
from threading import Lock


class EventRecorder:
    """
    Append-only event recorder for NEON v2.
    Records immutable factual events in JSONL format.
    """

    def __init__(self, base_path=".", filename="events.jsonl"):
        self.file_path = os.path.join(base_path, "v2", filename)
        self._lock = Lock()

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def record(self, event_type: str, data: dict | None = None):
        """
        Record a single immutable event.
        """
        if data is None:
            data = {}

        event = {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "type": event_type,
            "data": data
        }

        line = json.dumps(event, separators=(",", ":"))

        # Atomic append
        with self._lock:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())
