import pytest

from tests.cli import run_cmd


@pytest.mark.integration
def test_projects():
    # get current projects
    cur_projects = run_cmd(['project list'], json_output=True)
    assert 0 == len(cur_projects)
    # create new project
    new_project = run_cmd(['project create',
                           '--name=integration'],
                          json_output=True)
    assert 'id' in new_project
    assert 'name' in new_project
    assert 'description' in new_project
    assert 'created_at' in new_project
    assert 'integration' == new_project['name']
    # get project
    project = run_cmd(['project show',
                       '%s' % new_project['id']],
                      json_output=True)
    assert 'id' in project
    assert 'name' in project
    assert 'description' in project
    assert 'created_at' in project
    assert 'collaborators' in project
    assert new_project['id'] == project['id']
    # delte project
    output = run_cmd(['project delete',
                      '%s' % new_project['id'],
                      '--yes-i-really-want-to-delete'])
    assert '' == output


@pytest.mark.integration
def teardown():
    for project in run_cmd(['project list'], json_output=True):
        run_cmd(['project delete',
                 '%s' % project['id'],
                 '--yes-i-really-want-to-delete'])
