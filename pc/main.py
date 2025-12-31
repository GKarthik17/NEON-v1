import time
from core.fsm import NeonFSM, State
from utils.logger import get_logger

def main():
    logger = get_logger()
    logger.info("NEON v1 starting...")

    fsm = NeonFSM(logger)
    fsm.start()

    while True:
        try:
            # Time-based supervision (runs always)
            fsm.decision_tick()
            time.sleep(1)

            # Blocking input (ONLY when waiting for user)
            cmd = input("NEON> ").strip()
            if cmd.lower() in ("exit", "quit"):
                break

            fsm.handle_input(cmd)

        except KeyboardInterrupt:
            break

    logger.info("NEON v1 stopped")

if __name__ == "__main__":
    main()
