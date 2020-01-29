#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from jexia_cli.base import (ProjectServiceFieldList,
                            ProjectServiceFieldCommand,
                            ProjectServiceFieldDelete)
from jexia_cli.formatters import formatter_constraints


LOG = logging.getLogger(__name__)


class List(ProjectServiceFieldList):
    '''
    Show fields of fileset
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'constraints': formatter_constraints,
    }
    resource = 'fileset'
    svc_url = 'bestla/fs'


class Create(ProjectServiceFieldCommand):
    '''
    Create new field in fileset.
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'constraints': formatter_constraints,
    }
    resource = 'fileset'
    field_action = 'create'
    svc_url = 'bestla/fs'


class Update(ProjectServiceFieldCommand):
    '''
    Update the field's constraints in fileset.
    '''

    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    _formatters = {
        'properties': lambda v: json.dumps(v),
        'constraints': formatter_constraints,
    }
    resource = 'fileset'
    field_action = 'update'
    svc_url = 'bestla/fs'


class Delete(ProjectServiceFieldDelete):
    '''
    Delete field from the fileset
    '''

    resource = 'fileset'
    svc_url = 'bestla/fs'
