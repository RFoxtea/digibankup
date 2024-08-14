from pathlib import Path


def rmtree(f: Path):
    """
    Deletes directory, including subdirectories and files.

    Args:
        f: Path of directory to delete.
    """
    if f.is_file():
        f.unlink()
    else:
        for child in f.iterdir():
            rmtree(child)
        f.rmdir()


def touch_parents(f: Path):
    """
    Performs mkdir on parents and creates file.

    Args:
        f: Path of file to create.
    """
    f.parent.mkdir(parents=True, exist_ok=True)
    f.touch()


def format_filesize(filesize, suffix="B"):
    """Formats filesize into ISO 80000-13 units.

    Args:
        filesize: Filesize in bare units.
        suffix: ISO abbreviation of unit type."""
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(filesize) < 1024.0:
            return f"{filesize:3.1f} {unit}{suffix}"
        filesize /= 1024.0
    return f"{filesize:.1f} Yi{suffix}"


def str_to_bool(s: str):
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'ja', 'j', 'waar', 'w']
