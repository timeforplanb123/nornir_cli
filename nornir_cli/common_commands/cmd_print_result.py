import logging

import click

from nornir_cli.common_commands import (
    PRINT_RESULT_OPTIONS,
    PRINT_RESULT_WRITE_RESULT_OPTIONS,
    _json_loads,
    _pickle_to_hidden_file,
    common_options,
    print_result,
    print_stat as ps,
)


ERROR_MESSAGE = (
    "Get Result object at first. Initialize Nornir and run any command to do this.\n"
    "There should be something like...\n\n"
    "Initializing Nornir, advanced  the inventory filtering and Nornir object saving:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yml filter --hosts -s -a "
    "'name__contains=spine'\n\n"
    "Run any plugin command, get Result object and run print_result command:\n"
    '   nornir_cli nornir-netmiko netmiko_send_command --command_string "display '
    'version" print_result --attributes \'["result", "diff"]\' --count=5\n\n'
    "Or run it as a single command:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yml filter --hosts -s -a "
    "'name__contains=spine' netmiko_send_command --command_string \"display "
    'version" print_result --attributes \'["result", "diff"]\' --count=5\n\n'
    "To use `print_result` command in `custom runbook`, please read the documentation"
)


@click.command()
@common_options(PRINT_RESULT_OPTIONS)
@common_options(PRINT_RESULT_WRITE_RESULT_OPTIONS)
@click.pass_context
def cli(ctx, attributes, failed, severity_level, print_host, count, print_stat):
    """
    print_result from nornir_utils
    """

    try:
        result = ctx.obj["result"]
    except KeyError:
        raise ctx.fail(ERROR_MESSAGE)

    print_result(
        result,
        vars=_json_loads([attributes])[0],
        failed=failed,
        severity_level=getattr(logging, severity_level, 20),
        count=count,
        print_host=print_host,
    )

    # print statistic
    if print_stat:
        try:
            nr = ctx.obj["nornir"]
        except KeyError:
            nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)

        ps(nr, result)
