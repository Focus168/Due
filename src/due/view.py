import sys
import os
import time
import datetime
import subprocess
from . import model

def refresh_screen(target_name=None, data_path=None):
    """
    Main TUI loop.

    Displays:
    - All active deadlines (dashboard mode)
    - A single matching deadline (target mode)
    """
    RED = "\033[38;5;196m"
    ORANGE = "\033[38;5;214m"
    GREEN = "\033[38;5;28m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m\033[38;5;240m"  # small gray text for hints
    HIDE = "\033[?25l"
    SHOW = "\033[?25h"

    path = data_path or model.get_data_path()
    last_mtime = model.get_file_mtime(path)
    first_run = True

    def clear_screen():
        """清屏并光标回左上角：优先用系统 clear（输出到当前终端），否则用 ANSI。"""
        if sys.stdout.isatty():
            subprocess.run(["clear"])
        else:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()

    try:
        sys.stdout.write(HIDE)

        while True:
            now = datetime.datetime.now()

            base_ddls, estimated_set = model.load_deadlines(path)
            all_ddls = base_ddls.copy()

            # Inject ARR deadlines
            for name, ddl in model.get_arr_list(3):
                all_ddls[name] = ddl

            # Target (single deadline) mode
            if target_name:
                key = target_name.upper()
                matches = [(n, d) for n, d in all_ddls.items() if key in n.upper()]
                if not matches:
                    print(f"Unknown target '{target_name}'")
                    break

                name, ddl = matches[0]
                remaining = ddl - now
                if remaining.total_seconds() <= 0:
                    print(f"{RED}{name} TIME'S UP!{RESET}")
                    break

                days = remaining.days
                color = RED if days < 2 else ORANGE if days < 14 else GREEN
                timer = (
                    f"{days:02d}d "
                    f"{remaining.seconds//3600:02d}h "
                    f"{(remaining.seconds%3600)//60:02d}m "
                    f"{remaining.seconds%60:02d}s"
                )

                if first_run:
                    print(f"{GREEN}Countdown to {name} started!{RESET}")

                sys.stdout.write(
                    f"\r{color}Time until {name}: {timer}{RESET}\033[K"
                )
                sys.stdout.flush()

            # Dashboard mode
            else:
                active = []
                for name, ddl in all_ddls.items():
                    rem = ddl - now
                    if rem.total_seconds() > 0:
                        active.append((name, ddl, rem))

                active.sort(key=lambda x: x[2])

                clear_screen()

                print(
                    f"{BOLD}"
                    f"{'CONFERENCE':<10} | {'BEIJING TIME':^20} | {'REMAINING':<18}"
                    f"{RESET}",
                    flush=True,
                )
                print("-" * 55, flush=True)

                for name, ddl, rem in active:
                    color = RED if rem.days < 2 else ORANGE if rem.days < 14 else GREEN
                    mark = "E" if name in estimated_set else "C"
                    timer = (
                        f"{rem.days:02d}d "
                        f"{rem.seconds//3600:02d}h "
                        f"{(rem.seconds%3600)//60:02d}m "
                        f"{rem.seconds%60:02d}s"
                    )
                    print(
                        f"{color}{name:<10}{RESET} | "
                        f"({mark}) {ddl.strftime('%Y-%m-%d %H:%M'):^15} | "
                        f"{color}{timer}{RESET}\033[K",
                        flush=True,
                    )

                hint = (
                    f"{active[0][0]} Final Call!" if active and active[0][2].days < 2
                    else f"Next urgent: {active[0][0]} in {active[0][2].days}d"
                    if active and active[0][2].days < 14
                    else f"Next: {active[0][0]}" if active
                    else "All deadlines passed."
                )

                print(
                    f"\n{BOLD}Now:{RESET} {now.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"{RED}{hint}{RESET}\033[K",
                    flush=True,
                )
                print(
                    f"{DIM}To add a deadline: due add \"NAME\" \"YYYY-MM-DD HH:MM\" [--estimated]{RESET}\033[K",
                    flush=True,
                )

            first_run = False
            time.sleep(1)

    except KeyboardInterrupt:
        sys.stdout.write(SHOW)
        print("\nDashboard closed.")

