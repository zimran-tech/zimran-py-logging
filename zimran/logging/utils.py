import os
from typing import Any

import yaml

from zimran.logging.exceptions import InvalidConfigurationError, InvalidEnvironmentError


def _get_sample_rate(environment: str) -> float:
    if environment == 'production':
        return 0.2

    if environment == 'staging':
        return 1.0

    raise InvalidEnvironmentError(environment)


def read_logger_config(config_path: str | None = None) -> dict[str, Any]:
    if config_path is not None:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config

        raise InvalidConfigurationError(config_path)

    return {}
