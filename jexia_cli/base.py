import abc
import logging

import six
from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne


def get_dict_properties(item, fields, mixed_case_fields=None, formatters=None):
    """Return a tuple containing the item properties.

    :param item: a single dict resource
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name] if field_name in item else ''
        if data == '<nil>':
            data = ''
        if field in formatters:
            data = formatters[field](data)
        row.append(data)
    return tuple(row)


class CLICommand(Command):
    logger = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        pass


@six.add_metaclass(abc.ABCMeta)
class DisplayCommand(CLICommand):
    columns = []
    _formatters = {}

    def setup_columns(self, data):
        pass


class ShowCommand(DisplayCommand, ShowOne):

    def setup_columns(self, data):
        return (
            self.columns,
            get_dict_properties(
                data,
                self.columns,
                formatters=self._formatters
            ),
        )


class ListCommand(DisplayCommand, Lister):

    def setup_columns(self, data):
        return (
            self.columns,
            (
                get_dict_properties(
                    item,
                    self.columns,
                    formatters=self._formatters,
                ) for item in data),
        )


class ProjectCommand(CLICommand):

    def get_parser(self, prog_name):
        parser = super(ProjectCommand, self).get_parser(prog_name)
        if not self.app or not self.app.interactive_mode or \
                not self.app.context.get('project'):
            parser.add_argument(
                '--project',
                metavar='PROJECT_ID',
                help='Project''s ID',
                required=True,
            )
        else:
            parser.add_argument(
                '--project',
                metavar='PROJECT_ID',
                help='Project''s ID',
                required=False,
                default=self.app.context.get('project'),
            )
        return parser


class ProjectListCommand(ListCommand, ProjectCommand):

    pass


class ProjectShowCommand(ShowCommand, ProjectCommand):

    pass
