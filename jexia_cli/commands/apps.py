#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication
from jexia_sdk.http import HTTPClientError


LOG = logging.getLogger(__name__)
APP_HOSTING_DOMAIN = 'jexia.app'


class List(ProjectListCommand):
    '''
    List of apps
    '''

    columns = ['id', 'repo_name', 'repo_url', 'env_vars', 'public_url']
    _formatters = {
        'env_vars': lambda v: json.dumps(v),
    }

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url='/project/%s/app' % parsed_args.project)
        apps = result.get('applications') or []
        for app in apps:
            app['public_url'] = ('https://%s.%s'
                                 % (app['id'], APP_HOSTING_DOMAIN))
        return self.setup_columns(apps)


class Create(ProjectShowCommand):
    '''
    Create new app
    '''

    columns = ['id', 'repo_name', 'repo_url', 'env_vars', 'public_url']
    _formatters = {
        'env_vars': lambda v: json.dumps(v),
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--repo',
            metavar='REPO',
            help='App\'s repository',
            required=True,
        )
        parser.add_argument(
            '--var',
            metavar='KEY=VALUE',
            action='append',
            default=[],
            help=('Environment variables for the application. This is '
                  'repeatable option.'),
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        env_vars = dict()
        for opt in parsed_args.var:
            try:
                key, val = opt.split('=')
            except Exception:
                raise HTTPClientError('incorrect value for --var option, '
                                      'should be key=value')
            env_vars[key] = val
        result = self.app.client.request(
            method='POST',
            url='/project/%s/app' % parsed_args.project,
            data={
                "env_vars": env_vars,
                "repo_url": parsed_args.repo,
            }
        )
        if result:
            result['public_url'] = ('https://%s.%s'
                                    % (result['id'], APP_HOSTING_DOMAIN))
        return self.setup_columns(result)


class Update(ProjectShowCommand):
    '''
    Update application
    '''

    columns = ['id', 'repo_name', 'repo_url', 'env_vars', 'public_url']
    _formatters = {
        'env_vars': lambda v: json.dumps(v),
    }

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            '--repo',
            metavar='REPO',
            help='App\'s repository',
        )
        parser.add_argument(
            '--var',
            metavar='KEY=VALUE',
            action='append',
            default=[],
            help=('Environment variables for the application. This is '
                  'repeatable option.'),
        )
        parser.add_argument(
            'app',
            metavar="APP_ID",
            help='UUID of app which should be updated',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url='/project/%s/app' % parsed_args.project)
        app = next((a for a in result['applications']
                    if a['id'] == parsed_args.app), None)
        if not app:
            raise HTTPClientError(
                'application %s not found' % parsed_args.app)
        repo_url = parsed_args.repo or app['repo_url']
        env_vars = app['env_vars']
        for opt in parsed_args.var:
            try:
                key, val = opt.split('=')
            except Exception:
                raise HTTPClientError('incorrect value for --var option, '
                                      'should be key=value')
            if val == '':
                if key in env_vars:
                    env_vars.pop(key)
                else:
                    raise HTTPClientError('incorrect value for --var option, '
                                          'value or variable cannot be empty')
            else:
                env_vars[key] = val
        result = self.app.client.request(
            method='PATCH',
            url='/project/%s/app/%s' % (parsed_args.project, parsed_args.app),
            data={
                "env_vars": env_vars,
                "repo_url": repo_url,
            }
        )
        result['public_url'] = 'https://%s' % result['public_url']
        return self.setup_columns(result)


class Delete(ProjectCommand):
    '''
    Delete app
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'app',
            metavar="APP_ID",
            help='UUID of app which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.app.client.request(
            method='DELETE',
            url=('/project/%s/app/%s'
                 % (parsed_args.project, parsed_args.app)))
