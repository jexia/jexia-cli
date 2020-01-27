#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication
from jexia_sdk.http import HTTPClientError

LOG = logging.getLogger(__name__)
CONSTRAINTS = {
    'default': str,
    'required': lambda v: v == 'true',
    'max_value': float,
    'min_value': float,
    'lowercase': lambda v: v == 'true',
    'uppercase': lambda v: v == 'true',
    'alphanumeric': lambda v: v == 'true',
    'regexp': str,
    'alpha': lambda v: v == 'true',
    'numeric': lambda v: v == 'true',
    'min_length': int,
    'max_length': int,
}


def formatter_constraints(val):
    fields = []
    for con in val:
        fields.append('%s=%s' % (con['type'], con['value']))
    return ', '.join(fields)


class List(ProjectListCommand):
    '''
    Show fields of dataset
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'constraints': formatter_constraints,
    }

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            '--dataset',
            metavar="DATASET_ID",
            help='Dataset\'s ID',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/management/%s/mimir/ds' % parsed_args.project)
        ds = next((d for d in result if d['id'] == parsed_args.dataset), None)
        if not ds:
            raise HTTPClientError('Dataset %s not found' % parsed_args.dataset)
        return self.setup_columns(ds['inputs'] or [])


class Create(ProjectShowCommand):
    '''
    Create new field in dataset.
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'constraints': formatter_constraints,
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--dataset',
            metavar="DATASET_ID",
            help='Dataset\'s ID',
            required=True,
        )
        parser.add_argument(
            '--name',
            metavar='NAME',
            help='Field\'s name',
            required=True,
        )
        parser.add_argument(
            '--type',
            metavar='TYPE',
            help='Field\'s type',
            required=True,
            choices=['string', 'integer', 'float', 'date', 'datetime',
                     'boolean', 'json', 'uuid']
        )
        parser.add_argument(
            '--constraint',
            metavar='TYPE=VALUE',
            action='append',
            help=('Field\'s constraints, repeatable option (see documentation'
                  'to get more information)'),
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/management/%s/mimir/ds' % parsed_args.project)
        ds = next((d for d in result if d['id'] == parsed_args.dataset), None)
        if not ds:
            raise HTTPClientError('Dataset %s not found' % parsed_args.dataset)
        constraints = list()
        for con in parsed_args.constraint:
            try:
                name, val = con.split('=')
            except Exception:
                raise HTTPClientError('incorrect value for constraint, should'
                                      ' be key=value')
            if name not in CONSTRAINTS.keys():
                raise HTTPClientError('incorrect type of constraint %s'
                                      % name)
            try:
                val = CONSTRAINTS[name](val)
            except Exception:
                raise HTTPClientError('incorrect value for type %s: %s'
                                      % (name, val))
            if val:
                constraints.append({'type': name, 'value': val})
        result = self.app.client.request(
            method='POST',
            data={'name': parsed_args.name,
                  'type': parsed_args.type,
                  'constraints': constraints},
            url='/management/%s/mimir/ds/%s/field' % (parsed_args.project,
                                                      parsed_args.dataset))
        return self.setup_columns(result)


class Update(ProjectShowCommand):
    '''
    Update the field's constraints in dataset.
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'constraints': formatter_constraints,
    }

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            '--dataset',
            metavar="DATASET_ID",
            help='Dataset\'s ID',
            required=True,
        )
        parser.add_argument(
            '--constraint',
            metavar='TYPE=VALUE',
            action='append',
            help=('Field\'s constraints, repeatable option (see documentation'
                  'to get more information)'),
        )
        parser.add_argument(
            'field',
            metavar="FIELD_ID",
            help='UUID of field which should be updated',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET', url='/management/%s/mimir/ds' % parsed_args.project)
        ds = next((d for d in result if d['id'] == parsed_args.dataset), None)
        if not ds:
            raise HTTPClientError('Dataset %s not found' % parsed_args.dataset)
        field = next((f for f in ds['inputs'] if f['id'] == parsed_args.field),
                     None)
        if not field:
            raise HTTPClientError('Field %s not found' % parsed_args.field)
        constraints = {c['type']: c['value'] for c in field['constraints']}
        for con in parsed_args.constraint:
            try:
                name, val = con.split('=')
            except Exception:
                raise HTTPClientError('incorrect value for constraint, should'
                                      ' be key=value')
            if name not in CONSTRAINTS.keys():
                raise HTTPClientError('incorrect type of constraint %s'
                                      % name)
            try:
                val = CONSTRAINTS[name](val)
            except Exception:
                raise HTTPClientError('incorrect value for type %s: %s'
                                      % (name, val))
            constraints[name] = val
            if not val:
                constraints.pop(name)
        result = self.app.client.request(
            method='PUT',
            data=[{'type': k, 'value': v} for k, v in constraints.items()],
            url=('/management/%s/mimir/ds/%s/constraints/%s'
                 % (parsed_args.project,
                    parsed_args.dataset,
                    parsed_args.field)))
        field['constraints'] = result
        return self.setup_columns(field)


class Delete(ProjectCommand):
    '''
    Delete field from the dataset
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            '--dataset',
            metavar="DATASET_ID",
            help='Dataset\'s ID',
            required=True,
        )
        parser.add_argument(
            'field',
            metavar="FIELD_ID",
            help='UUID of field which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url='/management/%s/mimir/ds/%s/field/%s' % (parsed_args.project,
                                                         parsed_args.dataset,
                                                         parsed_args.field))
