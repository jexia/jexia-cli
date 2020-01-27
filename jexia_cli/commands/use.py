#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cliff.command import Command
from jexia_cli.utils import with_authentication


class Use(Command):
    '''
    Choose project to manage resources. this command only for interactive mode.
    You can use it instead of `--project` option in each command.
    '''

    def get_parser(self, prog_name):
        parser = super(Use, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='PROJECT_ID',
            help='UUID of project which should be used in this context',
        )
        return parser

    @with_authentication
    def take_action(self, parsed_args):
        if not self.app.interactive_mode:
            raise Exception('This command can be used only'
                            ' in interactive mode')
        self.app.context['project'] = parsed_args.project
        interpreter = self.app.interpreter
        interpreter.prompt = '(%s %s) ' % (interpreter.parent_app.NAME,
                                           parsed_args.project)
