import click
from nornir_utils.plugins.functions import print_result
import logging
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir_cli.common_commands import _pickle_to_hidden_file, _json_loads, _info
from tqdm import tqdm


# def _get_color(f, ch):
#    if f:
#        color = "red"
#    elif ch:
#        color = "yellow"
#    else:
#        color = "green"
#    return color


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
    # ch_sum = 0
    # for host in nr.inventory.hosts:
    #    f, ch = (task[host].failed, task[host].changed)
    #    ch_sum += int(ch)
    #    click.secho(
    #        f"{host:<50}: ok={not f:<15} changed={ch:<15} failed={f:<15}",
    #        fg=_get_color(f, ch),
    #        bold=True,
    #    )
    # print()
    # f_sum = len(nr.data.failed_hosts)
    # ok_sum = len(nr.inventory.hosts) - f_sum
    # for state, summary, color in zip(
    #    ("OK", "CHANGED", "FAILED"), (ok_sum, ch_sum, f_sum), ("green", "yellow", "red")
    # ):
    #    click.secho(
    #        f"{state:<8}: {summary}",
    #        fg=color,
    #        bold=True,
    #    )
    # print()
