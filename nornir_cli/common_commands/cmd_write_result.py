import logging
import os
from pathlib import Path

import click

from nornir_cli.common_commands import (
    PRINT_RESULT_WRITE_RESULT_OPTIONS,
    WRITE_RESULT_OPTIONS,
    WRITE_RESULT_WRITE_RESULTS_OPTIONS,
    _json_loads,
    _pickle_to_hidden_file,
    common_options,
    print_stat as ps,
    write_result,
)


ERROR_MESSAGE = (
    "Get Result object at first. Initialize Nornir and run any command to do this.\n"
    "There should be something like...\n\n"
    "Initializing Nornir, advanced  the inventory filtering and Nornir object saving:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yml filter --hosts -s -a "
    "'name__contains=spine'\n\n"
    "Run any plugin command, get Result object and run write_result command:\n"
    '   nornir_cli nornir-netmiko netmiko_send_command --command_string "display '
    'version" --no_print_result --no_print_stat'
    'write_result --filename results.txt --attributes \'["result", "diff"]\'\n\n'
    "Or run it as a single command:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yml filter --hosts -s -a "
    "'name__contains=spine' netmiko_send_command --command_string \"display "
    'version" --no_print_result --no_print_stat'
    'write_result --attributes \'["result", "diff"]\'\n\n'
    "To use `write_result` command in `custom runbook`, please read the documentation"
)


@click.command(short_help="Write `Result` object to file")
@common_options(WRITE_RESULT_OPTIONS)
@common_options(WRITE_RESULT_WRITE_RESULTS_OPTIONS)
@common_options(PRINT_RESULT_WRITE_RESULT_OPTIONS)
@click.pass_context
def cli(
    ctx,
    filename,
    attributes,
    append,
    print_diff,
    diff_to_file,
    write_host,
    failed,
    severity_level,
    count,
    print_stat,
    no_errors,
):
    """
    Write an object of type `nornir.core.task.Result` to file
    """

    try:
        result = ctx.obj["result"]
    except KeyError:
        raise ctx.fail(ERROR_MESSAGE)

    try:
        diff = write_result(
            result,
            filename=filename,
            vars=_json_loads([attributes])[0],
            failed=failed,
            severity_level=getattr(logging, severity_level, 20),
            count=count,
            write_host=write_host,
            append=append,
            no_errors=no_errors,
        )

        if print_diff:
            print(diff)

        if diff_to_file:
            Path(os.path.dirname(diff_to_file)).mkdir(parents=True, exist_ok=True)
            with open(diff_to_file, mode="w") as f:
                f.write(diff)
    except Exception as err:
        raise click.ClickException(err)

    if print_stat:
        try:
            nr = ctx.obj["nornir"]
        except KeyError:
            nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)

        ps(nr, result)
