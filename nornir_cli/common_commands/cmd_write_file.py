import os
from pathlib import Path

import click

from nornir_cli.common_commands import (
    WRITE_FILE_OPTIONS,
    common_options,
)


@click.command()
@common_options(WRITE_FILE_OPTIONS)
@click.pass_context
def cli(ctx, filename, content, append, line_feed):
    """
    Write_file, but not from nornir_utils
    """

    try:

        dirname = os.path.dirname(filename)
        Path(dirname).mkdir(parents=True, exist_ok=True)

        content = line_feed * "\n" + content if line_feed else content

        mode = "a+" if append else "w+"

        with open(filename, mode=mode) as f:
            f.write(content)

    except Exception as err:
        raise click.ClickException(err)
