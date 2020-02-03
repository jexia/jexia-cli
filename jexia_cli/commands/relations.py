#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from jexia_cli.base import (ProjectCommand, ProjectListCommand,
                            ProjectShowCommand)
from jexia_cli.utils import with_authentication
from jexia_sdk.http import HTTPClientError


LOG = logging.getLogger(__name__)
RELATION_TYPES = ['ONE-MANY', 'MANY-MANY', 'MANY-ONE', 'ONE-ONE']
REALTION_RESOURCES = {
    'dataset': 'mimir/ds/relation',
    'fileset': 'bestla/fs/relation',
}


class List(ProjectListCommand):
    '''
    List relation between usersets and datasets or filesets
    '''

    columns = ['id', 'relation', 'resource', 'resource_id']

    @with_authentication
    def take_action(self, parsed_args):
        relations = list()
        result = self.app.client.request(
            method='GET', url='/management/%s/mimir/ds' % parsed_args.project)
        for ds in result:
            for rel in ds.get('relations', []):
                relations.append({
                    'id': rel['id'],
                    'relation': '%s-%s' % (rel['type']['to_cardinality'],
                                           rel['type']['from_cardinality']),
                    'resource': 'dataset',
                    'resource_id': rel['from_resource']['resource_id'],
                })
        result = self.app.client.request(
            method='GET', url='/management/%s/bestla/fs' % parsed_args.project)
        for fs in result:
            for rel in fs.get('relations', []):
                relations.append({
                    'id': rel['id'],
                    'relation': '%s-%s' % (rel['type']['to_cardinality'],
                                           rel['type']['from_cardinality']),
                    'resource': 'fileset',
                    'resource_id': rel['from_resource']['resource_id'],
                })
        return self.setup_columns(relations)


class Create(ProjectShowCommand):
    '''
    Create relation between usersets and dataset or fileset
    '''

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--relation',
            metavar='RELATION',
            help=('Relation\'s type from userset to other resource (%s)'
                  % ', '.join(RELATION_TYPES)),
            required=True,
            choices=RELATION_TYPES
        )
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--dataset',
            metavar='DATASET',
            help='ID of dataset',
        )
        group.add_argument(
            '--fileset',
            metavar='FILESET',
            help='ID of fileset',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        self.columns = ['id', 'relation']
        result = self.app.client.request(
            method='GET',
            url='/management/%s/midgard/schema' % parsed_args.project)
        ums = next((r['id'] for r in result if r['name'] == 'umsUsers'), None)
        if not ums:
            raise HTTPClientError('Userset scheme not found')
        data = {
            'to_resource': {
                'namespace': 'midgard',
                'resource_id': ums,
            },
        }
        relation = parsed_args.relation.split('-')
        data['type'] = {
            'from_cardinality': relation[1],
            'to_cardinality': relation[0],
        }
        url_namespace = ''
        to_resource = ''
        if parsed_args.dataset:
            data['from_resource'] = {
                'namespace': 'mimir',
                'resource_id': parsed_args.dataset,
            }
            url_namespace = 'mimir/ds/relation'
            to_resource = 'dataset'
        if parsed_args.fileset:
            data['from_resource'] = {
                'namespace': 'bestla',
                'resource_id': parsed_args.fileset,
            }
            url_namespace = 'bestla/fs/relation'
            to_resource = 'fileset'
        result = self.app.client.request(
            method='POST',
            url='/management/%s/%s' % (parsed_args.project, url_namespace),
            data=data)
        formatted_result = {
            'id': result['id'],
            to_resource: result['to_resource']['resource_id'],
            'relation': '%s-%s' % (result['type']['to_cardinality'],
                                   result['type']['from_cardinality']),
        }
        self.columns.insert(2, to_resource)
        return self.setup_columns(formatted_result)


class Delete(ProjectCommand):
    '''
    Delete dataset
    '''

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            '--resource',
            metavar="RESOURCE",
            help=('Type of resource in relation (%s).'
                  % ', '.join(REALTION_RESOURCES.keys())),
            choices=list(REALTION_RESOURCES.keys()),
            required=True,
        )
        parser.add_argument(
            'relation',
            metavar="RELATION_ID",
            help='UUID of relation which should be deleted',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        url = ('/management/%s/%s/%s'
               % (parsed_args.project,
                  REALTION_RESOURCES[parsed_args.resource],
                  parsed_args.relation))
        self.app.client.request(method='DELETE', url=url)
