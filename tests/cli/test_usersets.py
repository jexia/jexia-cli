import os
import pytest

from tests.cli import run_cmd


USERSET_COLUMNS = ['id', 'email', 'active', 'created_at', 'updated_at']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_CREATED_RESOURCE = None


@pytest.fixture()
def integration_teardown():
    yield
    if _CREATED_RESOURCE:
        run_cmd(['userset delete', '--project=%s' % PROJECT_ID,
                 _CREATED_RESOURCE])


@pytest.mark.integration
def test_usersets_integration(integration_teardown):
    global _CREATED_RESOURCE
    # get current usersets
    usersets = run_cmd(['userset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    initial_number_of_usersets = len(usersets)
    # create new userset
    userset = run_cmd(['userset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--email=test-integration@example.com',
                       '--password=test'])
    _CREATED_RESOURCE = userset.get('id')
    assert set(USERSET_COLUMNS) == set(userset.keys())
    # list of usersets
    usersets = run_cmd(['userset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_usersets + 1 == len(usersets)
    assert set(USERSET_COLUMNS) == set(usersets[0].keys())
    # update userset
    userset = run_cmd(['userset update',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--deactivate',
                       userset['id']])
    assert set(USERSET_COLUMNS) == set(userset.keys())
    assert not userset['active']
    # delete userset
    output = run_cmd(['userset delete',
                      '--project=%s' % PROJECT_ID,
                      userset['id']])
    assert '' == output
    # check deletion
    usersets = run_cmd(['userset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_usersets == len(usersets)
