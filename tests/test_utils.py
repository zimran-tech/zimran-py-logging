import pytest
from sentry_sdk.integrations.loguru import LoguruIntegration

from zimran.logging.exceptions import InvalidEnvironmentError
from zimran.logging.utils import _get_sample_rate, setup_sentry


def test_get_sample_rate() -> None:
    assert _get_sample_rate('production') == 0.2
    assert _get_sample_rate('staging') == 1

    with pytest.raises(InvalidEnvironmentError):
        _get_sample_rate('development')


def test_setup_sentry_strips_timestamp_from_event_message(monkeypatch: pytest.MonkeyPatch) -> None:
    # LoguruIntegration's default format is prefixed with a timestamp, which Sentry then uses as the
    # event title and grouping key. setup_sentry must override it to '{message}' so issues group by
    # the log message instead of being unique per timestamp.
    captured: dict = {}
    monkeypatch.setattr('zimran.logging.utils.init', lambda **kwargs: captured.update(kwargs))

    setup_sentry(dsn='https://public@example.com/1', environment='staging')

    integration = next(i for i in captured['integrations'] if isinstance(i, LoguruIntegration))
    assert integration.event_format == '{message}'
    assert integration.breadcrumb_format == '{message}'
