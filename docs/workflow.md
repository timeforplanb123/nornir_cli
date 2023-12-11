**`nornir_cli`** has a workflow that is familiar to the nornir user. There is:

* [Initializing Nornir](https://timeforplanb123.github.io/nornir_cli/workflow/#initializing-nornir)
* [Inventory](https://timeforplanb123.github.io/nornir_cli/workflow/#inventory)
* [Tasks and runbooks](https://timeforplanb123.github.io/nornir_cli/workflow/#tasks-and-runbooks)

You can run a workflow as a single command or you can split it into parts 

## Initializing Nornir 

You can initialize nornir with a configuration file, with code or with a combination of both.

#### With configuration file

Let's start with a configuration file. It is a typical Nornir configuration file.

By default, `nornir_cli` uses `config.yaml` in your current working directory. But you can specify path to your own configuration file with option `--config_file` or `-c`:
```text
# with default config.yaml in current working directory
$ nornir_cli nornir-netmiko init

# with path to config_file
$ nornir_cli nornir-netmiko init -c ~/config.yaml
```
Why is `nornir-netmiko` here? `nornir_cli` runs Tasks based on Nornir plugins or your custom Nornir runbooks, so the first step is to select an available plugin or custom group (see [Runbook collections](https://timeforplanb123.github.io/nornir_cli/workflow/#runbook-collections)).

For version `1.3.0`, the following Nornir plugins are available:
```text
$ nornir_cli --help
Usage: nornir_cli [OPTIONS] COMMAND [ARGS]...

  Nornir CLI

  Orchestrate your Inventory and start Tasks and Runbooks

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  nornir-f5        nornir_f5 plugin
  nornir-http      nornir_http plugin
  nornir-jinja2    nornir_jinja2 plugin
  nornir-napalm    nornir_napalm plugin
  nornir-netconf   nornir_netconf plugin
  nornir-netmiko   nornir_netmiko plugin
  nornir-paramiko  nornir_paramiko plugin
  nornir-pyez      nornir_pyez plugin
  nornir-pyxl      nornir_pyxl plugin
  nornir-scrapli   nornir_scrapli plugin
```
#### Without a configuration file

You can initialize nornir programmatically without a configuration file.

`-f` or `--from_dict` option waits json string:

`-c` or `--config_file` can be `""`, `None`, `null`


Here you can pass parameters as json strings using "=" or without it. In the case of "=", the `nornir_cli` completely repeats the syntax from Nornir runbooks, and you can use the Nornir configuration patterns that are already familiar to you (or see the [Nornir docs](https://nornir.readthedocs.io/en/latest/tutorial/initializing_nornir.html){target="_blank"}). In the case without using "=", you can pass all parameters as a json string. This can be useful in scripts or automation pipelines, when using `nornir_cli` with json utilities such as `jq`, `jc`. 
This way(json string using "=" or json string without "=") you can pass parameters to initializing, filtering and Nornir plugins/tasks running processes.

Examples:

=== "json string using '=':"
    ```text
    $ nornir_cli nornir-netmiko init -c "" -f 'inventory={"plugin":"NetBoxInventory2", \
    "options": {"nb_url": "http://your_netbox_domain", "nb_token": "your_netbox_token", \
    "ssl_verify": false}} runner={"plugin": "threaded", "options": {"num_workers": 50}} \
    logging={"enabled":true, "level": "DEBUG", "to_console": true}'
    ```
=== "json string:"
    ```text
    $ nornir_cli nornir-netmiko init -c "" -f '{"inventory":{"plugin":"NetBoxInventory2", \
    "options": {"nb_url": "http://your_netbox_domain", "nb_token": "your_netbox_token", \
    "ssl_verify": false}}, "runner":{"plugin": "threaded", "options": {"num_workers": 50}}, \
    "logging":{"enabled":true, "level": "DEBUG", "to_console": true}}'
    ```

Or you can initialize nornir with a combination of both methods:

#### Both ways

=== "json string using '=':"
    ```text
    $ nornir_cli nornir-netmiko init -f 'runner={"plugin": "threaded", "options": {"num_workers": 50}}'
    ```
=== "the same thing, but without '=':"
    ```text
    $ nornir_cli nornir-netmiko init -f '{"runner":{"plugin": "threaded", "options": {"num_workers": 50}}}'
    ```

`-c` or `--config_file` uses `config.yaml` in your current working directory, by default, so there is no `-c` option and only `-f` option here

## Inventory
`nornir_cli` follows `Nornir` [filtering interface](https://nornir.readthedocs.io/en/latest/tutorial/inventory.html#Filtering-the-inventory){target="_blank"}.

`init` returns [nornir.core.Nornir](https://github.com/nornir-automation/nornir/blob/e4f6b8c6258ae2dcfb286098b30652c7a31ecf30/nornir/core/__init__.py#L18){target="_blank"} object, which saved to `temp.pkl` file for future reference. `init` is enough to perform once in any way described [above](https://timeforplanb123.github.io/nornir_cli/workflow/#initializing-nornir). After that, you can filter inventory.


Now, let's take [nornir_netbox inventory plugin](https://github.com/wvandeun/nornir_netbox){target="_blank"} and do `init`, at first:

**config.yaml:**
```yaml
# we will use NetBox Inventory
inventory:
plugin: NetBoxInventory2
options:
  nb_url: "http://your_nebox_domain"
  nb_token: "your_netbox_token"
  ssl_verify: False
```

**init:**
```text
# -u / --username and -p / --password  will assign a username and password in defaults
# -co / --connection_options will assign options for Scrapli framework
# huawei is here just as an example
$ nornir_cli nornir-scrapli init -u username -p password -co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}'
```

And now let's filter [NetBox](https://github.com/netbox-community/netbox){target="_blank} inventory, as instance:

#### Filtering

=== "simple filtering:"
    ```text
    # let's filter current inventory and get dev_1 inventory object 
    # --hosts shows filtered hosts list
    $ nornir_cli nornir-scrapli filter --hosts name=dev_1
    [
        "dev_1"
    ]
    ```
=== "simple filtering with json string:"
    ```text
    # --inventory=host shows "hosts" inventory parameters for filtered hosts (dev_1 in example)
    # --hosts shows filtered hosts list
    # huawei is here just as an example
    $ nornir_cli nornir-scrapli filter --inventory=hosts --hosts 'primary_ip={"address": "10.1.0.1/32", "family": 4, "id": 13, "url": "http://your_netbox_domain/api/ipam/ip-addresses/13/"} name=dev_1'

    # or an alternative way(json string without "=")
    # $ nornir_cli nornir-scrapli filter --inventory=hosts --hosts '{"primary_ip":{"address": "10.1.0.1/32", "family": 4, "id": 13, "url": "http://your_netbox_domain/api/ipam/ip-addresses/13/"}, "name":"dev_1"}'
    {
        "hosts": {
            "dev_1": {
                "name": "dev_1",
                "connection_options": {},
                "groups": [],
                "data": {
                    "id": 13,
                    "name": "dev_1",
                    "display_name": "dev_1",
                    "device_type": {
                
                ...

                "hostname": "10.1.0.1",
                "port": null,
                "username": "username",
                "password": "password",
                "platform": "huawei"
            }
        } 
    }
    [
        "dev_1"
    ]
    ```
=== "advanced filtering:"
    ```text
    # --hosts shows filtered hosts list
    # -a / --advanced option enables advanced filtering
    $ nornir_cli nornir-scrapli filter --hosts -a 'name__contains=dev_1 device_role__name__contains=spine'
    [
        "dev_1"
    ]

    # the same with &
    $ nornir_cli nornir-scrapli filter --hosts -a 'name__contains=dev_1 & device_role__name__contains=spine'
    [
        "dev_1"
    ]

    # or |
    $ nornir_cli nornir-scrapli filter --hosts -a 'name__contains=dev_1 | name__contains=dev_2'
    Are you sure you want to output list of all required hosts on stdout? [Y/n]:
    [
        "dev_1"
        "dev_2"
    ]

    # another example
    # --count shows the first 3 items from filtered inventory (for hosts list with --hosts option in example)
    $ nornir_cli nornir-netmiko filter --hosts --count 3 -a 'data__device_type__model__contains=S2320-28TP-EI-DC & name__contains=dev_ | data__device_type__model__contains=S2320-28TP-EI-DC & name__contains=access'
    [
        "dev_1"
        "dev_2"
        "access_1"
    ]
    ```

By default, the filtered Inventory is not saved for future reference. It was done to perform `init` only once, and then to filter Inventory and run any commands from Nornir Plugins (see available plugins with `nornir_cli --help` command) or Nornir Runbooks (see [Runbook collections](https://timeforplanb123.github.io/nornir_cli/workflow/#runbook-collections)) as a single command (see [Command chains](https://timeforplanb123.github.io/nornir_cli/workflow/#command-chains)). This is useful and saves time on `init` with large inventories.

But, you can save the Inventory state after filtering with `-s` or `--save` option and work with new Inventory object. So any commands from Nornir Plugins or Nornir Runbooks will be run for the saved object.

Filter Inventory ans save it as much as needed. Perform `init` if you need to return full Inventory state again.

As instance, let's save Inventory after simple filtering:
```text
# get new inventory object with single host (dev_1)
# --hosts shows filtered and saved hosts
$ nornir_cli nornir-scrapli filter --hosts -s name=dev_1
[
    "dev_1"
]
```

**IMPORTANT:** if you want to save the Inventory state after filtering for future references, please use `--save` or `-s` option.

#### Show inventory

As you may have already noticed, it's possible to view the current inventory state with `show_inventory` command:
```text
$ nornir_cli nornir-scrapli show_inventory -i hosts -h -g --count 6
# hosts inventory
{
    "hosts": {
        "dev_1": {
            "name": "dev_1",
            "connection_options": {},
            "groups": [],
            "data": {
                "id": 13,
                "name": "dev_1",
                "display_name": "dev_1",
                "device_type": {
            
            ...

            "hostname": "10.1.0.1",
            "port": null,
            "username": "username",
            "password": "password",
            "platform": "huawei"
        }
    }
}
        ...  # there is 6 Hosts Inventory in json format
# hosts list
[
    "dev_1"
    "dev_2"
    "dev_3"
    "dev_4"
    "dev_5"
    "access_1"
]
# groups list
[]
```
`-i` or `--inventory` option can be `hosts`, `groups`, `defaults` or `all`.

`-cou` or `--count` is counter, that refers to each requested parameter.

`-cou` or `--count` can be:

- `--count -100` - last 100 items

- `--count 100` - first 100 items

- `--count 0` - 0 items

- without `--count` option - all items (default value)

As instance:

=== "to show the first 2 hosts from Inventory:"
    ```text
    $ nornir_cli nornir-scrapli show_inventory -h -cou 2
    # hosts list for the first 2 hosts 
    [
        "dev_1"
        "dev_2"
    ]
    ```
    `-h` or `--hosts` option is default option, so the same is `nornir_cli nornir-scrapli show_inventory -cou 2`.

    For the latest 2 hosts from Inventory use `-cou -2`
=== "to show the first 2 hosts, groups (if exist):"
    ```text
    $ nornir_cli nornir-scrapli show_inventory -h -g -cou 2
    # hosts list for the first 2 hosts
    [
        "dev_1"
        "dev_2"
    ]
    # groups list for the first 2 groups (groups don't exist)
    []
    ```
=== "to show the first 2 hosts and their hosts inventory:"
    ```text
    $ nornir_cli nornir-scrapli show_inventory -h -i hosts -cou 2
    # hosts inventory for the first 2 hosts
    {
        "hosts": {
            "dev_1": {
                "name": "dev_1",
                "connection_options": {},
                "groups": [],
                "data": {
                    "id": 13,
                    "name": "dev_1",
                    "display_name": "dev_1",
                    "device_type": {
                
                ...

                "hostname": "10.1.0.1",
                "port": null,
                "username": "username",
                "password": "password",
                "platform": "huawei"
            }
            "dev_2": {
                "name": "dev_2",
                "connection_options": {},
                "groups": [],
                "data": {
                    "id": 14,
                    "name": "dev_2",
                    "display_name": "dev_2",
                    "device_type": {
                
                ...

                "hostname": "10.1.0.2",
                "port": null,
                "username": "username",
                "password": "password",
                "platform": "huawei"
            }
        }
    }

    # hosts list for the first 2 hosts
    [
        "dev_1"
        "dev_2"
    ]
    ```
=== "to show the first 2 hosts and all inventory:"
    ```text
    $ nornir_cli nornir-scrapli show_inventory -h -i all -cou 2
    # hosts inventory for the first 2 hosts
    {
        "hosts": {
            "dev_1": {
                "name": "dev_1",
                "connection_options": {},
                "groups": [],
                "data": {
                    "id": 13,
                    "name": "dev_1",
                    "display_name": "dev_1",
                    "device_type": {
                
                ...

                "hostname": "10.1.0.1",
                "port": null,
                "username": "username",
                "password": "password",
                "platform": "huawei"
            }
            "dev_2": {
                "name": "dev_2",
                "connection_options": {},
                "groups": [],
                "data": {
                    "id": 14,
                    "name": "dev_2",
                    "display_name": "dev_2",
                    "device_type": {
                
                ...

                "hostname": "10.1.0.2",
                "port": null,
                "username": "username",
                "password": "password",
                "platform": "huawei"
            }
        }
    }
    # groups inventory for the first 2 groups (groups don't exist)
    {
        "groups": {}
    }
    # defaults inventory is always 1, so counter (`-cou` or `--count`) doesn't work for it
    {
        "defaults": {
            "data": {},
            "connection_options": {},
            "hostname": null,
            "port": null,
            "username": "username",
            "password": "password",
            "platform": null
        }
    }
    # hosts list for the first 2 hosts
    [
        "dev_1"
        "dev_2"
    ]
    ```
    `all` inventory here is the first 2 hosts, groups (groups don't exist in example) and defaults inventory parameters. Counter (`-cou` or `--count`) doesn't work for defaults, because defaults is always 1.

And you can invoke `show_inventory` command from `init` or `filter` commands with `-i / --inventory`, `-h / --hosts`, `-g / --groups` options.

#### Changing credentials

You can change credentials in any time for current Inventory with `change_credentials` command.

To save Inventory state for future references use `-s` or `--save` option.

```text
$ nornir_cli nornir-scrapli change_credentials --help
Usage: nornir_cli nornir-scrapli change_credentials [OPTIONS]

  Change username and password for current Nornir object.

  If no options are specified, the username and password will be changed for
  defaults only, as instance:

      nornir_cli nornir-scrapli change_credentials -u user -p password
      show_inventory -i defaults

  If only hosts or groups are specified (use string for single host and list
  of strings for many hosts), then the username and password will be changed
  only for them, as instance:

      nornir_cli nornir-scrapli change_credentials -u user -p password -h
      '["spine_1"]'

  To change the username and password for all hosts or groups, use "all" as
  option value, as instance:

      nornir_cli nornir-scrapli change_credentials -u user -p password -h
      "all"

Options:
  -u, --username TEXT  Hosts, groups or defaults username
  -p, --password TEXT  Hosts, groups or defaults password
  -h, --hosts TEXT     List of hosts (json string) or single host (str)
  -g, --groups TEXT    List of groups (json string) or single group (str)
  -d, --defaults       Defaults credentials
  -s, --save           Save Nornir object with new credentials to pickle file
                       for later use
  --help               Show this message and exit.
```

Let's take [nornir_netbox inventory plugin](https://github.com/wvandeun/nornir_netbox){target="_blank"} and do `init`, at first:

**config.yaml:**
```yaml
# we will use NetBox Inventory
inventory:
plugin: NetBoxInventory2
options:
  nb_url: "http://your_nebox_domain"
  nb_token: "your_netbox_token"
  ssl_verify: False
```

**init:**
```text
# -u / --username and -p / --password  will assign a username and password in defaults
$ nornir_cli nornir-scrapli init -u username -p password
```

And now let's `change_credentials` for `defaults` Inventory and run `show_inventory` with new credentials:
```text
# use -s option to save Inventory with new credentials for future references
$ nornir_cli nornir-scrapli change_credentials -u user -p pass show_inventory -i defaults
{
    "defaults": {
        "data": {},
        "connection_options": {},
        "hostname": null,
        "port": null,
        "username": "user",
        "password": "pass",
        "platform": null
    }
}
```

`change_credentials` for all `hosts` and check `hosts` Inventory with new credentials (you can do the same for `groups` Inventory):
```text
# use -s option to save Inventory with new credentials for future references
$ nornir_cli nornir-scrapli change_credentials -u user -p pass -h all show_inventory -i hosts
{
    "hosts": {
        "dev_1": {
            "name": "dev_1",
            "connection_options": {},
            "groups": [],
            "data": {},
            "hostname": "10.3.2.1",
            "port": 22,
            "username": "user",
            "password": "pass",
            "platform": null
        }
        ...
        # other hosts
        ...
    }
}
```

`change_credentials` for `hosts` list and check `hosts` Inventory with new credentials (you can do the same for `groups` Inventory):
```text
# use -s option to save Inventory with new credentials for future references
$ nornir_cli nornir-scrapli change_credentials -u username -p password -h '["dev_1"]' show_inventory -i hosts
{
    "hosts": {
        "dev_1": {
            "name": "dev_1",
            "connection_options": {},
            "groups": [],
            "data": {},
            "hostname": "10.3.2.1",
            "port": 22,
            "username": "username",
            "password": "password",
            "platform": null
        }
        ...
        # other hosts with "user" username and "password" password
        ...
    }
}
```

Also, you can use [environment variables](https://timeforplanb123.github.io/nornir_cli/useful/#environment-variables), `NORNIR_CLI_USERNAME` and `NORNIR_CLI_PASSWORD`:
```text
$ export NORNIR_CLI_USERNAME=user
$ export NORNIR_CLI_PASSWORD=pass

# use -s option to save Inventory with new credentials for future references
$ nornir_cli nornir-scrapli change_credentials -h '["dev_1"]' show_inventory -i hosts
{
    "hosts": {
        "dev_1": {
            "name": "dev_1",
            "connection_options": {},
            "groups": [],
            "data": {},
            "hostname": "10.3.2.1",
            "port": 22,
            "username": "user",
            "password": "pass",
            "platform": null
        }
        ...
        # other hosts with "user" username and "password" password
        ...
    }
}
```

## Tasks and runbooks


**I must say that each argument or option parameter can be passed to the Task as a json string. It's important.**


#### Single tasks

Ok, now we have filtered inventory for `dev_1`:

=== "config.yaml:"
    ```yaml
    # we will use NetBox Inventory
    inventory:
    plugin: NetBoxInventory2
    options:
      nb_url: "http://your_nebox_domain"
      nb_token: "your_netbox_token"
      ssl_verify: False
    ```
=== "init:"
    ```text
    # -u / --username and -p / --password  will assign a username and password in defaults
    # -co / --connection_options will assign options for Scrapli framework
    # huawei is here just as an example
    $ nornir_cli nornir-scrapli init -u username -p password -co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}'
    ```
=== "simple filtering:"
    ```text
    # let's filter current inventory, get dev_1 inventory object and save it
    # --hosts shows filtered hosts list
    $ nornir_cli nornir-scrapli filter --hosts -s name=dev_1

    # or an alternative way(json string)
    # $ nornir_cli nornir-scrapli filter --hosts -s '{"name":"dev_1"}'
    [
        "dev_1"
    ]
    ```

And let's start some Task based on Nornir plugins:

At first, let's check all available Tasks/commands for current list of Nornir plugins:

=== "norir-netmiko:"
    ```text
    $ nornir_cli nornir-netmiko
    Usage: nornir_cli nornir-netmiko [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                     [ARGS]...]...

      nornir_netmiko plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials     Change username and password
      filter                 Do simple or advanced filtering
      init                   Initialize a Nornir
      netmiko_commit         Execute Netmiko commit method
      netmiko_file_transfer  Execute Netmiko file_transfer method
      netmiko_multiline      Execute Netmiko send_multiline method (or
                             send_multiline_timing)
      netmiko_save_config    Execute Netmiko save_config method
      netmiko_send_command   Execute Netmiko send_command method (or
                             send_command_timing)
      netmiko_send_config    Execute Netmiko send_config_set method (or
                             send_config_from_file)
      print_result           print_result from nornir_utils
      show_inventory         Show current inventory
      write_file             Write_file, but not from nornir_utils
      write_result           Write `Result` object to file
      write_results          Write `Result` object to files
    ```
=== "nornir-scrapli:"
    ```text
    $ nornir_cli nornir-scrapli
    Usage: nornir_cli nornir-scrapli [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                 [ARGS]...]...

      nornir_scrapli plugin

    Options:
      --help  Show this message and exit.

    Commands:
      cfg_abort_config         Abort a device candidate config with scrapli-cfg
      cfg_commit_config        Commit a device candidate config with scrapli-cfg
      cfg_diff_config          Diff a device candidate config vs a source config
                               with scrapli-cfg
      cfg_get_config           Get device config with scrapli-cfg
      cfg_get_version          Get device version with scrapli-cfg
      cfg_load_config          Load device config with scrapli-cfg
      change_credentials       Change username and password
      filter                   Do simple or advanced filtering
      get_prompt               Get current prompt from device using scrapli
      init                     Initialize a Nornir
      netconf_capabilities     Retrieve the device config with scrapli_netconf
      netconf_commit           Commit the device config with scrapli_netconf
      netconf_delete_config    Send a "delete-config" rcp to the device with
                               scrapli_netconf
      netconf_discard          Discard the device config with scrapli_netconf
      netconf_edit_config      Edit config from the device with scrapli_netconf
      netconf_get              Get from the device with scrapli_netconf
      netconf_get_config       Get config from the device with scrapli_netconf
      netconf_lock             Lock the device with scrapli_netconf
      netconf_rpc              Send a "bare" rcp to the device with
                               scrapli_netconf
      netconf_unlock           Unlock the device with scrapli_netconf
      netconf_validate         Send a "validate" rcp to the device with
                               scrapli_netconf
      print_result             print_result from nornir_utils
      send_command             Send a single command to device using scrapli
      send_commands            Send a list of commands to device using scrapli
      send_commands_from_file  Send a list of commands from a file to device using
                               scrapli
      send_config              Send a config to device using scrapli
      send_configs             Send configs to device using scrapli
      send_configs_from_file   Send configs from a file to device using scrapli
      send_interactive         Send inputs in an interactive fashion using
                               scrapli; usually used to handle prompts
      show_inventory           Show current inventory
      write_file               Write_file, but not from nornir_utils
      write_result             Write `Result` object to file
      write_results            Write `Result` object to files
    ```
=== "nornir-napalm:"
    ```text
    $ nornir_cli nornir-napalm
    Usage: nornir_cli nornir-napalm [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                [ARGS]...]...

      nornir_napalm plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials  Change username and password
      filter              Do simple or advanced filtering
      init                Initialize a Nornir
      napalm_cli          Run commands on remote devices using napalm
      napalm_configure    Loads configuration into a network devices using napalm
      napalm_get          Gather information from network devices using napalm
      napalm_ping         Executes ping on the device and returns a dictionary
                          with the result
      napalm_validate     Gather information with napalm and validate it
      print_result        print_result from nornir_utils
      show_inventory      Show current inventory
      write_file          Write_file, but not from nornir_utils
      write_result        Write `Result` object to file
      write_results       Write `Result` object to files
    ```
=== "nornir-jinja2:"
    ```text
    $ nornir_cli nornir-jinja2
    Usage: nornir_cli nornir-jinja2 [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                [ARGS]...]...

      nornir_jinja2 plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials  Change username and password
      filter              Do simple or advanced filtering
      init                Initialize a Nornir
      print_result        print_result from nornir_utils
      show_inventory      Show current inventory
      template_file       Renders contants of a file with jinja2. All the host
                          data is available in the template
      template_string     Renders a string with jinja2. All the host data is
                          available in the template
      write_file          Write_file, but not from nornir_utils
      write_result        Write `Result` object to file
      write_results       Write `Result` object to files
    ```
=== "nornir-pyez:"
    ```text
    $ nornir_cli nornir-pyez
    Usage: nornir_cli nornir-pyez [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                  [ARGS]...]...

      nornir_pyez plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials             Change username and password
      filter                         Do simple or advanced filtering
      init                           Initialize a Nornir
      print_result                   print_result from nornir_utils
      pyez_chassis_inventory
      pyez_checksum
      pyez_cmd
      pyez_commit
      pyez_config
      pyez_diff
      pyez_facts
      pyez_get_arp
      pyez_get_config
      pyez_get_int_optics_diag_info
      pyez_int_terse
      pyez_rollback
      pyez_route_info
      pyez_rpc
      pyez_scp
      pyez_sec_ike
      pyez_sec_ipsec
      pyez_sec_nat_dest
      pyez_sec_nat_src
      pyez_sec_policy
      pyez_sec_zones
      show_inventory                 Show current inventory
      write_file                     Write_file, but not from nornir_utils
      write_result                   Write `Result` object to file
      write_results                  Write `Result` object to files
    ```
=== "nornir-f5:"
    ```text
    $ nornir_cli nornir-f5
    Usage: nornir_cli nornir-f5 [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                [ARGS]...]...

      nornir_f5 plugin

    Options:
      --help  Show this message and exit.

    Commands:
      atc                             Task to deploy declaratives on F5 devices
      atc_info                        Task to verify if ATC service is available
                                      and collect service info
      bigip_cm_config_sync            Task to synchronize the configuration
                                      between devices
      bigip_cm_failover_status        Task to get the failover status of the
                                      device
      bigip_cm_sync_status            Task to get the synchronization status of
                                      the device
      bigip_shared_file_transfer_uploads
                                      Upload a file to a BIG-IP system using the
                                      iControl REST API
      bigip_shared_iapp_lx_package    Task to manage Javascript LX packages on a
                                      BIG-IP
      bigip_sys_version               Gets the system version of the BIG-IP
      bigip_util_unix_ls              Task to list information about the FILEs
      bigip_util_unix_rm              Task to delete a file from a BIG-IP system
      change_credentials              Change username and password
      filter                          Do simple or advanced filtering
      init                            Initialize a Nornir
      print_result                    print_result from nornir_utils
      show_inventory                  Show current inventory
      write_file                      Write_file, but not from nornir_utils
      write_result                    Write `Result` object to file
      write_results                   Write `Result` object to files
    ```
=== "nornir-paramiko:"
    ```text
    $ nornir_cli nornir-paramiko
    Usage: nornir_cli nornir-paramiko [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                      [ARGS]...]...

      nornir_paramiko plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials  Change username and password
      filter              Do simple or advanced filtering
      init                Initialize a Nornir
      paramiko_command    Executes a command remotely on the host
      paramiko_sftp       Transfer files from/to the device using sftp protocol
      print_result        print_result from nornir_utils
      show_inventory      Show current inventory
      write_file          Write_file, but not from nornir_utils
      write_result        Write `Result` object to file
      write_results       Write `Result` object to files
    ```
=== "nornir-http:"
    ```text
    $ nornir_cli nornir-http
    Usage: nornir_cli nornir-http [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                  [ARGS]...]...

      nornir_http plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials  Change username and password
      filter              Do simple or advanced filtering
      http_method         This is a helper task that uses `httpx
                          <https://www.python-httpx.org/api/>`_ to interact with
                          an HTTP server
      init                Initialize a Nornir
      print_result        print_result from nornir_utils
      show_inventory      Show current inventory
      write_file          Write_file, but not from nornir_utils
      write_result        Write `Result` object to file
      write_results       Write `Result` object to files
    ```
=== "nornir-pyxl:"
    ```text
    $ nornir_cli nornir-pyxl
    Usage: nornir_cli nornir-pyxl [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                  [ARGS]...]...

      nornir_pyxl plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials  Change username and password
      filter              Do simple or advanced filtering
      init                Initialize a Nornir
      print_result        print_result from nornir_utils
      pyxl_ez_data        Loads a specific sheet from a workbook(xlsx file)
      show_inventory      Show current inventory
      write_file          Write_file, but not from nornir_utils
      write_result        Write `Result` object to file
      write_results       Write `Result` object to files
    ```
=== "nornir-netconf:"
    ```text
    $ nornir_cli nornir-netconf
    Usage: nornir_cli nornir-netconf [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                     [ARGS]...]...

      nornir_netconf plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials    Change username and password
      filter                Do simple or advanced filtering
      init                  Initialize a Nornir
      netconf_capabilities  Gather Netconf capabilities from device
      netconf_commit        Commit operation
      netconf_edit_config   Edit configuration of device using Netconf
      netconf_get           Get information over Netconf from device
      netconf_get_config    Get configuration over Netconf from device
      netconf_get_schemas   Fetch provided schemas and write to a file
      netconf_lock          NETCONF locking operations for a specified datastore
      print_result          print_result from nornir_utils
      show_inventory        Show current inventory
      write_file            Write_file, but not from nornir_utils
      write_result          Write `Result` object to file
      write_results         Write `Result` object to files
    ```
=== "nornir-routeros"
    ```text
    Usage: nornir_cli nornir-routeros [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                      [ARGS]...]...

      nornir_routeros plugin

    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials    Change username and password
      filter                Do simple or advanced filtering
      init                  Initialize a Nornir
      print_result          print_result from nornir_utils
      routeros_command      Runs a RouterOS command such as ping or fetch
      routeros_config_item  Configures an item
      routeros_get          Returns a RouterOS resource
      show_inventory        Show current inventory
      write_file            Write_file, but not from nornir_utils
      write_result          Write `Result` object to file
      write_results         Write `Result` object to files
    ```

And start `netmiko_send_command`, for example:

```text
$ nornir_cli nornir-netmiko netmiko_send_command --command_string "display clock"

# or using json string as command argument
# $ nornir_cli nornir-netmiko netmiko_send_command '{"command_string":"display clock"}'
netmiko_send_command************************************************************
* dev_1 ** changed : False *****************************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
2021-03-19 12:57:11+03:00
Friday
Time Zone(Moscow) : UTC+03:00
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dev_1            : ok=1               changed=0               failed=0

OK      : 1
CHANGED : 0
FAILED  : 0
```

Before, we added connection options for scrapli in `init` command.
Let's check out some `nornir-scrapli` command:

```text
$ nornir_cli nornir-scrapli send_command --command "display clock"

# or using json string as command argument
# $ nornir_cli nornir-scrapli send_command '{"command":"display clock"}'
send_command********************************************************************
* dev_1 ** changed : False *****************************************************
vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
2021-03-19 13:18:53+03:00
Friday
Time Zone(Moscow) : UTC+03:00
^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dev_1            : ok=1               changed=0               failed=0

OK      : 1
CHANGED : 0
FAILED  : 0
```

As you may have noticed, there is a result and statistic in the output above. There are options `--print_result` and `--print_stat` for this. Options `--no_print_result` and `--no_print_stat` disable it.

`nornir-scrapli send_command` options, as instance:
```text
$ nornir_cli nornir-scrapli send_command --help
Usage: nornir_cli nornir-scrapli send_command [OPTIONS] [ARGUMENTS]

  Send a single command to device using scrapli

      Args:

          command: string to send to device in privilege exec mode

          strip_prompt: True/False strip prompt from returned output

          failed_when_contains: string or list of strings indicating failure
          if found in response

          timeout_ops: timeout ops value for this operation; only sets the
          timeout_ops value for the duration of the operation, value is reset
          to initial value after operation is completed

      Returns: nornir Result attributes(optional), statistic, progress
      bar(optional)

Options:
  --pg_bar                        Progress bar flag
  --print_result / --no_print_result
                                  print_result from nornir_utils  [default:
                                  print_result]
  --print_stat / --no_print_stat  Print Result statistic for Nornir object
                                  [default: print_stat]
  --command TEXT                  [required]
  --strip_prompt BOOLEAN          [default: True]
  --failed_when_contains TEXT     [default: None]
  --timeout_ops TEXT              [default: None]
  --help                          Show this message and exit.
```

The examples above show 2 ways to pass parameters to the command:
- using the command option:
```text
$ nornir_cli nornir-netmiko netmiko_send_command --command_string "display clock"
```
- using a json string argument:
```text
$ nornir_cli nornir-netmiko netmiko_send_command '{"command_string":"display clock"}'
# or
$ nornir_cli nornir-netmiko netmiko_send_command 'command_string=display clock'
# or
$ nornir_cli nornir-netmiko netmiko_send_command '"command_string"="display clock"'
```

When using options and arguments at the same time, the priority of options will be higher. For example, `nornir_cli nornir-netmiko netmiko_send_command --command_string "disp ver" '{"command_string":"disp clock"}'` will send `disp ver` command to device.

#### Result processing

**print_result**

As you can see, you can disable default option `--print_result`, `--print_stat` and use `print_result` command instead of these. 

`--print_result` option uses default arguments, but `print_result` command allows you to customize the output. You can output [`class Result`](https://github.com/nornir-automation/nornir/blob/2e0c9f4e8997f05ac60e94956faa6443302133d4/nornir/core/task.py#L185){target="_blank"} attributes, limit results with `--count` option, print statistic with `--print_stat` option, etc. 

Let's see `print_result` options and run it:
=== "print_result options:"
    ```text
    $ nornir_cli nornir-scrapli print_result --help
    Usage: nornir_cli nornir-scrapli print_result [OPTIONS]

      print_result from nornir_utils

    Options:
      -ph, --print_host BOOLEAN       Print hostnames  [default: True]
      -attrs, --attributes TEXT       Result class attributes you want to print
      -ps, --print_stat / -no_ps, --no_print_stat
                                      Print Result statistic for Nornir object
                                      [default: no_ps]
      -cou, --count INTEGER           Results counter
      -sl, --severity_level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                      Show only errors with this severity level or
                                      higher  [default: INFO]
      --failed BOOLEAN                If True assume the task failed  [default:
                                      False]
      --help                          Show this message and exit.
    ```
=== "run print_result:"
    ```text
    $ nornir_cli nornir-scrapli send_command --command "disp clock" --no_print_result --no_print_stat print_result -attrs '["result", "diff"]' -ps

    # or using json string as command argument
    # please note that the arguments must be specified after the options
    # $ nornir_cli nornir-scrapli send_command --no_print_result --no_print_stat '{"command":"disp clock"}' print_result -attrs '["result", "diff"]' -ps
    send_command********************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    2021-10-03 16:40:06+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00
    ^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    dev_1         : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0

    # send_command doesn't have "diff" attribute, so it's not displayed
    ```

**write_result and write_results**

Result can be written to a file using `write_result` command for all hosts from current Inventory. 

By default, `write_result`  tries to create a file in the current directory or in the specified directory, if file doesn't exist.

`write_result` command has many options. For example, you can exclude errors from a file, write "diff" to another file or output it, use different write modes, limit entries number, etc.

If you want to see which hosts have completed the task with an error, but do not add errors to the files, use `--no_errors` or `-ne` with `--print_stat` or `-ps` option.

=== "write_result options:"
    ```text
    $ nornir_cli nornir-scrapli write_result --help
    Usage: nornir_cli nornir-scrapli write_result [OPTIONS]

      Write an object of type `nornir.core.task.Result` to file

    Options:
      -f, --filename TEXT             File you want to write into  [required]
      -ne, --no_errors                Do not write errors to file  [default:
                                      False]
      -wh, --write_host BOOLEAN       Write hostnames  [default: True]
      -dtf, --diff_to_file PATH       Write diff to file
      -pd, --print_diff / -no_pd, --no_print_diff
                                      Print diff  [default: no_pd]
      -a, --append                    Whether you want to replace the contents or
                                      append to it  [default: False]
      -attrs, --attributes TEXT       Result attributes you want to write (str or
                                      list(json string)). There can be any Result
                                      attributes or text. By default, the result
                                      attribute is used
      -ps, --print_stat / -no_ps, --no_print_stat
                                      Print Result statistic for Nornir object
                                      [default: no_ps]
      -cou, --count INTEGER           Results counter
      -sl, --severity_level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                      Show only errors with this severity level or
                                      higher  [default: INFO]
      --failed BOOLEAN                If True assume the task failed  [default:
                                      False]
      --help                          Show this message and exit.
    ```
=== "run write_result and print_stat:"
    ```text
    $ nornir_cli nornir-scrapli send_command --command "disp clock" --no_print_result --no_print_stat write_result -f test.txt -ne -ps -attrs '["result", "diff"]'

    # or using json string as command argument
    # please note that the arguments must be specified after the options
    # $ nornir_cli nornir-scrapli send_command --no_print_result --no_print_stat '{"command":"disp clock"}' write_result -f test.txt -ne -ps -attrs '["result", "diff"]'
    dev_1         : ok=1               changed=0               failed=0              

    OK      : 1
    CHANGED : 0
    FAILED  : 0

    # send_command doesn't have "diff" attribute, so it's not displayed
    ```
=== "test.txt:"
    ```text
    vvvv dev_1: ** send_command ** changed : False  INFO

    2021-10-03 17:03:41+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00
    ```

Result can be written to a files with hostnames as filenames using `write_results` command for all hosts from current Inventory. For example, it is usefull for diagnostic commands, that run many `show something` or `display something` commands.

By default, `write_results`  tries to create a specified directory, if it doesn't exist.

`write_results` command has the same options as `write_result`, but uses `-d` or `--dirname` instead of `-f` or `--filename`.

If you want to see which hosts have completed the task with an error, but do not add errors to the files, use `--no_errors` or `-ne` with `--print_stat` or `-ps` option.

=== "write_results options:"
    ```text
    $ nornir_cli nornir-scrapli write_results --help
    Usage: nornir_cli nornir-scrapli write_results [OPTIONS]

      Write an object of type `nornir.core.task.Result` to files with hostname
      names

    Options:
      -d, --dirname TEXT              Direcotry you want to write into  [required]
      -ne, --no_errors                Do not write errors to file  [default:
                                      False]
      -wh, --write_host BOOLEAN       Write hostnames  [default: True]
      -dtf, --diff_to_file PATH       Write diff to file
      -pd, --print_diff / -no_pd, --no_print_diff
                                      Print diff  [default: no_pd]
      -a, --append                    Whether you want to replace the contents or
                                      append to it  [default: False]
      -attrs, --attributes TEXT       Result attributes you want to write (str or
                                      list(json string)). There can be any Result
                                      attributes or text. By default, the result
                                      attribute is used
      -ps, --print_stat / -no_ps, --no_print_stat
                                      Print Result statistic for Nornir object
                                      [default: no_ps]
      -cou, --count INTEGER           Results counter
      -sl, --severity_level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                      Show only errors with this severity level or
                                      higher  [default: INFO]
      --failed BOOLEAN                If True assume the task failed  [default:
                                      False]
      --help                          Show this message and exit.
    ```
=== "run write_results and print_stat:"
    ```text
    $ nornir_cli nornir-scrapli send_command --command "disp clock" --no_print_result --no_print_stat write_results -d test -ne -ps -attrs '["result", "diff"]'

    # or using json string as command argument
    # please note that the arguments must be specified after the options
    # $ nornir_cli nornir-scrapli send_command --no_print_result --no_print_stat '{"command":"disp clock"}' write_results -d test -ne -ps -attrs '["result", "diff"]'
    dev_1         : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0

    # send_command doesn't have "diff" attribute, so it's not displayed
    ```
=== "test/dev_1:"
    ```text
    vvvv dev_1 ** send_command ** changed : False  INFO

    2021-10-03 17:28:57+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00
    ```

**write_file**

`write_file` command writes any text to a file with the required number of indents. So you can add some useful data to previously generated file `test.txt`:

=== "write_file options:"
    ```text
    $ nornir_cli nornir-scrapli write_file --help
    Usage: nornir_cli nornir-scrapli write_file [OPTIONS]

      Write_file, but not from nornir_utils

    Options:
      -l, --line_feed      number of \n before text  [default: 0;x>=0]
      -a, --append         Whether you want to replace the contents or append to
                           it  [default: False]
      -c, --content TEXT   Content you want to write (string)  [required]
      -f, --filename TEXT  File you want to write into  [required]
      --help               Show this message and exit.
    ```
=== "run write_file:"
    ```text
    $ nornir_cli nornir-scrapli write_file -lll -a -c "some useful data" -f test.txt
    ```
=== "test.txt:"
    ```text
    vvvv dev_1 ** send_command ** changed : False  INFO

    2021-10-03 17:03:41+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00


    some useful data
    ```


#### What about netconf?

If some devices support netconf, you can use `nornir-scrapli`, `nornir-netconf` or `nornir-pyez` Nornir plugins from `nornir_cli`.

[Here is easy way to get xml tree from yang](https://timeforplanb123.github.io/nornir_cli/useful/#how-to-craft-xml-from-yang)

As instance,`dev_3` understands netconf XML. Let's get `nornir.core.Nornir` object for `dev_3` and run some netconf command with nornir-scrapli and nornir-netconf:

**nornir-scrapli:**
=== "get Nornir object for dev_3:"
    ```text
    $ nornir_cli nornir-scrapli init -u username -p password -co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' filter --hosts -s 'name=dev_3'
    [
        "dev_3"
    ]
    ```
=== "nornir-scrapli:"
    ```text
    $ nornir_cli nornir-scrapli netconf_get --filter_='<ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm"><interfaces><interface><ifName/></interface></interfaces></ifm>' --filter_type subtree

    # or
    # $ nornir_cli nornir-scrapli netconf_get --filter_ '<ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm"><interfaces><interface><ifName/></interface></interfaces></ifm>' --filter_type subtree

    ...
    netconf_get*********************************************************************
    * dev_3 ** changed : False *****************************************************
    vvvv netconf_get ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
      <data>
        <ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm">
          <interfaces>
            <interface>
              <ifIndex>1</ifIndex>
              <ifName>Virtual-Template0</ifName>
            </interface>
            
            ...

            <interface>
              <ifIndex>717</ifIndex>
              <ifName>GigabitEthernet4/1/1.514</ifName>
            </interface>
          </interfaces>
        </ifm>
      </data>
    </rpc-reply>

    ^^^^ END netconf_get ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_3                                        : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```

**nornir-netconf with write_result command:**
=== "get Nornir object for dev_3:"
    ```text
    nornir_cli nornir-netconf init -u username -p password -c None -co '{"netconf": {"extras":{"allow_agent": false, "look_for_keys": false, "hostkey_verify": false}}}' -f 'inventory={"plugin":"NetBoxInventory2", "options": {"nb_url": "http://your_netbox_domain", "nb_token": "your_netbox_token", "ssl_verify": false}} runner={"plugin": "threaded", "options": {"num_workers": 50}}'

    $ nornir_cli nornir-netconf filter -s 'name=dev_3'
    [
       "dev_3"
    ]
    ```
=== "nornir-netconf:"
    ```text
    $ nornir_cli nornir-netconf netconf_get --path '<ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm" content-version="1.0" format-version="1.0">  <interfaces>    <interface>      <ifName/>    </interface>  </interfaces></ifm>' --filter_type subtree  --no_print_result --no_print_stat write_result -f netconf.txt
    ```
=== "netconf.txt:"
    ```text
    vvvv dev_3: netconf_get ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO

    {'error': None, 'errors': [], 'ok': True, 'rpc': <?xml version="1.0" encoding="UTF-8"?>
    <rpc-reply message-id="urn:uuid:3" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <data>
        <ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm">
          <interfaces>
            <interface>
              <ifName>Virtual-Template0</ifName>
            </interface>
            <interface>
              <ifName>NULL0</ifName>
            </interface>
            <interface>
              <ifName>GigabitEthernet0/0/0</ifName>
            </interface>
            ...
            </interfaces>
        </ifm>
      </data>
    </rpc-reply>}
    ```

#### What about http, xlsx, jinja2?

`nornir_cli` includes `nornir-http`, `nornir-pyxl`, `nornir-jinja2` Nornir plugins. 

Remember that when using these plugins, each command is run for each host from the Inventory. Therefore, if you need to process `xlsx`, execute `http request` or get a single `jinja2` template without binding to devices, then run the command from the Nornir plugin for one device from the Inventory. 

See [examples](https://timeforplanb123.github.io/nornir_cli/examples/)

#### Command chains

And, of course, you can run any command chains, even very scary ones. For `nornir_cli` version `<= 1.2.0`, you can use the following syntax:

```text
$ nornir_cli nornir-scrapli init -u username -p password \
-co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' \
filter --hosts -s 'name=dev_1' send_command --command "display clock" \
send_interactive --interact_events '[["save", "Are you sure to continue?[Y/N]", false], \
["Y", "Save the configuration successfully.", true]]'
```

For `nornir_cli` version ` >= 1.3.0`, you can use only json strings as an argument:

```text
# $ nornir_cli nornir-scrapli init -u username -p password \
-co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' \
filter --hosts -s '{"name":"dev_1"}' send_command '{"command":"display clock"}' \
send_interactive '{"interact_events":[["save", "Are you sure to continue?[Y/N]", false], \
["Y", "Save the configuration successfully.", true]]}'
[
    "dev_1"
]

send_command********************************************************************
* dev_1 ** changed : False *****************************************************
vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
2021-03-19 14:12:38+03:00
Friday
Time Zone(Moscow) : UTC+03:00
^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dev_1            : ok=1               changed=0               failed=0

OK      : 1
CHANGED : 0
FAILED  : 0

send_interactive****************************************************************
* dev_1 ** changed : True ******************************************************
vvvv send_interactive ** changed : True vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
^^^^ END send_interactive ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dev_1            : ok=1               changed=1               failed=0

OK      : 1
CHANGED : 1
FAILED  : 0
```

**Again, i repeat that each argument can be passed to the Task as a json string.**

#### Runbook collections

If you solve some automation tasks with the Nornir, then you, probably, have Nornir runbooks.You can use `nornir_cli` as interface for manage these Nornir runbooks.

Create any directory trees in the `custom_commands` directory and put your Nornir runbooks there, following the simple rules. Then run them for any hosts from CLI, managing your inventory with `nornir_cli`. This is very similar to [`Ansible Roles`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html){target="_blank"}.

Let's create a collection of your Nornir runbooks using `nornir_cli`. 

For example, I have [Nornir runbook called `"cmd_dhcp_snooping.py"`](https://timeforplanb123.github.io/nornir_cli/examples/#custom-nornir-runbooks), and I want to add it to a `dhcp` group in `nornir_cli`. 
Then, my directory tree:

```text
$ tree ~/virtenvs/py3.8.4/lib/python3.8/site-packages/nornir_cli/custom_commands/
/home/user/virtenvs/py3.8.4/lib/python3.8/site-packages/nornir_cli/custom_commands/
├── dhcp
│   ├── cmd_dhcp_snooping.py
│   └── templates
│       ├── dhcp_snooping.j2
│       └── disp_int.template
└── __init__.py

2 directories, 4 files
```

And my `nornir_cli` structure:

=== "nornir_cli:"
    ```text
    $ nornir_cli
    Usage: nornir_cli [OPTIONS] COMMAND [ARGS]...

      Nornir CLI

      Orchestrate your Inventory and start Tasks and Runbooks

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      dhcp
      nornir-f5        nornir_f5 plugin
      nornir-http      nornir_http plugin
      nornir-jinja2    nornir_jinja2 plugin
      nornir-napalm    nornir_napalm plugin
      nornir-netconf   nornir_netconf plugin
      nornir-netmiko   nornir_netmiko plugin
      nornir-paramiko  nornir_paramiko plugin
      nornir-pyez      nornir_pyez plugin
      nornir-pyxl      nornir_pyxl plugin
      nornir-scrapli   nornir_scrapli plugin
    ```
=== "nornir_cli dhcp:"
    ```text
    $ nornir_cli dhcp
    Usage: nornir_cli dhcp [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...


    Options:
      --help  Show this message and exit.

    Commands:
      change_credentials  Change username and password
      dhcp_snooping       Configure dhcp snooping
      filter              Do simple or advanced filtering
      init                Initialize a Nornir
      print_result        print_result from nornir_utils
      show_inventory      Show current inventory
      write_file          Write_file, but not from nornir_utils
      write_result        Write `Result` object to file
      write_results       Write `Result` object to files
    ```

Ok, let's run the `dhcp_snooping` command on all access switches from our NetBox Inventory:

=== "get access switches:"
    ```text
    $ nornir_cli dhcp init filter --hosts -s -a 'data__device_type__model__contains=S2320-28TP-EI-DC & name__contains=access'
    [
        "access_1"
    ]
    ```
=== "run dhcp_snooping:"
    ```text
    $ nornir_cli dhcp dhcp_snooping
    access_1            : ok=1               changed=1               failed=0

    OK      : 1
    CHANGED : 1
    FAILED  : 0
    ```

More detailed - [**How to add your custom Nornir runbook in `nornir_cli`**](https://timeforplanb123.github.io/nornir_cli/useful/#how-to-add-custom-nornir-runbook)
