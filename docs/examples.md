## Tasks and runbooks

#### Single Task

=== "one:"
    ```text
    # as one comand with config.yaml

    $ nornir_cli nornir-netmiko init -u username -p password \
    filter --hosts -a 'name__contains=dev_1 device_role__name__contains=leaf' \
    netmiko_send_command --command_string "display clock"
    [
        "dev_1"
    ]
    netmiko_send_command************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    2021-03-21 23:15:23+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00
    ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_1            : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```
=== "two:"
    ```text
    # as one comand without config.yaml

    $ nornir_cli nornir-netmiko init -u username -p password -c "" -f \
    'inventory={"plugin":"NetBoxInventory2", "options": {"nb_url": "your_netbox_domain", \
    "nb_token": "your_netbox_token", "ssl_verify": false}} \
    runner={"plugin": "threaded", "options": {"num_workers": 50}} \
    logging={"enabled":true, "level": "DEBUG", "to_console": true}' \
    filter --hosts -a 'name__contains=dev_1 \
    device_role__name__contains=leaf' netmiko_send_command --command_string "display clock"

    netmiko_send_command************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    2021-03-21 23:20:53+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00
    ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_1            : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```
=== "three:"
    ```text
    # as many commands with config.yaml

    $ nornir_cli nornir-netmiko init -u username -p password

    $ nornir_cli nornir-netmiko filter --hosts -a -s 'name__contains=dev_1 device_role__name__contains=leaf'
    [
        "dev_1"
    ]

    $ nornir_cli nornir-netmiko netmiko_send_command --command_string "display clock"

    netmiko_send_command************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    2021-03-21 23:30:13+03:00
    Sunday
    Time Zone(Moscow) : UTC+03:00
    ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_1            : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```
=== "four:"
    ```text
    # of course, the same thing can be done without a configuration file
    ```

#### Task chains

```text
# any chain of commands in a group/plugin is possible

$ nornir_cli nornir-scrapli init -u username -p password \
-co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' \
filter --hosts -s 'name=dev_1' send_command --command "display clock" \
send_interactive --interact_events '[["save", "Are you sure to continue?[Y/N]", \
false], ["Y", "Save the configuration successfully.", true]]'
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

#### Custom Nornir runbooks

[How to add a previously written Nornir runbook in `nornir_cli`](http://timeforplanb123.github.io/nornir_cli/useful/#how-to-add-custom-nornir-runbook)

[How to run custom
runbook](https://timeforplanb123.github.io/nornir_cli/workflow/#runbook-collections)

And here is an example of this runbook:
=== "Nornir runbook example:"
    ```python
    # nornir_cli/custom_commands/dhcp/cmd_dhcp_snooping.py

    import os
    from nornir_netmiko import netmiko_send_command, netmiko_send_config
    from nornir.core.plugins.connections import ConnectionPluginRegister
    from nornir_jinja2.plugins.tasks import template_file
    from nornir_cli.common_commands import custom, print_stat 


    @custom
    def cli(ctx):
        """
        Configure dhcp snooping
        """
        def _get_trusted_untrusted(task):
            ConnectionPluginRegister.auto_register()
            # Get parameters in format:
            #    [ { 'description': 'NNI',
            #        'mac_address': 'xxxx-yyyy-zzzz',
            #        'mtu': '',
            #        'name': 'Ethernet0/0/1'},]
            intfs = task.run(
                task=netmiko_send_command,
                name="interfaces list",
                command_string="disp int",
                use_textfsm=True,
                textfsm_template=os.path.join(
                    os.getcwd(), "nornir_cli/custom_commands/templates/disp_int.template"
                ),
            )
            # Get trusted interfaces
            task.host["trusted"] = [
                i["name"] for i in intfs.result if "NNI" in i["description"]
            ]
            # Get untrusted interfaces
            task.host["untrusted"] = [
                i["name"]
                for i in intfs.result
                if "NNI" not in i["description"] and not i["mtu"]
            ]
            # Render j2 template
            template = task.run(
                task=template_file,
                path="nornir_cli/custom_commands/templates",
                template="dhcp_snooping.j2",
            )
            # Configure commands from j2 template
            task.host["template"] = template.result
            task.run(
                task=netmiko_send_config,
                name="Configure dhcp snooping",
                config_commands=template.result,
                cmd_verify=False,
                exit_config_mode=False,
            )

        result = ctx.nornir.run(task=_get_trusted_untrusted, on_failed=True)
        # add result to ctx.result for print_result, write_result, write_results
        # `netmiko_send_config` doesn't return data, so `result` will be empty
        # ctx.result = result

        # Show statistic
        print_stat(ctx.nornir, result)
    ```
=== "jinja2 template:"
    ```jinja
    # nornir_cli/custom_commands/dhcp/templates/dhcp_snooping.j2

    dhcp enable
    dhcp snooping enable
    #
    {% for intf in host.untrusted %}
    interface {{ intf }}
     dhcp snooping enable no-user-binding
     Y
     dhcp snooping check dhcp-chaddr enable
    {% endfor %}
    #
    {% for intf in host.trusted %}
    interface {{ intf }}
     dhcp snooping enable no-user-binding
     Y
     dhcp snooping trusted
    {% endfor %}
    #
    q
    q
    save
    Y
    ```
=== "textfsm template:"
    ```text
    # nornir_cli/custom_commands/dhcp/templates/disp_int.template

    Value NAME (\S+)
    Value DESCRIPTION (.*)
    Value MAC_ADDRESS (\w+-\w+-\w+)
    Value MTU (\d+)

    Start
      ^\S+ current state.* -> Continue.Record
      ^${NAME} current state.*
      ^Description:${DESCRIPTION}
      ^.* Maximum Transmit Unit is ${MTU}
      ^.* Hardware address is ${MAC_ADDRESS}
    ```
#### Textfsm

```text
$ nornir_cli nornir-netmiko netmiko_send_command --command_string "disp int" --use_textfsm True --textfsm_template nornir_cli/custom_commands/templates/disp_int.template 

