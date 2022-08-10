import logging
import os
from pathlib import Path

import click

from nornir_cli.common_commands import (
    PRINT_RESULT_WRITE_RESULT_OPTIONS,
    WRITE_RESULTS_OPTIONS,
    WRITE_RESULT_WRITE_RESULTS_OPTIONS,
    _json_loads,
    _pickle_to_hidden_file,
    common_options,
    print_stat as ps,
    write_results,
)


ERROR_MESSAGE = (
    "Get Result object at first. Initialize Nornir and run any command to do this.\n"
    "There should be something like...\n\n"
    "Initializing Nornir, advanced  the inventory filtering and Nornir object saving:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yml filter --hosts -s -a "
    "'name__contains=spine | name__contains=leaf'\n\n"
    "Run any plugin command, get Result object and run write_result command:\n"
    '   nornir_cli nornir-netmiko netmiko_send_command --command_string "display '
    'version" --no_print_result --no_print_stat'
    'write_results --dirname ./results --attributes \'["result", "diff"]\' --print_stat\n\n'
    "Or run it as a single command:\n"
    "   nornir_cli nornir-netmiko init -c ~/config.yml filter --hosts -s -a "
    "'name__contains=spine | name__contains=leaf' netmiko_send_command --command_string \"display "
    'version" --no_print_result --no_print_stat'
    'write_results --dirname ./results --attributes \'["result", "diff"]\' '
    "--print_stat\n\n"
    "To use `write_results` command in `custom runbook`, please read the documentation"
)


@click.command(short_help="Write `Result` object to files")
@common_options(WRITE_RESULTS_OPTIONS)
@common_options(WRITE_RESULT_WRITE_RESULTS_OPTIONS)
@common_options(PRINT_RESULT_WRITE_RESULT_OPTIONS)
@click.pass_context
def cli(
    ctx,
    dirname,
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
    Write an object of type `nornir.core.task.Result` to files with hostname names
    """

    try:
        result = ctx.obj["result"]
    except KeyError:
        raise ctx.fail(ERROR_MESSAGE)

    try:
        diffs = write_results(
            result,
            dirname=dirname,
            vars=_json_loads([attributes])[0],
            failed=failed,
            severity_level=getattr(logging, severity_level, 20),
            count=count,
            write_host=write_host,
            no_errors=no_errors,
            append=append,
        )

        if print_diff:
            for diff in diffs:
                print()
                print("\n\n".join(diff))
            print()

        if diff_to_file:
            Path(diff_to_file).mkdir(parents=True, exist_ok=True)
            for name, diff in diffs:
                with open(os.path.join(diff_to_file, name), mode="w") as f:
                    f.write(diff)
    except Exception as err:
        raise click.ClickException(err)

    if print_stat:
        try:
            nr = ctx.obj["nornir"]
        except KeyError:
            nr = _pickle_to_hidden_file("temp.pkl", mode="rb", dump=False)

        ps(nr, result)
