#!/usr/bin/env python3
"""Main entry point for the DDL Countdown Dashboard.

This module orchestrates the interaction between the data model and the
TUI view. It handles CLI arguments for one-off commands and manages
the lifecycle of the interactive dashboard.
"""

import sys
from . import model
from . import view

def main():
    """Parses CLI arguments and launches either the dashboard or a subcommand."""
    path = model.get_data_path()

    def get_combined_data():
        """Fetches and merges stored deadlines with dynamically generated ones.
        
        Returns:
            tuple: A dictionary of all deadlines and a set of estimated ones.
        """
        # Load persistent data from the local JSON file.
        base_ddls, estimated = model.load_deadlines(path)
        
        # Generate dynamic ARR (Annual Rolling Review) deadlines.
        arr_list = model.get_arr_list(3)
        
        # Merge datasets into a single unified view.
        all_ddls = base_ddls.copy()
        for name, ddl in arr_list:
            all_ddls[name] = ddl
            
        return all_ddls, estimated
 
    def handle_add_from_view(name, time_str, is_est):
        """Callback to allow the View to trigger data persistence in the Model."""
        model.add_deadline(name, time_str, is_est, path)

    # Process CLI subcommands (one-off tasks).
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
            # Static list mode for a quick snapshot of all tasks.
            data, estimated = get_combined_data()
            view.render_list(data, estimated)
            return

    # Handle Target-specific focus or general Dashboard Mode.
    target = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ["add", "list"] else None
    if target in ("add", "list"):
        target = None

    # Inject data retrieval logic into the View to enable real-time updates.
    view.refresh_screen(target, get_combined_data, handle_add_from_view)


if __name__ == "__main__":
    main()