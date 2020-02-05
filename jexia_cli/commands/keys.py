#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication


LOG = logging.getLogger(__name__)


class List(ProjectListCommand):
    '''
    List of keys
    '''

    columns = ['key', 'description']

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url='/management/%s/utgard/' % parsed_args.project)
        return self.setup_columns(result or [])


class Create(ProjectShowCommand):
    '''
    Create new key
    '''

    columns = ['key', 'description']

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='DESCRIPTION',
            help='Key\'s description',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST',
            url='/management/%s/utgard/' % parsed_args.project,
            data={
                "description": parsed_args.description,
            }
        )
        return self.setup_columns(result)


class Update(ProjectShowCommand):
    '''
    Update new key
    '''

    columns = ['key', 'description']

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='DESCRIPTION',
            help='Key\'s description',
            required=True,
        )
        parser.add_argument(
            'key',
            metavar="KEY_ID",
            help='UUID of key which should be updated',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='PUT',
            url='/management/%s/utgard/%s' % (parsed_args.project,
                                              parsed_args.key),
            data={
                "description": parsed_args.description,
            }
        )
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete key
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'key',
            metavar="KEY_ID",
            help='UUID of key which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url=('/management/%s/utgard/%s'
                 % (parsed_args.project, parsed_args.key)))
