import pytest

from zimran.logging.patcher import (
    GDPRPatcher,
    SENSITIVE_MESSAGE,
    NON_PRIMITIVE_TYPE,
    SENSITIVE_FIELD,
    MASKED,
)


@pytest.fixture
def gdpr_patcher():
    return GDPRPatcher()


@pytest.fixture
def production_gdpr_patcher():
    return GDPRPatcher(environment='production')


def test_sensitive_info_in_message(gdpr_patcher):
    record = {
        'message': 'User has been registered: user@zimran.io.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {},
    }
    gdpr_patcher(record)
    assert 'ncd' in record['extra']
    assert isinstance(record['extra']['ncd'], list)
    assert record['extra']['ncd'][0] == {
        'field': 'message',
        'warning': SENSITIVE_MESSAGE,
    }


def test_sensitive_info_in_extra(gdpr_patcher):
    record = {
        'message': 'Regular message.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'email': 'user@zimran.io',
            'ip_address': '192.158.1.38',
            'user_id': '1234',
        },
    }
    gdpr_patcher(record)
    assert 'ncd' in record['extra']
    assert isinstance(record['extra']['ncd'], list)
    assert record['extra']['ncd'] == [
        {
            'field': 'email',
            'warning': SENSITIVE_FIELD,
        },
        {
            'field': 'ip_address',
            'warning': SENSITIVE_FIELD,
        }
    ]


def test_sensitive_info_in_extra_complex_structure(gdpr_patcher):
    record = {
        'message': 'Regular message.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'user_data': {
                'ssn': '123-45-6789',
                'name': 'John Doe',
            },
            'user_id': '1234',
        },
    }
    gdpr_patcher(record)
    assert 'ncd' in record['extra']
    assert isinstance(record['extra']['ncd'], list)
    assert record['extra']['ncd'] == [
        {
            'field': 'user_data',
            'warning': NON_PRIMITIVE_TYPE,
        },
    ]


def test_no_sensitive_info(gdpr_patcher):
    record = {
        'message': 'Regular message without sensitive data.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'info': 'Just some information.',
        },
    }
    gdpr_patcher(record)
    assert 'ncd' not in record['extra']


# ----------


def test_mask_sensitive_info_in_message(production_gdpr_patcher):
    record = {
        'message': 'User has been registered: user@zimran.io.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {},
    }
    production_gdpr_patcher(record)
    assert 'ncd' in record['extra']
    assert isinstance(record['extra']['ncd'], list)
    assert record['extra']['ncd'][0] == {
        'field': 'message',
        'warning': SENSITIVE_MESSAGE,
    }
    assert record['message'] == MASKED


def test_mask_sensitive_info_in_extra(production_gdpr_patcher):
    record = {
        'message': 'Regular message.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'email': 'user@zimran.io',
            'ip_address': '192.158.1.38',
            'user_id': '1234',
        },
    }
    production_gdpr_patcher(record)
    assert 'ncd' in record['extra']
    assert isinstance(record['extra']['ncd'], list)
    assert record['extra']['ncd'] == [
        {
            'field': 'email',
            'warning': SENSITIVE_FIELD,
        },
        {
            'field': 'ip_address',
            'warning': SENSITIVE_FIELD,
        }
    ]
    assert record['extra']['email'] == MASKED
    assert record['extra']['ip_address'] == MASKED


def test_mask_sensitive_info_in_extra_complex_structure(production_gdpr_patcher):
    record = {
        'message': 'Regular message.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'user_data': {
                'ssn': '123-45-6789',
                'name': 'John Doe',
            },
            'user_id': '1234',
        },
    }
    production_gdpr_patcher(record)
    assert 'ncd' in record['extra']
    assert isinstance(record['extra']['ncd'], list)
    assert record['extra']['ncd'] == [
        {
            'field': 'user_data',
            'warning': NON_PRIMITIVE_TYPE,
        },
    ]
    assert record['extra']['user_data'] == MASKED


def test_mask_no_sensitive_info(production_gdpr_patcher):
    record = {
        'message': 'Regular message without sensitive data.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'info': 'Just some information.',
        },
    }
    production_gdpr_patcher(record)
    assert 'ncd' not in record['extra']

