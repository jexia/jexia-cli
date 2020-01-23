#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime


def format_datetime(val):
    return str(datetime.fromtimestamp(val))
