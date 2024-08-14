from logging import getLogger
from pathlib import Path
from configparser import ConfigParser

import digibankup.fog as fog
import digibankup.snipeit as snipeit
import digibankup.backupsinfo as backupsinfo
from digibankup.util import rmtree
from digibankup.config import Backupflags


logger = getLogger(__name__)


def rotate_backups(config: ConfigParser):
    """
    Rotates backup directories after finishing a backup.

    Args:
        config: Contains configuration settings for the backup.
    """

    backups_path = Path(config['paths']['backups'])
    backup_count = Path(config['settings']['backup_count'])

    if (backups_path / backup_count).is_dir():
        rmtree(backups_path / backup_count)

    backup_dirs = sorted(
        [i for i in backups_path.iterdir() if i.name.isdigit()],
        key=lambda x: int(x.name), reverse=True
    )

    for i in backup_dirs:
        i.rename(backups_path / str(int(i.name) + 1))


def backup(config: ConfigParser, backup_path: Path, backups_info: dict,
           backupflags: Backupflags):
    """
    Performs a backup.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        backups_info: Dict containing date of last backup.
        backupflags: Contains flags indicating which backups to perform.
    """

    backups_path = Path(config['paths']['backups'])

    if backup_path.is_dir():
        logger.warning(f"Directory {backup_path} exists. "
                       f"Recursively removing directory.")
        rmtree(backup_path)

    backup_path.mkdir(parents=True)

    fog.backup(config, backup_path, backupflags)
    snipeit.backup(config, backup_path, backupflags)

    logger.info("Backup performed successfully.")

    rotate_backups(config)

    logger.info(f"Backup stored at {backups_path / '1'}. Other backup "
                f"directory names incremented by 1.")

    backupsinfo.write_backups_info(config, backups_info)
