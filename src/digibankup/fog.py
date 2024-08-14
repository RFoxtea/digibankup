"""Backups the FOG Project server."""

from os import fspath, stat
from logging import getLogger
from pathlib import Path
import shutil
from configparser import ConfigParser
from typing import Callable

import requests

from digibankup.util import touch_parents, format_filesize
from digibankup.config import Backupflags

logger = getLogger(__name__)


def init_paths(config: ConfigParser, backup_path: Path) -> None:
    """
    Initializes paths used during the FOG Project backup process.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
    """
    touch_parents(backup_path / config['subpaths']['fog_db'])
    (backup_path / config['subpaths']['fog_images']).mkdir(parents=True,
                                                           exist_ok=True)
    (backup_path / config['subpaths']['fog_snapins']).mkdir(parents=True,
                                                            exist_ok=True)
    (backup_path / config['subpaths']['fog_reports']).mkdir(parents=True,
                                                            exist_ok=True)


def get_fogsettings(config: ConfigParser) -> dict:
    """
    Retrieves .fogsettings file and parses it into a dict.

    Assumes that .fogsettings consists only of variable declarations separated
    with '=' and comments initiated with '#'.

    Args:
        config: Contains configuration settings for the backup.

    Returns:
        Dictionary containing variables set in the .fogsettings file.
    """
    fogsettings_path = Path(config['paths']['fogsettings'])
    fogsettings_text = fogsettings_path.read_text()
    fogsettings_lines = fogsettings_text.split('\n')
    fogsettings_pairs = [line.split("=") for line in fogsettings_lines
                         if line and line[0] != "#"]
    return {a: b[1:-1] for a, b in fogsettings_pairs}


def get_webdirdest(fogsettings: dict) -> Path:
    """
    Determines the root web directory of the FOG Server.

    Args:
        fogsettings: Dictionary containing the values of .fogsettings file.

    Returns:
        The Path of the root web directory of the FOG Server.
    """
    osid: str = fogsettings['osid']
    docroot: str
    webdirdest: str

    if 'docroot' in fogsettings:
        docroot = fogsettings['docroot']
    else:
        logger.warning("No docroot in .fogsettings. "
                       "Falling back on hardcoded default.")
        docroot = "/var/www/html/"

    if "fog" in docroot:
        webdirdest = docroot + "/"
    else:
        webdirdest = docroot + "fog/"

    if (osid == "2" and docroot == "/var/www/html/"
            and not Path(docroot).exists()):
        docroot = "/var/www/"
        webdirdest = docroot + "fog/"

    return Path(webdirdest)


def backup_db(config: ConfigParser,
              backup_path: Path, fogsettings: dict) -> None:
    """
    Performs backup of the FOG Server SQL database.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        fogsettings: Dictionary containing the values of .fogsettings file.
    """
    logger.info("== Backing up FOG Project SQL database. ==")
    fog_db_backup_path = backup_path / config['subpaths']['fog_db']

    r = requests.post(f'http://'
                      f'{fogsettings['ipaddress']}/'
                      f'{fogsettings['webroot']}'
                      f'/management/export.php?type=sql',
                      data={'nojson': '1'})

    fog_db_backup_path.write_bytes(r.content)
    logger.info(f"FOG Project SQL database written to {fog_db_backup_path}.")


def copy_function_maker(logging_min_filesize) -> Callable:
    """
    Prepares a logged copy_function for the shutil.copytree function.

    Args:
        logging_min_filesize: Files with a size smaller than this (in bits) are
            not logged. Prevents spam of various tiny files.

    Returns:
        copy_function that includes logging.
    """
    def copy_function(src, dst, *, follow_symlinks=True):
        """Copies files and logs it if the file is large enough..

        Args:
            src: Source directory.
            dst: Destination directory.
            follow_symlinks: If false, symlinks won't be followed. This
                resembles GNU's "cp -P src dst".
            """
        filesize = stat(src).st_size
        if filesize > logging_min_filesize:
            logger.info(f"Copying {fspath(src)} to {fspath(dst)}. "
                        f"Filesize: {format_filesize(filesize)}")
        shutil.copy2(src=src, dst=dst, follow_symlinks=follow_symlinks)
        return dst
    return copy_function


