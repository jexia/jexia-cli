import os
import pytest

from tests.cli import run_cmd


CHANNEL_COLUMNS = ['id', 'name', 'type', 'immutable', 'properties']
PROJECT_ID = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
_CREATED_RESOURCE = None


@pytest.fixture()
def integration_teardown():
    yield
    if _CREATED_RESOURCE:
        run_cmd(['channel delete', '--project=%s' % PROJECT_ID,
                 _CREATED_RESOURCE])


@pytest.mark.integration
def test_channels_integration(integration_teardown):
    global _CREATED_RESOURCE
    # get current channels
    channels = run_cmd(['channel list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    initial_number_of_channels = len(channels)
    # create new channel
    channel = run_cmd(['channel create',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=test-integration'])
    _CREATED_RESOURCE = channel.get('id')
    assert set(CHANNEL_COLUMNS) == set(channel.keys())
    assert channel['properties'] == '{"store_messages": false}'
    # list of channels
    channels = run_cmd(['channel list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_channels + 1 == len(channels)
    assert set(CHANNEL_COLUMNS) == set(channels[0].keys())
    # update channel
    channel = run_cmd(['channel update',
                       '-f=json',
                       '--project=%s' % PROJECT_ID,
                       '--name=test-integration-2',
                       '--store-messages',
                       channel['id']])
    assert set(CHANNEL_COLUMNS) == set(channel.keys())
    assert channel['properties'] == '{"store_messages": true}'
    assert channel['name'] == 'test-integration-2'
    # delete channel
    output = run_cmd(['channel delete',
                      '--project=%s' % PROJECT_ID,
                      channel['id']])
    assert '' == output
    # check deletion
    channels = run_cmd(['channel list',
                        '-f=json',
                        '--project=%s' % PROJECT_ID])
    assert initial_number_of_channels == len(channels)
