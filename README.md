# Due Dashboard ⏳
> A minimalist, hacker-style deadline countdown CLI tool for researchers.
> Zero dependencies. Pure Python.

[中文版 (Chinese Version)](./README_zh-CN.md)

## Quick Start

Get up and running in seconds. No `pip install` required.

### 1. Installation
Clone the repository and navigate to the project directory:

```bash
git clone [https://github.com/your-username/due-dashboard.git](https://github.com/your-username/due-dashboard.git)
cd due-dashboard
```

### 2. Launch Dashboard (Interactive Mode)

Run the controller module to start the TUI (Text User Interface):

```bash
python3 -m src.due.controller
```
You will see the live countdown dashboard. Press ENTER to pause and access the menu.

## Usage
**Command Line Arguments**

You can also use one-off commands to manage tasks without entering the dashboard.

**Add a new deadline:**
```bash
# Format: add "Name" "YYYY-MM-DD HH:MM"
python3 -m src.due.controller add "ICLR 2026" "2025-10-01 23:59"
```

**Add an estimated deadline (marked with [E]):**
```bash
python3 -m src.due.controller add "NeurIPS" "2025-05-22 05:00" --estimated
```

**List all tasks (Static view):**
```bash
python3 -m src.due.controller list
```

## Interactive Controls
While the dashboard is running:

- ENTER: Pause and open command menu.

- `show "Name"`: Focus Mode (Concentrate on a single task).

- `ls`: Return to full dashboard.

-  `Ctrl+C`: Exit.

## Requirements & Environment
Designed to be lightweight and portable.

- OS: macOS / Linux / Windows

- Python: Python 3.6+

- Dependencies: None (Uses standard library only: os, sys, json, datetime, shlex)

## Data Storage
Your data is safely stored in your local user configuration directory (XDG Standard):

- macOS/Linux: ~/.config/due/data.json

- Windows: C:\Users\You\.config\due\data.json