import sys
from typing import Any

from loguru import logger
from sentry_sdk import init
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration

from zimran.logging.exceptions import InvalidEnvironmentError


def _get_sample_rate(environment: str) -> float:
    if environment == 'production':
        return 0.2

    if environment == 'staging':
        return 1

    raise InvalidEnvironmentError(environment)


def setup_logger(debug: bool) -> None:
    logger.remove()

    if debug:
        logger.add(sys.stdout, level='DEBUG')
    else:
        logger.add(sys.stdout, level='INFO', serialize=True)


def setup_sentry(dsn: str, environment: str, **kwargs: dict[str, Any]) -> None:
    try:
        sample_rate = _get_sample_rate(environment)
    except InvalidEnvironmentError:
        return

    kwargs.setdefault('integrations', [FastApiIntegration(), LoguruIntegration()])  # type: ignore

    init(dsn=dsn, environment=environment, sample_rate=sample_rate, **kwargs)  # type: ignore
