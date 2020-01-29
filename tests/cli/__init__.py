import json
import os
import logging

from jexia_cli.shell import CLI
from jexia_sdk.http import HTTPClient


LOG = logging.getLogger(__name__)
SHELL_CONFIG = {
    'email': os.environ['JEXIA_CLI_TEST_EMAIL'],
    'password': os.environ['JEXIA_CLI_TEST_PASSWORD'],
}


class FakeStdout(object):
    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        pass


def run_cmd(args, json_output=True, print_output=True):
    args.insert(0, '--debug')
    LOG.debug('Execute command: jexia %s' % ' '.join(args))
    stdout = FakeStdout()

    shell = CLI()
    shell.initialize_app = lambda c: None
    shell.stdout = stdout
    shell.client = HTTPClient(domain=os.environ['JEXIA_CLI_TEST_DOMAIN'],
                              ssl_check=False)
    shell.config = SHELL_CONFIG
    shell.run(args)
    result = "".join(stdout.content)
    if print_output:
        print(result)
    if json_output and result:
        return json.loads(result)
    return result
