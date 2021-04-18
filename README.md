[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI](https://img.shields.io/pypi/v/nornir-cli.svg)](https://pypi.org/project/nornir-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-passing-green.svg)](https://timeforplanb123.github.io/nornir_cli/)

nornir_cli
==========

---

**Documentation**: <a href="https://timeforplanb123.github.io/nornir_cli" target="_blank">https://timeforplanb123.github.io/nornir_cli</a>

---

**nornir_cli** is CLI tool based on <a href="https://github.com/nornir-automation/nornir" target="_blank">Nornir framework</a>,
<a href="https://nornir.tech/nornir/plugins/" target="_blank">Nornir Plugins</a> and <a href="https://github.com/pallets/click" target="_blank">Click</a>


## Features 

* **Manage your custom nornir runbooks**

    * Create and manage your own runbooks collections
    * Add your custom nornir runbooks to runbooks collections and run it for any hosts directly from the CLI 
    * Or use `nornir_cli` for inventory management only, and take the result in your nornir runbooks. By excluding getting and filtering the inventory in your runbooks, you will make them more versatile.

* **Manage Inventory**

    Get Inventory, filter Inventory, output Inventory and save Inventory state from the CLI.
    This is really useful for large, structured Inventory - for example, <a href="https://github.com/netbox-community/netbox" target="_blank">NetBox</a> with <a href="https://github.com/wvandeun/nornir_netbox" target="_blank">nornir_netbox plugin</a>.

* **Run Nornir Plugins**

    Run Tasks based on Nornir Plugins from the CLI, check result and statistic

* **Build a chain of `nornir_cli` commands**

    Initialize Nornir, filter Inventory and start Task/Tasks chains or runbook/runbooks chains in one command

* **Json input. Json output**

    Json strings are everywhere! Ok, only in commands options

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
nornir_cli, version 0.2.0

```

#### Simple Example


#### config.yaml
```yaml
# Simple Nornir configuration file
inventory:
    plugin: SimpleInventory
    options:
        host_file: "inventory/hosts.yaml"
```
#### hosts.yaml
```yaml
# Single host inventory
dev_1:
    hostname: 10.1.0.1
    username: username 
    password: password
    # huawei is just an example here
    platform: huawei
```
#### nornir_cli
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
