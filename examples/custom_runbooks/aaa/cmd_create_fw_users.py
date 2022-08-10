import os

import click

from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir.core.task import Result

from nornir_cli.common_commands import custom

from nornir_jinja2.plugins.tasks import template_file

from nornir_netmiko import netmiko_send_command, netmiko_send_config


USERNAMES_ERROR_MESSAGE = (
    "-u or --usernames should be:\n"
    "'user1 user2 user3' for many users\n"
    "user1 for single user.\n"
    "And don't use special characters, please"
)

SERVICE_TYPES_ERROR_MESSAGE = (
    "-s or --service_types should be:\n"
    "'ftp web terminal ssh' for many types (api ftp ssh telnet terminal web)\n"
    "ssh for single type.\n"
    "And don't use special characters, please"
)

SPECIAL_CHARACTERS = "'\"[!@#$%^&*()-+?_=,<>}{~:]/\"'"


def validate_user_parameters(
    task, valid_user_parameters, current_user_parameters
):
    for dict_0, dict_1 in zip(valid_user_parameters, current_user_parameters):
        if dict_0 != dict_1:
            return Result(host=task.host, result="Validation error")


def _validate_users(ctx, param, value):
    # simple check on special characters
    if any(c in SPECIAL_CHARACTERS for c in value):
        raise ctx.fail(
            click.BadParameter(
                f"{USERNAMES_ERROR_MESSAGE}",
            ).format_message(),
        )
    else:
        return set(value.split())


def _validate_service_types(ctx, param, value):
    available_types = ["api", "ftp", "ssh", "telnet", "terminal", "web"]
    if not any(c in SPECIAL_CHARACTERS for c in value):
        if any(typ in available_types for typ in value.split()):
            return value
    else:
        raise ctx.fail(
            click.BadParameter(
                f"{SERVICE_TYPES_ERROR_MESSAGE}",
            ).format_message(),
        )


@click.option(
    "-u",
    "--usernames",
    required=True,
    callback=_validate_users,
    help="Usernames or username to create: 'user1 user2 user3' or user1",
)
@click.option(
    "-r",
    "--role",
    default="service-admin",
    show_default=True,
    type=click.Choice(
        [
            "audit-admin",
            "device-admin",
            "device-admin(monitor)",
            "service-admin",
            "system-admin",
        ]
    ),
    help="Role to bind",
)
@click.option(
    "-s",
    "--service_types",
    default="ftp web terminal ssh",
    show_default=True,
    callback=_validate_service_types,
    help="Service types to bind",
)
@custom
def cli(ctx, usernames, role, service_types):
    """
    Example of creation new tacacs users on Huawei Firewalls
    """

    def create_fw_users(task):
        ConnectionPluginRegister.auto_register()

        task.host["users"] = usernames
        task.host["role"] = role
        task.host["service_types"] = service_types

        valid_user_parameters = [
            {
                "username": user,
                "service_type": sorted(service_types.split()),
                "user_level": "15",
                "ftp_dir": "cfcard:",
            }
            for user in usernames
        ]

        template = task.run(
            task=template_file,
            name="Create template",
            path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "templates"
            ),
            template="create_fw_user.j2",
        )

        task.run(
            task=netmiko_send_config,
            name="Create new users",
            config_commands=template.result,
            cmd_verify=False,
            exit_config_mode=False,
        )

        current_user_parameters = []
        for user in usernames:
            current_user_parameters.append(
                task.run(
                    task=netmiko_send_command,
                    name="Get validation data",
                    command_string=f"disp manager-user username {user}",
                    use_textfsm=True,
                    textfsm_template=os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "templates/disp_manager_user.template",
                    ),
                ).result[0]
            )
        current_user_parameters = [
            {**dict_, "service_type": sorted(dict_["service_type"].split())}
            for dict_ in current_user_parameters
        ]

        task.run(
            task=validate_user_parameters,
            name="Validate user parameters",
            valid_user_parameters=valid_user_parameters,
            current_user_parameters=current_user_parameters,
        )

    result = ctx.nornir.run(task=create_fw_users, on_failed=True)

    for host in ctx.nornir.inventory.hosts:
        f, ch = (result[host].failed, result[host].changed)
        if f:
            click.secho(
                f"{host:<25}: Oh! Here is some exception:"
                f" {result[host].exception}",
                fg="red",
                bold=True,
            )
        elif ch:
            click.secho(
                f"{host:<25}: {' '.join(usernames)}"
                " have been created or changed",
                fg="yellow",
                bold=True,
            )
        elif "Validation error" in result[host][4].result:
            click.secho(
                f"{host:<25}: {' '.join(usernames)} validation error",
                fg="red",
                bold=True,
            )
