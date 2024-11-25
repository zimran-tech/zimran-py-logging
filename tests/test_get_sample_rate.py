import pytest

from zimran.logging.exceptions import InvalidEnvironmentError
from zimran.logging.utils import _get_sample_rate


def test_get_sample_rate() -> None:
    assert _get_sample_rate('production') == 0.2
    assert _get_sample_rate('staging') == 1

    with pytest.raises(InvalidEnvironmentError):
        _get_sample_rate('development')
