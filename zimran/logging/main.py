import sys
from typing import Any

import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration

from zimran.logging.exceptions import InvalidEnvironmentError
from zimran.logging.patcher import GDPRPatcher
from zimran.logging.utils import _get_sample_rate


def sentry_sink(message) -> None:
    record = message.record

    if ncd := record.get('extra', {}).get('ncd', None):
        try:
            sentry_sdk.capture_event(
                event={
                    'message': 'Log record contains non-compliant data',
                    'level': 'warning',
                    'extra': {
                        'Record': record,
                        'Non Compliant Data': ncd,
                    }
                }
            )
        except Exception:
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
