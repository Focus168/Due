import os
import json
import datetime
from pathlib import Path
from . import utils

def get_data_path():
    """
    Determine the storage path for the data file.
    Uses ~/.config/ddl_dashboard/data.json
    """
    app_dir = Path.home() / ".config" / "due"
    app_dir.mkdir(parents=True, exist_ok=True)
    return str(app_dir / "data.json")

def get_arr_list(count=3):
    """
    Generate upcoming ARR-style monthly deadlines.
    (Moved from Controller to Model)
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
    # 这里虽然是 Model，但为了方便 CLI 反馈，保留 print，或者以后改成 return True
    print(f"Added: {name} -> {dt_str}")