#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import abc
import six
from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

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


def get_dict_properties(item, fields, mixed_case_fields=None, formatters=None):
    """Return a tuple containing the item properties.

    :param item: a single dict resource
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name] if field_name in item else ''
        if data == '<nil>':
            data = ''
        if field in formatters:
            data = formatters[field](data)
        row.append(data)
    return tuple(row)


class CLICommand(Command):
    logger = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        pass


@six.add_metaclass(abc.ABCMeta)
class DisplayCommand(CLICommand):
    columns = []
    _formatters = {}

    def setup_columns(self, data):
        pass


class ShowCommand(DisplayCommand, ShowOne):

    def setup_columns(self, data):
        return (
            self.columns,
            get_dict_properties(
                data,
                self.columns,
                formatters=self._formatters
            ),
        )


class ListCommand(DisplayCommand, Lister):

    def setup_columns(self, data):
        return (
            self.columns,
            (
                get_dict_properties(
                    item,
                    self.columns,
                    formatters=self._formatters,
                ) for item in data),
        )


class ProjectCommand(CLICommand):

    def get_parser(self, prog_name):
        parser = super(ProjectCommand, self).get_parser(prog_name)
        if not self.app or not self.app.interactive_mode or \
                not self.app.context.get('project'):
            parser.add_argument(
                '--project',
                metavar='PROJECT_ID',
                help='Project''s ID',
                required=True,
            )
        else:
            parser.add_argument(
                '--project',
                metavar='PROJECT_ID',
                help='Project''s ID',
                required=False,
                default=self.app.context.get('project'),
            )
        return parser


class ProjectListCommand(ListCommand, ProjectCommand):

    pass


class ProjectShowCommand(ShowCommand, ProjectCommand):

    pass


class ProjectServiceFieldList(ProjectListCommand):

    def get_parser(self, prog_name):
        parser = super(ProjectServiceFieldList, self).get_parser(prog_name)
        parser.add_argument(
            '--%s' % self.resource,
            metavar='%s_ID' % self.resource.upper(),
            help='%s\'s ID' % self.resource.capitalize(),
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        resource_id = getattr(parsed_args, self.resource)
        result = self.app.client.request(
            method='GET',
            url='/management/%s/%s' % (parsed_args.project, self.svc_url))
        rs_data = next((r for r in result if r['id'] == resource_id), None)
        if not rs_data:
            raise HTTPClientError(
                '%s %s not found' % (self.resource.capitalize(),
                                     resource_id))
        return self.setup_columns(rs_data['inputs'] or [])


class ProjectServiceFieldCommand(ProjectShowCommand):

    def get_parser(self, prog_name):
        parser = super(ProjectServiceFieldCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--%s' % self.resource,
            metavar='%s_ID' % self.resource.upper(),
            help='%s\'s ID' % self.resource.capitalize(),
            required=True,
        )
        if self.field_action == 'create':
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
        if self.field_action == 'update':
            parser.add_argument(
                'field',
                metavar="FIELD_ID",
                help='UUID of field which should be updated',
            )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        resource_id = getattr(parsed_args, self.resource)
        result = self.app.client.request(
            method='GET',
            url='/management/%s/%s' % (parsed_args.project, self.svc_url))
        rs_data = next((r for r in result if r['id'] == resource_id), None)
        if not rs_data:
            raise HTTPClientError(
                '%s %s not found' % (self.resource.capitalize(),
                                     resource_id))
        if self.field_action == 'create':
            result = self._action_create(
                parsed_args.constraint, parsed_args.name, parsed_args.type,
                parsed_args.project, resource_id)
        if self.field_action == 'update':
            result = self._action_update(
                parsed_args.constraint, parsed_args.project, parsed_args.field,
                resource_id, rs_data)
        return self.setup_columns(result)

    def _action_create(self, opt_constraint, opt_name, opt_type, opt_project,
                       resource_id):
        constraints = list()
        for con in opt_constraint:
            name, val = self._parse_constraint(con)
            if val:
                constraints.append({'type': name, 'value': val})
        return self.app.client.request(
            method='POST',
            data={'name': opt_name,
                  'type': opt_type,
                  'constraints': constraints},
            url='/management/%s/%s/%s/field' % (opt_project,
                                                self.svc_url,
                                                resource_id)
        )

    def _action_update(self, opt_constraint, opt_project, opt_field,
                       resource_id, resource_data):
        field = next((f for f in resource_data['inputs']
                      if f['id'] == opt_field), None)
        if not field:
            raise HTTPClientError('Field %s not found' % opt_field)
        constraints = {c['type']: c['value'] for c in field['constraints']}
        for con in opt_constraint:
            name, val = self._parse_constraint(con)
            constraints[name] = val
            if not val:
                constraints.pop(name)
        result = self.app.client.request(
            method='PUT',
            data=[{'type': k, 'value': v} for k, v in constraints.items()],
            url=('/management/%s/%s/%s/constraints/%s'
                 % (opt_project,
                    self.svc_url,
                    resource_id,
                    opt_field)))
        field['constraints'] = result
        return field

    def _parse_constraint(self, constraint):
        try:
            name, val = constraint.split('=')
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
        return name, val


class ProjectServiceFieldDelete(ProjectCommand):

    def get_parser(self, prog_name):
        parser = super(ProjectServiceFieldDelete, self).get_parser(prog_name)
        parser.add_argument(
            '--%s' % self.resource,
            metavar='%s_ID' % self.resource.upper(),
            help='%s\'s ID' % self.resource.capitalize(),
            required=True,
        )
        parser.add_argument(
            'field',
            metavar="FIELD_ID",
            help='UUID of field which should be updated',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url=('/management/%s/%s/%s/field/%s'
                 % (parsed_args.project, self.svc_url,
                    getattr(parsed_args, self.resource),
                    parsed_args.field)))
