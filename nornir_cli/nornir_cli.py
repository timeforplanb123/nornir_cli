import inspect
import os
import re
from itertools import chain

import click

from httpx import Timeout

from nornir_cli import __version__
from nornir_cli.common_commands import (
    PLUGIN_OPTIONS,
    _doc_generator,
    common_options,
)


COMMAND_EXCEPTIONS = {"nornir_pyxl.plugins": ["pyxl_data_map"]}

# methods with a large and complex __doc__ :(
METHOD_EXCEPTIONS = ("send_interactive",)

# when click short_help is more than one string and is the __doc__ part before "Arguments:" or "Args:"
SHORT_HELP_EXCEPTIONS = ("http_method",)

CMD_FOLDERS = ["common_commands"]

PACKAGE_NAME = "nornir_cli"

SETTINGS = {
    "nornir_scrapli": {
        "NetconfDriver": "scrapli_netconf.driver",
        "NetworkDriver": "scrapli.driver",
        "GenericDriver": "scrapli.driver",
    },
    "nornir_netmiko": {
        "BaseConnection": "netmiko",
        "file_transfer": "netmiko",
    },
    "nornir_http": {
        "request": "httpx",
    },
}

NO__ALL__ = {
    "nornir_routeros.plugins": [
        "routeros_command",
        "routeros_config_item",
        "routeros_get",
    ],
    "nornir_paramiko.plugins": ["paramiko_command", "paramiko_sftp"],
    "nornir_http": ["http_method"],
}

PARAMETER_TYPES = {
    str: click.STRING,
    type(None): click.STRING,
    int: click.INT,
    float: click.FLOAT,
    bool: click.BOOL,
}


# get original function from original modules (check SETTINGS)
def get_sources(plugin, l):
    try:
        for key, value in SETTINGS[plugin].items():
            m = lambda: None
            m.sub = __import__(value, fromlist=[key])
            o = getattr(m.sub, key, None)
            source_f = [f for f in o.__dict__.keys() if not f.startswith("_")]
            command = sorted(
                [i for i in source_f if l[l.find("_") + 1 : :] in i], key=len
            )
            if command:
                return getattr(o, command[0], None)
            elif inspect.isfunction(o):
                return o
    except KeyError:
        return


def _get_cmd_folder(cmd_folders):
    for cmd_folder in cmd_folders:
        yield os.path.abspath(os.path.join(os.path.dirname(__file__), cmd_folder))


def _get_cli(path, cmd_name, cmd_folder):
    if f"cmd_{cmd_name}.py" in os.listdir(cmd_folder):
        obj = __import__(f"{path}.cmd_{cmd_name}", None, None, ["cli"])
        return obj.cli


# mini factory for the production of classes for our plugins
# https://click.palletsprojects.com/en/8.0.x/commands/#custom-multi-commands
def class_factory(name, plugin, cmd_path=[], BaseClass=click.Group):
    def list_commands(self, ctx):
        ctx.obj[plugin] = __import__(plugin, fromlist=["tasks"])
        try:
            plugin_command_list = list(ctx.obj[plugin].tasks.__all__)
        except AttributeError:
            plugin_command_list = NO__ALL__[plugin]

        # exclude commands that are not implemented in nornir_cli
        if plugin in COMMAND_EXCEPTIONS:
            plugin_command_list = [
                i for i in plugin_command_list if i not in COMMAND_EXCEPTIONS[plugin]
            ]

        return sorted(
            [
                filename[4:-3]
                for filename in os.listdir(next(_get_cmd_folder(["common_commands"])))
                if filename.endswith(".py") and filename.startswith("cmd_")
            ]
            + plugin_command_list
        )

    def list_custom_commands(self, ctx):
        cmd_folders = _get_cmd_folder(CMD_FOLDERS + cmd_path)
        return sorted(
            [
                filename[4:-3]
                for filename in chain(*map(os.listdir, cmd_folders))
                if filename.endswith(".py") and filename.startswith("cmd_")
            ]
        )

    def get_command(self, ctx, cmd_name):
        ctx.obj["kwargs"] = {}
        try:
            # init, filter, show_inventory, etc
            command = _get_cli(
                f"{PACKAGE_NAME}.common_commands",
                cmd_name,
                next(_get_cmd_folder(["common_commands"])),
            )
            if command:
                return command

            # nornir-plugin commands
            plugin_command = _get_cli(
                f"{PACKAGE_NAME}.plugin_commands",
                "common",
                next(_get_cmd_folder(["plugin_commands"])),
            )

            ctx.obj[plugin] = __import__(plugin, fromlist=["tasks"])
            ctx.obj["original"] = getattr(ctx.obj[plugin].tasks, cmd_name, None)

            # decorate the command and wrap it with click.Options
            return decorator(plugin, ctx)(plugin_command)
        except (ImportError, AttributeError):
            return

    def get_custom_command(self, ctx, cmd_name):
        try:
            for abs_path, rel_path in zip(
                _get_cmd_folder(CMD_FOLDERS + cmd_path),
                CMD_FOLDERS + [i.replace(os.sep, ".") for i in cmd_path],
            ):
                command = _get_cli(f"{PACKAGE_NAME}.{rel_path}", cmd_name, abs_path)
                if command:
                    return command
        except (ImportError, AttributeError):
            return

    newclass = type(
        name,
        (BaseClass,),
        {
            "list_commands": list_commands if plugin else list_custom_commands,
            "get_command": get_command if plugin else get_custom_command,
        },
    )
    return newclass


