"""
Contains classes, functions, and defaults values pertaining to configuration.
"""

from configparser import ConfigParser
from os import PathLike
from dataclasses import dataclass
from collections.abc import Mapping

from digibankup.util import str_to_bool


@dataclass
class Backupflags:
    """
    Flags determining which part of the backup to perform.
    """
    snipeit: bool
    fog_db: bool
    fog_images: bool
    fog_snapins: bool
    fog_reports: bool

    @classmethod
    def from_config(cls, config: Mapping, cl_flags: dict):
        """
        Configure these flags from config file and command line.

        Args:
            config: 'perform' subsection of configuration settings.
            cl_flags: Flags passed to command line.
        """
        if isinstance(config, ConfigParser):
            config = config['perform']

        config_parsed = {k: str_to_bool(v) for k, v in config.items()}
        cl_flags = {k: v for k, v in cl_flags.items() if v is not None}

        return cls(**(config_parsed | cl_flags))


default_config_dict = {
    'paths': {
        'backups': '/mnt/nasbackup/test/backups',
        'info': '/mnt/nasbackup/test/info.dat',
        'log': '/mnt/nasbackup/test/backup.log',
        'fogsettings': '/opt/fog/.fogsettings',
        'fog_snapins': '/opt/fog/snapins'
    },
    'mount': {
        'type': 'nfs',
        'point': '/mnt/nasbackup',
        'server_ip': '192.168.24.116',
        'server_dir': '/shares/backup'
    },
    'subpaths': {
        'fog_db': 'fog/db.sql',
        'fog_images': 'fog/images',
        'fog_snapins': 'fog/snapins',
        'fog_reports': 'fog/reports',
        'snipeit': 'snipeit',
    },
    'settings': {
        'backup_count': '16',
        'timezone': 'Europe/Brussels',
        'backup_interval': '7',
        'logging_min_filesize': '8388608',
        'log': 'True',
        'check_date': 'False'
    },
    'perform': {
        'snipeit': 'False',
        'fog_db': 'True',
        'fog_images': 'False',
        'fog_snapins': 'True',
        'fog_reports': 'True',
    },
    'default_info': {
        'last_datetime': '0001-01-01T00:00:00+01:00',
    },
    'snipe_it': {
        'api_endpoint': 'https://inventaris.digibankmechelen.be/api/v1/',
        'api_token': ('something')
    }
}


def get_config(cl_config: str | PathLike = '') -> ConfigParser:
    """
    Retrieves configuration settings for the backup.

    Args:
        cl_config: Path for the config file as entered in the command line.

    Returns:
        Configuration settings for the backup
    """
    config = ConfigParser()
    config.read_dict(default_config_dict)
    config.read([cl_config])
    return config
