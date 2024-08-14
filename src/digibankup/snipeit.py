"""Performs backup of the SnipeIT server. (NOT IMPLEMENTED)"""
from os import PathLike
from logging import getLogger
import requests
from configparser import ConfigParser

from digibankup.config import Backupflags

logger = getLogger(__name__)


#  Currently not implemented because Snipe IT version does not support backups.
#  Component would work if Snipe IT were updated.
def backup(config: ConfigParser, backup_path: PathLike,
           backupflags: Backupflags) -> None:
    """Performs backup of Snipe IT inventory.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        backupflags: Contains flags indicating which backups to perform.
            If the snipeit flag is not True the body of this function will not
            execute."""
    return

    if not backupflags.snipeit:
        return

    logger.info("==== Backing up Snipe IT server. ====")

    url = config['snipe_it']['api_endpoint'] + 'settings/backups'

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + config['snipe_it']['api_token']
    }

    response = requests.get(url, headers=headers)

    print(response)

    logger.error("CANNOT BACK UP SNIPE IT. SNIPE IT BACKUP NOT IMPLEMENTED.")
