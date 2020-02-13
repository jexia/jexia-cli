#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication
from jexia_sdk.http import HTTPClientError


LOG = logging.getLogger(__name__)
USERSET_ANY = 'ANY'
DISPLAY_SUBJECT_TYPES = {
    'ums': 'userset',
    'apk': 'API key',
}
ALLOWED_ACTIONS = ['delete', 'update', 'create', 'read']


def format_subjects(subjects):
    result = list()
    for sub in subjects:
        type, uuid = sub.split(':')
        if uuid == u'\u003c.*\u003e':
            uuid = USERSET_ANY
        result.append('%s: %s' % (DISPLAY_SUBJECT_TYPES[type], uuid))
    return '\n'.join(result)


class BasePolicyCommand(object):

    def _parse_policy_result(self, project_id, result):
        umsScheme = self.app.client.request(
            method='GET',
            url='/management/%s/midgard/schema' % project_id)
        ums = next((r['id'] for r in umsScheme if r['name'] == 'umsUsers'),
                   None)
        if not ums:
            raise HTTPClientError('Userset scheme not found')
        datasets = self.app.client.request(
            method='GET',
            url='/management/%s/mimir/ds' % project_id)
        datasets = [d['id'] for d in datasets]
        filesets = self.app.client.request(
            method='GET', url='/management/%s/bestla/fs' % project_id)
        filesets = [f['id'] for f in filesets]
        for policy in result:
            translated_resources = list()
            for resource in policy['resources']:
                if resource == ums:
                    translated_resources.append('All users')
                elif resource in datasets:
                    translated_resources.append('dataset: %s' % resource)
                elif resource in filesets:
                    translated_resources.append('fileset: %s' % resource)
                else:
                    translated_resources.append('unknown: %s' % resource)
            policy['resources'] = translated_resources
        return result

    def _parse_subjects(self, parsed_args):
        umsScheme = self.app.client.request(
            method='GET',
            url='/management/%s/midgard/schema' % parsed_args.project)
        ums = next((r['id'] for r in umsScheme if r['name'] == 'umsUsers'),
                   None)
        if not ums:
            raise HTTPClientError('Userset scheme not found')
        subjects = list()
        for userset in parsed_args.userset:
            if userset == USERSET_ANY:
                subjects.append('ums:<.*>')
            else:
                subjects.append('ums:%s' % userset)
        subjects += ['apk:%s' % k for k in parsed_args.api_key]
        if not subjects:
            raise HTTPClientError('at least one option of --userset, '
                                  '--api-key required')
        return subjects


class List(ProjectListCommand, BasePolicyCommand):
    '''
    List of policies
    '''

    columns = ['id', 'description', 'subjects', 'resources', 'actions']

    _formatters = {
        'subjects': format_subjects,
        'actions': lambda v: ', '.join(v),
        'resources': lambda v: '\n'.join(v),
    }

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url='/management/%s/rakshak/' % parsed_args.project)
        self._parse_policy_result(parsed_args.project, result)
        return self.setup_columns(result or [])


class Create(ProjectShowCommand, BasePolicyCommand):
    '''
    Create new policy
    '''

    columns = ['id', 'description', 'subjects', 'resources', 'actions']

    _formatters = {
        'subjects': format_subjects,
        'actions': lambda v: ', '.join(v),
        'resources': lambda v: '\n'.join(v),
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='DESCRIPTION',
            help='Policy description',
            required=True,
        )
        parser.add_argument(
            '--action',
            metavar='ACTION',
            action='append',
            help=('Allowed action for this resources (%s). This is repeatable'
                  ' option.' % ', '.join(ALLOWED_ACTIONS)),
            required=True,
            choices=ALLOWED_ACTIONS
        )
        parser.add_argument(
            '--userset',
            metavar='USERSET',
            action='append',
            help=('Userset that should has access to manage resources.'
                  'Can be UUID of userset or "%s" (as alias for "All '
                  'users"). This is repeatable option.' % USERSET_ANY),
            default=[],
        )
        parser.add_argument(
            '--api-key',
            metavar='APY_KEY',
            action='append',
            help=('UUID of API key that should has access to manage resources.'
                  'This is repeatable option.'),
            default=[],
        )
        parser.add_argument(
            '--resource',
            metavar='RESOURCE',
            action='append',
            help=('Dataset\'s or fileset\'s uuid which should be as a '
                  'resource in the policy. This is repeatable option.'),
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST',
            url='/management/%s/rakshak/' % parsed_args.project,
            data={'description': parsed_args.description,
                  'subjects': self._parse_subjects(parsed_args),
                  'resources': parsed_args.resource,
                  'actions': parsed_args.action,
                  'effect': 'allow'})
        self._parse_policy_result(parsed_args.project, [result])
        return self.setup_columns(result)


class Update(ProjectShowCommand, BasePolicyCommand):
    '''
    Update the policy
    '''

    columns = ['id', 'description', 'subjects', 'resources', 'actions']

    _formatters = {
        'subjects': format_subjects,
        'actions': lambda v: ', '.join(v),
        'resources': lambda v: '\n'.join(v),
    }

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='DESCRIPTION',
            help='Policy description',
            required=True,
        )
        parser.add_argument(
            '--action',
            metavar='ACTION',
            action='append',
            help=('Allowed action for this resources (%s). This is repeatable'
                  ' option.' % ', '.join(ALLOWED_ACTIONS)),
            required=True,
            choices=ALLOWED_ACTIONS
        )
        parser.add_argument(
            '--userset',
            metavar='USERSET',
            action='append',
            help=('Userset that should has access to manage resources.'
                  'Can be UUID of userset or "%s" (as alias for "All '
                  'users"). This is repeatable option.' % USERSET_ANY),
            default=[],
        )
        parser.add_argument(
            '--api-key',
            metavar='APY_KEY',
            action='append',
            help=('UUID of API kye that should has access to manage resources.'
                  'This is repeatable option.'),
            default=[],
        )
        parser.add_argument(
            '--resource',
            metavar='RESOURCE',
            action='append',
            help=('Dataset\'s or fileset\'s uuid which should be as a '
                  'resource in the policy. This is repeatable option.'),
            required=True,
        )
        parser.add_argument(
            'policy',
            metavar="POLICY_ID",
            help='UUID of policy which should be changed',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='PUT',
            url=('/management/%s/rakshak/%s'
                 % (parsed_args.project, parsed_args.policy)),
            data={'id': parsed_args.policy,
                  'description': parsed_args.description,
                  'subjects': self._parse_subjects(parsed_args),
                  'resources': parsed_args.resource,
                  'actions': parsed_args.action,
                  'effect': 'allow'})
        self._parse_policy_result(parsed_args.project, [result])
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete policy
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar="POLICY_ID",
            help='UUID of policy which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url='/management/%s/rakshak/%s' % (parsed_args.project,
                                               parsed_args.policy))
