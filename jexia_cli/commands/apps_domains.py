#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication


LOG = logging.getLogger(__name__)


class List(ProjectListCommand):
    '''
    List of application's domains
    '''

    columns = ['id', 'domain']

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            '--app',
            metavar="APP_ID",
            help='UUID of app',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url=('/project/%s/app/%s/domain'
                               % (parsed_args.project, parsed_args.app))
        )
        return self.setup_columns(result.get('domains') or [])


class Create(ProjectShowCommand):
    '''
    Create new domain for an application
    '''

    columns = ['id', 'domain']

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--app',
            metavar="APP_ID",
            help='UUID of app',
            required=True,
        )
        parser.add_argument(
            '--fqdn',
            metavar='FQDN',
            help='FQDN for application',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST',
            url=('/project/%s/app/%s/domain'
                 % (parsed_args.project, parsed_args.app)),
            data={'domain': parsed_args.fqdn}
        )
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete application's domain
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            '--app',
            metavar="APP_ID",
            help='UUID of app',
            required=True,
        )
        parser.add_argument(
            'domain',
            metavar="DOMAIN_ID",
            help='UUID of domain which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url=('/project/%s/app/%s/domain/%s'
                 % (parsed_args.project, parsed_args.app,
                    parsed_args.domain))
        )
