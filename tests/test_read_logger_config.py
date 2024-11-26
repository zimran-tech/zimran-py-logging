import pytest

from zimran.logging.exceptions import InvalidConfigurationError
from zimran.logging.utils import read_logger_config


def test_read_logger_config(tmp_path):
    config_content = """
    sensitive_patterns:
      - '\\b\\d{3}-\\d{2}-\\d{4}\\b'
    """
    config_file = tmp_path / 'logger_configuration.yaml'
    config_file.write_text(config_content)

    config = read_logger_config(str(config_file))
    assert isinstance(config, dict)
    assert 'sensitive_patterns' in config
    assert config['sensitive_patterns'] == ['\\b\\d{3}-\\d{2}-\\d{4}\\b']


def test_read_logger_config_invalid():
    with pytest.raises(InvalidConfigurationError):
        read_logger_config('non_existent_file.yaml')
