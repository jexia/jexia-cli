#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.formatters import formatter_fields
from jexia_cli.utils import with_authentication


LOG = logging.getLogger(__name__)


def formatter_provider(val):
    fields = []
    if not val:
        return ''
    for opt in val.get('options', []):
        fields.append('%s=%s' % (opt['key'], opt['value']))
    return '%s:' % val['id'] + ','.join(fields)


class List(ProjectListCommand):
    '''
    List of filesets
    '''

    columns = ['id', 'name', 'properties', 'inputs', 'provider']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'inputs': formatter_fields,
        'provider': formatter_provider,
    }

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/management/%s/bestla/fs' % parsed_args.project)
        return self.setup_columns(result or [])


class Create(ProjectShowCommand):
    '''
    Create new fileset
    '''

    columns = ['id', 'name', 'properties', 'inputs', 'provider']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'inputs': formatter_fields,
        'provider': formatter_provider,
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Fileset\'s name',
            required=True,
        )
        subparsers = parser.add_subparsers(help='Choose a provider')
        subparsers.required = True
        subparsers.dest = 'provider'
        subparsers.metavar = 'PROVIDER'
        # subparser for AWS S3 bucket provider
        aws_parser = subparsers.add_parser(
            'aws-s3',
            help='Amazone S3 bucket',
            add_help=False
        )
        aws_parser.add_argument(
            '--key',
            metavar='KEY',
            help='AWS key',
            required=True,
        )
        aws_parser.add_argument(
            '--secret',
            metavar='SECRET',
            help='AWS secret',
            required=True,
        )
        aws_parser.add_argument(
            '--bucket',
            metavar='BUCKET',
            help='AWS S3 bucket',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        if parsed_args.provider == 'aws-s3':
            opts = ['key', 'secret', 'bucket']
            options_data = list()
            for opt in opts:
                options_data.append({'key': opt,
                                     'value': getattr(parsed_args, opt)})
            provider_data = {
                'id': parsed_args.provider,
                'options': options_data,
                'valid': False
            }
        result = self.app.client.request(
            method='POST',
            url='/management/%s/bestla/fs' % parsed_args.project,
            data={'name': parsed_args.name,
                  'provider': provider_data})
        return self.setup_columns(result)


class Update(ProjectShowCommand):
    '''
    Update fileset
    '''

    columns = ['id', 'name', 'properties', 'inputs', 'provider']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'inputs': formatter_fields,
        'provider': formatter_provider,
    }

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Fileset\'s name',
            required=True,
        )
        parser.add_argument(
            'fileset',
            metavar="FILESET_ID",
            help='UUID of fileset which should be changed',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='PUT',
            url='/management/%s/bestla/fs/%s' % (parsed_args.project,
                                                 parsed_args.fileset),
            data={'name': parsed_args.name})
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete fileset
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'fileset',
            metavar="FILESET_ID",
            help='UUID of fileset which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url='/management/%s/bestla/fs/%s' % (parsed_args.project,
                                                 parsed_args.fileset))
