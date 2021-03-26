import os
import click
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir_jinja2.plugins.tasks import template_file
from nornir_cli.common_commands import custom
from nornir_cli.plugin_commands.cmd_common import _get_color


@click.command("dhcp_snooping")
@custom
def cli(ctx):
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
    ch_sum = 0
    for host in ctx.inventory.hosts:
        f, ch = (task[host].failed, task[host].changed)
        ch_sum += int(ch)
        click.secho(
            f"{host:<50}: ok={not f:<15} changed={ch:<15} failed={f:<15}",
            fg=_get_color(f, ch),
            bold=True,
        )
    print()
    f_sum = len(ctx.data.failed_hosts)
    ok_sum = len(ctx.inventory.hosts) - f_sum
    for state, summary, color in zip(
        ("OK", "CHANGED", "FAILED"), (ok_sum, ch_sum, f_sum), ("green", "yellow", "red")
    ):
        click.secho(
            f"{state:<8}: {summary}",
            fg=color,
            bold=True,
        )
    print()
