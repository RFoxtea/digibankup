"""Mounts and unmounts drives used for the backup. (NOT IMPLEMENTED)"""

from os import PathLike
from pathlib import Path
from subprocess import check_call
from logging import getLogger

logger = getLogger(__name__)


def nfs_mount(server_ip: str, server_dir: str, point: Path):
    mount_address = server_ip + ":" + server_dir

    logger.info(f"Mounting NFS directory {mount_address} "
                f"at mountpoint {point}.")

    point.mkdir(exist_ok=True)

    check_call(['mount', server_ip + ":" + server_dir, point])


def nfs_umount(point: Path):
    point.mkdir(exist_ok=True)

    logger.info(f"Unmounting NFS mountpoint {point}.")

    check_call(['umount', point])


class NFS():
    @classmethod
    def from_config(cls, mount_config: dict[str, str]):
        return cls(
            server_ip=mount_config['server_ip'],
            server_dir=mount_config['server_dir'],
            point=mount_config['point']
        )

    def __init__(self, server_ip: str, server_dir: str, point: PathLike | str):
        self.server_ip: str = server_ip
        self.server_dir: str = server_dir
        self.point: Path = Path(point)

    def __enter__(self):
        nfs_mount(server_ip=self.server_ip,
                  server_dir=self.server_dir,
                  point=self.point)
        return self

    def __exit__(self, *e):
        nfs_umount(self.point)


def mount(mount_config: dict[str, str]):
    return MOUNT_TYPES[mount_config['type']].from_config(mount_config)


MOUNT_TYPES = {
    'nfs': NFS
}
