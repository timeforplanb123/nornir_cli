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
Why is `nornir-netmiko` here? `nornir_cli` runs Tasks based on Nornir plugins or your custom Nornir runbooks, so the first step is to select an available plugin or custom.

For version `0.3.0`, the following Nornir plugins are available:
```text
$ nornir_cli --help
Usage: nornir_cli [OPTIONS] COMMAND [ARGS]...

  Nornir CLI

  Orchestrate your Inventory and start Tasks and Runbooks

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  nornir-f5       nornir_f5 plugin
  nornir-jinja2   nornir_jinja2 plugin
  nornir-napalm   nornir_napalm plugin
  nornir-netmiko  nornir_netmiko plugin
  nornir-pyez     nornir_pyez plugin
  nornir-scrapli  nornir_scrapli plugin
```
#### Without a configuration file

You can initialize nornir programmatically without a configuration file.

`-f` or `--from_dict` option waits json string:
```text
$ nornir_cli nornir-netmiko init -c "" -f 'inventory={"plugin":"NetBoxInventory2", \
"options": {"nb_url": "http://your_netbox_domain", "nb_token": "your_netbox_token", \
"ssl_verify": false}} runner={"plugin": "threaded", "options": {"num_workers": 50}} \
logging={"enabled":true, "level": "DEBUG", "to_console": true}'
```

Or with a combination of both methods:

#### Both ways
```text
$ nornir_cli nornir-netmiko init -f 'runner={"plugin": "threaded", "options": {"num_workers": 50}}'
```

