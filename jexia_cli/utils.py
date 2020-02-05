#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import six
import os
import sys
import yaml
import getpass

from jexia_cli.constants import DEFAULT_CONFIG_PATH


LOG = logging.getLogger(__name__)


def with_authentication(func):
    def wrapper(*args, **kwargs):
        if not args[0].app.client.is_authenticated():
            email = args[0].app.config.get('email', None)
            password = args[0].app.config.get('password', None)
            if not email or not password:
                email, password = ask_email_password()
            args[0].app.client.auth_management(email, password)
        return func(*args, **kwargs)
    return wrapper


def confirm_action(action):
    """Func must be a take_action func."""

    def wrap(func):
        def wrap(*args, **kwargs):
            if not hasattr(args[1], "yes_i_really_want_to_" + action):
                LOG.error("Please add confirm argument into parser.")
                sys.exit(-1)

            accept = getattr(args[1], "yes_i_really_want_to_" + action)
            if not accept:
                LOG.warning("Confirm action by --yes-i-really-want-to-%s",
                            action)
                sys.exit(-1)

            return func(*args, **kwargs)

        return wrap

    return wrap


def ask_email_password():
    email = six.moves.input('Please enter email for Jexia account: ')
    password = getpass.getpass(
        prompt='Please enter password for Jexia account: ')
    return email, password


def load_config(config_file):
    config = dict()
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as exc:
        LOG.debug("Config file %s could not be loaded: %s"
                  % (config_file, exc))
    return config


def save_config(data):
    directory = os.path.dirname(DEFAULT_CONFIG_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(DEFAULT_CONFIG_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
