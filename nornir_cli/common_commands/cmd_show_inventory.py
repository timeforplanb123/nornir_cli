import click
from itertools import islice
from nornir_cli.common_commands import (
    _pickle_to_hidden_file,
    common_options,
)
from nornir_cli.common_commands.common import (
    SHOW_INVENTORY_OPTIONS,
)
import json


def _get_inventory(nr_obj, count, **kwargs):

    d = {  # "inventory": nr_obj.inventory.dict().setdefault(kwargs["inventory"]).items(),
        # "groups": nr_obj.inventory.groups,
        # "hosts": nr_obj.inventory.hosts,
        str: dict,
        bool: list,
    }

    if not any(kwargs.values()):
        kwargs = {
            "hosts": True,
        }

    for k, v in kwargs.items():
        if v:
            try:
                o = nr_obj.inventory.dict()[k]
            except KeyError:
                o = nr_obj.inventory.dict()[v].items()
            l = len(o)
            _ = [0, count or l] if count >= 0 else [l + count, l]
            json_string = json.dumps(
                d[type(v)](islice(o, *_)), indent=4, ensure_ascii=False
            ).encode("utf8")
            yield json_string.decode()


@click.command()
@common_options(SHOW_INVENTORY_OPTIONS)
@click.pass_context
def cli(ctx, count, hosts, groups, inventory):
    """
    Show current inventory
    """

    try:
        nr = ctx.obj["nornir"]
    except KeyError:
        nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)

    if not count or ctx.resilient_parsing:
        click.confirm("Are you sure you want to output all on stdout?", abort=True)

    d = {
        x: y
        for x, y in zip(("inventory", "hosts", "groups"), (inventory, hosts, groups))
    }
    try:
        for item in _get_inventory(nr, count, **d):
            print(item)
    except ValueError:
        raise ctx.fail(
            click.BadParameter(
                f"count cannot be equal to {count}",
            ).format_message(),
        )
