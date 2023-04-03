import sys

from loguru import logger
from sentry_sdk import init


def setup_logger(debug: bool) -> None:
    logger.remove()

    if debug:
        logger.add(sys.stdout, level='DEBUG')
    else:
        logger.add(sys.stdout, level='INFO', serialize=True)


def setup_sentry(dsn: str, environment: str, sample_rate=0.2) -> None:
    init(dsn=dsn, environment=environment, sample_rate=sample_rate)
