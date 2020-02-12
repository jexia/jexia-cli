#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import itertools
from threading import Thread, Event

from jexia_cli.base import ProjectListCommand, ProjectShowCommand
from jexia_cli.utils import with_authentication
from jexia_sdk.http import HTTPClientError


LOG = logging.getLogger(__name__)
STATUSES = {
    '0': 'Unknown',
    '1': 'In progress',
    '2': 'Success',
    '3': 'Error',
}


class List(ProjectListCommand):
    '''
    List application deployments
    '''

    columns = ['id', 'info', 'app_id', 'status']
    _formatters = {
        'status': lambda v: STATUSES.get(v, 'Unknown'),
    }

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
            method='GET',
            url=('/project/%s/app/%s/deploy'
                 % (parsed_args.project, parsed_args.app)))
        deployments = result.get('deployments') or []
        return self.setup_columns(deployments)


class Show(ProjectShowCommand):
    '''
    Show application deployment with build logs
    '''

    columns = ['id', 'app_id', 'info', 'status', 'build_log']
    _formatters = {
        'status': lambda v: STATUSES.get(v, 'Unknown'),
    }

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument(
            '--app',
            metavar="APP_ID",
            help='UUID of app to show deployment',
            required=True,
        )
        parser.add_argument(
            'deployment',
            metavar="DEPLOYMENT_ID",
            help='UUID of deployment to show details',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='GET',
            url=('/project/%s/app/%s/deploy'
                 % (parsed_args.project, parsed_args.app)))
        deployment = next((d for d in result['deployments']
                           if d['id'] == parsed_args.deployment), None)
        if not deployment:
            raise HTTPClientError(
                'deployment %s not found' % parsed_args.deployment)
        return self.setup_columns(deployment)


class Create(ProjectShowCommand):
    '''
    Deploy the application
    '''

    columns = ['id', 'info', 'app_id', 'status']
    _formatters = {
        'status': lambda v: STATUSES.get(v, 'Unknown'),
    }

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--api-key',
            metavar='API_KEY',
            default='',
            help='API key for application',
        )
        parser.add_argument(
            '--api-secret',
            metavar='API_SECRET',
            default='',
            help='API secret for application',
        )
        parser.add_argument(
            '--skip-build',
            action='store_true',
            default=False,
            help=('Skip build stage and just update env variables or domains'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help=('Wait deployment status success or error'),
        )
        parser.add_argument(
            '--app',
            metavar="APP_ID",
            help='UUID of app which should be deployed',
            required=True,
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        result = self.app.client.request(
            method='POST',
            url=('/project/%s/app/%s/deploy'
                 % (parsed_args.project, parsed_args.app)),
            data={
                'api_key': parsed_args.api_key,
                'api_secret': parsed_args.api_secret,
                'skip_build': parsed_args.skip_build,
            }
        )
        if not parsed_args.wait:
            return self.setup_columns(result)
        else:
            # We have to fetch deployment status via API instead of websockets
            # because Python's websocket library doesn't work with Python 2.7
            # and with Jexia's websockets.
            stop_event = Event()
            pb = Thread(target=self._progressbar, args=(stop_event, ))
            pb.start()
            while True:
                deps = self.app.client.request(
                    method='GET',
                    url=('/project/%s/app/%s/deploy'
                         % (parsed_args.project, parsed_args.app)))
                deployment = next((d for d in deps['deployments']
                                   if d['id'] == result['id']), None)
                if deployment and deployment['status'] in ["3", "2"]:
                    stop_event.set()
                    pb.join()
                    return self.setup_columns(deployment)
                time.sleep(5)

    def _progressbar(self, stop_event):
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        while not stop_event.isSet():
            self.app.stdout.write(next(spinner))
            self.app.stdout.flush()
            time.sleep(0.1)
            self.app.stdout.write('\b')
