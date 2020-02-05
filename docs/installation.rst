.. _installation:

Installation
============

Unix-like OS
~~~~~~~~~~~~

Install Jexia CLI with ``pip``:

.. code-block:: console

    sudo pip install jexia-cli

or with easy_install:

.. code-block:: console

    sudo easy_install jexia-cli

or to virtualenv:

.. code-block:: console

    virtualenv env
    env/bin/pip install jexia-cli
    sudo ln -s `pwd`/env/bin/jexia /usr/local/sbin/jexia

Windows OS
~~~~~~~~~~
Install Jexia CLI with ``pip``:

.. code-block:: console

    pip install jexia-cli

or with easy_install:

.. code-block:: console

    easy_install jexia-cli

Development
===========

The development version can be downloaded from
`GitHub <https://github.com/jexia/jexia-cli>`_.

.. code-block:: console

    git clone https://github.com/jexia/jexia-cli.git
    cd jexia-cli
    pip install -e .[dev,test]


Jexia-CLI requires Python version 2.7, 3.3, 3.4 or 3.5.
It's also working with PyPy and PyPy3.
