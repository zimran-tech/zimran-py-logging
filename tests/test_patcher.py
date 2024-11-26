import pytest

from zimran.gdpr.patcher import GDPRPatcher


@pytest.fixture
def gdpr_patcher():
    return GDPRPatcher()


def test_sensitive_info_in_message(gdpr_patcher):
    record = {
        'message': 'User has been registered: user@zimran.io.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {},
    }
    gdpr_patcher(record)
    assert record['level']['name'] == 'WARNING'
    assert record['level']['no'] == 30
    assert 'sensitive_fields' in record['extra']
    assert record['extra']['sensitive_fields'] == ['message']
    assert record['message'] == (
        'User has been registered: user@zimran.io. '
        '- This log possibly contains non-compliant fields.'
    )


def test_sensitive_info_in_extra(gdpr_patcher):
    record = {
        'message': 'Regular message.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {'email': 'user@zimran.io', 'ip_address': '192.158.1.38', 'user_id': '1234'},
    }
    gdpr_patcher(record)
    assert record['level']['name'] == 'WARNING'
    assert record['level']['no'] == 30
    assert 'sensitive_fields' in record['extra']
    assert record['extra']['sensitive_fields'] == ['email', 'ip_address']
    assert (
        record['message'] == 'Regular message. - This log possibly contains non-compliant fields.'
    )


def test_sensitive_info_in_extra_complex_structure(gdpr_patcher):
    record = {
        'message': 'Regular message.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {'user_data': {'ssn': '123-45-6789', 'name': 'John Doe'}, 'user_id': '1234'},
    }
    gdpr_patcher(record)
    assert record['level']['name'] == 'WARNING'
    assert record['level']['no'] == 30
    assert 'sensitive_fields' in record['extra']
    assert record['extra']['sensitive_fields'] == ['user_data']
    assert (
        record['message'] == 'Regular message. - This log possibly contains non-compliant fields.'
    )


def test_no_sensitive_info(gdpr_patcher):
    record = {
        'message': 'Regular message without sensitive data.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {'info': 'Just some information.'},
    }
    gdpr_patcher(record)
    assert record['level']['name'] == 'INFO'
    assert record['level']['no'] == 20
    assert 'sensitive_fields' not in record['extra']
    assert record['message'] == 'Regular message without sensitive data.'
