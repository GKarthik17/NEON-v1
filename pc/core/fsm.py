from enum import Enum, auto

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

    def start(self):
        self.logger.info("FSM initialized")
        self.transition(State.IDLE)

    def transition(self, next_state):
        self.logger.info(f"FSM transition: {self.state.name} -> {next_state.name}")
        self.state = next_state

    def handle_input(self, cmd: str):
        self.logger.info(f"Input received in {self.state.name}: {cmd}")

        # Temporary routing (will be replaced by parser)
        if cmd == "start":
            self.transition(State.PLANNING)
        elif cmd == "exec":
            self.transition(State.EXECUTION)
        elif cmd == "avoid":
            self.transition(State.AVOIDANCE)
        elif cmd == "burnout":
            self.transition(State.BURNOUT)
        elif cmd == "recover":
            self.transition(State.RECOVERY)
        elif cmd == "override":
            self.transition(State.OVERRIDE)
        elif cmd == "idle":
            self.transition(State.IDLE)
        else:
            self.logger.warning("Unknown command")
