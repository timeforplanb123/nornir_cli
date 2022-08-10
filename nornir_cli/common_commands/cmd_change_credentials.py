import click

from nornir_cli.common_commands import (
    _json_loads,
    _pickle_to_hidden_file,
)


@click.command(short_help="Change username and password")
@click.option(
    "-u",
    "--username",
    envvar="NORNIR_CLI_USERNAME",
    help="Hosts, groups or defaults username",
)
@click.option(
    "-p",
    "--password",
    envvar="NORNIR_CLI_PASSWORD",
    help="Hosts, groups or defaults password",
)
@click.option(
    "-h",
    "--hosts",
    help="List of hosts (json string) or single host (str)",
)
@click.option(
    "-g",
    "--groups",
    help="List of groups (json string) or single group (str)",
)
@click.option("-d", "--defaults", is_flag=True, help="Defaults credentials")
@click.option(
    "-s",
    "--save",
    is_flag=True,
    help="Save Nornir object with new credentials to pickle file for later use",
)
@click.pass_context
def cli(ctx, username, password, hosts, groups, defaults, save):
    """
    Change username and password for current Nornir object.\n\n
    If no options are specified, the username and password will be changed for defaults
    only, as instance:\n
        nornir_cli nornir-scrapli change_credentials -u user -p password show_inventory -i defaults\n\n
    If only hosts or groups are specified (use string for single host and list of
    strings for many hosts), then the username and password will be
    changed only for them, as instance:\n
        nornir_cli nornir-scrapli change_credentials -u user -p password -h '["spine_1"]'\n\n
    To change the username and password for all hosts or groups, use "all" as option
    value, as instance:\n
        nornir_cli nornir-scrapli change_credentials -u user -p password -h "all"
    """

    def _change_username_or_password(item, username, password):
        if username:
            item.username = username
        if password:
            item.password = password

    try:
        nr = ctx.obj["nornir"]
    except KeyError:
        nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)

    for s, k, v in zip(
        ("--hosts", "--groups"),
        (hosts, groups),
        (nr.inventory.hosts, nr.inventory.groups),
    ):
        if k == "all":
            for item in v.values():
                _change_username_or_password(item, username, password)
        elif k:
            k = _json_loads(
                [k], parameter=f"{s}", typ=(str, list), parameter_types="str or list"
            )[0]
            if isinstance(k, str):
                k = [k]
            for item in k:
                try:
                    _change_username_or_password(v[item], username, password)
                except KeyError:
                    raise click.BadParameter(f"{item} does not exists")

    if defaults or not (hosts and groups and defaults):
        defaults_inv = nr.inventory.defaults

        _change_username_or_password(defaults_inv, username, password)

    ctx.obj["nornir"] = nr

    if save:
        _pickle_to_hidden_file("temp.pkl", obj=nr)
