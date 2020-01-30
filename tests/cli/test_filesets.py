import os
import pytest

from tests.cli import run_cmd


FILESET_COLUMNS = ['id', 'name', 'properties', 'inputs', 'provider']
FILESET_FIELD_COLUMNS = ['id', 'name', 'type', 'immutable', 'properties',
                         'constraints']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_CREATED_RESOURCE = None


@pytest.fixture()
def integration_teardown():
    yield
    if _CREATED_RESOURCE:
        run_cmd(['fileset delete', '--project=%s' % PROJECT_ID,
                 _CREATED_RESOURCE])


@pytest.mark.integration
def test_filesets_integration(integration_teardown):
    global _CREATED_RESOURCE
    # get current usersets
    filesets = run_cmd(['fileset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    initial_number_of_filesets = len(filesets)
    # create new AWS S3 fileset
    fileset = run_cmd(['fileset create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=test-integration',
                       'aws-s3',
                       '--key=%s' % os.environ['JEXIA_CLI_TEST_AWS_KEY'],
                       '--secret=%s' % os.environ['JEXIA_CLI_TEST_AWS_SECRET'],
                       '--bucket=%s' % os.environ['JEXIA_CLI_TEST_AWS_BUCKET']
                       ])
    _CREATED_RESOURCE = fileset.get('id')
    assert set(FILESET_COLUMNS) == set(fileset.keys())
    # list of filesets
    filesets = run_cmd(['fileset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_filesets + 1 == len(filesets)
    assert set(FILESET_COLUMNS) == set(filesets[0].keys())
    # update fileset
    fileset = run_cmd(['fileset update',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=test-integration-renamed',
                       fileset.get('id')])
    assert set(FILESET_COLUMNS) == set(fileset.keys())
    # list of fileset fields
    fields = run_cmd(['fileset field list',
                      '-f=json',
                      '--project=%s' % PROJECT_ID,
                      '--fileset=%s' % fileset['id']])
    assert 8 == len(fields)
    assert set(FILESET_FIELD_COLUMNS) == set(fields[0].keys())
    # create fileset field
    field = run_cmd(['fileset field create',
                     '-f=json',
                     '--project=%s' % PROJECT_ID,
                     '--fileset=%s' % fileset['id'],
                     '--name=test',
                     '--type=string',
                     '--constraint=min_length=1000',
                     '--constraint=required=true',
                     '--constraint=default=some-val'])
    assert set(FILESET_FIELD_COLUMNS) == set(field.keys())
    assert 'min_length=1000' in field['constraints']
    assert 'required=True' in field['constraints']
    assert 'default=some-val' in field['constraints']
    # update fileset field
    field = run_cmd(['fileset field update',
                     '-f=json',
                     '--project=%s' % PROJECT_ID,
                     '--fileset=%s' % fileset['id'],
                     '--constraint=required=false',
                     '--constraint=default=',
                     field['id']])
    assert set(FILESET_FIELD_COLUMNS) == set(field.keys())
    assert 'min_length=1000' == field['constraints']
    # delete fileset field
    output = run_cmd(['fileset field delete',
                      '--project=%s' % PROJECT_ID,
                      '--fileset=%s' % fileset['id'],
                      field['id']])
    assert '' == output
    # check deletion
    fields = run_cmd(['fileset field list',
                      '-f=json',
                      '--project=%s' % PROJECT_ID,
                      '--fileset=%s' % fileset['id']])
    assert 8 == len(fields)
    # delete fileset
    output = run_cmd(['fileset delete',
                      '--project=%s' % PROJECT_ID,
                      fileset['id']])
    assert '' == output
    # check deletion
    filesets = run_cmd(['fileset list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_filesets == len(filesets)
