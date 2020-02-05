import os
import pytest

from tests.cli import run_cmd


KEY_COLUMNS = ['key', 'description']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_CREATED_RESOURCE = None


@pytest.fixture()
def integration_teardown():
    yield
    if _CREATED_RESOURCE:
        run_cmd(['key delete', '--project=%s' % PROJECT_ID,
                 _CREATED_RESOURCE])


@pytest.mark.integration
def test_keys_integration(integration_teardown):
    global _CREATED_RESOURCE
    # get current keys
    keys = run_cmd(['key list',
                    '-f=json',
                    '--project=%s' % PROJECT_ID])
    initial_number_of_keys = len(keys)
    # create new key
    key = run_cmd(['key create',
                   '-f=json',
                   '--project=%s' % PROJECT_ID,
                   '--description=test-integration'])
    _CREATED_RESOURCE = key.get('key')
    assert set(KEY_COLUMNS) == set(key.keys())
    # list of keys
    keys = run_cmd(['key list',
                    '-f=json',
                    '--project=%s' % PROJECT_ID])
    assert initial_number_of_keys + 1 == len(keys)
    assert set(KEY_COLUMNS) == set(keys[0].keys())
    # update key
    key = run_cmd(['key update',
                   '-f=json',
                   '--project=%s' % PROJECT_ID,
                   '--description=test-integration-2',
                   key['key']])
    assert set(KEY_COLUMNS) == set(key.keys())
    assert key['description'] == 'test-integration-2'
    # delete key
    output = run_cmd(['key delete',
                      '--project=%s' % PROJECT_ID,
                      key['key']])
    assert '' == output
    # check deletion
    keys = run_cmd(['key list',
                    '-f=json',
                    '--project=%s' % PROJECT_ID])
    assert initial_number_of_keys == len(keys)
