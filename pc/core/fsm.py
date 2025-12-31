from enum import Enum, auto
from interface.parser import CommandParser
from core.task_manager import TaskManager
from core.decision_engine import DecisionEngine



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

        self.task_manager = TaskManager(logger)
        self.decision_engine = DecisionEngine(logger)

    def start(self):
        self.logger.info("FSM initialized")
        self.transition(State.IDLE)

    def transition(self, next_state):
        self.logger.info(f"FSM transition: {self.state.name} -> {next_state.name}")
        self.state = next_state

    def handle_input(self, raw_cmd: str):
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

        else:
            self.logger.warning("Unhandled command")

    def handle_event(self, event: str):
        self.logger.info(f"FSM event received: {event}")

        if event == "AVOIDANCE":
            self.transition(State.AVOIDANCE)

        elif event == "BURNOUT":
            self.transition(State.BURNOUT)

        elif event == "RECOVERY":
            self.transition(State.RECOVERY)

        elif event == "CONTINUE":
            # Explicit no-op (stay in EXECUTION)
            pass

        else:
            self.logger.warning(f"Unknown FSM event: {event}")

    def decision_tick(self):
        """
        Called periodically or on EXECUTION state.
        Converts task facts → FSM events.
        """
        facts = self.task_manager.tick()
        event = self.decision_engine.evaluate(facts)

        if event:
            self.handle_event(event)

