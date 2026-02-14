import sys
import time
import datetime
import subprocess
from . import utils

def render_list(ddl_dict, estimated_set):
    """
    Render static list. Now accepts RAW DATA, not path.
    """
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


def refresh_screen(target_name, data_fetcher_func):
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

    # ❌ 不再自己算 mtime，完全依赖外部传入的函数
    first_run = True

    def clear_screen():
        if sys.stdout.isatty():
            subprocess.run(["clear"])
        else:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()

    try:
        sys.stdout.write(HIDE)

        while True:
            now = datetime.datetime.now()

            # ✅ 关键点：调用传入的函数来获取数据！
            # View 不知道这个数据怎么来的，它只管要。
            all_ddls, estimated_set = data_fetcher_func()

            if target_name:
                # Target Mode Logic
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

                sys.stdout.write(f"\r{color}Time until {name}: {timer}{RESET}\033[K")
                sys.stdout.flush()

            else:
                # Dashboard Mode Logic
                active = []
                for name, ddl in all_ddls.items():
                    rem = ddl - now
                    if rem.total_seconds() > 0:
                        active.append((name, ddl, rem))

                active.sort(key=lambda x: x[2])

                clear_screen()
                print(f"{BOLD}{'CONFERENCE':<10} | {'BEIJING TIME':^20} | {'REMAINING':<18}{RESET}", flush=True)
                print("-" * 55, flush=True)

                for name, ddl, rem in active:
                    color = RED if rem.days < 2 else ORANGE if rem.days < 14 else GREEN
                    mark = "E" if name in estimated_set else "C"
                    timer = f"{rem.days:02d}d {rem.seconds//3600:02d}h {(rem.seconds%3600)//60:02d}m {rem.seconds%60:02d}s"
                    print(f"{color}{name:<10}{RESET} | ({mark}) {ddl.strftime('%Y-%m-%d %H:%M'):^15} | {color}{timer}{RESET}\033[K", flush=True)

                hint = "All deadlines passed."
                if active:
                     if active[0][2].days < 2: hint = f"{active[0][0]} Final Call!"
                     elif active[0][2].days < 14: hint = f"Next urgent: {active[0][0]} in {active[0][2].days}d"
                     else: hint = f"Next: {active[0][0]}"

                print(f"\n{BOLD}Now:{RESET} {now.strftime('%Y-%m-%d %H:%M:%S')} | {RED}{hint}{RESET}\033[K", flush=True)
                print(f"{DIM}To add: due add \"NAME\" \"YYYY-MM-DD HH:MM\" [--estimated]{RESET}\033[K", flush=True)

            first_run = False
            time.sleep(1)

    except KeyboardInterrupt:
        sys.stdout.write(SHOW)
        print("\nDashboard closed.")