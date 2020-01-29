#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime


def format_datetime(val):
    return str(datetime.fromtimestamp(int(val)))


def formatter_constraints(val):
    fields = []
    for con in val:
        fields.append('%s=%s' % (con['type'], con['value']))
    return ', '.join(fields)


def formatter_fields(val):
    fields = []
    for opt in val:
        if opt['immutable']:
            fields.append('%s* (%s)' % (opt['name'], opt['type']))
        else:
            fields.append('%s (%s)' % (opt['name'], opt['type']))
    return '\n'.join(fields)
