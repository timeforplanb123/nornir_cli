from itertools import dropwhile, takewhile

import click

from nornir.core.filter import F

from nornir_cli.common_commands import (
    SHOW_INVENTORY_OPTIONS,
    _get_lists,
    _get_dict_from_json_string,
    _json_loads,
    _pickle_to_hidden_file,
    common_options,
)
from nornir_cli.common_commands.cmd_show_inventory import cli as show_inventory


ERROR_MESSAGE = (
    "Filter optiions. There should be something like...\n\n"
    "Simple filtering:\n"
    "   nornir_cli nornir-netmiko <init> filter site=cmh role=spine\n\n"
    "Or:\n"
    '   nornir_cli nornir-netmiko <init> filter \'{"name":"spine_1"}\'\n\n'
    "Simple filtering with json:\n"
    "   nornir_cli nornir-netmiko <init> filter --hosts "
    '\'primary_ip={"address": "10.1.10.10/32", "family": 4, "id": 4482, '
    '"url": "http://netbox-domain/api/ipam/ip-addresses/4482/"} name=spine_1\'\n\n'
    "The same:\n"
    "   nornir_cli nornir-netmiko <init> filter --hosts "
    '\'{"primary_ip":{"address": "10.1.10.10/32", "family": 4, "id": 4482, '
    '"url": "http://netbox-domain/api/ipam/ip-addresses/4482/"}, "name":"spine_1"}\'\n\n'
    "Advanced filtering:\n"
    "   nornir_cli nornir-netmiko <init> filter -a "
    "'name__contains=cmh device_role__name__contains=access'\n\n"
    "The same:\n"
    "   nornir_cli nornir-netmiko <init> filter -a "
    "'name__contains=cmh & device_role__name__contains=access'\n\n"
    "Or:\n"
    "   nornir_cli nornir-netmiko <init> filter -a "
    "'name__contains=cmh | name__contains=access'\n\n"
    "where <init> is optional command"
)


# add quotes for filter values
def _get_quotes(t):
    return ", ".join(["{}='{}'".format(*_) for _ in [__.split("=") for __ in t]])


# get Nornir object after advanced filter
def _get_obj_after_adv_filter(nr, t):
    body = ""
    t = t.split()
    while True:
        try:
            begin = takewhile(lambda x: len(x) > 2, t)
            body += f"F({_get_quotes(begin)}) "
            t = dropwhile(lambda x: len(x) > 2, t)
            body += f"{next(t)} "
            t = tuple(t)
        except StopIteration:
            break
    exec(f"o = nr.filter({body})")
    return locals()["o"]


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    short_help="Do simple or advanced filtering",
)
@click.option(
    "-a",
    "--advanced_filter",
    is_flag=True,
    help="Use an advanced filtering (string)",
)
@common_options(SHOW_INVENTORY_OPTIONS)
@click.option(
    "-s",
    "--save",
    is_flag=True,
    help="Save filtered Nornir object to pickle file for later use",
)
@click.argument("f", required=False)
@click.pass_context
# Leftover argumetns via ctx.args doesn't work. Oh, really? :'( https://github.com/pallets/click/issues/473
def cli(ctx, advanced_filter, f, save, **kwargs):
    """
    Do simple or advanced filtering
    that will enable us to operate on groups of hosts
    based on their properties.
    """
    try:
        ctx.obj["nornir"] = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)
        if advanced_filter:
            ctx.obj["nornir"] = _get_obj_after_adv_filter(ctx.obj["nornir"], f)
        else:
            d = _get_dict_from_json_string(f)
            ctx.obj["nornir"] = ctx.obj["nornir"].filter(**d)
        if save:
            _pickle_to_hidden_file("temp.pkl", obj=ctx.obj["nornir"])

        # run show_inventory command
        if any(kwargs.values()):
            ctx.invoke(show_inventory, **kwargs)
    except (ValueError, TypeError, IndexError):
        raise ctx.fail(
            click.BadParameter(
                f"{ERROR_MESSAGE}",
            ).format_message(),
        )
