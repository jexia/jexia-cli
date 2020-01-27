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

.. autoprogram-cliff:: jexia_cli.commands
   :command: project list

.. autoprogram-cliff:: jexia_cli.commands
   :command: project create

.. autoprogram-cliff:: jexia_cli.commands
   :command: project show

.. autoprogram-cliff:: jexia_cli.commands
   :command: project delete

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset list

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset create

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset delete

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset field list

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset field create

Allowed constraints for all of types:
  * **default** (*string*) - default value
  * **required** (*true*/*false*) - required field

Allowed constraints for *integer*/*float* fields:
  * **max_value** (*integer*/*float*) - maximum value
  * **min_value** (*integer*/*float*) - minimum value

Allowed constraints for *string* fields:
  * **lowercase** (*true*/*false*) - field can only contain
    lowercase values
  * **uppercase** (*true*/*false*) - field can only contain
    uppercase values
  * **alphanumeric** (*true*/*false*) - field can only contain
    alpha-numeric values
  * **regexp** (*regex expression*) - field can only contain value matched
    to the regex expression
  * **alpha** (*true*/*false*) - field can only contain letters
  * **numeric** (*true*/*false*) - field can only contain numbers
  * **min_length** (*integer*) - minimum length of string
  * **max_length** (*integer*) - maximum length of string

**Example of usage**:

.. code-block:: console

    $ jexia dataset field create --project=8ae43645-2dfb-45c7-a7bd-991dde8b775a --dataset=825cbad3-f5b7-4d4c-a65e-07d3b5002929 --type=string --name=test-field --constraint required=true --constraint default=some-value --constraint regexp='.*'
    +-------------+----------------------------------------------+
    | Field       | Value                                        |
    +-------------+----------------------------------------------+
    | id          | 8e151f87-eab7-4284-88d8-a2b51157a7a4         |
    | name        | test-field                                   |
    | type        | string                                       |
    | immutable   | False                                        |
    | properties  | {}                                           |
    | constraints | required=True, default=some-value, regexp=.* |
    +-------------+----------------------------------------------+

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset field update

Allowed constraints for all of types:
  * **default** (*string*) - default value
  * **required** (*true*/*false*) - required field

Allowed constraints for *integer*/*float* fields:
  * **max_value** (*integer*/*float*) - maximum value
  * **min_value** (*integer*/*float*) - minimum value

Allowed constraints for *string* fields:
  * **lowercase** (*true*/*false*) - field can only contain
    lowercase values
  * **uppercase** (*true*/*false*) - field can only contain
    uppercase values
  * **alphanumeric** (*true*/*false*) - field can only contain
    alpha-numeric values
  * **regexp** (*regex expression*) - field can only contain value matched
    to the regex expression
  * **alpha** (*true*/*false*) - field can only contain letters
  * **numeric** (*true*/*false*) - field can only contain numbers
  * **min_length** (*integer*) - minimum length of string
  * **max_length** (*integer*) - maximum length of string

**Example of usage**:

To update constraints of field add new constraints:

.. code-block:: console

    $ jexia dataset field update --project=8ae43645-2dfb-45c7-a7bd-991dde8b775a --dataset=825cbad3-f5b7-4d4c-a65e-07d3b5002929 --constrain default="another-value" --constraint required=false 8e151f87-eab7-4284-88d8-a2b51157a7a4
    +-------------+--------------------------------------+
    | Field       | Value                                |
    +-------------+--------------------------------------+
    | id          | 8e151f87-eab7-4284-88d8-a2b51157a7a4 |
    | name        | test-field                           |
    | type        | string                               |
    | immutable   | False                                |
    | properties  | {}                                   |
    | constraints | default=another-value, regexp=.*     |
    +-------------+--------------------------------------+

To remove constraint use empty (or false for boolean) value:

.. code-block:: console

    $ jexia dataset field update --project=8ae43645-2dfb-45c7-a7bd-991dde8b775a --dataset=825cbad3-f5b7-4d4c-a65e-07d3b5002929 --constrain default="" 8e151f87-eab7-4284-88d8-a2b51157a7a4
    +-------------+--------------------------------------+
    | Field       | Value                                |
    +-------------+--------------------------------------+
    | id          | 8e151f87-eab7-4284-88d8-a2b51157a7a4 |
    | name        | test-field                           |
    | type        | string                               |
    | immutable   | False                                |
    | properties  | {}                                   |
    | constraints | regexp=.*                            |
    +-------------+--------------------------------------+

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset field delete

