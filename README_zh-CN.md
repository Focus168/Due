Due: DDL Countdown Dashboard
极简、硬核、终端原生。 A terminal-based countdown dashboard for deadline fighters.

设计哲学 (Design Philosophy)
What: 这是什么？ Due 是一个运行在终端（Terminal）里的倒计时看板工具。它摒弃了复杂的 GUI，只用最纯粹的字符和颜色，为您展示距离 Deadline 还有多少时间。

Why: 为什么要做？ 市面上的时间管理工具过于复杂且臃肿。

我要紧迫感：我希望看到秒数在跳动，看到颜色随着时间流逝从绿变红，直观感受时间流逝（Time Flux）。

我要极简：无需注册账号，无需云端同步。文件即数据，本地即一切。

我要专注：作为开发者，我希望在不离开终端的情况下掌握时间进度。

How: 怎么用？ 克隆仓库，一行命令启动。它会自动读取配置，当您在后台修改数据文件时，界面会实时热重载（Hot-Reload）。

功能特性 (Features)
实时大盘 (Dashboard)：按剩余时间自动排序，动态刷新，支持三级颜色预警。

专注模式 (Target Mode)：使用 due icml 仅追踪特定目标，屏蔽其他干扰。

本地优先 (Local-First)：数据存储在用户目录的 JSON 文件中，隐私安全，易于备份。

自动热重载：手动编辑 JSON 数据后，看板会自动更新，无需重启程序。

零依赖 (Zero-Dependency)：完全基于 Python 标准库开发，无需安装任何第三方包。

安装与运行 (Installation)
本项目采用标准的 Python src-layout 结构，推荐以下两种方式运行：

方式一：直接运行源码 (推荐)

Bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/ddl-dashboard.git
cd ddl-dashboard

# 2. 运行主程序 (注意：需在根目录下作为模块运行)
python3 -m src.due.main
方式二：设置别名 (可选)

为了像原生命令一样便捷使用，可以将以下 alias 加入您的 .bashrc 或 .zshrc：

Bash
alias due="python3 /path/to/ddl-dashboard/src/due/main.py"
设置完成后，即可直接在终端输入 due 使用。

使用指南 (Usage)
本项目支持标准的 CRUD 操作：

Bash
# 1. 进入倒计时大盘 (默认模式)
python3 -m src.due.main

# 2. 添加一个新的 DDL
# 格式: due add "名称" "YYYY-MM-DD HH:MM"
python3 -m src.due.main add "ACL 2026" "2026-02-15 19:59"

# 3. 添加一个估算日期的 DDL (标记为 Estimated)
python3 -m src.due.main add "CVPR" "2026-03-15 23:59" --estimated

# 4. 列出所有任务 (静态列表)
python3 -m src.due.main list

# 5. 单目标专注模式 (只看包含 'icml' 的任务)
python3 -m src.due.main icml
数据存储 (Data Storage)
您的数据不会存储在代码目录，而是存储在用户配置目录中，遵循 XDG 标准：

Linux/Mac: ~/.config/due/deadlines.json

Windows: 用户主目录下的配置文件夹

JSON 数据格式示例： 支持手动编辑该 JSON 文件进行批量管理：

JSON
{
  "conferences": {
    "ICML": {
      "datetime": "2026-01-29 19:59",
      "estimated": false
    },
    "NeurIPS": {
      "datetime": "2026-05-20 19:59",
      "estimated": true
    }
  }
}
颜色预警说明：

红色 (Red)：剩余时间 < 2 天 (Final Call)

橙色 (Orange)：2 天 < 剩余时间 < 14 天 (Urgent)

绿色 (Green)：剩余时间 > 14 天 (Safe)

贡献 (Contributing)
这是一个处于敏捷开发阶段的 MVP (Minimum Viable Product) 项目。

目前代码结构遵循 MVC 架构：

src/due/model.py: 数据处理与持久化

src/due/view.py: 终端渲染与刷新

src/due/main.py: 路由分发与控制

欢迎提交 Issue 或 Pull Request。

License
MIT License