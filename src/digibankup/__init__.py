from logging import getLogger
from pathlib import Path
from configparser import ConfigParser

import click

import digibankup.backup as backup
import digibankup.backupsinfo as backupsinfo
from digibankup.config import get_config, Backupflags
from digibankup.util import touch_parents, str_to_bool

logger = getLogger(__name__)


def init_paths(config: ConfigParser):
    """
    Initializes paths of outer backup directory and touches relevant files.

    Args:
        config: Contains configuration settings for the backup.
    """
    Path(config['paths']['backups']).mkdir(parents=True, exist_ok=True)
    touch_parents(Path(config['paths']['info']))
    touch_parents(Path(config['paths']['log']))


@click.command()
@click.option('--log/--no-log', is_flag=True, default=None,
              help='Log steps of backup.')
@click.option('--check-date', is_flag=True, default=None,
              help='Check if sufficient time has been elapsed since backup.')
@click.option('--snipeit/--no-snipeit', is_flag=True, default=None,
              help='Backup Snipe IT server. (NOT IMPLEMENTED)')
@click.option('--fogdb/--no-fogdb', 'fog_db', is_flag=True, default=None,
              help='Backup FOG Project database.')
@click.option('--fogimages/--no-fogimages', 'fog_images',
              is_flag=True, default=None,
              help='Backup FOG Project images (Warning: Very slow.).')
@click.option('--fogsnapins/--no-fogsnapins', 'fog_snapins',
              is_flag=True, default=None,
              help='Backup FOG Project snapins.')
@click.option('--fogreports/--no-fogreports', 'fog_reports',
              is_flag=True, default=None,
              help='Backup FOG Project reports.')
@click.option('--config', 'config_path', default="",
              help='Path of a config file to use.')
@click.option('--export-config', 'config_export_path', default="",
              help='Path at which to export the configuration.')
def main(log, check_date, snipeit, fog_db, fog_images, fog_snapins,
         fog_reports, config_path='', config_export_path='') -> None:
    """Performs backups of FOG Project and Snipe IT servers."""
    config: ConfigParser = get_config(Path(config_path))

    if check_date is None:
        check_date = str_to_bool(config['settings']['check_date'])

    if log is None:
        log = str_to_bool(config['settings']['log'])

    cl_flags = {'snipeit': snipeit,
                'fog_db': fog_db,
                'fog_images': fog_images,
                'fog_snapins': fog_snapins,
                'fog_reports': fog_reports}

    backupflags = Backupflags.from_config(
        config=config,
        cl_flags=cl_flags
    )

    init_paths(config)

    if log:
        from digibankup.logging import configure_logging
        configure_logging(config)

    logger.info("====== DIGIBANKUP 0.0.2 by Raf V. ======")

    backups_info: dict = backupsinfo.get_backups_info(config)

    backup_path = Path(config['paths']['backups']) / '0'

    if check_date:
        if backupsinfo.performed_recent_backup(config, backups_info):
            logger.info("Backup has already been performed recently. "
                        "Not performing backup.")
            return
        logger.info("No backup performed recently.")
    logger.info(f"Initializing backup process at {backup_path}.")

    backup.backup(config, backup_path, backups_info, backupflags)

    if config_export_path != '':
        config.write(Path(config_export_path).open('w'))
