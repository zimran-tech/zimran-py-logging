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
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['message']
    assert record['message'] == (
        'User has been registered: user@zimran.io.'
        ' # POTENTIAL USE OF NON-COMPLIANT DATA.'
    )


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
    assert record['level']['name'] == 'WARNING'
    assert record['level']['no'] == 30
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['email', 'ip_address']
    assert (
        record['message'] == 'Regular message. # POTENTIAL USE OF NON-COMPLIANT DATA.'
    )


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
    assert record['level']['name'] == 'WARNING'
    assert record['level']['no'] == 30
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['user_data']
    assert (
        record['message'] == 'Regular message. # POTENTIAL USE OF NON-COMPLIANT DATA.'
    )


def test_no_sensitive_info(gdpr_patcher):
    record = {
        'message': 'Regular message without sensitive data.',
        'level': {'name': 'INFO', 'no': 20},
        'extra': {
            'info': 'Just some information.',
        },
    }
    gdpr_patcher(record)
    assert record['level']['name'] == 'INFO'
    assert record['level']['no'] == 20
    assert 'LSF' not in record['extra']
    assert record['message'] == 'Regular message without sensitive data.'


def test_sensitive_data_in_error_log(gdpr_patcher):
    record = {
        'message': 'Error occurred while process: user@zimran.io.',
        'level': {'name': 'ERROR', 'no': 40},
        'extra': {
            'user_id': '1234',
            'payload': {
                'ssn': '123-45-6789',
                'name': 'John Doe'
            },
            'error': 'Key error.'
        },
    }
    gdpr_patcher(record)
    assert record['level']['name'] == 'ERROR'
    assert record['level']['no'] == 40
    assert 'LSF' in record['extra']
    assert record['message'] == (
        'Error occurred while process: user@zimran.io.'
        ' # POTENTIAL USE OF NON-COMPLIANT DATA.'
    )
    assert 'LSF' in record['extra']
    assert record['extra']['LSF'] == ['message', 'payload']
