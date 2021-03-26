import os
import click
import inspect
from itertools import chain
from nornir_cli.common_commands import _doc_generator
from nornir_cli import __version__


CMD_FOLDERS = ["common_commands", "custom_commands"]

PACKAGE_NAME = "nornir_cli"

SETTINGS = {
    "nornir_scrapli": {
        "NetconfScrape": "scrapli_netconf.driver",
        "NetworkDriver": "scrapli.driver",
        "GenericDriver": "scrapli.driver",
    },
    "nornir_netmiko": {
        "BaseConnection": "netmiko",
        "file_transfer": "netmiko",
    },
}

PARAMETER_TYPES = {
    str: click.STRING,
    type(None): click.STRING,
    int: click.INT,
    float: click.FLOAT,
    bool: click.BOOL,
}

# options callback
# def callback(ctx, param, value):
#     if value != param.get_default(ctx):
#         ctx.obj["kwargs"].update(dict([[param.name, _json_loads([value])[0]]]))
#         ctx.obj["parameters"].append({ctx.obj["original"]: ctx.obj["kwargs"]})
#         ctx.obj["generator"] = (
#             dict(list(item.items())) for item in ctx.obj["parameters"]
#         )

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
# https://click.palletsprojects.com/en/7.x/commands/?highlight=multi%20command#custom-multi-commands
def class_factory(name, plugin, BaseClass=click.Group):
    def list_commands(self, ctx):
        ctx.obj[plugin] = __import__(plugin, fromlist=["tasks"])
        return [
            filename[4:-3]
            for filename in os.listdir(next(_get_cmd_folder(["common_commands"])))
            if filename.endswith(".py") and filename.startswith("cmd_")
        ] + list(ctx.obj[plugin].tasks.__all__)

    def list_custom_commands(self, ctx):
        cmd_folders = _get_cmd_folder(CMD_FOLDERS)
        return [
            filename[4:-3]
            for filename in chain(*map(os.listdir, cmd_folders))
            if filename.endswith(".py") and filename.startswith("cmd_")
        ]

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

            # decorate the command and cover it with click.Options
            return decorator(plugin, ctx)(plugin_command)
        except (ImportError, AttributeError):
            return

    def get_custom_command(self, ctx, cmd_name):
        try:
            for abs_path, rel_path in zip(_get_cmd_folder(CMD_FOLDERS), CMD_FOLDERS):
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
        return init_nornir_cli.group(cls=scls, chain=True)(f)

    scls = class_factory("LazyClass", param)
    return wrapper


#
def decorator(plugin, ctx):
    def wrapper(f):
        # methods with a large and complex __doc__ :(
        method_exceptions = ("send_interactive",)

        short_help = obj_or.__doc__.split("\n")[1].strip(", ., :")

        f.__doc__ = "\n".join(list(_doc_generator(obj_or.__doc__)))

        if obj_or.__name__ in method_exceptions:
            f.__doc__ = f"{short_help}\n" + "\n".join(
                list(
                    _doc_generator(obj_or.__doc__[obj_or.__doc__.find("    Args:") : :])
                )
            )

        cmd = click.command(name=obj_or.__name__, short_help=short_help)(f)

        click.option(
            "--pg_bar",
            is_flag=True,
            show_default=True,
        )(cmd)
        click.option(
            "--show_result/--no_show_result",
            default=True,
            show_default=True,
        )(cmd)

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
            default_value = str(v.default) if not isinstance(v.default, type) else None
            click.option(
                "--" + k,
                default=default_value,
                show_default=True,
                required=False if default_value else True,
                # expose_value=False,
                # callback=callback,
                # is_eager=True,
                type=PARAMETER_TYPES.setdefault(type(v.default), click.STRING),
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


@dec()
def custom():
    """
    custom nornir runbooks
    """
    pass
