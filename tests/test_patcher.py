import pytest

from zimran.logging.patcher import GDPRPatcher


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
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['message']


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
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['email', 'ip_address']



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
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['user_data']


def test_no_sensitive_info(gdpr_patcher):
    record = {
        'message': 'Regular message without sensitive data.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'info': 'Just some information.',
        },
    }
    gdpr_patcher(record)
    assert 'LSF' not in record['extra']
