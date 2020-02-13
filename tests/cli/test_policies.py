import os
import pytest

from tests.cli import run_cmd


POLICY_COLUMNS = ['id', 'description', 'subjects', 'resources', 'actions']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_TEARDOWN_RESOURCES = list()


@pytest.fixture()
def integration_teardown():
    yield
    for res in _TEARDOWN_RESOURCES:
        run_cmd(['%s delete' % res['res'],
                 '--project=%s' % PROJECT_ID] + res['args'])


@pytest.mark.integration
def test_policies_integration(integration_teardown):
    global _TEARDOWN_RESOURCES
    # create new dataset
    dataset = run_cmd(['dataset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=dataset-for-policy-2'])
    _TEARDOWN_RESOURCES.append({'res': 'dataset', 'args': [dataset.get('id')]})
    # create new AWS S3 fileset
    fileset = run_cmd(['fileset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=fileset-for-policy-2',
                       'aws-s3',
                       '--key=%s' % os.environ['JEXIA_CLI_TEST_AWS_KEY'],
                       '--secret=%s' % os.environ['JEXIA_CLI_TEST_AWS_SECRET'],
                       '--bucket=%s' % os.environ['JEXIA_CLI_TEST_AWS_BUCKET']
                       ])
    _TEARDOWN_RESOURCES.append({'res': 'fileset', 'args': [fileset.get('id')]})
    # create new API key
    key = run_cmd(['key create',
                   '-f=json',
                   '--project=%s' % PROJECT_ID,
                   '--description=test-integration'])
    _TEARDOWN_RESOURCES.append({'res': 'key', 'args': [key['key']]})
    # get current policies
    policies = run_cmd(['policy list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    initial_number_of_policies = len(policies)
    if initial_number_of_policies > 0:
        assert set(POLICY_COLUMNS) == set(policies[0].keys())
    # create new policy
    policy = run_cmd(['policy create',
                      '-f=json',
                      '--project=%s' % PROJECT_ID,
                      '--description=test-policy-integration',
                      '--action=read',
                      '--action=delete',
                      '--action=create',
                      '--userset=ANY',
                      '--api-key=%s' % key['key'],
                      '--resource=%s' % dataset['id'],
                      '--resource=%s' % fileset['id']])
    _TEARDOWN_RESOURCES.append({'res': 'policy',
                                'args': [policy['id']]})
    assert set(POLICY_COLUMNS) == set(policy.keys())
    assert 'dataset: %s' % dataset['id'] in policy['resources']
    assert 'fileset: %s' % fileset['id'] in policy['resources']
    assert 'API key: %s' % key['key'] in policy['subjects']
    assert 'userset: ANY' in policy['subjects']
    assert 'delete' in policy['actions']
    assert 'create' in policy['actions']
    assert 'read' in policy['actions']
    # update policy
    policy = run_cmd(['policy update',
                      '-f=json',
                      '--project=%s' % PROJECT_ID,
                      '--description=test-policy-integration',
                      '--action=read',
                      '--api-key=%s' % key['key'],
                      '--resource=%s' % fileset['id'],
                      policy['id']])
    assert set(POLICY_COLUMNS) == set(policy.keys())
    assert 'dataset: %s' % dataset['id'] not in policy['resources']
    assert 'fileset: %s' % fileset['id'] in policy['resources']
    assert 'API key: %s' % key['key'] in policy['subjects']
    assert 'userset: ANY' not in policy['subjects']
    assert 'delete' not in policy['actions']
    assert 'create' not in policy['actions']
    assert 'read' in policy['actions']
    # list of policies
    policies = run_cmd(['policy list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_policies + 1 == len(policies)
    # delete policy
    output = run_cmd(['policy delete',
                      '--project=%s' % PROJECT_ID,
                      policy['id']])
    assert '' == output
    # check deletion
    policies = run_cmd(['policy list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_policies == len(policies)