netmiko_send_command************************************************************
* dev_1 ** changed : False *****************************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
[ { 'description': 'NNI',
    'mac_address': 'f898-ef49-b5d0',
    'mtu': '',
    'name': 'Ethernet0/0/1'},
  { 'description': '',
    'mac_address': 'f898-ef49-b5d0',
    'mtu': '',
    'name': 'Ethernet0/0/2'},

    ...

]
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dev_1            : ok=1               changed=0               failed=0

OK      : 1
CHANGED : 0
FAILED  : 0
```

#### routeros 

=== "config.yaml:"
    ```yaml
    config.yaml:
    # Simple Nornir configuration file
    inventory:
        plugin: SimpleInventory
        options:
            host_file: "inventory/hosts.yaml"
    ```
=== "inventory/hosts,yaml:"
    ```yaml
    # Single host inventory
    dev_1:
        hostname: 10.1.2.3
        username: username
        password: password
        port: 8728
        connection_options:
          routerosapi:
            extras:
              use_ssl: False
    ```
=== "routeros_command:"
    ```text
    $ nornir_cli nornir-routeros init -c "/home/user/config.yaml" routeros_command --path / --command  ping --command_args '{"address": "1.1.1.1", "count": "4"}'

    routeros_command****************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv routeros_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    [ { 'avg-rtt': b'22ms',
        'host': b'1.1.1.1',
        'max-rtt': b'22ms',
        'min-rtt': b'22ms',
        'packet-loss': b'0',
        'received': b'1',
        'sent': b'1',
        'seq': b'0',
        'size': b'56',
        'time': b'22ms',
        'ttl': b'56'},
        ...
    ^^^^ END routeros_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_1                                             : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```

#### nornir-paramiko

`nornir-paramiko` does not work correctly with network devices, because it uses `exec_command`([see here](https://stackoverflow.com/questions/32697981/paramiko-issues-channel-closed-when-executing-a-command){target="_blank"}) instead of `send` and `recv`. It works correctly with `linux/unix`:

=== "config.yaml:"
    ```yaml
    # Simple Nornir configuration file
    inventory:
        plugin: SimpleInventory
        options:
            host_file: "inventory/hosts.yaml"
    ```
=== "inventory/hosts.yaml:"
    ```yaml
    # Single host inventory
    host_1:
        hostname: 10.3.2.1
        username: username
        password: password
        connection_options:
          paramiko:
            extras:
              allow_agent: False
              look_for_keys: False
    ```
=== "paramiko_command:"
    ```text
    $ nornir_cli nornir-paramiko init paramiko_command --command "pwd"
    paramiko_command****************************************************************
    * host_1 ** changed : False ****************************************************
    vvvv paramiko_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    /home/user

    ^^^^ END paramiko_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    host_1                                     : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```
#### nornir-pyxl

As instance, `Untitled.xlsx` file has single sheet - `Sheet1`

=== "config.yaml:"
    ```yaml
    # Simple Nornir configuration file
    inventory:
        plugin: SimpleInventory
        options:
            host_file: "inventory/hosts.yaml"
    ```
=== "inventory/hosts.yaml:"
    ```yaml
    # Single host inventory
    dev_1:
        hostname: 10.1.2.3
        username: username
        password: password
    ```
=== "Untitled.xlsx:"
    ```text
    SITE_ID	CLLI	SYSTEM NAME	NTP SERVER 1IP	NTP SERVER 2IP	NTP SERVER 3IP	NTP SERVER 4IP
    Q345501	PHNZAZ	PHNZAZ-63569	192.168.1.100	192.168.1.102/32	192.168.100.3	time.ntp.com
    ```
=== "pyxl_ez_data:"
    ```text
    nornir_cli nornir-pyxl init pyxl_ez_data --workbook Untitled.xlsx --sheetname Sheet1
    pyxl_ez_data********************************************************************
    * dev_1 ** changed : False *****************************************************
    vvvv pyxl_ez_data ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    [ { 'clli': 'PHNZAZ',
        'ntp_server_1ip': '192.168.1.100',
        'ntp_server_2ip': '192.168.1.102/32',
        'ntp_server_3ip': '192.168.100.3',
        'ntp_server_4ip': 'time.ntp.com',
        'site_id': 'Q345501',
        'system_name': 'PHNZAZ-63569'}]
    ^^^^ END pyxl_ez_data ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    dev_1                                     : ok=1               changed=0               failed=0

    OK      : 1
    CHANGED : 0
    FAILED  : 0
    ```

`nornir-pyxl` includes [`pyxl_map_data`](https://github.com/h4ndzdatm0ld/nornir_pyxl#example---map-data-with-nested-dict-magic-key){target="_blank"} command, but it does not work int `nornir_cli` and was added to command exceptions

## --help

The help option can be used anywhere, for example:

```text
$ nornir_cli nornir-netmiko init -u username -p password filter \
--hosts -a -s 'name__contains=dev_1 device_role__name__contains=leaf' \
netmiko_save_config --help
Usage: nornir_cli nornir-netmiko netmiko_save_config [OPTIONS]

  Execute Netmiko save_config method

      Arguments: cmd(str, optional): Command used to save the configuration.
      confirm(bool, optional): Does device prompt for confirmation before
      executing save operation confirm_response(str, optional): Response send
      to device when it prompts for confirmation

      Returns: nornir Result attributes(optional), statistic, progress
      bar(optional)

Options:
  --pg_bar                        [default: False]
  --print_result / --no_print_result
                                  print_result from nornir_utils  [default:
                                  print_result]
  --print_stat / --no_print_stat  Print Result statistic for Nornir object
                                  [default: print_stat]
  --cmd TEXT                      [default: ]
  --confirm BOOLEAN               [default: False]
  --confirm_response TEXT         [default: ]
  --help                          Show this message and exit.


$ nornir_cli nornir-netmiko init --help -u username -p password \
filter --hosts -a -s 'name__contains=dev_1 device_role__name__contains=leaf' \
netmiko_save_config
Usage: nornir_cli nornir-netmiko init [OPTIONS]

  Initialize nornir with a configuration file, with code or with a combination
  of both.

Options:
  -c, --config_file PATH          Path to configuration file  [default:
                                  config.yaml]
  -f, --from_dict TEXT            InitNornir dictionary arguments (json
                                  string)
  -co, --connection_options TEXT  Specify any connection parameters (json
                                  string)
  -d, --dry_run BOOLEAN           Whether to simulate changes or not
                                  [default: False]
  -u, --username TEXT             Default username
  -p, --password TEXT             Default password
  -cou, --count INTEGER           Number of elements you want to show
  -g, --groups                    Show groups list
  -h, --hosts                     Show hosts list
  -i, --inventory [hosts|groups|defaults|all]
                                  Show hosts, groups or defaults inventory
  --help                          Show this message and exit.


$ nornir_cli nornir-netmiko init -u username -p password filter --help \
--hosts -a -s 'name__contains=dev_1 device_role__name__contains=leaf' \
netmiko_save_config
Usage: nornir_cli nornir-netmiko filter [OPTIONS] [F]

  Do simple or advanced filtering that will enable us to operate on groups of
  hosts based on their properties.

Options:
  -a, --advanced_filter           Use an advanced filtering (string)
  -cou, --count INTEGER           Number of elements you want to show
  -g, --groups                    Show groups list
  -h, --hosts                     Show hosts list
  -i, --inventory [hosts|groups|defaults|all]
                                  Show hosts, groups or defaults inventory
  -s, --save                      Save filtered Nornir object to pickle file
                                  for later use
  --help                          Show this message and exit.
```

## Logging  

By default, Nornir logs to a `nornir.log` file. 
For logging to console configure `logging` parameter in `config.yaml` or do `init` from dictionary, as instance:
```text
$ nornir_cli nornir-netmiko init -c "" -f 'inventory={"plugin":"NetBoxInventory2", \
"options": {"nb_url": "http://your_netbox_domain", "nb_token": "your_netbox_token", \
"ssl_verify": false}} runner={"plugin": "threaded", "options": {"num_workers": 50}} \
logging={"enabled":true, "level": "DEBUG", "to_console": true}'
```
