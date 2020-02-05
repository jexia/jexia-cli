#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication


LOG = logging.getLogger(__name__)


class List(ProjectListCommand):
    '''
    List of channels
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties']
    _formatters = {
        'properties': lambda v: json.dumps(v),
    }

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url='/management/%s/sharky/channel' % parsed_args.project)
        return self.setup_columns(result or [])


class Create(ProjectShowCommand):
    '''
    Create new channel
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties']
    _formatters = {
        'properties': lambda v: json.dumps(v),
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Channel\'s name',
            required=True,
        )
        parser.add_argument(
            '--store-messages',
            action='store_true',
            default=False,
            help=('Store all messages that have been sent through the channel'
                  ' in the persistent storage'),
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST',
            url='/management/%s/sharky/channel' % parsed_args.project,
            data={
                "name": parsed_args.name,
                "properties": {"store_messages": parsed_args.store_messages},
            }
        )
        return self.setup_columns(result)


class Update(ProjectShowCommand):
    '''
    Update the channel
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties']
    _formatters = {
        'properties': lambda v: json.dumps(v),
    }

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Channel\'s name',
            required=True,
        )
        parser.add_argument(
            '--store-messages',
            action='store_true',
            default=False,
            help=('Store all messages that have been sent through the channel'
                  ' in the persistent storage'),
        )
        parser.add_argument(
            'channel',
            metavar="CHANNEL_ID",
            help='UUID of channel which should be updated',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='PUT',
            url=('/management/%s/sharky/channel/%s'
                 % (parsed_args.project, parsed_args.channel)),
            data={
                "id": parsed_args.channel,
                "name": parsed_args.name,
                "properties": {"store_messages": parsed_args.store_messages},
            }
        )
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete channel
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'channel',
            metavar="CHANNEL_ID",
            help='UUID of channel which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url=('/management/%s/sharky/channel/%s'
                 % (parsed_args.project, parsed_args.channel)))
