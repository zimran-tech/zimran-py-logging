import sys
import uuid

from loguru import logger
from sentry_sdk import init

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


def setup_sentry(dsn: str, environment: str) -> None:
    try:
        sample_rate = _get_sample_rate(environment)
    except InvalidEnvironmentError:
        return

    init(dsn=dsn, environment=environment, sample_rate=sample_rate)


def setup_fastapi_logger(app, debug: bool):
    setup_logger(debug=debug)

    @app.middleware('http')
    def logging_requests(request, call_next):
        correlation_id = request.headers.get('x-zmrn-correlation-id')
        if not correlation_id:
            _set_request_correlation_id(request)

        response = call_next(request)
        context = {
            'correlation_id': request.headers.get('x-zmrn-correlation-id'),
            'method': request.method,
            'url': str(request.url),
            'path_params': request.path_params,
            'query_params': dict(request.query_params),
        }
        logger.info('request performed', context=context)
        return response


def _set_request_correlation_id(request):
    headers = request.headers.mutablecopy()
    headers.append('x-zmrn-correlation-id', str(uuid.uuid4()))
    request._headers = headers
    request.scope.update(headers=request.headers.raw)
