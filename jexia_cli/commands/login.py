#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from cliff.command import Command

from jexia_cli.constants import DEFAULT_CONFIG_PATH
from jexia_cli.utils import (ask_email_password, save_config)


LOG = logging.getLogger(__name__)


class Login(Command):
    '''
    Ask and save credentials to config file.
    '''

    def take_action(self, parsed_args):
        email, password = ask_email_password()
        save_config({'email': email, 'password': password})
        self.app.stdout.write('config saved to %s\n' % DEFAULT_CONFIG_PATH)
        self.app.client.auth_management(email, password)
