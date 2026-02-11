#!/usr/bin/env python3
"""
DDL Countdown Dashboard

A terminal-based countdown dashboard for conference deadlines.
Data is stored in a JSON file and automatically reloaded when modified.
Supports adding new deadlines via CLI subcommands.
"""

import datetime
import os
import sys
from . import model
from . import view
from . import utils



def get_arr_list(count=3):
    """
    Generate upcoming ARR-style monthly deadlines.

    Each deadline is set to the 16th of the month at 19:59.
    Returns a list of (name, datetime) tuples.
    """
    now = datetime.datetime.now()
    result = []
    year, month = now.year, now.month

    while len(result) < count:
        ddl = datetime.datetime(year, month, 16, 19, 59, 0)
        if ddl > now:
            result.append((f"ARR {month:02d}", ddl))
        month += 1
        if month > 12:
            month = 1
            year += 1

    return result

def get_file_mtime(path):
    """
    Get last modification time of a file.
    """
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0

def cmd_list(data_path=None):
    """
    List all stored deadlines.
    """
    ddl_dict, estimated_set = model.load_deadlines(data_path)
    if not ddl_dict:
        print("No deadlines found. Use 'add' to create one.")
        return

    now = datetime.datetime.now()
    for name in sorted(ddl_dict, key=lambda n: ddl_dict[n]):
        ddl = ddl_dict[name]
        rem = ddl - now
        flag = " [E]" if name in estimated_set else ""
        status = (
            f"(remaining {rem.days}d)"
            if rem.total_seconds() > 0
            else "[expired]"
        )
        print(f"{name}: {ddl.strftime('%Y-%m-%d %H:%M')} {status}{flag}")


def main():
    """
    CLI entry point.
    """
    path = model.get_data_path()

    if len(sys.argv) >= 2:
        cmd = sys.argv[1].lower()
        if cmd == "add":
            if len(sys.argv) < 4:
                print('Usage: due add "NAME" "YYYY-MM-DD HH:MM" [--estimated]')
                sys.exit(1)
            model.add_deadline(
                sys.argv[2],
                sys.argv[3],
                estimated="--estimated" in sys.argv,
                data_path=path,
            )
            return

        if cmd == "list":
            cmd_list(data_path=path)
            return

    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target in ("add", "list"):
        target = None

    view.refresh_screen(target, data_path=path)


if __name__ == "__main__":
    main()