架构设计文档 (Architecture Design Doc)
项目名称: Due (DDL Dashboard) 状态: 正在开发 (In Development) 作者: Focus168 最后更新: 2026-02-18

1. 系统概览 (System Overview)
1.1 目标 (Goal)

构建一个基于终端（Terminal-based）的轻量级倒计时看板工具。该工具旨在帮助用户以极简的方式管理会议、作业或项目截止日期（DDL），并通过动态刷新的视觉效果提供紧迫感。

1.2 设计哲学 (Design Philosophy)

极简主义 (Minimalism): 仅提供核心的 CRUD（增删改查）功能，无多余的 GUI 依赖。

本地优先 (Local-First): 数据以 JSON 格式存储在用户本地，不依赖云端服务，确保隐私与速度。

视觉驱动 (Visual Urgency): 通过终端 ANSI 转义序列实现高频刷新，直观呈现时间流逝。

零依赖 (Zero-Dependency): 核心功能仅依赖 Python 标准库，确保极高的可移植性和安装便捷性。

2. 目录结构 (Directory Structure)
本项目遵循现代 Python 包管理的标准结构（src-layout），以避免导入混乱并支持打包发布。

Plaintext
ddl-dashboard/
├── pyproject.toml          # [核心] 项目配置、依赖管理、CLI 入口点定义
├── README.md               # 用户说明书
├── ARCHITECTURE.md         # 架构设计文档
├── .gitignore              # Git 忽略规则
├── src/
│   └── due/                # 核心源码包
│       ├── __init__.py     # 包标识
│       ├── main.py         # Controller: 程序入口与路由分发
│       ├── model.py        # Model: 数据持久化与业务逻辑
│       ├── view.py         # View: TUI 渲染与屏幕刷新
│       └── utils.py        # Utils: 通用工具函数 (如时间解析)
└── tests/                  # 测试套件 (预留)

3. 架构设计 (Architecture Design)
系统采用经典的 MVC (Model-View-Controller) 架构模式，以实现关注点分离（Separation of Concerns）。

3.1 Controller (main.py)

职责: 系统的“大脑”。负责程序启动、参数解析（Argument Parsing）和指令路由（Routing）。

逻辑: 接收用户输入的 CLI 指令，调用 Model 层处理数据，并选择合适的 View 进行展示。

依赖: 引用 model 和 view。

3.2 Model (model.py)

职责: 系统的“仓库”。负责数据的加载（Load）、保存（Save）、校验（Validation）和结构定义。

逻辑: * 处理 JSON 文件的读写。

管理数据存储路径（遵循 XDG 标准或用户主目录）。

实现数据的 CRUD 操作原子逻辑。

依赖: 仅依赖 Python 标准库 (json, os, datetime)，不引用 Controller 或 View。

3.3 View (view.py)

职责: 系统的“画师”。负责终端界面的绘制和用户交互反馈。

逻辑:

定义 ANSI 颜色代码。

实现屏幕刷新循环（Dashboard Loop）。

格式化输出列表和倒计时信息。

依赖: 仅依赖 Python 标准库，不引用 Controller。

4. 路由与指令设计 (Routing & Commands)

本系统采用混合路由策略：支持 CLI 参数启动（一次性执行）与 REPL 交互模式（运行时指令）。

4.1 CLI 启动模式 (Entry Points)

通过 python -m src.due.controller [args] 触发。

指令 (Command)	参数 (Arguments)	描述 (Description)
(Default)	(None)	启动交互式动态倒计时看板 (Dashboard TUI)。
add	name time [--est]	快速添加任务并退出 (Headless mode)。
list	(None)	打印当前所有任务的静态列表并退出。
[target]	name_keyword	启动看板并直接聚焦 (Focus) 于特定任务。
4.2 交互式指令 (Interactive REPL)

在看板运行中，通过键盘中断进入暂停状态，支持以下运行时指令：

指令 (Command)	参数 (Arguments)	处理器 (Handler)	功能描述
ls	(None)	view.switch_to_dashboard	切换视图至全局看板模式。
show / focus	name	view.switch_to_target	切换视图至单任务专注模式。
add	name time [--est]	controller.handle_add	运行时添加任务，添加后自动恢复刷新。
del / rm	name	controller.handle_delete	(Pending) 根据名称删除指定任务。
q / quit	(None)	sys.exit	安全退出程序。

5. 数据流与存储 (Data Flow & Storage)

5.1 数据持久化 (Persistence)

系统遵循 XDG Base Directory 标准，实现用户数据与程序代码的物理隔离。

存储格式: 标准 JSON ({"conferences": {...}})。

存储路径: ~/.config/due/data.json (macOS/Linux)。

初始化策略 (Copy-on-Write / Templating):

程序启动时检查用户配置目录。

若 data.json 不存在，读取源码包内的 default_deadlines.json (Factory Defaults)。

将默认模板复制至用户目录，完成初始化。

后续所有读写操作仅针对用户目录下的副本，确保程序升级不覆盖用户数据。

5.2 数据流向 (Data Flow)

以 "Interactive Delete" (交互式删除) 为例：

View Layer: 用户在 TUI 输入 del "ICML"。view.py 解析输入，调用注入的 delete_handler 回调函数。

Controller Layer: controller.py 接收请求，调用 model.delete_deadline("ICML")。

Model Layer:

加载 ~/.config/due/data.json 至内存。

执行字典键值移除操作 (Key Removal)。

调用 json.dump 原子性回写文件。

Feedback: View 层捕获执行结果，刷新屏幕显示更新后的任务列表。

6. 工程约束与决策 (Constraints & Decisions)

6.1 零依赖原则 (Zero-Dependency)

决策: 仅使用 Python 标准库 (os, sys, json, datetime, shlex, select)。

理由: 确保极高的可移植性 (Portability) 和安装简便性，无需 pip install 即可在任何标准 Python 3 环境运行。

6.2 健壮性设计 (Robustness)

非阻塞 I/O: 使用 select.select 实现键盘监听，确保在等待用户输入时不会阻塞主线程的倒计时刷新（UI Render Loop）。

参数解析: 使用 shlex.split 处理带引号的复杂字符串参数，确保 add "Task Name" ... 被正确解析为单个参数。

容错机制:

遇到损坏的 JSON 文件时，自动降级为空状态，防止 Crash。

用户输入错误格式日期时，REPL 保持在循环中提示重试，而非直接抛出异常退出。

7. 未来规划 (Future Work)
添加新路由: 支持 del / rm 命令，允许用户通过 CLI 或 REPL 删除指定任务。

高级数据管理: 实现 undo (撤销) 功能，防止误删操作。

视图增强: 增加按时间排序 (Sort by Date) 或按紧急程度排序 (Sort by Urgency) 的切换选项。

打包分发: 提供 setup.py 或 pyproject.toml，支持通过 pipx install due-dashboard 全局安装。