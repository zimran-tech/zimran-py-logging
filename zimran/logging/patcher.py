import os.path
import re
from typing import Any, TypedDict

from zimran.logging.utils import read_logger_config


NON_PRIMITIVE_TYPE = (
    'field\'s value type is non-primitive; '
    'consider to provide logs with primitive type arguments'
)
SENSITIVE_FIELD = (
    'field\'s value is sensitive; '
    'consider to provide logs with non-sensitive values'
)
SENSITIVE_MESSAGE = (
    'message\'s text is sensitive; consider '
    'to provide message with non-sensitive parts and to avoid using f-strings'
)
MASKED = '[MASKED]'

PRIMITIVE_TYPES = (int, float, str, bool, type(None))


class NonCompliantField(TypedDict):
    field: str
    warning: str


class GDPRPatcher:
    def __init__(
            self,
            config: str | None = None,
            environment: str = 'staging',
    ):
        self.environment = environment
        self.config = config
        self.__compiled_patterns: list[re.Pattern] = self.__get_compiled_patterns()

    def __call__(self, record: dict[str, Any]) -> None:
        if data := self.__detect_non_compliant_fields(record):
            record['extra']['ncd'] = data

    def __detect_non_compliant_fields(self, record: dict[str, Any]) -> list[NonCompliantField]:
        non_compliant_fields: list[NonCompliantField] = []
        extra = record.setdefault('extra', {})

        if self.__contains_sensitive_data(record['message']):
            non_compliant_fields.append({
            'field': 'message',
            'warning': SENSITIVE_MESSAGE,
        })
            if self.environment == 'production':
                record['message'] = MASKED

        for key, value in extra.items():
            if not isinstance(value, PRIMITIVE_TYPES):
                # non-primitive types are not recommended to log
                # as they may contain sensitive data and typically are overheads
                non_compliant_fields.append({
                    'field': key,
                    'warning': NON_PRIMITIVE_TYPE,
                })
                if self.environment == 'production':
                    record['extra'][key] = MASKED

            elif isinstance(value, str) and self.__contains_sensitive_data(value):
                non_compliant_fields.append({
                    'field': key,
                    'warning': SENSITIVE_FIELD,
                })
                if self.environment == 'production':
                    record['extra'][key] = MASKED

        return non_compliant_fields

    def __contains_sensitive_data(self, value: str) -> bool:
        return any(regex.search(value) for regex in self.__compiled_patterns)

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
