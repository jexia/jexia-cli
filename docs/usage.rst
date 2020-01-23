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
   :command: project list

.. autoprogram-cliff:: jexia_cli.commands
   :command: project create

.. autoprogram-cliff:: jexia_cli.commands
   :command: project show

.. autoprogram-cliff:: jexia_cli.commands
   :command: project delete

