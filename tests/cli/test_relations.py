import os
import pytest

from tests.cli import run_cmd


RELATION_COLUMNS = ['id', 'relation', 'resource', 'resource_id']
RELATION_FIELD_COLUMNS = ['id', 'name', 'type', 'immutable', 'properties',
                          'constraints']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_TEARDOWN_RESOURCES = list()


@pytest.fixture()
def integration_teardown():
    yield
    for res in _TEARDOWN_RESOURCES:
        run_cmd(['%s delete' % res['res'],
                 '--project=%s' % PROJECT_ID] + res['args'])


@pytest.mark.integration
def test_relations_integration(integration_teardown):
    global _TEARDOWN_RESOURCES
    # create new dataset
    dataset = run_cmd(['dataset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=dataset-for-relation-2'])
    _TEARDOWN_RESOURCES.append({'res': 'dataset', 'args': [dataset.get('id')]})
    # create new AWS S3 fileset
    fileset = run_cmd(['fileset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=fileset-for-relation-2',
                       'aws-s3',
                       '--key=%s' % os.environ['JEXIA_CLI_TEST_AWS_KEY'],
                       '--secret=%s' % os.environ['JEXIA_CLI_TEST_AWS_SECRET'],
                       '--bucket=%s' % os.environ['JEXIA_CLI_TEST_AWS_BUCKET']
                       ])
    _TEARDOWN_RESOURCES.append({'res': 'fileset', 'args': [fileset.get('id')]})
    # get current relations
    relations = run_cmd(['relation list',
                         '-f=json',
                         '--project=%s' % PROJECT_ID])
    initial_number_of_relations = len(relations)
    if initial_number_of_relations > 0:
        assert set(RELATION_COLUMNS) == set(relations[0].keys())
    # create new relation to fileset
    fs_relation = run_cmd(['relation create',
                           '-f=json',
                           '--project=%s' % PROJECT_ID,
                           '--relation=MANY-ONE',
                           '--fileset=%s' % fileset['id']])
    _TEARDOWN_RESOURCES.append({'res': 'relation',
                                'args': ['--resource=fileset',
                                         fs_relation.get('id')]})
    assert set(['id', 'relation', 'fileset']) == set(fs_relation.keys())
    # create new relation to dataset
    ds_relation = run_cmd(['relation create',
                           '-f=json',
                           '--project=%s' % PROJECT_ID,
                           '--relation=MANY-ONE',
                           '--dataset=%s' % dataset['id']])
    _TEARDOWN_RESOURCES.append({'res': 'relation',
                                'args': ['--resource=dataset',
                                         ds_relation.get('id')]})
    assert set(['id', 'relation', 'dataset']) == set(ds_relation.keys())
    # list of relations
    relations = run_cmd(['relation list',
                         '-f=json',
                         '--project=%s' % PROJECT_ID])
    assert initial_number_of_relations + 2 == len(relations)
    assert set(RELATION_COLUMNS) == set(relations[0].keys())
    # delete relation to fileset
    output = run_cmd(['relation delete',
                      '--project=%s' % PROJECT_ID,
                      '--resource=fileset',
                      fs_relation['id']])
    assert '' == output
    # delete relation to dataset
    output = run_cmd(['relation delete',
                      '--project=%s' % PROJECT_ID,
                      '--resource=dataset',
                      ds_relation['id']])
    assert '' == output
    # check deletion
    relations = run_cmd(['relation list',
                         '-f=json',
                         '--project=%s' % PROJECT_ID])
    assert initial_number_of_relations == len(relations)
