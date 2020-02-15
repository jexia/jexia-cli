dataset
~~~~~~~

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

.. include:: constraints.rst

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

.. include:: constraints.rst

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

    $ jexia dataset field update --project=8ae43645-2dfb-45c7-a7bd-991dde8b775a --dataset=825cbad3-f5b7-4d4c-a65e-07d3b5002929 --constrain default= 8e151f87-eab7-4284-88d8-a2b51157a7a4
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

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset export

**Example of usage**:

To export 2 datasets with data and specific columns ypu can do something like this:

.. code-block:: console

    $ jexia dataset export --project=8ae43645-2dfb-45c7-a7bd-991dde8b775a --with-data --filter=status,app_id 8e151f87-eab7-4284-88d8-a2b51157a7a4 8534d548-43e5-4ea9-b941-2cd577e6fae8 > res.json
    $ cat res.json
    [
        {
            "data": [
                {
                    "repo_name": "jexia-vue-todo",
                    "repo_url": "https://github.com/jexia/jexia-vue-todo.git"
                }
            ],
            "inputs": [
                {
                    "constraints": [],
                    "name": "repo_url",
                    "type": "string"
                },
                {
                    "constraints": [],
                    "name": "repo_name",
                    "type": "string"
                }
            ],
            "name": "applications"
        },
        {
            "data": [
                {
                    "app_id": "c5c78cda-94fa-4c93-8941-8b9a31345233",
                    "status": "done"
                },
                {
                    "app_id": "c5c78cda-94fa-4c93-8941-8b9a31345233",
                    "status": "done"
                }
            ],
            "inputs": [
                {
                    "constraints": [
                    {
                        "type": "required",
                        "value": true
                    }
                    ],
                    "name": "app_id",
                    "type": "uuid"
                },
                {
                    "constraints": [
                    {
                        "type": "default",
                        "value": "pending"
                    }
                    ],
                    "name": "status",
                    "type": "string"
                }
            ],
            "name": "builds"
        }
    ]

.. autoprogram-cliff:: jexia_cli.commands
   :command: dataset import

**Example of usage**:

To export 2 datasets with data and specific columns ypu can do something like this:

.. code-block:: console

    $ jexia dataset import --project=41724d4f-2d2f-4106-ab6c-075481c2f161 < res.json
    dataset "applications" created
    dataset "builds" created
