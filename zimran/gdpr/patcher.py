import os.path
import re
from typing import Any

from zimran.logging.utils import read_logger_config


class GDPRPatcher:
    def __init__(self, config: str | None = None):
        self.config = config
        self.__compiled_patterns: list[re.Pattern] = self.__get_compiled_patterns()

    def __call__(self, record: dict[str, Any]) -> None:
        sensitive_fields_detected = []

        if self.__contains_sensitive_data(record['message']):
            sensitive_fields_detected.append('message')

        extra = record['extra']
        for key, value in extra.items():
            if isinstance(value, (dict, list, tuple, set)):
                # complex data structures may contain sensitive information
                sensitive_fields_detected.append(key)

            elif isinstance(value, str):
                if self.__contains_sensitive_data(value):
                    sensitive_fields_detected.append(key)

            elif not isinstance(value, (int, float, bool, type(None))):
                # for primitive types (int, float, bool, None), do nothing
                # any other non-primitive types may contain sensitive information
                sensitive_fields_detected.append(key)

        if sensitive_fields_detected:
            record['level']['name'] = "WARNING"
            record['level']['no'] = 30
            record['extra']['sensitive_fields'] = sensitive_fields_detected
            record['message'] += ' - This log possibly contains non-compliant fields.'

    def __contains_sensitive_data(self, text: str) -> bool:
        for regex in self.__compiled_patterns:
            if regex.search(text):
                return True

        return False

    def __get_compiled_patterns(self) -> list[re.Pattern]:
        patterns_config = read_logger_config(
            os.path.join(os.path.dirname(__file__), 'patterns.yaml')
        )
        service_config = read_logger_config(self.config)

        patterns = patterns_config.get('sensitive_patterns', [])
        service_patterns = service_config.get('sensitive_patterns', [])

        compiled_patterns = [
            re.compile(pattern) for pattern in list(set(patterns + service_patterns))
        ]
        return compiled_patterns
