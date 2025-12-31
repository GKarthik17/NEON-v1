import time
from enum import Enum, auto
from interface.parser import CommandParser
from core.task_manager import TaskManager
from core.decision_engine import DecisionEngine
from core.time_tracker import TimeTracker
from memory.storage import MemoryStorage




class State(Enum):
    INIT = auto()
    IDLE = auto()
    PLANNING = auto()
    EXECUTION = auto()
    AVOIDANCE = auto()
    BURNOUT = auto()
    RECOVERY = auto()
    OVERRIDE = auto()
    SHUTDOWN = auto()

class NeonFSM:
    def __init__(self, logger):
        self.logger = logger
        self.state = State.INIT
        self.parser = CommandParser()
        self.task_manager = TaskManager(logger)
        self.decision_engine = DecisionEngine(logger)
        self.time_tracker = TimeTracker()
        self.execution_entered_at = None
        self.recovery_entered_at = None
        self.total_execution_time = 0
        self.memory = MemoryStorage(logger)



    def start(self):
        self.logger.info("FSM initialized")
        self.transition(State.IDLE)
        state = self.memory.load()
        if state:
            self.task_manager.restore_state(state)

    def save_memory(self):
        data = self.task_manager.export_state()
        self.memory.save(data)

    def transition(self, next_state):
        self.logger.info(f"FSM transition: {self.state.name} -> {next_state.name}")
        now = time.monotonic()

        # Accumulate execution effort when leaving EXECUTION
        if self.state == State.EXECUTION and self.execution_entered_at:
            self.total_execution_time += now - self.execution_entered_at

        # Mark entry times
        if next_state == State.EXECUTION:
            self.execution_entered_at = now

        if next_state == State.RECOVERY:
            self.recovery_entered_at = now

        self.state = next_state



    def handle_input(self, raw_cmd: str):
        self.time_tracker.mark_input()
        try:
            cmd = self.parser.parse(raw_cmd)
            self.logger.info(f"Parsed command: {cmd}")
            self.route_command(cmd)
            # Automatic supervision during execution
            if self.state == State.EXECUTION:
                self.decision_tick()

        except Exception as e:
            self.logger.error(f"Command error: {e}")

    def route_command(self, cmd):
        if cmd.domain == "SYS" and cmd.action == "START_DAY":
            self.transition(State.PLANNING)

        elif cmd.domain == "STATE" and cmd.action == "FORCE":
            state_name = cmd.params[0]
            self.transition(State[state_name])

        elif cmd.domain == "SYS" and cmd.action == "SHUTDOWN":
            self.transition(State.SHUTDOWN)

        elif cmd.domain == "TASK" and cmd.action == "ADD":
            # Syntax: TASK:ADD <name> <duration>
            name = cmd.params[0]
            duration = int(cmd.params[1])

            task_id = self.task_manager.add_active_task(name, duration)
            self.save_memory()

        elif cmd.domain == "TASK" and cmd.action == "ADD_PASSIVE":
            # Syntax: TASK:ADD_PASSIVE <name>
            name = cmd.params[0]

            task_id = self.task_manager.add_passive_task(name)
            self.save_memory()

        elif cmd.domain == "TASK" and cmd.action == "FOCUS":
            # Syntax: TASK:FOCUS <task_id>
            task_id = int(cmd.params[0])
            self.task_manager.activate_task(task_id)
            self.save_memory()

        elif cmd.domain == "TASK" and cmd.action == "DONE":
            self.task_manager.complete_active_task()
            self.save_memory()

        elif cmd.domain == "TASK" and cmd.action == "FAIL":
            self.task_manager.fail_active_task()
            self.save_memory()

        elif cmd.domain == "TASK" and cmd.action == "LIST":
            active, passive = self.task_manager.list_tasks()

            self.logger.info("=== ACTIVE TASKS ===")
            if not active:
                self.logger.info("No active tasks")
            else:
                for t in active:
                    self.logger.info(
                        f"[{t['id']}] {t['name']} | "
                        f"Status: {t['status']} | "
                        f"Duration: {t['duration']} min"
                    )

            self.logger.info("=== PASSIVE TASKS ===")
            if not passive:
                self.logger.info("No passive tasks")
            else:
                for t in passive:
                    self.logger.info(
                        f"[{t['id']}] {t['name']} | "
                        f"Compliance: {t['compliance_score']:.2f}"
                    )

        elif cmd.domain == "TASK" and cmd.action == "FOCUS":
            if self.state == State.RECOVERY:
                self.logger.warning("Cannot focus active tasks during RECOVERY")
                return
            task_id = int(cmd.params[0])
            self.task_manager.activate_task(task_id)
            self.save_memory()

        elif cmd.domain == "STATE" and cmd.action == "ALLOW_RECOVERY":
            if self.state != State.RECOVERY:
                self.logger.warning("ALLOW_RECOVERY ignored: not in RECOVERY state")
                return

            self.logger.info("Manual recovery override accepted")
            self.transition(State.IDLE)

        else:
            self.logger.warning("Unhandled command")
        

    def handle_event(self, event: str):
        self.logger.info(f"FSM event received: {event}")

        if event == "AVOIDANCE":
            self.transition(State.AVOIDANCE)

        elif event == "BURNOUT":
            self.transition(State.BURNOUT)
            # Immediately move to RECOVERY after classification
            self.transition(State.RECOVERY)

        elif event == "RECOVERY_COMPLETE":
            # Safe path back to work
            self.transition(State.IDLE)

        elif event == "CONTINUE":
            pass

        if event == "CONTINUE":
            return



    def decision_tick(self):
        """
        Called periodically or on EXECUTION state.
        Converts task facts → FSM events.
        """
       
        facts = self.task_manager.tick(self.time_tracker)

        if self.state in (State.SHUTDOWN,):
            return
        # Execution duration
        if self.state == State.EXECUTION and self.execution_entered_at:
            facts["execution_duration"] = time.monotonic() - self.execution_entered_at
        else:
            facts["execution_duration"] = 0

        # Total effort
        facts["total_execution_time"] = self.total_execution_time

        # Recovery duration
        if self.state == State.RECOVERY and self.recovery_entered_at:
            facts["recovery_duration"] = time.monotonic() - self.recovery_entered_at
        else:
            facts["recovery_duration"] = 0

        event = self.decision_engine.evaluate(facts, current_state=self.state.name)
        if event:
            self.handle_event(event)



