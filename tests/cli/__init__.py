import json
import os

from jexia_cli.shell import CLI
from jexia_sdk.http import HTTPClient


def prepare_to_run_command(cmd):
    pass


class FakeStdout(object):
    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        pass


def run_cmd(args, json_output=False, print_output=True):
    if json_output:
        args.extend(['-f', 'json'])
    stdout = FakeStdout()

    shell = CLI()
    shell.prepare_to_run_command = prepare_to_run_command
    shell.stdout = stdout
    shell.client = HTTPClient(domain=os.environ['JEXIA_CLI_TEST_DOMAIN'],
                              ssl_check=False)
    shell.config = {
        'email': os.environ['JEXIA_CLI_TEST_EMAIL'],
        'password': os.environ['JEXIA_CLI_TEST_PASSWORD'],
    }
    shell.run(args)
    result = "".join(stdout.content)
    if print_output:
        print(result)
    if json_output and result:
        return json.loads(result)
    return result