def backup_images(config: ConfigParser, backup_path: Path,
                  fogsettings: dict) -> None:
    """
    Performs backup of the FOG Server images folder.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        fogsettings: Dictionary containing the values of .fogsettings file.
    """
    logger.info("== Backing up FOG Project images. ==")

    fog_images_path = Path(fogsettings["storageLocation"])
    fog_images_backup_path = backup_path / config['subpaths']['fog_images']

    logging_min_filesize = int(config['settings']['logging_min_filesize'])
    copy_function = copy_function_maker(logging_min_filesize)

    try:
        shutil.copytree(fog_images_path, fog_images_backup_path,
                        copy_function=copy_function, dirs_exist_ok=True)
    except (shutil.Error, FileNotFoundError) as e:
        logger.error(f"Could not copy images from {fog_images_path} to "
                     f"{fog_images_backup_path}.", exc_info=e)
    logger.info(f"FOG Project images written to {fog_images_backup_path}.")


def backup_snapins(config: ConfigParser, backup_path: Path,
                   fogsettings: dict) -> None:
    """
    Performs backup of the FOG Server snapins.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        fogsettings: Dictionary containing the values of .fogsettings file.
    """
    logger.info("== Backing up FOG Project snapins. ==")

    fog_snapins_path = Path(config["paths"]["fog_snapins"])
    fog_snapins_backup_path = backup_path / config['subpaths']['fog_snapins']

    logging_min_filesize = int(config['settings']['logging_min_filesize'])
    copy_function = copy_function_maker(logging_min_filesize)

    try:
        shutil.copytree(fog_snapins_path, fog_snapins_backup_path,
                        copy_function=copy_function, dirs_exist_ok=True)
    except (shutil.Error, FileNotFoundError) as e:
        logger.error(f"Could not copy snapins from {fog_snapins_path} to "
                     f"{fog_snapins_backup_path}.", exc_info=e)

    logger.info(f"FOG Project snapins written to {fog_snapins_backup_path}.")


def backup_reports(config: ConfigParser, backup_path: Path,
                   fogsettings: dict) -> None:
    """
    Performs backup of the FOG Server reports.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        fogsettings: Dictionary containing the values of .fogsettings file.
    """
    logger.info("== Backing up FOG Project reports. ==")

    fog_reports_path = get_webdirdest(fogsettings) / "lib/reports"
    fog_reports_backup_path = backup_path / config['subpaths']['fog_reports']

    logging_min_filesize = int(config['settings']['logging_min_filesize'])
    copy_function = copy_function_maker(logging_min_filesize)

    try:
        shutil.copytree(fog_reports_path, fog_reports_backup_path,
                        copy_function=copy_function, dirs_exist_ok=True)
    except (shutil.Error, FileNotFoundError) as e:
        logger.error(f"Could not copy reports from {fog_reports_path} to "
                     f"{fog_reports_backup_path}.", exc_info=e)

    logger.info(f"FOG Project reports written to {fog_reports_backup_path}.")


def backup(config: ConfigParser, backup_path: Path,
           backupflags: Backupflags) -> None:
    """
    Performs backup of FOG server.

    Args:
        config: Contains configuration settings for the backup.
        backup_path: Root destination path of the ongoing backup.
        backupflags: Contains flags indicating which backups to perform.
    """
    logger.info("==== Backing up FOG Project server. ====")

    init_paths(config, backup_path)

    fogsettings = get_fogsettings(config)

    if backupflags.fog_db:
        backup_db(config, backup_path, fogsettings)
    if backupflags.fog_images:
        backup_images(config, backup_path, fogsettings)
    if backupflags.fog_snapins:
        backup_snapins(config, backup_path, fogsettings)
    if backupflags.fog_reports:
        backup_reports(config, backup_path, fogsettings)
