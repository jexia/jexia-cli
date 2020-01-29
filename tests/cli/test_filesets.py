import os
import pytest

from tests.cli import run_cmd


@pytest.mark.integration
def test_filesets_integration():
    project_id = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
    # create new AWS S3 fileset
    fileset = run_cmd(['fileset create',
                       '-f=json',
                       '--project=%s' % project_id,
                       '--name=test',
                       'aws-s3',
                       '--key=%s' % os.environ['JEXIA_CLI_TEST_AWS_KEY'],
                       '--secret=%s' % os.environ['JEXIA_CLI_TEST_AWS_SECRET'],
                       '--bucket=%s' % os.environ['JEXIA_CLI_TEST_AWS_BUCKET']
                       ])
    columns = ['id', 'name', 'properties', 'inputs', 'provider']
    for column in columns:
        assert column in fileset
    # list of filesets
    filesets = run_cmd(['fileset list',
                        '-f=json',
                        '--project=%s' % project_id])
    assert 1 == len(filesets)
    # list of fileset fields
    fields = run_cmd(['fileset field list',
                      '-f=json',
                      '--project=%s' % project_id,
                      '--fileset=%s' % fileset['id']])
    assert 8 == len(fields)
    # create fileset field
    field = run_cmd(['fileset field create',
                     '-f=json',
                     '--project=%s' % project_id,
                     '--fileset=%s' % fileset['id'],
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

    # update fileset field
    field = run_cmd(['fileset field update',
                     '-f=json',
                     '--project=%s' % project_id,
                     '--fileset=%s' % fileset['id'],
                     '--constraint=required=false',
                     '--constraint=default=',
                     field['id']])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    for column in columns:
        assert column in field
    assert 'min_length=1000' == field['constraints']
    # delete fileset field
    output = run_cmd(['fileset field delete',
                      '--project=%s' % project_id,
                      '--fileset=%s' % fileset['id'],
                      field['id']])
    assert '' == output
    # check deletion
    fields = run_cmd(['fileset field list',
                      '-f=json',
                      '--project=%s' % project_id,
                      '--fileset=%s' % fileset['id']])
    assert 8 == len(fields)
    # delete fileset
    output = run_cmd(['fileset delete',
                      '--project=%s' % project_id,
                      fileset['id']])
    assert '' == output
    # check deletion
    filesets = run_cmd(['fileset list',
                        '-f=json',
                        '--project=%s' % project_id])
    assert 0 == len(filesets)
