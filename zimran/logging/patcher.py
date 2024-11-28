import os.path
import re
from typing import Any, TypedDict

from zimran.logging.utils import read_logger_config


NON_PRIMITIVE_TYPE = 'field\'s value type is non-primitive; consider to provide logs with primitive type arguments'
SENSITIVE_FIELD = 'field\'s value is sensitive; consider to provide logs with non-sensitive values'

PRIMITIVE_TYPES = (int, float, str, bool, type(None))


class NonCompliantField(TypedDict):
    field: str
    message: str


class GDPRPatcher:
    def __init__(self, config: str | None = None):
        self.config = config
        self.__compiled_patterns: list[re.Pattern] = self.__get_compiled_patterns()

    def __call__(self, record: dict[str, Any]) -> None:
        if non_compliant_data := self.__detect_non_compliant_fields(record):
            record['extra']['ncd'] = non_compliant_data

    def __detect_non_compliant_fields(self, record: dict[str, Any]) -> list[NonCompliantField]:
        non_compliant_fields: list = []

        if self.__contains_sensitive_data(record['message']):
            non_compliant_fields.append({
                'field': 'message',
                'message': SENSITIVE_FIELD,
            })

        extra = record.setdefault('extra', {})

        for key, value in extra.items():
            if not isinstance(value, PRIMITIVE_TYPES):
                # non-primitive types are not recommended to log
                # as they may contain sensitive data and typically are overheads
                non_compliant_fields.append({
                    'field': key,
                    'message': NON_PRIMITIVE_TYPE,
                })

            elif isinstance(value, str) and self.__contains_sensitive_data(value):
                non_compliant_fields.append({
                    'field': key,
                    'message': SENSITIVE_FIELD,
                })

        return non_compliant_fields

    def __contains_sensitive_data(self, text: str) -> bool:
        return any(regex.search(text) for regex in self.__compiled_patterns)

    def __get_compiled_patterns(self) -> list[re.Pattern]:
        patterns_config = read_logger_config(
            os.path.join(os.path.dirname(__file__), 'patterns.yaml'),
        )
        service_config = read_logger_config(self.config)

        patterns = patterns_config.get('sensitive_patterns', [])
        service_patterns = service_config.get('sensitive_patterns', [])

        compiled_patterns = [
            re.compile(pattern) for pattern in list(set(patterns + service_patterns))
        ]
        return compiled_patterns
