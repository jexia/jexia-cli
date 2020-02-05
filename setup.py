from io import open
from os import path
import re
from setuptools import setup, find_packages


PYPI_RST_FILTERS = (
    # Replace Python crossreferences by simple monospace
    (r':(?:class|func|meth|mod|attr|obj|exc|data|const):`~(?:\w+\.)*(\w+)`', r'``\1``'),
    (r':(?:class|func|meth|mod|attr|obj|exc|data|const):`([^`]+)`', r'``\1``'),
    # replace doc references
    (r':doc:`(.+) <(.*)>`', r'`\1 <http://jexia-cli.readthedocs.org/en/stable\2.html>`_'),
    # replace issues references
    (r':issue:`(.+?)`', r'`#\1 <https://github.com/jexia/jexia-cli-python/issues/\1>`_'),
    # replace pr references
    (r':pr:`(.+?)`', r'`#\1 <https://github.com/jexia/jexia-cli-python/pull/\1>`_'),
    # replace commit references
    (r':commit:`(.+?)`', r'`#\1 <https://github.com/jexia/jexia-cli-python/commit/\1>`_'),
    # Drop unrecognized currentmodule
    (r'\.\. currentmodule:: .*', ''),
)


def rst(filename):
    '''
    Load rst file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - all badges
    '''
    content = open(filename).read()
    for regex, replacement in PYPI_RST_FILTERS:
        content = re.sub(regex, replacement, content)
    return content


def pip(filename):
    '''Parse pip reqs file and transform it to setuptools requirements.'''
    requirements = []
    for line in open(path.join('requirements', '{0}.txt'.format(filename))):
        line = line.strip()
        if not line or '://' in line or line.startswith('#'):
            continue
        requirements.append(line)
    return requirements


install_requires = pip('install')
doc_require = pip('doc')
tests_require = pip('test')
dev_require = tests_require + pip('develop')
long_description = '\n'.join((
    rst('README.rst'),
    rst('CHANGELOG.rst'),
    ''
))

exec(compile(open('jexia_cli/__init__.py').read(), 'jexia_cli/__init__.py', 'exec'))

setup(
    name = "jexia_cli",
    version = __version__,
    author = "Jexia",
    author_email = "sdk-team@jexia.com",
    description = ("Official CLI tool for Jexia platform"),
    long_description = long_description,
    license = "MIT",
    url = "https://github.com/jexia/jexia-cli",
    install_requires = install_requires,
    tests_require = tests_require,
    extras_require = {
        'test': tests_require,
        'doc': doc_require,
        'dev': dev_require,
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords = "jexia cli",
    packages = find_packages(exclude=['tests']),
    python_requires = '>=2.7.15, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    project_urls = {
        'Bug Reports': 'https://github.com/jexia/jexia-cli/issues',
        'Source': 'https://github.com/jexia/jexia-cli/',
    },
    entry_points = {
        'console_scripts': [
            'jexia=jexia_cli.shell:main',
        ],
        'jexia_cli.commands': [
            'login = jexia_cli.commands.login:Login',
            'use = jexia_cli.commands.use:Use',
            'project_list = jexia_cli.commands.projects:List',
            'project_create = jexia_cli.commands.projects:Create',
            'project_show = jexia_cli.commands.projects:Show',
            'project_delete = jexia_cli.commands.projects:Delete',
            'dataset_list = jexia_cli.commands.datasets:List',
            'dataset_create = jexia_cli.commands.datasets:Create',
            'dataset_delete = jexia_cli.commands.datasets:Delete',
            'dataset_field_list = jexia_cli.commands.datasets_fields:List',
            'dataset_field_create = jexia_cli.commands.datasets_fields:Create',
            'dataset_field_update = jexia_cli.commands.datasets_fields:Update',
            'dataset_field_delete = jexia_cli.commands.datasets_fields:Delete',
            'fileset_list = jexia_cli.commands.filesets:List',
            'fileset_create = jexia_cli.commands.filesets:Create',
            'fileset_update = jexia_cli.commands.filesets:Update',
            'fileset_delete = jexia_cli.commands.filesets:Delete',
            'fileset_field_list = jexia_cli.commands.filesets_fields:List',
            'fileset_field_create = jexia_cli.commands.filesets_fields:Create',
            'fileset_field_update = jexia_cli.commands.filesets_fields:Update',
            'fileset_field_delete = jexia_cli.commands.filesets_fields:Delete',
            'userset_list = jexia_cli.commands.usersets:List',
            'userset_create = jexia_cli.commands.usersets:Create',
            'userset_update = jexia_cli.commands.usersets:Update',
            'userset_delete = jexia_cli.commands.usersets:Delete',
            'relation_list = jexia_cli.commands.relations:List',
            'relation_create = jexia_cli.commands.relations:Create',
            'relation_delete = jexia_cli.commands.relations:Delete',
            'channel_list = jexia_cli.commands.channels:List',
            'channel_create = jexia_cli.commands.channels:Create',
            'channel_update = jexia_cli.commands.channels:Update',
            'channel_delete = jexia_cli.commands.channels:Delete',
            'key_list = jexia_cli.commands.keys:List',
            'key_create = jexia_cli.commands.keys:Create',
            'key_update = jexia_cli.commands.keys:Update',
            'key_delete = jexia_cli.commands.keys:Delete',
        ]
    },
)
