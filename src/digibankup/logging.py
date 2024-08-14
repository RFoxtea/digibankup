"""Configures logging when running Digibankup as a standalone utility."""
import logging
import logging.handlers
from configparser import ConfigParser


def configure_logging(config: ConfigParser):
    """
    Configures logging when running Digibankup as a standalone utility.

    Args:
        config: Configuration settings for the backup.
    """
    logger = logging.getLogger("digibankup")

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        '%Y-%m-%d %H:%M:%S')

    rotating_handler = logging.handlers.TimedRotatingFileHandler(
        filename=config['paths']['log'],
        when='W0',
        backupCount=int(config['settings']['backup_count'])
    )
    rotating_handler.setFormatter(formatter)
    logger.addHandler(rotating_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.setLevel(logging.INFO)
