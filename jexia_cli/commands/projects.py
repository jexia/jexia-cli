#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from jexia_cli.base import CLICommand, ListCommand, ShowCommand
from jexia_cli.formatters import format_timestamp_to_utc
from jexia_cli.utils import confirm_action, with_authentication

LOG = logging.getLogger(__name__)


class List(ListCommand):
    '''
    List of projects
    '''

    columns = ['id', 'name', 'description', 'created_at']
    _formatters = {"created_at": format_timestamp_to_utc}

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='LIMIT',
            type=int,
            default=10,
            help='Number of rows to show',
        )
        parser.add_argument(
            '--page',
            metavar='PAGE',
            type=int,
            default=0,
            help='Number of page to show',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/projects', limit=parsed_args.limit,
            page=parsed_args.page)
        return self.setup_columns(result['projects'] or [])


class Create(ShowCommand):
    '''
    Create new project
    '''

    columns = ['id', 'name', 'description', 'created_at']
    _formatters = {"created_at": format_timestamp_to_utc}

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Project\'s name',
            required=True,
        )
        parser.add_argument(
            '--description',
            metavar='DESCRIPTION',
            help='Project\'s description',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST', url='/project',
            data={'name': parsed_args.name,
                  'description': parsed_args.description})
        return self.setup_columns(result)


class Show(ShowCommand):
    '''
    Show project details
    '''

    columns = ['id', 'name', 'description', 'created_at', 'collaborators']
    _formatters = {"created_at": format_timestamp_to_utc}

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='PROJECT_ID',
            help='UUID of project which should be shown',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/project/%s' % parsed_args.project)
        return self.setup_columns(result)


class Delete(CLICommand):
    '''
    Delete project
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar="PROJECT_ID",
            help='UUID of project which should be deleted',
        )
        parser.add_argument(
            '--yes-i-really-want-to-delete',
            default=False,
            action='store_true',
            required=True,
        )
        return parser

    @with_authentication
    @confirm_action('delete')
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE', url='/project/%s' % parsed_args.project,
            data={'password': self.app.config['password']})
