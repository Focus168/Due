import os
import json
from pathlib import Path
from . import utils

# Directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Default data file (project-local)
DEFAULT_DATA_PATH = os.path.join(SCRIPT_DIR, "deadlines.json")

# User-level fallback data file
USER_DATA_PATH = os.path.join(os.path.expanduser("~"), ".countdown_deadlines.json")

def load_deadlines(data_path=None):
    """
    Load deadlines from JSON file.

    Returns:
    - dict: {name -> datetime}
    - set: names marked as estimated
    """
    path = data_path or get_data_path()
    ddl_dict = {}
    estimated = set()

    if not os.path.exists(path):
        return ddl_dict, estimated

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conferences = data.get("conferences", {})
        for name, info in conferences.items():
            if isinstance(info, dict):
                ddl_dict[name] = utils.parse_datetime(info.get("datetime", ""))
                if info.get("estimated", False):
                    estimated.add(name)
            else:
                # Backward compatibility: datetime string only
                ddl_dict[name] = utils.parse_datetime(str(info))

    except (json.JSONDecodeError, ValueError):
        # Fail silently and return empty state
        pass

    return ddl_dict, estimated


def save_deadlines(ddl_dict, estimated_set, data_path=None):
    """
    Save deadlines to JSON file.
    """
    path = data_path or get_data_path()

    data = {
        "conferences": {
            name: {
                "datetime": d.strftime("%Y-%m-%d %H:%M"),
                "estimated": name in estimated_set,
            }
            for name, d in ddl_dict.items()
        }
    }

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_data_path():
    """
    Determine which data file to use.

    Priority:
    1. deadlines.json in script directory
    2. ~/.countdown_deadlines.json
    """
    if os.path.exists(DEFAULT_DATA_PATH):
        return DEFAULT_DATA_PATH
    return USER_DATA_PATH


def get_data_path():
    # Automatically get users' config catalog, such ~/.config/ddl_dashboard/data.json
    app_dir = Path.home() / ".config" / "ddl_dashboard"
    app_dir.mkdir(parents=True, exist_ok=True) # if the catalog does not exist, then create one
    return app_dir / "data.json"

def add_deadline(name, dt_str, estimated=False, data_path=None):
    """
    Add a new deadline entry.
    """
    path = data_path or get_data_path()
    ddl_dict, estimated_set = load_deadlines(path)

    ddl_dict[name] = utils.parse_datetime(dt_str)
    if estimated:
        estimated_set.add(name)

    save_deadlines(ddl_dict, estimated_set, path)
    print(f"Added: {name} -> {dt_str}")
