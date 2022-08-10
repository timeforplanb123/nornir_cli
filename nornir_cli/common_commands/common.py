import functools
import json
import os
import pickle
import platform
import re
from dataclasses import dataclass
from itertools import dropwhile, takewhile

import click

from nornir.core import Nornir
from nornir.core.inventory import ConnectionOptions
from nornir.core.task import Result


# custom decorator to get the current Nornir and Result objects and put them to ctx
# parameter. After decorating, ctx.nornir = Nornir object and ctx.result = Result
# object. These objects can be modified.
# ctx.nornir object can contain Nornir object only
def custom(f):
    @click.command(help=f.__doc__)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        @dataclass
        class CustomContext:
            nornir: Nornir
            result: Result

            def __getattr__(self, name):
                try:
                    return ctx.obj[name]
                except KeyError:
                    raise click.ClickException(f"The {name} attribute doesn't exist")

            def __setattr__(self, name, value):
                if name == "nornir":
                    if not isinstance(value, Nornir):
                        raise click.ClickException(
                            f"{name} attribute can be an object of the <class 'nornir.core.Nornir'> only, not a {type(value)}"
                        )
                ctx.obj[name] = self.__dict__[name] = value

        d = {
            "nornir": _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False),
            "result": "",
        }

        l = []

        for key, value in d.items():
            try:
                l.append(ctx.obj[key])
            except KeyError:
                l.append(value)

        ct = CustomContext(*l)

        return f(ct, *args, **kwargs)

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
def _json_loads(ls, parameter=None, typ=None, parameter_types=None):
    l = []
    for i in ls:
        try:
            i = json.loads(i)
            if parameter and typ and parameter_types:
                if not isinstance(i, typ):
                    raise click.BadParameter(
                        f"{parameter} should only be a {parameter_types}"
                    )
            l.append(i)
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
        r"|^\s*task(?P<task>.*)"
        r"|(?P<returns>.*Returns.*|.*Examples.*)"
        r"|(?P<colon>^\S+:.*)"
        r"|(?P<dash>.* – .*)"
    )
    for line in s.split("\n"):
        match = re.search(regex, line.lstrip())
        if match:
            if match.lastgroup == "returns":
                yield f"\n\n    Returns: nornir Result attributes(optional), statistic, progress bar(optional)"
                break
            elif match.lastgroup == "task":
                continue
            elif match.lastgroup == "kwargs":
                yield f"\n        other options/arguments: {match.group(1)}"
            elif match.lastgroup == "colon" or "dash":
                yield f"\n{line}"
        else:
            yield line.strip()


def _get_color(f, ch):
    if f:
        color = "red"
    elif ch:
        color = "yellow"
    else:
        color = "green"
    return color


# function showing statistic
def print_stat(ctx, result):
    ch_sum = 0
    for host in ctx.inventory.hosts:
        f, ch = (result[host].failed, result[host].changed)
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


# function draws a task progress bar
def multiple_progress_bar(task, method, pg_bar, **kwargs):
    task.run(task=method, **kwargs)
    if pg_bar:
        pg_bar.update()
