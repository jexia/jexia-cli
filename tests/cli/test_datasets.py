import pytest

from tests.cli import run_cmd


@pytest.mark.integration
def test_datasets_integration():
    # create new project
    new_project = run_cmd(['project create',
                           '--name=integration'])
    # create new dataset
    dataset = run_cmd(['dataset create',
                       '--project=%s' % new_project['id'],
                       '--name=test'])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'inputs',
               'outputs']
    for column in columns:
        assert column in dataset
    # list of datasets
    datasets = run_cmd(['dataset list',
                        '--project=%s' % new_project['id']])
    assert 1 == len(datasets)
    # list of dataset fields
    fields = run_cmd(['dataset field list',
                      '--project=%s' % new_project['id'],
                      '--dataset=%s' % dataset['id']])
    assert 3 == len(fields)
    # create dataset field
    field = run_cmd(['dataset field create',
                     '--project=%s' % new_project['id'],
                     '--dataset=%s' % dataset['id'],
                     '--name=test',
                     '--type=string',
                     '--constraint=min_length=1000',
                     '--constraint=required=true',
                     '--constraint=default=some-val'])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    for column in columns:
        assert column in field
    assert 'min_length=1000' in field['constraints']
    assert 'required=True' in field['constraints']
    assert 'default=some-val' in field['constraints']

    # update dataset field
    field = run_cmd(['dataset field update',
                     '--project=%s' % new_project['id'],
                     '--dataset=%s' % dataset['id'],
                     '--constraint=required=false',
                     '--constraint=default=',
                     field['id']])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    for column in columns:
        assert column in field
    assert 'min_length=1000' == field['constraints']
    # delete dataset field
    output = run_cmd(['dataset field delete',
                      '--project=%s' % new_project['id'],
                      '--dataset=%s' % dataset['id'],
                      field['id']], json_output=False)
    assert '' == output
    # check deletion
    fields = run_cmd(['dataset field list',
                      '--project=%s' % new_project['id'],
                      '--dataset=%s' % dataset['id']])
    assert 3 == len(fields)
    # delete dataset
    output = run_cmd(['dataset delete',
                      '--project=%s' % new_project['id'],
                      dataset['id']], json_output=False)
    assert '' == output
    # check deletion
    datasets = run_cmd(['dataset list',
                        '--project=%s' % new_project['id']])
    assert 0 == len(datasets)
    # delete project
    run_cmd(['project delete',
             '%s' % new_project['id'],
             '--yes-i-really-want-to-delete'], json_output=False)