## Inventory
`nornir_cli` follows `Nornir` [filtering interface](https://nornir.readthedocs.io/en/latest/tutorial/inventory.html#Filtering-the-inventory){target="_blank"}.

`init` returns [nornir.core.Nornir](https://github.com/nornir-automation/nornir/blob/e4f6b8c6258ae2dcfb286098b30652c7a31ecf30/nornir/core/__init__.py#L18){target="_blank"} object, which saved to `temp.pkl` file for future reference. Now, let's filter inventory:

#### Filtering

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
=== "simple filtering:"
    ```text
    # At first, let's do the init command with Nornir NetBox plugin
    # -u / --username and -p / --password  will assign a username and password in Defaults
    # -co / --connection_options will assign options for Scrapli framework
    # huawei is here just as an example
    $ nornir_cli nornir-scrapli init -u username -p password -co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}'
    
    # let's filter something
    $ nornir_cli nornir-scrapli filter --hosts name=dev_1
    Are you sure you want to output all on stdout? [y/N]: y
    [
        "dev_1"
    ]
    ```
=== "simple filtering with json string:"
    ```text
    # huawei is here just as an example
    $ nornir_cli nornir-scrapli filter --count 1 --inventory=hosts --hosts 'primary_ip={"address": "10.1.0.1/32", "family": 4, "id": 13, "url": "http://your_netbox_domain/api/ipam/ip-addresses/13/"} name=dev_1'
    {
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
    [
        "dev_1"
    ]
    ```
=== "advanced filtering:"
    ```text
    # -a / --advanced option enables advanced filtering
    $ nornir_cli nornir-scrapli filter --hosts -a 'name__contains=dev_1 device_role__name__contains=spine'
    Are you sure you want to output all on stdout? [y/N]: y
    [
        "dev_1"
    ]

    # the same with &
    $ nornir_cli nornir-scrapli filter --hosts -a 'name__contains=dev_1 & device_role__name__contains=spine'
    Are you sure you want to output all on stdout? [y/N]: y
    [
        "dev_1"
    ]

    # or |
    $ nornir_cli nornir-scrapli filter --hosts -a 'name__contains=dev_1 | name__contains=dev_2'
    Are you sure you want to output all on stdout? [y/N]: y
    [
        "dev_1"
        "dev_2"
    ]

    # another example
    $ nornir_cli nornir-netmiko filter --hosts --count 3 -a 'data__device_type__model__contains=S2320-28TP-EI-DC & name__contains=dev_ | data__device_type__model__contains=S2320-28TP-EI-DC & name__contains=access'
    [
        "dev_1"
        "dev_2"
        "access_1"
    ]
    ```

**IMPORTANT:** if you want to save the Inventory state after filtering for future references, please use `--save` or `-s` option.

#### Show inventory

As you may have already noticed, it's possible to view the current inventory state with show_inventory command:
```text
$ nornir_cli nornir-scrapli show_inventory -i hosts -h -g --count 6
# hosts inventory
{
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
`-cou` or `--count` shows hosts/groups list and/or hosts/groups/defaults inventory.

- `--count -100` - last 100 items

- `--count 100` - first 100 items

- `--count 0` - all items (default value)

And you can invoke `show_inventory` command from `init` or `filter` commands with `-i / --inventory`, `-h / --hosts`, `-g / --groups` options.


## Tasks and runbooks


**I must say that each argument can be passed to the Task as a json string. It's important.**


#### Single tasks

Ok, now we have filtered inventory and let's start some Task based on Nornir Plugins:

At first, let's check all available Tasks/commands for current list of nornir plugins:

=== "norir-netmiko:"
    ```text
    $ nornir_cli nornir-netmiko --help
    Usage: nornir_cli nornir-netmiko [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                     [ARGS]...]...

      nornir_netmiko plugin

    Options:
      --help  Show this message and exit.

    Commands:
      init                   Initialize a Nornir
      filter                 Do simple or advanced filtering
      show_inventory         Show current inventory
      netmiko_commit         Execute Netmiko commit method
      netmiko_file_transfer  Execute Netmiko file_transfer method
      netmiko_save_config    Execute Netmiko save_config method
      netmiko_send_command   Execute Netmiko send_command method (or
                             send_command_timing)

      netmiko_send_config    Execute Netmiko send_config_set method (or
                             send_config_from_file)
    ```
=== "nornir-scrapli:"
    ```text
    $ nornir_cli nornir-scrapli --help
    Usage: nornir_cli nornir-scrapli [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                 [ARGS]...]...

      nornir_scrapli plugin

    Options:
      --help  Show this message and exit.

    Commands:
      init                     Initialize a Nornir
      filter                   Do simple or advanced filtering
      show_inventory           Show current inventory
      get_prompt               Get current prompt from device using scrapli
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

      send_command             Send a single command to device using scrapli
      send_commands            Send a list of commands to device using scrapli
      send_commands_from_file  Send a list of commands from a file to device using
                               scrapli

      send_config              Send a config to device using scrapli
      send_configs             Send configs to device using scrapli
      send_configs_from_file   Send configs from a file to device using scrapli
      send_interactive         Send inputs in an interactive fashion using
                               scrapli; usually used to handle prompts

    ```
=== "nornir-napalm:"
    ```text
    $ nornir_cli nornir-napalm --help
    Usage: nornir_cli nornir-napalm [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                [ARGS]...]...

      nornir_napalm plugin

    Options:
      --help  Show this message and exit.

    Commands:
      init              Initialize a Nornir
      filter            Do simple or advanced filtering
      show_inventory    Show current inventory
      napalm_cli        Run commands on remote devices using napalm
      napalm_configure  Loads configuration into a network devices using napalm
      napalm_get        Gather information from network devices using napalm
      napalm_ping       Executes ping on the device and returns a dictionary with
                        the result

      napalm_validate   Gather information with napalm and validate it
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
      init             Initialize a Nornir
      filter           Do simple or advanced filtering
      show_inventory   Show current inventory
      template_file    Renders contants of a file with jinja2. All the host data
                       is available in the template

      template_string  Renders a string with jinja2. All the host data is
                       available in the template
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
      init               Initialize a Nornir
      filter             Do simple or advanced filtering
      show_inventory     Show current inventory
      pyez_facts
      pyez_config
      pyez_get_config
      pyez_diff
      pyez_commit
      pyez_int_terse
      pyez_route_info
      pyez_rpc
      pyez_sec_ike
      pyez_sec_ipsec
      pyez_sec_nat_dest
      pyez_sec_nat_src
      pyez_sec_policy
      pyez_sec_zones
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
      init                            Initialize a Nornir
      filter                          Do simple or advanced filtering
      show_inventory                  Show current inventory
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
    ```

And start `netmiko_send_command`, for example:

```text
$ nornir_cli nornir-netmiko netmiko_send_command --command_string "display clock"
netmiko_send_command************************************************************
* dev_1 ** changed : False ********************
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
Let's check out some command:

```text
$ nornir_cli nornir-scrapli send_command --command "display clock"
send_command********************************************************************
* dev_1 ** changed : False ********************
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

#### What about netconf?

[Here is easy way to get xml tree from yang](https://timeforplanb123.github.io/nornir_cli/useful/#how-to-craft-xml-from-yang)

`dev_3`, as instance, understands netconf. Get `nornir.core.Nornir` object for `dev_3` and run some netconf command with Scrapli:
```text
$ nornir_cli nornir-scrapli init -u username -p password -co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' filter --hosts -s 'name=dev_3'
Are you sure you want to output all on stdout? [y/N]: y
[
    "dev_3"
]

$ nornir_cli nornir-scrapli netconf_get --filter_='<ifm xmlns="http://www.huawei.com/netconf/vrp/huawei-ifm"><interfaces><interface><ifName/></interface></interfaces></ifm>' --filter_type subtree

...
netconf_get*********************************************************************
* dev_3 ** changed : False ************************************************
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

#### Commands chains

And, of course, you can run any commands chains, even those scary ones:

```text
$ nornir_cli nornir-scrapli init -u username -p password \
-co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' \
filter --hosts -s 'name=dev_1' send_command --command "display clock" \
send_interactive --interact_events '[["save", "Are you sure to continue?[Y/N]", false], \
["Y", "Save the configuration successfully.", true]]'
Are you sure you want to output all on stdout? [y/N]: y
[
    "dev_1"
]

send_command********************************************************************
* dev_1 ** changed : False ********************
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
* dev_1 ** changed : True *********************
vvvv send_interactive ** changed : True vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
^^^^ END send_interactive ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dev_1            : ok=1               changed=1               failed=0

OK      : 1
CHANGED : 1
FAILED  : 0
```

**Again, i repeat that each argument can be passed to the Task as a json string. This can be seen from the example above.**

#### Runbook collections

You can create and manage a collection of your nornir runbooks using `nornir_cli`. 

Create any directory trees in the `custom_commands` directory and put your nornir runbooks there, following the simple rules. Then run them for any hosts from CLI, managing your inventory with `nornir_cli`. This is very similar to [`Ansible Roles`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html){target="_blank"}.

For example, I have [Nornir runbook called `"cmd_dhcp_snooping.py"`](https://timeforplanb123.github.io/nornir_cli/examples/#custom-nornir-runbooks), and I want to add it to a `dhcp` group in `nornir_cli`. 
Then, our directory tree:

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

And our `nornir_cli` structure:

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
      nornir-jinja2   nornir_jinja2 plugin
      nornir-napalm   nornir_napalm plugin
      nornir-netmiko  nornir_netmiko plugin
      nornir-scrapli  nornir_scrapli plugin
    ```
=== "nornir_cli dhcp:"
    ```text
    $ nornir_cli dhcp
    Usage: nornir_cli dhcp [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...


    Options:
      --help  Show this message and exit.

    Commands:
      init            Initialize a Nornir
      filter          Do simple or advanced filtering
      show_inventory  Show current inventory
      dhcp_snooping   Configure dhcp snooping
    ```

Ok, let's run our `dhcp_snooping` command on all access switches from our NetBox Inventory:

=== "get access switches:"
    ```text
    $ nornir_cli dhcp init filter --hosts -s -a 'data__device_type__model__contains=S2320-28TP-EI-DC & name__contains=access'
    Are you sure you want to output all on stdout? [y/N]: y
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
