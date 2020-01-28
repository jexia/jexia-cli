import mock
import pytest

from tests.cli import run_cmd, SHELL_CONFIG


PROJECT_LIST_RESP = {
    'accounts': [{
        'account_owner_id': '3054b850-a1d9-4860-8b4e-2b63b7322907',
        'plan_id': 'cbaeb217-aadf-41c3-87c9-8b8bb0a29969',
        'plan_name': 'Hobby',
        'plan_amount': 0,
        'is_free_plan': True
    }],
    'max_number_free': '3',
    'projects': [{
        'id': '3054b850-a1d9-4860-8b4e-2b63b7322907',
        'owner': '284e31e6-b21b-418f-b19e-21d1c741db63',
        'is_owner': True,
        'name': 'integration',
        'description': '<nil>',
        'created_at': 1580208898
    }]
}
PROJECT_CREATE_RESP = {
    'is_owner': 'true',
    'description': '<nil>',
    'created_at': '1580210078',
    'owner': '284e31e6-b21b-418f-b19e-21d1c741db63',
    'id': '5f0c9f45-cbd8-4054-8158-b64c39fb8be9',
    'name': 'integration'
}
PROJECT_SHOW_RESP = {
    'collaborators': None,
    'is_owner': 'true',
    'name': 'integration',
    'created_at': '1580210078',
    'owner': '284e31e6-b21b-418f-b19e-21d1c741db63',
    'id': '5f0c9f45-cbd8-4054-8158-b64c39fb8be9',
    'description': '<nil>'
}


@mock.patch('jexia_sdk.http.HTTPClient.request',
            return_value=PROJECT_LIST_RESP)
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_list(mock_auth, mock_req):
    cur_projects = run_cmd(['project list'])
    mock_req.assert_called_once_with(
        limit=10, method='GET', page=0, url='/projects')
    resp = [
        {
            "id": "3054b850-a1d9-4860-8b4e-2b63b7322907",
            "name": "integration",
            "description": "",
            "created_at": "2020-01-28 13:54:58"
        }
    ]
    assert cur_projects == resp


@mock.patch('jexia_sdk.http.HTTPClient.request',
            return_value={'projects': []})
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_list_options(mock_auth, mock_req):
    cur_projects = run_cmd(['project list', '--limit=100', '--page=20'])
    mock_req.assert_called_once_with(
        limit=100, method='GET', page=20, url='/projects')
    assert cur_projects == []


@mock.patch('jexia_sdk.http.HTTPClient.request',
            return_value=PROJECT_CREATE_RESP)
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_create(mock_auth, mock_req):
    res = run_cmd(['project create', '--name=test'])
    mock_req.assert_called_once_with(
        method='POST', url='/project',
        data={'name': 'test', 'description': None})
    resp = {
        'id': '5f0c9f45-cbd8-4054-8158-b64c39fb8be9',
        'name': 'integration',
        'description': '',
        'created_at': '2020-01-28 14:14:38'
    }
    assert res == resp


@mock.patch('jexia_sdk.http.HTTPClient.request', return_value=[])
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_create_options(mock_auth, mock_req):
    run_cmd(['project create', '--name=test', '--description=descr'])
    mock_req.assert_called_once_with(
        method='POST', url='/project',
        data={'name': 'test', 'description': 'descr'})


@mock.patch('jexia_sdk.http.HTTPClient.request', return_value=[])
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_create_options_fail(mock_auth, mock_req, capsys):
    with pytest.raises(SystemExit):
        run_cmd(['project create'])
    _, err = capsys.readouterr()
    assert 'arguments are required: --name' in err


@mock.patch('jexia_sdk.http.HTTPClient.request',
            return_value=PROJECT_SHOW_RESP)
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_show(mock_auth, mock_req):
    res = run_cmd(['project show', 'test'])
    mock_req.assert_called_once_with(
        method='GET', url='/project/test')
    resp = {
        'id': '5f0c9f45-cbd8-4054-8158-b64c39fb8be9',
        'name': 'integration',
        'description': '',
        'created_at': '2020-01-28 14:14:38',
        'collaborators': None
    }
    assert res == resp


@mock.patch('jexia_sdk.http.HTTPClient.request', return_value=[])
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_show_options_fail(mock_auth, mock_req, capsys):
    with pytest.raises(SystemExit):
        run_cmd(['project show'], json_output=False)
    _, err = capsys.readouterr()
    assert 'arguments are required: PROJECT_ID' in err


@mock.patch('jexia_sdk.http.HTTPClient.request', return_value='')
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_delete(mock_auth, mock_req):
    res = run_cmd(['project delete', 'test', '--yes-i-really-want-to-delete'],
                  json_output=False)
    mock_req.assert_called_once_with(
        method='DELETE', url='/project/test',
        data={'password': SHELL_CONFIG['password']})
    assert res == ''


@mock.patch('jexia_sdk.http.HTTPClient.request', return_value='')
@mock.patch('jexia_sdk.http.HTTPClient.auth_management')
def test_project_delete_options_fail(mock_auth, mock_req, capsys):
    with pytest.raises(SystemExit):
        run_cmd(['project delete'], json_output=False)
    _, err = capsys.readouterr()
    assert 'arguments are required: PROJECT_ID' in err


@pytest.mark.integration
def test_projects_integration():
    # get current projects
    cur_projects = run_cmd(['project list'])
    # create new project
    new_project = run_cmd(['project create',
                           '--name=integration'])
    assert 'id' in new_project
    assert 'name' in new_project
    assert 'description' in new_project
    assert 'created_at' in new_project
    assert 'integration' == new_project['name']
    # get project
    project = run_cmd(['project show',
                       '%s' % new_project['id']])
    assert 'id' in project
    assert 'name' in project
    assert 'description' in project
    assert 'created_at' in project
    assert 'collaborators' in project
    assert new_project['id'] == project['id']
    # check number of projects
    projects = run_cmd(['project list'])
    assert len(cur_projects) + 1 == len(projects)
    # delete project
    output = run_cmd(['project delete',
                      '%s' % new_project['id'],
                      '--yes-i-really-want-to-delete'], json_output=False)
    assert '' == output
    # check number of projects
    projects = run_cmd(['project list'])
    assert len(cur_projects) == len(projects)
