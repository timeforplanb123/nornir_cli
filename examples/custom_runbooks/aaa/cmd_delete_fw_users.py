import os
import re

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


SPECIAL_CHARACTERS = "'\"[!@#$%^&*()-+?_=,<>}{~:]/\"'"


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


def _check_user(task, user):
    check_user = task.run(
        task=netmiko_send_command,
        name="Is the user here?",
        command_string=f"display manager-user username {user}",
    )
    return Result(host=task.host, result=check_user.result)


@click.option(
    "-u",
    "--usernames",
    required=True,
    callback=_validate_users,
    help="Usernames or username to delete: 'user1 user2 user3' or user1",
)
@custom
def cli(ctx, usernames):
    """
    Example of deletion users on Huawei Firewalls
    """

    def delete_fw_users(task):
        ConnectionPluginRegister.auto_register()

        deleted_users = []
        undeleted_users = []
        for user in usernames:
            check_user = task.run(
                task=_check_user,
                name="Is the user here?",
                user=user,
            )
            if "Active" in check_user[0].result:
                task.host["user"] = user
                template = task.run(
                    task=template_file,
                    name="Create template",
                    path=os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "templates",
                    ),
                    template="delete_fw_users.j2",
                )
                task.run(
                    task=netmiko_send_config,
                    name=f"Delete user {user}",
                    config_commands=template.result,
                    cmd_verify=False,
                    exit_config_mode=False,
                )
            check_user = task.run(
                task=_check_user,
                name="Is the user here?",
                user=user,
            )
            match = re.search(
                r".*" r"Info: User \S+ does not exist.", check_user[1].result
            )
            if match:
                deleted_users.append(user)
            else:
                undeleted_users.append(user)

        if deleted_users:
            click.secho(
                f"{task.host.name:<25}: {' '.join(deleted_users)}"
                " have not been created or deleted",
                fg="green",
                bold=True,
            )
        elif undeleted_users:
            click.secho(
                f"{task.host.name:<25}: {' '.join(undeleted_users)}"
                " have not been deleted",
                fg="red",
                bold=True,
            )

    ctx.nornir.run(task=delete_fw_users, on_failed=True)
