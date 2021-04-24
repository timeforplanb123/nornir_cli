import click
from nornir_utils.plugins.functions import print_result
import logging
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir_cli.common_commands import _pickle_to_hidden_file, _json_loads, _info
from tqdm import tqdm


def multiple_progress_bar(task, method, pg_bar, **kwargs):
    task.run(task=method, **kwargs)
    if pg_bar:
        pg_bar.update()


@click.pass_context
def cli(ctx, pg_bar, show_result, *args, **kwargs):
    ConnectionPluginRegister.auto_register()

    # 'None' = None
    kwargs.update({k: v for k, v in zip(kwargs, _json_loads(kwargs.values()))})

    current_func_params = next(ctx.obj["queue_functions_generator"])

    # try to pass not all arguments, but only the necessary ones
    if kwargs == list(current_func_params.values())[0]:
        function, parameters = list(current_func_params.items())[0]
    else:
        param_iterator = iter(current_func_params.values())
        params = list(next(param_iterator).items())
        function, parameters = list(current_func_params)[0], {
            key: value for key, value in kwargs.items() if (key, value) not in params
        }

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
            task = nr.run(
                task=multiple_progress_bar,
                method=function,
                pg_bar=pb,
                **parameters,
            )
        print()
    else:
        task = nr.run(
            task=function,
            **parameters,
        )

    # show_result option
    if show_result:
        print_result(task, severity_level=logging.DEBUG)
        print()

    # show statistic
    _info(nr, task)
