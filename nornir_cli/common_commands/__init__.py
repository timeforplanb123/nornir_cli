from nornir_cli.common_commands.common import (
    common_options,
    _pickle_to_hidden_file,
    _json_loads,
    _get_lists,
    _doc_generator,
    _validate_connection_options,
    custom,
    print_stat,
    multiple_progress_bar,
)

from nornir_cli.common_commands.static_options import (
    SHOW_INVENTORY_OPTIONS,
    CONNECTION_OPTIONS,
    PLUGIN_OPTIONS,
    PRINT_RESULT_OPTIONS,
    PRINT_RESULT_WRITE_RESULT_OPTIONS,
    WRITE_RESULT_OPTIONS,
    WRITE_RESULTS_OPTIONS,
    WRITE_RESULT_WRITE_RESULTS_OPTIONS,
    WRITE_FILE_OPTIONS,
)

from nornir_cli.common_commands import cmd_show_inventory
from nornir_cli.common_commands.print_result import print_result
from nornir_cli.common_commands.write_result import write_result
from nornir_cli.common_commands.write_results import write_results

__all__ = (
    "_pickle_to_hidden_file",
    "common_options",
    "cmd_show_inventory",
    "_json_loads",
    "_get_lists",
    "_doc_generator",
    "_validate_connection_options",
    "custom",
    "print_stat",
    "print_result",
    "write_result",
    "write_results",
    "multiple_progress_bar",
    "SHOW_INVENTORY_OPTIONS",
    "CONNECTION_OPTIONS",
    "PLUGIN_OPTIONS",
    "PRINT_RESULT_OPTIONS",
    "PRINT_RESULT_WRITE_RESULT_OPTIONS",
    "WRITE_RESULT_OPTIONS",
    "WRITE_RESULTS_OPTIONS",
    "WRITE_RESULT_WRITE_RESULTS_OPTIONS",
    "WRITE_FILE_OPTIONS",
)
