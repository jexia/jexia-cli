#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication


LOG = logging.getLogger(__name__)


class List(ProjectListCommand):
    '''
    List of usersets
    '''

    columns = ['id', 'email', 'active', 'created_at', 'updated_at']

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url='/management/%s/midgard/users' % parsed_args.project)
        return self.setup_columns(result or [])


class Create(ProjectShowCommand):
    '''
    Create new userset
    '''

    columns = ['id', 'email', 'active', 'created_at', 'updated_at']

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--email',
            metavar='EMAIL',
            help='Userset\'s email',
            required=True,
        )
        parser.add_argument(
            '--password',
            metavar='PASSWORD',
            help='Userset\'s password',
            required=True,
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Create disabled Userset',
            default=False,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST',
            url='/management/%s/midgard/users' % parsed_args.project,
            data={'email': parsed_args.email,
                  'password': parsed_args.password,
                  'active': not parsed_args.inactive})
        return self.setup_columns(result)


class Update(ProjectShowCommand):
    '''
    Update the userset
    '''

    columns = ['id', 'email', 'active', 'created_at', 'updated_at']

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.active = None
        parser.add_argument(
            '--activate',
            action='store_true',
            dest='active',
            help='Activate userset',
        )
        parser.add_argument(
            '--deactivate',
            action='store_false',
            dest='active',
            help='Deactivate userset',
        )
        parser.add_argument(
            '--password',
            metavar='PASSWORD',
            help='New userset\'s password',
        )
        parser.add_argument(
            'userset',
            metavar="USERSET_ID",
            help='UUID of userset which should be changedd',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        data = {'id': parsed_args.userset}
        if parsed_args.active is not None:
            data['active'] = parsed_args.active
        if parsed_args.password is not None:
            data['password'] = parsed_args.password
        result = self.app.client.request(
            method='PATCH',
            url='/management/%s/midgard/users/%s' % (parsed_args.project,
                                                     parsed_args.userset),
            data=data)
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete userset
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'userset',
            metavar="DATASET_ID",
            help='UUID of userset which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url='/management/%s/midgard/users/%s' % (parsed_args.project,
                                                     parsed_args.userset))
