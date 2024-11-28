import os.path
import re
from typing import Any, TypedDict, Literal

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

warning_mapper = {
    'm': SENSITIVE_MESSAGE,
    'f': SENSITIVE_FIELD,
    't': NON_PRIMITIVE_TYPE,
}

class NonCompliantField(TypedDict):
    field: str
    message: str


class GDPRPatcher:
    def __init__(
            self,
            config: str | None = None,
            environment: str = 'staging',
    ):
        self.environment = environment
        self.config = config
        self.__compiled_patterns: list[re.Pattern] = self.__get_compiled_patterns()
        self.__non_compliant_fields: list[NonCompliantField] = []

    def __call__(self, record: dict[str, Any]) -> None:
        self.__detect_non_compliant_fields(record)

        if self.__non_compliant_fields:
            record['extra']['ncd'] = self.__non_compliant_fields

    def __detect_non_compliant_fields(self, record: dict[str, Any]) -> None:
        extra = record.setdefault('extra', {})

        if self.__contains_sensitive_data(record['message']):
            self.__update_non_compliant_fields(record, key='message', mapper='m')

        for key, value in extra.items():
            if not isinstance(value, PRIMITIVE_TYPES):
                # non-primitive types are not recommended to log
                # as they may contain sensitive data and typically are overheads
                self.__update_non_compliant_fields(record, key=key, mapper='t')

            elif isinstance(value, str) and self.__contains_sensitive_data(value):
                self.__update_non_compliant_fields(record, key=key, mapper='f')

    def __contains_sensitive_data(self, value: str) -> bool:
        return any(regex.search(value) for regex in self.__compiled_patterns)

    def __update_non_compliant_fields(
            self,
            record: dict[str, Any],
            key: str,
            mapper: Literal['m', 'f', 't'],
    ) -> None:
        self.__non_compliant_fields.append({
            'field': key,
            'message': warning_mapper[mapper],
        })
        if self.environment == 'production':
            record['extra'][key] = MASKED

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
