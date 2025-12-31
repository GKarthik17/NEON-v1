import json
import os
from datetime import datetime

STATE_FILE = "neon_state.json"


class MemoryStorage:
    def __init__(self, logger, base_path="."):
        self.logger = logger
        self.file_path = os.path.join(base_path, STATE_FILE)

    def save(self, data: dict):
        try:
            tmp_file = self.file_path + ".tmp"
            with open(tmp_file, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_file, self.file_path)
            self.logger.info("Memory state saved")
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")

    def load(self):
        if not os.path.exists(self.file_path):
            self.logger.info("No previous memory state found")
            return None

        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            self.logger.info("Memory state loaded")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load memory: {e}")
            return None
