import json
from itertools import islice

import click

from nornir_cli.common_commands import (
    SHOW_INVENTORY_OPTIONS,
    _pickle_to_hidden_file,
    common_options,
)


def _get_inventory(nr_obj, count, **kwargs):

    d = {
        str: dict,
        bool: list,
    }

    if not any(kwargs.values()):
        kwargs = {
            "hosts": True,
        }

    for k, v in kwargs.items():
        if v:

            if v == "all":
                for inventory_key in ("hosts", "groups", "defaults"):
                    for item in _get_inventory(nr_obj, count, inventory=inventory_key):
                        if item:
                            yield item
            elif v == "defaults":
                yield {v: nr_obj.inventory.defaults.dict()}
            else:
                try:
                    o = nr_obj.inventory.dict()[k]
                except KeyError:
                    o = nr_obj.inventory.dict()[v].items()
                l = len(o)
                if isinstance(count, type(None)):
                    if l > 1:
                        msg = (
                            f"all required {v} in inventory"
                            if isinstance(v, str)
                            else f"list of all required {k}"
                        )
                        click.confirm(
                            f"Are you sure you want to output {msg} on stdout?",
                            default="Y",
                            abort=True,
                        )
                _ = [0, count or l] if count == None or count >= 0 else [l + count, l]
                inventory_part = d[type(v)](islice(o, *_))
                if isinstance(inventory_part, dict):
                    inventory_part = {v: inventory_part}
                yield inventory_part


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

    d = {
        x: y
        for x, y in zip(("inventory", "hosts", "groups"), (inventory, hosts, groups))
    }
    try:
        for item in _get_inventory(nr, count, **d):
            json_string = json.dumps(item, indent=4, ensure_ascii=False)
            print(json_string.encode("utf-8").decode())
    except ValueError:
        raise ctx.fail(
            click.BadParameter(
                f"count cannot be equal to {count}",
            ).format_message(),
        )
