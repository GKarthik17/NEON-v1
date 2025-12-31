from core.fsm import NeonFSM
from utils.logger import get_logger

def main():
    logger = get_logger()
    logger.info("NEON v1 starting...")

    fsm = NeonFSM(logger)
    fsm.start()

    # Main event loop (v1: CLI driven)
    while True:
        try:
            cmd = input("NEON> ").strip()
            if cmd.lower() in ("exit", "quit"):
                logger.info("Shutdown requested")
                break

            fsm.handle_input(cmd)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            break

    logger.info("NEON v1 stopped")

if __name__ == "__main__":
    main()
