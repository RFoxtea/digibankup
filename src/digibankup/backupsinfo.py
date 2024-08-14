"""Tracks the interval between backups through the backupsinfo file."""
from logging import getLogger
import json
from zoneinfo import ZoneInfo
from pathlib import Path
from configparser import ConfigParser

from datetime import datetime, date, timedelta

logger = getLogger(__name__)


def get_backups_info(config: ConfigParser) -> dict:
    """
    Retrieves date of last backup.

    Args:
        config: Contains configuration settings for the backup.
    """
    info_path = Path(config['paths']['info'])

    try:
        with info_path.open('r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"No info file about previous backups at {info_path}. "
                       f"Falling back on defaults.")
    except json.JSONDecodeError as e:
        logger.error(f"Could not parse info file about previous backups at "
                     f"{info_path}. Falling back on defaults.",
                     exc_info=e)
    except Exception as e:
        logger.critical(f"Error while retrieving info file about previous "
                        f"backups at {info_path}. Cannot continue.",
                        exc_info=e)
        raise e
    return dict(config['default_info'])


def write_backups_info(config: ConfigParser, backups_info: dict) -> None:
    """
    Stores date of last backup.

    Args:
        config: Contains configuration settings for the backup.
        backups_info: Previous backups_info dict, will be updated,
            and saved as JSON file.
    """
    info_path = Path(config['paths']['info'])
    timezone = ZoneInfo(config['settings']['timezone'])

    backups_info['last_datetime'] = datetime.now(timezone).isoformat()
    try:
        with info_path.open('w') as f:
            return json.dump(backups_info, f)
    except Exception as e:
        logger.critical("Error while writing backups_info.", exc_info=e)
        raise e


def performed_recent_backup(config: ConfigParser, backups_info: dict) -> bool:
    """
    Checks if a backup was performed recently.

    Args:
        config: Contains configuration settings for the backup.
        backups_info: Contents of (by default) info.dat, which tracks last
            backup time.

    Returns:
        Whether a backup has been raised in the required interval set in config
        by settings.backup_interval.

    Raises:
        ValueError: Raised when no valid last_datetime can be found in both
            backups_info and config['default_info'].
    """
    logger.debug("Checking if backup performed recently.")

    default_datetime = config['default_info']['last_datetime']
    backup_interval = timedelta(int(config['settings']['backup_interval']))
    timezone = ZoneInfo(config['settings']['timezone'])

    fallback = False

    if 'last_datetime' in backups_info:
        last_datetime_iso = backups_info['last_datetime']
        try:
            last_datetime = datetime.fromisoformat(last_datetime_iso)
        except ValueError as e:
            logger.error(f"Could not parse datetime {last_datetime_iso}. "
                         f"Is it in proper ISO 8601 format? "
                         f"Falling back on default.",
                         exc_info=e)
            fallback = True
    else:
        logger.warning(
            "backups_info does not contain last_datetime. "
            "Falling back on default.")
        fallback = True

    if fallback:
        try:
            last_datetime = datetime.fromisoformat(default_datetime)
        except ValueError as e:
            logger.critical(f"Could not parse default datetime "
                            f"{default_datetime}. "
                            f"Cannot continue.",
                            exc_info=e)
            raise e

    curr_backup_date: date = datetime.now(timezone).date()
    last_backup_date: date = last_datetime.date()

    return curr_backup_date - last_backup_date < backup_interval
