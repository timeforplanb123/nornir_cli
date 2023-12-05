import os

from nornir.core.plugins.connections import ConnectionPluginRegister

from nornir_cli.common_commands import custom, print_stat

from nornir_jinja2.plugins.tasks import template_file

from nornir_netmiko import netmiko_send_command, netmiko_send_config


@custom
def cli(ctx):
    """
    dhcp snooping configuration example
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
                os.path.dirname(os.path.abspath(__file__)),
                "templates/disp_int.template",
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
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
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
