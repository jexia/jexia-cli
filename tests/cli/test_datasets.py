import os
import pytest

from tests.cli import run_cmd


DATASET_COLUMNS = ['id', 'name', 'type', 'immutable', 'properties', 'inputs',
                   'outputs']
DATASET_FIELD_COLUMNS = ['id', 'name', 'type', 'immutable', 'properties',
                         'constraints']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_CREATED_RESOURCE = None


@pytest.fixture()
def integration_teardown():
    yield
    if _CREATED_RESOURCE:
        run_cmd(['dataset delete', '--project=%s' % PROJECT_ID,
                 _CREATED_RESOURCE])


@pytest.mark.integration
def test_datasets_integration(integration_teardown):
    global _CREATED_RESOURCE
    # get current datasets
    datasets = run_cmd(['dataset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    initial_number_of_datasets = len(datasets)
    # create new dataset
    dataset = run_cmd(['dataset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=test-integration'])
    _CREATED_RESOURCE = dataset.get('id')
    assert set(DATASET_COLUMNS) == set(dataset.keys())
    # list of datasets
    datasets = run_cmd(['dataset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_datasets + 1 == len(datasets)
    assert set(DATASET_COLUMNS) == set(datasets[0].keys())
    # list of dataset fields
    fields = run_cmd(['dataset field list',
                      '-f=json',
                      '--project=%s' % PROJECT_ID,
                      '--dataset=%s' % dataset['id']])
    assert 3 == len(fields)
    assert set(DATASET_FIELD_COLUMNS) == set(fields[0].keys())
    # create dataset field
    field = run_cmd(['dataset field create',
                     '-f=json',
                     '--project=%s' % PROJECT_ID,
                     '--dataset=%s' % dataset['id'],
                     '--name=test',
                     '--type=string',
                     '--constraint=min_length=1000',
                     '--constraint=required=true',
                     '--constraint=default=some-val'])
    assert set(DATASET_FIELD_COLUMNS) == set(field.keys())
    assert 'min_length=1000' in field['constraints']
    assert 'required=True' in field['constraints']
    assert 'default=some-val' in field['constraints']
    # update dataset field
    field = run_cmd(['dataset field update',
                     '-f=json',
                     '--project=%s' % PROJECT_ID,
                     '--dataset=%s' % dataset['id'],
                     '--constraint=required=false',
                     '--constraint=default=',
                     field['id']])
    assert set(DATASET_FIELD_COLUMNS) == set(field.keys())
    assert 'min_length=1000' == field['constraints']
    # delete dataset field
    output = run_cmd(['dataset field delete',
                      '--project=%s' % PROJECT_ID,
                      '--dataset=%s' % dataset['id'],
                      field['id']])
    assert '' == output
    # check deletion
    fields = run_cmd(['dataset field list',
                      '-f=json',
                      '--project=%s' % PROJECT_ID,
                      '--dataset=%s' % dataset['id']])
    assert 3 == len(fields)
    # delete dataset
    output = run_cmd(['dataset delete',
                      '--project=%s' % PROJECT_ID,
                      dataset['id']])
    assert '' == output
    # check deletion
    datasets = run_cmd(['dataset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_datasets == len(datasets)
