import time
from core.fsm import NeonFSM, State
from utils.logger import get_logger
from interface.non_blocking_input import NonBlockingInput

TICK_INTERVAL = 1.0  # seconds

def main():
    logger = get_logger()
    logger.info("NEON v1 starting...")

    fsm = NeonFSM(logger)
    fsm.start()

    input_reader = NonBlockingInput()
    last_tick = time.monotonic()

    print("NEON> ", end="", flush=True)

    while True:
        try:
            now = time.monotonic()

            # ---- TIME TICK ----
            if now - last_tick >= TICK_INTERVAL:
                fsm.decision_tick()
                last_tick = now

            # ---- NON-BLOCKING INPUT ----
            line = input_reader.poll()
            if line is not None:
                if line.lower() in ("exit", "quit"):
                    logger.info("Shutdown requested")
                    break

                fsm.handle_input(line)
                print("NEON> ", end="", flush=True)

            time.sleep(0.05)  # CPU friendly

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            break

    logger.info("NEON v1 stopped")

if __name__ == "__main__":
    main()
