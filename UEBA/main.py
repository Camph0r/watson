from threads.manage_thread import run_thread
from utils.logger import setup_logging
import logging


logger = logging.getLogger(__name__)


def main():

    setup_logging()

    logger.info("Jay sambo")
    run_thread()


if __name__ == "__main__":
    main()
