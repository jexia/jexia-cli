#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import sys

from datetime import datetime

from invoke import task

ROOT = os.path.dirname(__file__)

CLEAN_PATTERNS = [
    'build',
    'dist',
    'cover',
    '**/*.pyc',
    '.tox',
    '**/__pycache__',
    'reports',
    '*.egg-info',
    '.pytest_cache',
    '.coverage',
    '.cache',
]
CLEAN_DOCS = [
    'docs/_build'
]


def color(code):
    '''A simple ANSI color wrapper factory'''
    return lambda t: '\033[{0}{1}\033[0;m'.format(code, t)


green = color('1;32m')
red = color('1;31m')
blue = color('1;30m')
cyan = color('1;36m')
purple = color('1;35m')
white = color('1;39m')


def header(text):
    '''Display an header'''
    print(' '.join((blue('>>'), cyan(text))))
    sys.stdout.flush()


def info(text, *args, **kwargs):
    '''Display informations'''
    text = text.format(*args, **kwargs)
    print(' '.join((purple('>>>'), text)))
    sys.stdout.flush()


def success(text):
    '''Display a success message'''
    print(' '.join((green('>>'), white(text))))
    sys.stdout.flush()


def error(text):
    '''Display an error message'''
    print(red('✘ {0}'.format(text)))
    sys.stdout.flush()


def exit(text=None, code=-1):
    if text:
        error(text)
    sys.exit(-1)


def build_args(*args):
    return ' '.join(a for a in args if a)


@task
def clean(ctx):
    '''Cleanup all build artifacts'''
    header(clean.__doc__)
    with ctx.cd(ROOT):
        for pattern in CLEAN_PATTERNS + CLEAN_DOCS:
            info('Removing {0}', pattern)
            ctx.run('rm -rf {0}'.format(pattern))


@task
def deps(ctx):
    '''Install or update development dependencies'''
    header(deps.__doc__)
    with ctx.cd(ROOT):
        ctx.run('pip install -r requirements/develop.txt -r requirements/doc.txt -r requirements/test.txt', pty=True)


@task
def test_unit(ctx, profile=False):
    '''Run unit tests suite'''
    header(test_unit.__doc__)
    kwargs = build_args(
        '--profile' if profile else None,
    )
    with ctx.cd(ROOT):
        ctx.run('py.test -p no:warnings -m "not integration" {0}'.format(kwargs), pty=True)


@task
def test_integration(ctx, profile=False):
    '''Run integration tests suite'''
    header(test_integration.__doc__)
    kwargs = build_args(
        '--profile' if profile else None,
    )
    with ctx.cd(ROOT):
        ctx.run('py.test -p no:warnings -m "integration" {0}'.format(kwargs), pty=True)


@task
def cover(ctx, html=False):
    '''Run tests suite with coverage'''
    header(cover.__doc__)
    extra = '--cov-report=html' if html else ''
    with ctx.cd(ROOT):
        ctx.run('py.test -p no:warnings --cov=jexia_cli --cov-report=term {0}'.format(extra), pty=True)


@task
def tox(ctx):
    '''Run tests against Python versions'''
    header(tox.__doc__)
    ctx.run('tox', pty=True)


@task
def qa(ctx):
    '''Run a quality report'''
    header(qa.__doc__)
    with ctx.cd(ROOT):
        info('Python Static Analysis')
        flake8_results = ctx.run('flake8 jexia_cli tests', pty=True, warn=True)
        if flake8_results.failed:
            error('There is some lints to fix')
        else:
            success('No linter errors')
        info('Ensure PyPI can render README and CHANGELOG')
        readme_results = ctx.run('python setup.py check -r -s', pty=True, warn=True, hide=True)
        if readme_results.failed:
            print(readme_results.stdout)
            error('README and/or CHANGELOG is not renderable by PyPI')
        else:
            success('README and CHANGELOG are renderable by PyPI')
    if flake8_results.failed or readme_results.failed:
        exit('Quality check failed', flake8_results.return_code or readme_results.return_code)
    success('Quality check OK')


@task
def doc(ctx):
    '''Build the documentation'''
    header(doc.__doc__)
    with ctx.cd(ROOT):
        for pattern in CLEAN_DOCS:
            info('Removing {0}', pattern)
            ctx.run('rm -rf {0}'.format(pattern))
    with ctx.cd(os.path.join(ROOT, 'docs')):
        ctx.run('make html', pty=True)


@task
def dist(ctx):
    '''Package for distribution'''
    header(dist.__doc__)
    with ctx.cd(ROOT):
        ctx.run('python setup.py sdist', pty=True)


@task(clean, deps, test_unit, test_integration, doc, qa, dist, default=True)
def all(ctx):
    '''Run tests, reports and packaging'''
    pass
