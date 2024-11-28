import sys
from typing import Any

from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration

from zimran.logging.patcher import GDPRPatcher
from zimran.logging.exceptions import InvalidEnvironmentError
from zimran.logging.utils import _get_sample_rate


def sentry_sink(message):
    record = message.record

    if ncd := record.get('extra', {}).get('ncd', None):
        try:
            with sentry_sdk.new_scope() as scope:
                scope.set_extra('Record', record)
                scope.set_extra('Non Compliant Data', ncd)

                sentry_sdk.capture_message(
                    message='Log record contains non-compliant data',
                    level='warning',
                )
        except Exception as exc:
            pass


def setup_logger(debug: bool, environment: str, logger_config: str | None = None) -> None:
    logger.remove()

    if debug:
        logger.add(sys.stdout, level='DEBUG')
    else:
        logger.add(sys.stdout, level='INFO', serialize=True)

    patcher = GDPRPatcher(config=logger_config, environment=environment)
    logger.configure(patcher=patcher)
    logger.add(sentry_sink)


def setup_sentry(dsn: str, environment: str, **kwargs: Any) -> None:
    try:
        sample_rate = _get_sample_rate(environment)
    except InvalidEnvironmentError:
        return

    kwargs.setdefault('integrations', [FastApiIntegration(), LoguruIntegration()])  # type: ignore

    sentry_sdk.init(dsn=dsn, environment=environment, sample_rate=sample_rate, **kwargs)  # type: ignore
