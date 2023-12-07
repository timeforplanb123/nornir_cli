import click

from nornir.core.plugins.connections import ConnectionPluginRegister

from nornir_cli.common_commands import (
    _get_lists,
    _get_dict_from_json_string,
    _json_loads,
    _pickle_to_hidden_file,
    multiple_progress_bar,
    print_result as pr,
    print_stat as ps,
)

from tqdm import tqdm


ERROR_MESSAGE = (
    "Nornir plugin options and arguments.\n"
    "Check the required options and the command format"
    "(use json syntax for arguments).\n"
    "There should be something like...\n\n"
    "Only with required options:\n"
    '   nornir_cli nornir-netmiko netmiko_send_command --command_string "disp clock"\n\n'
    "Only with required options as an arguments(json-string):\n"
    "   nornir_cli nornir-netmiko netmiko_send_command "
    '\'{"command_string":"disp clock"}\'\n\n'
    "With required options and arguments(json-string). The priority of options will be "
    'higher, the command "disp ver" will be executed:\n'
    "   nornir_cli nornir-netmiko netmiko_send_command "
    '--command_string "disp ver" '
    '\'{"command_string":"disp clock"}\'\n\n'
    'With required options and arguments(json-string). The command "disp ver" '
    'will be executed with the "read_timeout" argument:\n'
    "   nornir_cli nornir-netmiko netmiko_send_command "
    '--command_string "disp ver" '
    "'{\"read_timeout\":11.0}'"
)


@click.pass_context
def cli(ctx, pg_bar, print_result, print_stat, arguments, *args, **kwargs):
    ConnectionPluginRegister.auto_register()

    try:
        # 'None' = None
        kwargs.update({k: v for k, v in zip(kwargs, _json_loads(kwargs.values()))})

        current_func_params = next(ctx.obj["queue_functions_generator"])

        # try to pass not all arguments, but only the necessary ones
        if kwargs == list(current_func_params.values())[0] and not arguments:
            function, parameters = list(current_func_params.items())[0]
        else:
            param_iterator = iter(current_func_params.values())
            params = list(next(param_iterator).items())
            function, parameters = list(current_func_params)[0], {
                key: value
                for key, value in kwargs.items()
                if (key, value) not in params
            }

            # use arguments to update parameters
            if arguments:
                parameters = {**_get_dict_from_json_string(arguments), **parameters}
        missing_options = [
            f"'--{option}'"
            for option in ctx.obj["required_options"]
            if parameters.get(option) == None
        ]
        if missing_options:
            raise ctx.fail(
                f"Missing options {', '.join(missing_options)}",
            )
    except (ValueError, IndexError, TypeError, KeyError):
        raise ctx.fail(
            click.BadParameter(
                f"{ERROR_MESSAGE}",
            ).format_message(),
        )

    # get the current Nornir object from Commands chain or from temp.pkl file
    try:
        nr = ctx.obj["nornir"]
    except KeyError:
        nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)

    nr.config.logging.configure()

    # pg_bar option
    if pg_bar:
        with tqdm(
            total=len(nr.inventory.hosts),
            desc="processing: ",
        ) as pb:
            result = nr.run(
                task=multiple_progress_bar,
                method=function,
                pg_bar=pb,
                **parameters,
            )
        print()
    else:
        result = nr.run(
            task=function,
            **parameters,
        )

    ctx.obj["result"] = result

    # print_result option
    if print_result:
        pr(result)
        print()

    # print statistic
    if print_stat:
        ps(nr, result)
