import os

import click

from ESSArch_Core.config import generate_local_settings


def create_local_settings_file(path, overwrite=None):
    content = generate_local_settings()

    if os.path.isfile(path) and overwrite is None:
        overwrite = click.confirm("File at '%s' already exists, should we overwrite it?" % click.format_filename(path))

    if not os.path.isfile(path) or overwrite:
        with click.open_file(path, 'w') as fp:
            fp.write(content)


@click.command()
@click.option('--overwrite/--no-overwrite', default=None)
@click.option('-p', '--path', type=str, prompt=True, default='/ESSArch/config/local_essarch_settings.py',
              show_default='/ESSArch/config/local_essarch_settings.py')
def generate(path, overwrite):
    """Generate settings file
    """

    create_local_settings_file(path, overwrite=overwrite)