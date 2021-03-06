**`nornir_cli`** is CLI tool based on [Nornir](https://github.com/nornir-automation/nornir){target="_blank"} framework, [Nornir Plugins](https://nornir.tech/nornir/plugins/){target="_blank"} and [Click](https://github.com/pallets/click){target="_blank"}

## Features 

* **Manage your custom nornir runbooks**

    * Create and manage your own runbook collections
    * Add your custom nornir runbooks to runbook collections and run it for any hosts directly from the CLI 
    * Or use `nornir_cli` for inventory management only, and take the result in your nornir runbooks. By excluding getting and filtering the inventory in your runbooks, you will make them more versatile.

* **Manage Inventory**

    Get Inventory, filter Inventory, output Inventory and save Inventory state from the CLI.
    This is really useful for large, structured Inventory - for example, [NetBox](https://github.com/netbox-community/netbox
){target="_blank"} with [nornir_netbox plugin](https://github.com/wvandeun/nornir_netbox){target="_blank"}.

* **Run Nornir Plugins**

    Run Tasks based on Nornir Plugins from the CLI, check result and statistic

* **Build a chain of `nornir_cli` commands**

    Initialize Nornir, filter Inventory and start Task/Tasks chains or runbook/runbooks chains in one command

* **Json input. Json output**

    Json strings are everywhere! Ok, only in command options

* **Custom Multi Commands with click**

    `nornir_cli` based on click Custom Multi Commands, so you can easily add your custom command by following some principles

* **Simple CLI network orchestrator**

    `nornir_cli` is a simple CLI orchestrator that you can use to interact with the SoT and manage your network

## Quick Start 

#### Install

Please, at first, check the dependencies in `pyproject.toml` and create new virtual environment if necessary and then:

**with pip:**

```text
pip install nornir_cli
```

**with git:**

```text
git clone https://github.com/timeforplanb123/nornir_cli.git
cd nornir_cli
pip install .
# or
poetry install
```

**with Docker:**

```text
git clone https://github.com/timeforplanb123/nornir_cli.git
cd nornir_cli
docker build -t timeforplanb123/nornir_cli .
docker run --rm -it timeforplanb123/nornir_cli sh

# nornir_cli --version
nornir_cli, version 0.3.0
```

#### Simple Example

=== "config.yaml"
    ```yaml
    # Simple Nornir configuration file
    inventory:
        plugin: SimpleInventory
        options:
            host_file: "inventory/hosts.yaml"
    ```
=== "hosts.yaml"
    ```yaml
    # Single host inventory
    dev_1:
        hostname: 10.1.0.1
        username: username 
        password: password
		# huawei is just an example here
        platform: huawei
    ```
=== "nornir_cli"
    ```text
    # As instance, let's run netmiko_send_command

    $ nornir_cli nornir-netmiko init netmiko_send_command --command_string "display clock"

    netmiko_send_command************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    2021-03-17 14:04:22+03:00
    Wednesday
    Time Zone(Moscow) : UTC+03:00
    ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_1                                             : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```