# dynamically create a class for plugin/group and inherit it
def dec(param=None):
    def wrapper(f):
        def finder():
            nonlocal gr

            nonlocal tree

            nonlocal path

            for p in tree:
                if not [ex for ex in custom_exceptions if p[0].endswith(ex)] and not [
                    p for p in p[1] if p not in custom_exceptions
                ]:
                    if [
                        filename
                        for filename in p[2]
                        if filename.endswith(".py") and filename.startswith("cmd_")
                    ]:

                        cmd_path = p[0].split(path)[1]

                        grps = cmd_path.split(os.sep)[1:]
                        for grp in grps[:-1]:
                            if grp in gr.commands:
                                gr = gr.commands[grp]
                                continue
                            gr = gr.group(name=grp)(f)
                        gr.group(
                            name=grps[-1],
                            cls=class_factory(
                                "LazyClass", param, ["custom_commands" + cmd_path]
                            ),
                            chain=True,
                        )(f)
                        gr = init_nornir_cli
                        finder()

        if f.__name__ == "custom":
            path = next(_get_cmd_folder(["custom_commands"]))
            tree = os.walk(path)

            root = next(tree)

            gr = init_nornir_cli
            if not [d for d in root[1] if d not in custom_exceptions]:
                if [
                    filename
                    for filename in root[2]
                    if filename.endswith(".py") and filename.startswith("cmd_")
                ]:
                    return gr.group(name=f.__name__, cls=scls, chain=True)(f)

            return finder()

        else:
            init_nornir_cli.group(cls=scls, chain=True)(f)

    custom_exceptions = ["__pycache__", "templates"]

    grp_exceptions = os.environ.get("NORNIR_CLI_GRP_EXCEPTIONS")
    if grp_exceptions:
        custom_exceptions += grp_exceptions.split(",")

    scls = class_factory("LazyClass", param, ["custom_commands"])

    return wrapper


