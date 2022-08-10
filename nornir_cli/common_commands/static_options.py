import pathlib

import click

from nornir_cli.common_commands.common import _validate_connection_options


# init options
CONNECTION_OPTIONS = [
    click.option(
        "-co",
        "--connection_options",
        callback=_validate_connection_options,
        help="Specify any connection parameters (json string)",
    ),
]

# nornir_plugin options
PLUGIN_OPTIONS = [
    click.option(
        "--pg_bar",
        help="Progress bar flag",
        is_flag=True,
        default=False,
        show_default=True,
    ),
    click.option(
        "--print_result/--no_print_result",
        help="print_result from nornir_utils",
        default=True,
        show_default=True,
    ),
    click.option(
        "--print_stat/--no_print_stat",
        help="Print Result statistic for Nornir object",
        default=True,
        show_default=True,
    ),
]

PRINT_RESULT_WRITE_RESULT_OPTIONS = [
    click.option(
        "--failed",
        type=click.BOOL,
        default=False,
        show_default=True,
        help="If True assume the task failed",
    ),
    click.option(
        "-sl",
        "--severity_level",
        type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]),
        default="INFO",
        show_default=True,
        help="Show only errors with this severity level or higher",
    ),
    click.option(
        "-cou",
        "--count",
        type=click.INT,
        help="Results counter",
    ),
    click.option(
        "-ps/-no_ps",
        "--print_stat/--no_print_stat",
        default=False,
        show_default=True,
        help="Print Result statistic for Nornir object",
    ),
]

# print_result options
PRINT_RESULT_OPTIONS = [
    click.option(
        "-attrs",
        "--attributes",
        help="Result class attributes you want to print",
    ),
    click.option(
        "-ph",
        "--print_host",
        type=click.BOOL,
        default=True,
        show_default=True,
        help="Print hostnames",
    ),
]

WRITE_RESULTS_OPTIONS = [
    click.option(
        "-d",
        "--dirname",
        required=True,
        help="Direcotry you want to write into",
    ),
]

WRITE_RESULT_OPTIONS = [
    click.option(
        "-f",
        "--filename",
        required=True,
        help="File you want to write into",
    ),
]

WRITE_RESULT_WRITE_RESULTS_OPTIONS = [
    click.option(
        "-attrs",
        "--attributes",
        help="Result attributes you want to write (str or list(json string)). There can be any Result attributes or text. By default, the result attribute is used",
    ),
    click.option(
        "-a",
        "--append",
        is_flag=True,
        default=False,
        show_default=True,
        help="Whether you want to replace the contents or append to it",
    ),
    click.option(
        "-pd/-no_pd",
        "--print_diff/--no_print_diff",
        default=False,
        show_default=True,
        help="Print diff",
    ),
    click.option(
        "-dtf",
        "--diff_to_file",
        type=pathlib.Path,
        help="Write diff to file",
    ),
    click.option(
        "-wh",
        "--write_host",
        type=click.BOOL,
        default=True,
        show_default=True,
        help="Write hostnames",
    ),
    click.option(
        "-ne",
        "--no_errors",
        is_flag=True,
        default=False,
        show_default=True,
        help="Do not write errors to file",
    ),
]

# show_inventory options
SHOW_INVENTORY_OPTIONS = [
    click.option(
        "-i",
        "--inventory",
        type=click.Choice(["hosts", "groups", "defaults", "all"]),
        help="Show hosts, groups or defaults inventory",
    ),
    click.option("-h", "--hosts", is_flag=True, help="Show hosts list"),
    click.option("-g", "--groups", is_flag=True, help="Show groups list"),
    click.option(
        "-cou",
        "--count",
        type=click.INT,
        help="Number of elements you want to show",
    ),
]

WRITE_FILE_OPTIONS = [
    click.option(
        "-f",
        "--filename",
        required=True,
        help="File you want to write into",
    ),
    click.option(
        "-c",
        "--content",
        required=True,
        help="Content you want to write (string)",
    ),
    click.option(
        "-a",
        "--append",
        is_flag=True,
        default=False,
        show_default=True,
        help="Whether you want to replace the contents or append to it",
    ),
    click.option(
        "-l",
        "--line_feed",
        count=True,
        show_default=True,
        help="number of \\n before text",
    ),
]
