#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging

from cliff.app import App
from cliff.commandmanager import CommandManager

from jexia_cli import __version__
from jexia_cli.constants import (DEFAULT_CONFIG_PATH, DEFAULT_DOMAIN)
from jexia_cli.utils import load_config
from jexia_sdk.http import HTTPClient


LOG = logging.getLogger(__name__)


class CLI(App):

    def __init__(self):
        super(CLI, self).__init__(
            description='Friendly Console Interface for Jexia platform.',
            version=__version__,
            command_manager=CommandManager('jexia_cli.commands'),
            deferred_help=False, )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(CLI, self).build_option_parser(description, version,
                                                      argparse_kwargs)
        parser.add_argument(
            '--config',
            default=os.environ.get('JEXIA_CONFIG', DEFAULT_CONFIG_PATH)
        )
        parser.add_argument(
            '--domain',
            default=os.environ.get('JEXIA_DOMAIN', DEFAULT_DOMAIN)
        )
        parser.add_argument(
            '--insecure',
            action='store_true',
            default=False,
        )
        return parser

    def configure_logging(self):
        if self.options.debug:
            self.options.verbose_level = 2
        super(CLI, self).configure_logging()

    def prepare_to_run_command(self, cmd):
        self.client = HTTPClient(domain=self.options.domain,
                                 ssl_check=not self.options.insecure)
        self.config = load_config(self.options.config)


def main(argv=sys.argv[1:]):
    shell = CLI()
    return shell.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
