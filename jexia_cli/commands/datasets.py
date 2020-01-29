#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.formatters import formatter_fields
from jexia_cli.utils import with_authentication


LOG = logging.getLogger(__name__)


class List(ProjectListCommand):
    '''
    List of datasets
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'inputs',
               'outputs']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'inputs': formatter_fields,
        'outputs': formatter_fields,
    }

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/management/%s/mimir/ds' % parsed_args.project)
        return self.setup_columns(result or [])


class Create(ProjectShowCommand):
    '''
    Create new dataset
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'inputs',
               'outputs']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'inputs': formatter_fields,
        'outputs': formatter_fields,
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Dataset\'s name',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST', url='/management/%s/mimir/ds' % parsed_args.project,
            data={'name': parsed_args.name})
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete dataset
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'dataset',
            metavar="DATASET_ID",
            help='UUID of dataset which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url='/management/%s/mimir/ds/%s' % (parsed_args.project,
                                                parsed_args.dataset))