# command decorator
def decorator(plugin, ctx):
    def wrapper(f):
        doc = ""
        if obj_or.__doc__:
            if obj_or.__name__ in SHORT_HELP_EXCEPTIONS:
                doc_title_regex = r"Arguments:" r"|Args:"
                doc_title_match = re.search(doc_title_regex, obj_or.__doc__)
                if doc_title_match:
                    doc = obj_or.__doc__[: obj_or.__doc__.find(doc_title_match.group())]
            if not doc:
                doc = [title for title in obj_or.__doc__.split("\n") if title][0]

            short_help = doc.strip(", ., : \n").split("\n")
            short_help = " ".join([title.strip() for title in short_help])

            f.__doc__ = "\n".join(list(_doc_generator(obj_or.__doc__)))

            if obj_or.__name__ in METHOD_EXCEPTIONS:
                f.__doc__ = f"{short_help}\n" + "\n".join(
                    list(
                        _doc_generator(
                            obj_or.__doc__[obj_or.__doc__.find("    Args:") : :]
                        )
                    )
                )
        else:
            short_help = ""
        cmd = click.command(name=obj_or.__name__, short_help=short_help)(f)

        common_options(PLUGIN_OPTIONS)(cmd)

        # get original function from the main module
        original_function = get_sources(plugin, obj_or.__name__)
        sig0 = inspect.signature(obj_or)
        p = dict(sig0.parameters)
        if original_function:
            sig = inspect.signature(original_function)
            k = dict(sig.parameters)
            p.update(k)
        all_dict = {
            key: value
            for key, value in p.items()
            if key not in ["self", "task", "args", "kwargs"]
        }

        # dynamically generate options
        for k, v in all_dict.items():
            default_value = (
                getattr(v.default, type_exceptions[type(v.default)])
                if isinstance(v.default, tuple(type_exceptions))
                else v.default
            )

            typ = type(default_value)

            default_value = (
                str(default_value) if not isinstance(default_value, type) else None
            )

            click.option(
                "--" + k,
                default=default_value,
                show_default=True,
                required=False if default_value or default_value == "" else True,
                type=PARAMETER_TYPES.setdefault(typ, click.STRING),
            )(cmd)

            # last original functions with arguments
            ctx.obj["queue_parameters"][obj_or].update({k: v.default})

        # list of dictionaries with original function (key) and set of arguments (value)
        ctx.obj["queue_functions"].append(ctx.obj["queue_parameters"])

        # ctx.obj["queue_functions"] in the form of a generator expression
        ctx.obj["queue_functions_generator"] = (
            func_param for func_param in ctx.obj["queue_functions"]
        )

        return cmd

    # if option type is non-default class
    # class Timeout = <class 'httpx.Timeout'>
    type_exceptions = {
        Timeout: "read",
    }

    # get original function from Nornir plugin
    obj_or = ctx.obj["original"]

    ctx.obj["queue_parameters"] = {}

    ctx.obj["queue_parameters"][obj_or] = {}

    return wrapper


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def init_nornir_cli(ctx):
    """
    Nornir CLI

    Orchestrate your Inventory and start Tasks and Runbooks
    """

    ctx.ensure_object(dict)
    # list of dictionaries with original function (key) and set of arguments (value)
    ctx.obj["queue_functions"] = []
    # last original functions with arguments
    ctx.obj["queue_parameters"] = {}


@dec("nornir_netmiko")
def nornir_netmiko():
    """
    nornir_netmiko plugin
    """
    pass


@dec("nornir_scrapli")
def nornir_scrapli():
    """
    nornir_scrapli plugin
    """
    pass


@dec("nornir_napalm.plugins")
def nornir_napalm():
    """
    nornir_napalm plugin
    """
    pass


@dec("nornir_jinja2.plugins")
def nornir_jinja2():
    """
    nornir_jinja2 plugin
    """
    pass


@dec("nornir_pyez.plugins")
def nornir_pyez():
    """
    nornir_pyez plugin
    """
    pass


@dec("nornir_f5.plugins")
def nornir_f5():
    """
    nornir_f5 plugin
    """
    pass


# nornir_cli is not compatible with nornir-routeros since 0.3.0 version
# nornir-routeros has been removed from nornir_cli 1.2.0
# @dec("nornir_routeros.plugins")
# def nornir_routeros():
#     """
#     nornir_routeros plugin
#     """
#     pass


@dec("nornir_paramiko.plugins")
def nornir_paramiko():
    """
    nornir_paramiko plugin
    """
    pass


@dec("nornir_http")
def nornir_http():
    """
    nornir_http plugin
    """
    pass


@dec("nornir_pyxl.plugins")
def nornir_pyxl():
    """
    nornir_pyxl plugin
    """
    pass


@dec("nornir_netconf.plugins")
def nornir_netconf():
    """
    nornir_netconf plugin
    """
    pass


@dec()
def custom():
    pass
