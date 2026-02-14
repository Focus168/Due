#!/usr/bin/env python3
"""
DDL Countdown Dashboard

A terminal-based countdown dashboard for conference deadlines.
Data is stored in a JSON file and automatically reloaded when modified.
Supports adding new deadlines via CLI subcommands.
"""

import sys
from . import model
from . import view

def main():
    """
    CLI entry point.
    """
    path = model.get_data_path()

    # ---------------------------------------------------------
    # Define how to get al the datat
    # Controller 负责把“存储的数据”和“生成的ARR数据”拼在一起
    # ---------------------------------------------------------
    def get_combined_data():
        # 1. 从文件加载基础数据
        base_ddls, estimated = model.load_deadlines(path)
        
        # 2. 生成 ARR 数据
        arr_list = model.get_arr_list(3)
        
        # 3. 合并 (Python 3.9+ 语法: base_ddls | dict(arr_list) 也可以)
        all_ddls = base_ddls.copy()
        for name, ddl in arr_list:
            all_ddls[name] = ddl
            
        return all_ddls, estimated
    # ---------------------------------------------------------

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
            # List 模式：只需要获取一次数据传给 View
            data, estimated = get_combined_data()
            view.render_list(data, estimated)
            return

    # Dashboard 模式
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target in ("add", "list"):
        target = None

    # 把“获取数据的函数”传给 View，而不是传数据本身
    # 这样 View 就可以在循环里不断调用它来刷新数据
    view.refresh_screen(target, get_combined_data)


if __name__ == "__main__":
    main()