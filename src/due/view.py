"""View layer for the DDL Countdown Dashboard.

The View layer does not directly reference the Model. It solely accepts data dictionaries and callback functions to maintain a decoupled architecture.
"""
import os
import sys
import time
import datetime
import subprocess
import select
import shlex
import random
from pathlib import Path
from typing import Callable, Optional, Tuple, Dict, Set

def render_list(ddl_dict: Dict[str, datetime.datetime], estimated_set: Set[str]) -> None:
    """Renders a static list of all deadlines to stdout.

    Args:
        ddl_dict: A dictionary mapping deadline names to datetime objects.
        estimated_set: A set of names that are marked as estimated.
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


def refresh_screen(
    initial_target_name: Optional[str], 
    data_fetcher_func: Callable[[], Tuple[Dict, Set]], 
    add_handler_func: Optional[Callable[[str, str, bool], None]] = None
) -> None:
    """Starts the main TUI (Text User Interface) loop with auto-refresh.

    Displays a dynamic dashboard of deadlines, sorted by urgency. The loop 
    refreshes every second and listens for user input to pause and execute 
    commands (e.g., adding new tasks).

    Args:
        initial_target_name: A substring to filter and focus on a specific
            deadline. If None, the dashboard shows all deadlines.
        data_fetcher_func: A callback function returning a tuple of
            `(ddl_dict, estimated_set)`, allowing the view to pull fresh data
            without backend coupling.
        add_handler_func: An optional callback function with signature
            `(name, time_str, is_estimated)` to handle 'add' commands.

    Raises:
        KeyboardInterrupt: If the user presses Ctrl+C to exit.
    """

    # ANSI Color Codes
    RED = "\033[38;5;196m"
    ORANGE = "\033[38;5;214m"
    GREEN = "\033[38;5;28m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m\033[38;5;240m"
    HIDE = "\033[?25l" 
    SHOW = "\033[?25h" 

    first_run = True
    current_target = initial_target_name

    def clear_screen():
        """Clears the terminal screen effectively across platforms."""
        if sys.stdout.isatty():
            subprocess.run(["clear"])
        else:
            sys.stdout.write("\033[2J\033[H") 
            sys.stdout.flush()

    try: 
        sys.stdout.write(HIDE)
        clear_screen()
        while True:
            # --- 1. Non-blocking Input Listener ---
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()
                if line: 
                    sys.stdout.write(SHOW) 
                    print(f"{BOLD}>> PAUSED. Enter command (add/q/c):{RESET}")
                    print(f"{DIM} Format: ls Show ALL deadlines (Dashboard){RESET}")
                    print(f"{DIM} Format: show \"Name\" Focus on ONE deadline{RESET}")
                    print(f"{DIM} Format: add \"Task Name\" \"YYYY-MM-DD HH:MM\" [--est]{RESET}")
                    print(f"{DIM} Format: q (to quit){RESET}")
                    
                    while True:
                        try:
                            raw_input = input(f"{BOLD}> {RESET}").strip()

                            # Resume operation on empty input
                            if not raw_input:
                                print("Resuming...")
                                break
                                
                            parts = shlex.split(raw_input)
                            cmd = parts[0].lower()

                            if cmd == 'q':
                                raise KeyboardInterrupt
                            
                            elif cmd == 'ls':
                                # --- Switch to Dashboard Mode ---
                                current_target = None
                                print(f"{GREEN}Switched to Dashboard view.{RESET}")
                                time.sleep(0.1)
                                break
                            
                            elif cmd in ('show', 'focus'):
                                # --- Target Mode rendering loop ---
                                if len(parts) < 2:
                                    print(f"{RED}Error: Please specify a name. e.g., show 'ICLR 27'{RESET}")
                                    continue

                                target_candidate = parts[1]
                                key = target_candidate.upper()
                                matches = [(n, d) for n, d in all_ddls.items() if key in n.upper()]

                                if not matches:
                                    print(f"{RED}Target '{target_candidate}' not found.{RESET}")
                                    continue
                                
                                name, ddl = matches[0]
                                clear_screen()
                                print(f"{GREEN}Focusing on '{name}'...{RESET}")
                                
                                sys.stdout.write(HIDE)

                                while True:
                                    # 1. Listen for exit signals (non-blocking)
                                    if sys.stdin in select.select([sys.stdin], [], [], 1.0)[0]:
                                        _ = sys.stdin.readline() 
                                        print(f"\n{GREEN}Returning to main menu...{RESET}")
                                        time.sleep(0.5)
                                        clear_screen()
                                        print(f"\n{BOLD}>> PAUSED. Enter command (add/q/c):{RESET}")
                                        print(f"{DIM} Format: ls Show ALL deadlines (Dashboard){RESET}")
                                        print(f"{DIM} Format: show \"Name\" Focus on ONE deadline{RESET}")
                                        print(f"{DIM} Format: add \"Task Name\" \"YYYY-MM-DD HH:MM\" [--est]{RESET}")
                                        print(f"{DIM} Format: q (to quit){RESET}")
                                        break 

                                    # 2. Calculate remaining time
                                    now = datetime.datetime.now()
                                    remaining = ddl - now
                                    
                                    if remaining.total_seconds() <= 0:
                                        print(f"\r{RED}{name} TIME'S UP!   {RESET}")
                                        time.sleep(0.5)
                                        clear_screen()
                                        break

                                    days = remaining.days
                                    color = RED if days < 2 else ORANGE if days < 14 else GREEN
                                    timer = (
                                        f"{days:02d}d "
                                        f"{remaining.seconds//3600:02d}h "
                                        f"{(remaining.seconds%3600)//60:02d}m "
                                        f"{remaining.seconds%60:02d}s"
                                    )

                                    # 3. Render countdown and sticky footer prompt
                                    sys.stdout.write(f"\r{color}Time until {name}: {timer}{RESET}\033[K")
                                    sys.stdout.write(f"\n{DIM}[Press ENTER to Return Main Menu][Ctrl+C to quit]{RESET}\033[K\033[A")
                                    sys.stdout.flush()

                            elif cmd == 'add' and add_handler_func:
                                if len(parts) < 3:
                                    print(f"{RED}Error: Missing arguments.{RESET}")
                                    print("Usage: add \"Name\" \"Time\" [--est]")
                                else:
                                    name = parts[1]
                                    time_str = parts[2]
                                    is_est = "--est" in parts or "--estimated" in parts
                                    
                                    try:
                                        add_handler_func(name, time_str, is_est)
                                        print(f"{GREEN}✓ Added '{name}' successfully.{RESET}")
                                    except Exception as e:
                                        print(f"{RED}Failed to add: {e}{RESET}")
                                        
                            else:
                                print(f"{ORANGE}Unknown command or bad format.{RESET}")

                        except ValueError as e:
                            print(f"{RED}Parsing Error: {e} (Did you forget a closing quote?){RESET}")
                    
                time.sleep(1) 
                sys.stdout.write(HIDE) 

            # --- 2. Data Fetching & Dashboard Rendering ---
            now = datetime.datetime.now()
            all_ddls, estimated_set = data_fetcher_func()

            if current_target:
                # Target Mode
                key = current_target.upper()
                matches = [(n, d) for n, d in all_ddls.items() if key in n.upper()]
                if not matches:
                    print(f"\n{RED}Target '{current_target}' not found. Switching to Dashboard...{RESET}")
                    current_target = None
                    time.sleep(0.5)
                    continue

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

                sys.stdout.write(f"\r{color}Time until {name}: {timer}{RESET}\033[K")
                sys.stdout.flush()

            else:
                # Dashboard Mode
                active = []
                for name, ddl in all_ddls.items():
                    rem = ddl - now
                    if rem.total_seconds() > 0:
                        active.append((name, ddl, rem))

                active.sort(key=lambda x: x[2])

                # Dynamically calculate column width
                if active:
                    max_name_len = max(len(x[0]) for x in active)
                    col_width = max(max_name_len, 12) 
                else:
                    col_width = 12
                
                clear_screen()
                print(f"\n{BOLD}{'DEADLINES':^{col_width}} | {'BEIJING TIME':^20} | {'REMAINING':^18}{RESET}", flush=True)
                print("-" * (col_width + 43), flush=True)

                for name, ddl, rem in active:
                    color = RED if rem.days < 2 else ORANGE if rem.days < 14 else GREEN
                    mark = "E" if name in estimated_set else "C"
                    timer = f"{rem.days:02d}d {rem.seconds//3600:02d}h {(rem.seconds%3600)//60:02d}m {rem.seconds%60:02d}s"
                    print(f"{color}{name:>{col_width}}{RESET} | ({mark}) {ddl.strftime('%Y-%m-%d %H:%M'):^15} | {color}{timer}{RESET}\033[K", flush=True)

                hint = "No upcoming deadlines."
                if active:
                     if active[0][2].days < 2: hint = f"{active[0][0]} Final Call!"
                     elif active[0][2].days < 14: hint = f"Next urgent: {active[0][0]} in {active[0][2].days}d"
                     else: hint = f"Next: {active[0][0]}"

                print(f"\n{BOLD}Now:{RESET} {now.strftime('%Y-%m-%d %H:%M:%S')} | {RED}{hint}{RESET}\033[K", flush=True)
                print(f"{DIM}[Press ENTER to pause and add task] [Ctrl+C to quit]{RESET}\033[K", flush=True)

            first_run = False
            time.sleep(1)

    except KeyboardInterrupt:
        sys.stdout.write(SHOW)

        # Determine data file path for exit metadata
        current_dir = os.getcwd()
        data_path = Path.home() / ".config" / "due" / "data.json"

        quotes = [
            "Deadlines are the ultimate inspiration. — Mark Twain",
            "Done is better than perfect. Keep moving.",
            "The only way to do great work is to love what you do.",
            "Time flows, but your code remains.",
            "Focus on the step in front of you, not the whole staircase.",
            "Rest, then conquer.",
            "See you at the top.", 
            "Every second you invest now pays dividends later.",
            "Simplicity is the ultimate sophistication.",
            "Focus is about saying no.",
            "Time flows, but your code remains."
        ]
        quote = random.choice(quotes)
        
        # Render exit screen
        CYAN = "\033[38;5;51m"
        GRAY = "\033[38;5;240m"
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        print(f"\n\n{RED}[!] INTERRUPT SIGNAL RECEIVED{RESET}")
        print(f"{GRAY}{timestamp} • Dashboard halted.{RESET}")
        print(f"{GRAY}>> Working Directory :{RESET} {current_dir}")
        print(f"{GRAY}>> Storage Location  :{RESET} {data_path}")
        print(f"\n   {CYAN}\"{quote}\"{RESET}\n")
        
        print(f"{DIM}[SESSION TERMINATED]{RESET}")
        sys.exit(0)