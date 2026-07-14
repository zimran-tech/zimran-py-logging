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

    # LoguruIntegration defaults its event/breadcrumb formats to LOGURU_FORMAT, which is prefixed
    # with a timestamp. Sentry uses the formatted message as the event title and grouping key, so
    # the default makes every error a unique, timestamp-cluttered issue. '{message}' keeps only the
    # log message.
    loguru_integration = LoguruIntegration(event_format='{message}', breadcrumb_format='{message}')
    kwargs.setdefault('integrations', [FastApiIntegration(), loguru_integration])  # type: ignore

    init(dsn=dsn, environment=environment, sample_rate=sample_rate, **kwargs)  # type: ignore
