## Tasks and runbooks

#### Single Task

=== "one:"
    ```text
    # as one comand with config.yaml

    $ nornir_cli nornir-netmiko init -u username -p password \
    filter --hosts -a 'name__contains=dev_1 device_role__name__contains=leaf' \
    netmiko_send_command --command_string "display clock"
    Are you sure you want to output all on stdout? [y/N]: y
    [
        "dev_1"
    ]
    netmiko_send_command************************************************************
    * dev_1 ** changed : False ********************
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
    * dev_1 ** changed : False ********************
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

    Are you sure you want to output all on stdout? [y/N]: y
    [
        "dev_1"
    ]

    $ nornir_cli nornir-netmiko netmiko_send_command --command_string "display clock"

    netmiko_send_command************************************************************
    * dev_1 ** changed : False ********************
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

#### Tasks chains

```text
# any chain of commands in a group/plugin is possible

$ nornir_cli nornir-scrapli init -u username -p password \
-co '{"scrapli": {"platform": "huawei_vrp", "extras":{"ssh_config_file": true}}}' \
filter --hosts -s 'name=dev_1' send_command --command "display clock" \
send_interactive --interact_events '[["save", "Are you sure to continue?[Y/N]", \
false], ["Y", "Save the configuration successfully.", true]]'
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

#### Custom Nornir runbooks

[How to add a previously written Nornir runbook in `nornir_cli`](http://timeforplanb123.github.io/nornir_cli/useful/#how-to-add-custom-nornir-runbook)

[How to run custom runbook](https://timeforplanb123.github.io/nornir_cli/workflow/#custom-runbooks)

And here is an example of this runbook:
=== "Nornir runbook example:"
    ```python
    # nornir_cli/custom_commands/dhcp/md_dhcp_snooping.py

    import os
    from nornir_netmiko import netmiko_send_command, netmiko_send_config
    from nornir.core.plugins.connections import ConnectionPluginRegister
    from nornir_jinja2.plugins.tasks import template_file
    from nornir_cli.common_commands import custom, _info


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

        task = ctx.run(task=_get_trusted_untrusted, on_failed=True)
        # Show statistic
        _info(ctx, task)
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
* dev_1 ** changed : False ********************
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

## --help

The help option can be used anywhere, for example:

```text
$ nornir_cli nornir-netmiko init -u username -p password filter \
--hosts -a -s 'name__contains=dev_1 device_role__name__contains=leaf' netmiko_save_config --help

Usage: nornir_cli nornir-netmiko netmiko_save_config [OPTIONS]

  Execute Netmiko save_config method

        Arguments: cmd(str, optional): Command used to save the configuration.
        confirm(bool, optional): Does device prompt for confirmation before
        executing save operation confirm_response(str, optional): Response
        send to device when it prompts for confirmation

        Returns: nornir result(optional), statistic, progress bar(optional)

Options:
  --pg_bar                        [default: False]
  --show_result / --no_show_result
                                  [default: True]
  --cmd TEXT                      [default: ]
  --confirm BOOLEAN               [default: False]
  --confirm_response TEXT         [default: ]
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
