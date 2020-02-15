#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import ProjectCommand
from jexia_cli.utils import with_authentication, with_cleanup_resources
from jexia_sdk.http import HTTPClientError


LOG = logging.getLogger(__name__)


class Export(ProjectCommand):
    '''
    Export datasets
    '''

    def get_parser(self, prog_name):
        parser = super(Export, self).get_parser(prog_name)
        parser.add_argument(
            '--with-data',
            action='store_true',
            default=False,
            help=('Include data to result'),
        )
        parser.add_argument(
            '--filter',
            help=('Columns that should be exported (column1,column2)'),
        )
        if not self.app or not self.app.interactive_mode:
            parser.add_argument(
                '--to',
                help=('Result will be saved to file'),
                required=False,
            )
        else:
            parser.add_argument(
                '--to',
                help=('Result will be saved to file'),
                required=True,
            )
        parser.add_argument(
            'dataset',
            metavar="DATASET_ID",
            nargs='+',
            help='UUID of dataset to export',
        )
        return parser

    @with_authentication
    @with_cleanup_resources
    def take_action(self, parsed_args):
        self.cleanup_resources = list()
        result = self.app.client.request(
            method='GET',
            url='/management/%s/mimir/ds' % parsed_args.project)
        res_datasets = [r['id'] for r in result]
        for ds in parsed_args.dataset:
            if ds not in res_datasets:
                raise HTTPClientError('Dataset %s not found'
                                      % parsed_args.dataset)
        if parsed_args.with_data:
            # create API key for data exporting
            api_key = self.app.client.request(
                method='POST',
                url='/management/%s/utgard/' % parsed_args.project,
                data={'description': 'jexia-cli-dataset-export'}
            )
            self.cleanup_resources.append({
                'method': 'DELETE',
                'url': '/management/%s/utgard/%s' % (parsed_args.project,
                                                     api_key['key'])})
            # create policy for API key
            policy = self.app.client.request(
                method='POST',
                url='/management/%s/rakshak/' % parsed_args.project,
                data={'description': 'jexia-cli-dataset-export',
                      'subjects': ['apk:%s' % api_key['key']],
                      'resources': parsed_args.dataset,
                      'actions': ['read'],
                      'effect': 'allow'}
            )
            self.cleanup_resources.append({
                'method': 'DELETE',
                'url': '/management/%s/rakshak/%s' % (parsed_args.project,
                                                      policy['id'])})
            # auth in consumption API
            self.app.consumption_client.auth_consumption(
                project=parsed_args.project,
                method='apk',
                key=api_key['key'],
                secret=api_key['secret'],
            )
        dump = list()
        for ds in result:
            if ds['id'] not in parsed_args.dataset:
                continue
            dataset_dump = self._prepare_dataset_dump(ds, parsed_args.filter)
            if parsed_args.with_data:
                dataset_dump['data'] = self._prepare_data_dump(dataset_dump)
            dump.append(dataset_dump)
        json_dump = json.dumps(dump, indent=2, sort_keys=True)
        if parsed_args.to:
            with open(parsed_args.to, "w") as f:
                f.write(json_dump)
        else:
            self.app.stdout.write(json_dump)

    def _prepare_dataset_dump(self, dataset, filter):
        res_dataset = dict()
        res_dataset['name'] = dataset['name']
        res_dataset['inputs'] = []
        columns = filter.split(',') if filter else []
        for opt in dataset['inputs']:
            if opt['name'] in ['id', 'updated_at', 'created_at']:
                continue
            if columns and opt['name'] not in columns:
                continue
            constraints = list()
            for constr in opt['constraints']:
                constraints.append({
                    'type': constr['type'],
                    'value': constr['value'],
                })
            res_dataset['inputs'].append({
                'name': opt['name'],
                'type': opt['type'],
                'constraints': constraints,
            })
        return res_dataset

    def _prepare_data_dump(self, dataset):
        columns = [c['name'] for c in dataset['inputs']]
        data = self.app.consumption_client.request(
            method='GET', url='/ds/%s' % dataset['name'])
        return [{k: v for k, v in d.items() if k in columns} for d in data]


class Import(ProjectCommand):
    '''
    Import datasets
    '''

    def get_parser(self, prog_name):
        parser = super(Import, self).get_parser(prog_name)
        if not self.app or not self.app.interactive_mode:
            parser.add_argument(
                '--file',
                help=('Dump file to import'),
                required=False,
            )
        else:
            parser.add_argument(
                '--file',
                help=('Dump file to import'),
                required=True,
            )
        return parser

    @with_authentication
    @with_cleanup_resources
    def take_action(self, parsed_args):
        self.cleanup_resources = list()
        dump = ""
        if parsed_args.file:
            with open(parsed_args.file, "r+") as f:
                dump = f.read()
        else:
            # try to read data from stdin
            for line in self.app.stdin:
                dump += line
        dump = json.loads(dump)
        for dataset in dump:
            # create dataset
            new_ds = self.app.client.request(
                method='POST', data={'name': dataset['name']},
                url='/management/%s/mimir/ds' % parsed_args.project)
            dataset['id'] = new_ds['id']
        # at least one dataset contains data for import
        if any('data' in d for d in dump):
            # create API key for data importing
            api_key = self.app.client.request(
                method='POST',
                url='/management/%s/utgard/' % parsed_args.project,
                data={'description': 'jexia-cli-dataset-import'}
            )
            self.cleanup_resources.append({
                'method': 'DELETE',
                'url': '/management/%s/utgard/%s' % (parsed_args.project,
                                                     api_key['key'])})
            # create policy for API key
            policy = self.app.client.request(
                method='POST',
                url='/management/%s/rakshak/' % parsed_args.project,
                data={'description': 'jexia-cli-dataset-import',
                      'subjects': ['apk:%s' % api_key['key']],
                      'resources': [d['id'] for d in dump],
                      'actions': ['read', 'create'],
                      'effect': 'allow'}
            )
            self.cleanup_resources.append({
                'method': 'DELETE',
                'url': '/management/%s/rakshak/%s' % (parsed_args.project,
                                                      policy['id'])})
            # auth in consumption API
            self.app.consumption_client.auth_consumption(
                project=parsed_args.project,
                method='apk',
                key=api_key['key'],
                secret=api_key['secret'],
            )
        for dataset in dump:
            # create columns
            for field in dataset['inputs']:
                self.app.client.request(
                    method='POST',
                    data={'name': field['name'],
                          'type': field['type'],
                          'constraints': field['constraints']},
                    url=('/management/%s/mimir/ds/%s/field'
                         % (parsed_args.project, dataset['id'])))
            # fill data
            if 'data' in dataset:
                self.app.consumption_client.request(
                    method='POST', url='/ds/%s' % dataset['name'],
                    data=dataset['data'])
            self.app.stdout.write('dataset "%s" created\n' % dataset['name'])
