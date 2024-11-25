import sys
from typing import Any

from loguru import logger
from sentry_sdk import init
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration

from zimran.logging.exceptions import InvalidEnvironmentError
from zimran.gdpr import GDPRPatcher
from zimran.logging.utils import _get_sample_rate


def setup_logger(debug: bool, environment: str, logger_config: str | None = None) -> None:
    logger.remove()

    if debug:
        logger.add(sys.stdout, level='DEBUG')
    else:
        logger.add(sys.stdout, level='INFO', serialize=True)

    if environment == 'staging':
        patcher = GDPRPatcher(logger_config)
        logger.configure(patcher=patcher)


def setup_sentry(dsn: str, environment: str, **kwargs: Any) -> None:
    try:
        sample_rate = _get_sample_rate(environment)
    except InvalidEnvironmentError:
        return

    kwargs.setdefault('integrations', [FastApiIntegration(), LoguruIntegration()])  # type: ignore

    init(dsn=dsn, environment=environment, sample_rate=sample_rate, **kwargs)  # type: ignore
