import click
import pickle
import functools
import platform
import json
import os
from itertools import takewhile, dropwhile
import re
from nornir.core.inventory import ConnectionOptions


# custom decorator to get the current Nornir object and put it to ctx parameter
def custom(f):
    @click.command(help=f.__doc__)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        try:
            ctx = ctx.obj["nornir"]
        except KeyError:
            ctx = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)
        return f(ctx, *args, **kwargs)

    return wrapper


# the decorator wraps the fucntion with general options
def common_options(options):
    def wrapper(f):
        return functools.reduce(lambda x, option: option(x), options, f)

    return wrapper


def _pickle_to_hidden_file(file_name, mode="wb", obj=None, dump=True):
    try:
        dot = "." if platform.system() not in "Windows" else ""
        hidden_file_name = dot + file_name
        path_to_hidden_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), hidden_file_name)
        )
        with open(path_to_hidden_file, mode) as hf:
            if dump:
                pickle.dump(obj, hf)
            else:
                return pickle.load(hf)
    except (pickle.UnpicklingError, FileNotFoundError, EOFError):
        raise click.ClickException("Uhm...At first, run init to get the nornir_object")


# load json or not json object
def _json_loads(ls):
    l = []
    for i in ls:
        try:
            l.append(json.loads(i))
        except (json.JSONDecodeError, TypeError):
            if i == "None":
                i = None
            l.append(i)
            continue
    return l


# validate ConnectionOptions
def _validate_connection_options(ctx, param, value):
    if value is not None:
        try:
            value = {
                connection_plugin: ConnectionOptions(**connection_params)
                for connection_plugin, connection_params in _json_loads([value])[
                    0
                ].items()
            }
            return value
        except (TypeError, AttributeError):
            ctx.fail(
                click.BadParameter(
                    f"'--connection_options' / '-co': {value}",
                ).format_message(),
            )


def _get_cmd_folder(cmd_folders):
    for cmd_folder in cmd_folders:
        yield os.path.abspath(os.path.join(os.path.dirname(__file__), cmd_folder))


# get list with filter objects
def _get_lists(s):
    body = []
    s = s.split()
    while True:
        if not s:
            break
        begin = list(takewhile(lambda x: "=" in x, s))
        s = list(dropwhile(lambda x: "=" in x, s))
        begin.extend([i for i in takewhile(lambda x: "=" not in x, s)])
        body.append("".join(begin))
        s = list(dropwhile(lambda x: "=" not in x, s))
    return body


# docstring generator for Commands
def _doc_generator(s):
    regex = (
        r".*kwargs: (?P<kwargs>.*)"
        r"|.*task: (?P<task>.*)"
        r"|(?P<returns>.*Returns.*)"
        r"|(?P<colon>^\S+:.*)"
        r"|(?P<dash>.* – .*)"
    )
    for line in s.split("\n"):
        match = re.search(regex, line.lstrip())
        if match:
            if match.lastgroup == "returns":
                yield f"    Returns: nornir result(optional), statistic, progress bar(optional)"
                break
            elif match.lastgroup == "task":
                continue
            elif match.lastgroup == "kwargs":
                yield f"\n        other options/arguments: {match.group(1)}"
            elif match.lastgroup == "colon" or "dash":
                yield f"\n{line}"
        else:
            yield line.strip()


# common options
CONNECTION_OPTIONS = [
    click.option(
        "-co",
        "--connection_options",
        callback=_validate_connection_options,
        help="Specify any connection parameters (json string)",
    ),
]

# common options
SHOW_INVENTORY_OPTIONS = [
    click.option(
        "-i",
        "--inventory",
        type=click.Choice(["hosts", "groups", "defaults"]),
        help="Show hosts, groups or defaults inventory",
    ),
    click.option("-h", "--hosts", is_flag=True, help="Show hosts list"),
    click.option("-g", "--groups", is_flag=True, help="Show groups list"),
    click.option(
        "-cou",
        "--count",
        type=click.INT,
        default=0,
        help="Number of elements you want to show",
    ),
]


def _get_color(f, ch):
    if f:
        color = "red"
    elif ch:
        color = "yellow"
    else:
        color = "green"
    return color


# function showing statistic
def _info(ctx, task):
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
