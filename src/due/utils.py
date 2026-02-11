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
