import click
from nornir import InitNornir
from nornir.core.plugins.inventory import TransformFunctionRegister
from nornir_cli.common_commands import (
    cmd_show_inventory,
    common_options,
    _pickle_to_hidden_file,
    _json_loads,
    _get_lists,
)
from nornir_cli.common_commands.common import (
    CONNECTION_OPTIONS,
    SHOW_INVENTORY_OPTIONS,
)
from nornir_cli.transform.function import adapt_host_data


ERROR_MESSAGE = (
    "Init options (these may be options in configuration file or init options).\n"
    "If the configuration file is correct or missing, check the command format"
    "(use json syntax with '--from_dict' / '-f' option).\n"
    "There should be something like...\n\n"
    "With default configuration file:\n"
    "   nornir_cli custom init\n\n"
    "Specifying the path to config file:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yaml\n\n"
    "Without a configuration file. And use json syntax here"
    "(programmatically initializing):\n"
    '   nornir_cli nornir-scrapli init -c "" -f '
    '\'inventory={"plugin":"SimpleInventory",options": {"host_file": '
    '"/home/user/inventory/hosts.yaml", "group_file": '
    '"/home/user/inventory/groups.yaml", '
    '"defaults_file": "/home/user/inventory/defaults.yaml"}}\'\n\n'
    "With combination of both methods:\n"
    '   nornir_cli nornir-napalm init -f \'logging={"enabled": true, "level":'
    '"DEBUG",'
    '"to_console": false}'
)


@click.command("init", short_help="Initialize a Nornir")
@click.option(
    "--config_file",
    "-c",
    default="config.yaml",
    show_default=True,
    type=click.Path(exists=False),
    help="Path to configuration file",
)
@click.option(
    "-f",
    "--from_dict",
    help="InitNornir dictionary arguments (json string)",
)
@common_options(CONNECTION_OPTIONS)
@click.option(
    "--dry_run",
    "-d",
    default=False,
    show_default=True,
    type=bool,
    help="Whether to simulate changes or not",
)
@click.option(
    "-u",
    "--username",
    envvar="NORNIR_CLI_USERNAME",
    help="Default username",
)
@click.option(
    "-p",
    "--password",
    envvar="NORNIR_CLI_PASSWORD",
    help="Default password",
)
@common_options(SHOW_INVENTORY_OPTIONS)
@click.pass_context
def cli(
    ctx,
    config_file,
    dry_run,
    username,
    password,
    from_dict,
    connection_options,
    **kwargs,
):
    """
    Initialize nornir with a configuration file, with code
    or with a combination of both.
    """

    ctx.ensure_object(dict)

    try:

        TransformFunctionRegister.register("adapt_host_data", adapt_host_data)

        if from_dict:
            d = dict(
                [
                    _json_loads(i)
                    for i in (value.split("=") for value in _get_lists(from_dict))
                ]
            )
            cf = (
                None
                if not config_file or config_file == "None" or "null"
                else config_file
            )
            ctx.obj["nornir"] = InitNornir(config_file=cf, dry_run=dry_run, **d)
        else:
            ctx.obj["nornir"] = InitNornir(config_file=config_file, dry_run=dry_run)

        defaults = ctx.obj["nornir"].inventory.defaults

        if username:
            defaults.username = username
        if password:
            defaults.password = password

        if connection_options:
            for param in ctx.obj["nornir"].inventory.hosts.values():
                param.connection_options = connection_options

        _pickle_to_hidden_file("temp.pkl", obj=ctx.obj["nornir"])

        # run show_inventory command
        if any(kwargs.values()):
            ctx.invoke(cmd_show_inventory.cli, **kwargs)

    except (ValueError, IndexError, TypeError, KeyError):
        raise ctx.fail(
            click.BadParameter(
                f"{ERROR_MESSAGE}",
            ).format_message(),
        )
    except (AttributeError):
        ctx.fail(
            f"File '{config_file}' is empty",
        )
    except (FileNotFoundError):
        raise ctx.fail(
            click.BadParameter(
                f"Path '{config_file}' does not exist",
                param_hint="'--config_file' / '-c'",
            ).format_message(),
        )
    except Exception as err:
        raise click.ClickException(err)
