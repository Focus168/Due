import os
import datetime

def parse_datetime(s):
    """
    Parse datetime string.

    Supported formats:
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DD HH:MM:SS
    """
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {s}")

def get_file_mtime(path):
    """
    Get last modification time of a file.
    """
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0