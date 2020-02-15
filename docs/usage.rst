.. _usage:

Using Jexia CLI tool
====================

This guide assumes you have a working understanding of `Jexia <http://jexia.com>`_,
and that you have already installed Jexia-CLI. If not, then follow the steps in
the :ref:`installation` section.

Credentials
----------------

To start using CLI tool you can save credentials:

.. code-block:: console

    $ jexia login

.. warning:: Credentials will be saved to the config file `<HOME_DIRECTORY>/.jexia/config.yml` as plain text

Also, you can run every command without saving credentials in this case CLI
tool will ask credentials every time.

Help
----

All available commands you can find by calling `help`:

.. code-block:: console

    $ jexia help

Commands
--------

.. autoprogram-cliff:: jexia_cli.commands
   :command: use

**Example of usage**:

.. code-block:: console

    $ jexia
    (jexia) project list
    +--------------------------------------+-------+-------------+---------------------+
    | id                                   | name  | description | created_at          |
    +--------------------------------------+-------+-------------+---------------------+
    | 8ae43645-2dfb-45c7-a7bd-991dde8b775a | test1 |             | 2020-01-24 17:15:57 |
    +--------------------------------------+-------+-------------+---------------------+
    (jexia) use 8ae43645-2dfb-45c7-a7bd-991dde8b775a
    (jexia 8ae43645-2dfb-45c7-a7bd-991dde8b775a) dataset list
    +--------------------------------------+-------+-------+-----------+------------+------------------------+------------------------+
    | id                                   | name  | type  | immutable | properties | inputs                 | outputs                |
    +--------------------------------------+-------+-------+-----------+------------+------------------------+------------------------+
    | 825cbad3-f5b7-4d4c-a65e-07d3b5002929 | test2 | table | False     | {}         | id* (uuid)             | id* (uuid)             |
    |                                      |       |       |           |            | created_at* (datetime) | created_at* (datetime) |
    |                                      |       |       |           |            | updated_at* (datetime) | updated_at* (datetime) |
    |                                      |       |       |           |            | test (string)          | test (string)          |
    |                                      |       |       |           |            | test2 (string)         | test2 (string)         |
    +--------------------------------------+-------+-------+-----------+------------+------------------------+------------------------+

.. warning::

    This command can be used only in interactive mode.

.. toctree::
    :maxdepth: 3

    project
    dataset
    fileset
    userset
    relation
    channel
    key
    app
    policy
