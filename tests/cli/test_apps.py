import json
import os
import pytest

from tests.cli import run_cmd


APP_COLUMNS = ['id', 'repo_name', 'repo_url', 'env_vars', 'public_url']
DEPLOY_COLUMNS = ['id', 'app_id', 'info', 'status']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_CREATED_RESOURCE = None


@pytest.fixture()
def integration_teardown():
    yield
    if _CREATED_RESOURCE:
        run_cmd(['app delete', '--project=%s' % PROJECT_ID,
                 _CREATED_RESOURCE])


@pytest.mark.integration
def test_apps_integration(integration_teardown):
    global _CREATED_RESOURCE
    # get current apps
    apps = run_cmd(['app list',
                    '-f=json',
                    '--project=%s' % PROJECT_ID])
    initial_number_of_apps = len(apps)
    # create new app
    app = run_cmd(['app create',
                   '-f=json',
                   '--project=%s' % PROJECT_ID,
                   '--repo=https://github.com/jexia/test-node-app.git',
                   '--var=key1=val1',
                   '--var=key2=val2'])
    _CREATED_RESOURCE = app.get('id')
    assert set(APP_COLUMNS) == set(app.keys())
    assert app['public_url'] == 'https://%s.jexia.app' % app.get('id')
    variables = json.loads(app['env_vars'])
    assert variables['key1'] == 'val1'
    assert variables['key2'] == 'val2'
    # list of apps
    apps = run_cmd(['app list',
                    '-f=json',
                    '--project=%s' % PROJECT_ID])
    assert initial_number_of_apps + 1 == len(apps)
    assert set(APP_COLUMNS) == set(apps[0].keys())
    # update app
    app = run_cmd(['app update',
                   '-f=json',
                   '--project=%s' % PROJECT_ID,
                   '--repo=https://github.com/jexia/test-node-fake.git',
                   '--var=key1=',
                   '--var=key2=val3',
                   app['id']])
    assert set(APP_COLUMNS) == set(app.keys())
    assert 'test-node-fake.git' in app['repo_url']
    assert app['env_vars'] == '{"key2": "val3"}'
    # deploy application
    deployment = run_cmd(['app deploy',
                          '-f=json',
                          '--project=%s' % PROJECT_ID,
                          '--app=%s' % app['id'],
                          '--api-key=qwerty',
                          '--api-secret=qwerty'])
    assert set(DEPLOY_COLUMNS) == set(deployment.keys())
    # show deployment
    deployment = run_cmd(['app deploy show',
                          '-f=json',
                          '--project=%s' % PROJECT_ID,
                          '--app=%s' % app['id'],
                          deployment['id']])
    assert set(DEPLOY_COLUMNS + ['build_log', 'app_id', 'info']) == set(
        deployment.keys())
    # list of deployments
    deployments = run_cmd(['app deploy list',
                           '-f=json',
                           '--project=%s' % PROJECT_ID,
                           '--app=%s' % app['id']])
    assert set(DEPLOY_COLUMNS) == set(deployments[0].keys())
    # delete app
    output = run_cmd(['app delete',
                      '--project=%s' % PROJECT_ID,
                      app['id']])
    assert '' == output
    # check deletion
    apps = run_cmd(['app list',
                    '-f=json',
                    '--project=%s' % PROJECT_ID])
    assert initial_number_of_apps == len(apps)
