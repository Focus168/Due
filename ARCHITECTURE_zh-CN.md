架构设计文档 (Architecture Design Doc)
项目名称: Due (DDL Dashboard) 状态: 正在开发 (In Development) 作者: [Your Name] 最后更新: 2026-02-12

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

Shutterstock

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
当前版本使用 Python 原生 sys.argv 进行参数解析。系统支持标准的 CRUD 操作。

命令模式: due <command> [arguments]

操作 (CRUD)	指令 (Command)	参数 (Arguments)	处理函数 (Handler)	描述
Read (View)	(无)	(无)	view.render_dashboard()	进入动态倒计时看板模式 (TUI)。
Create	add	name, date	model.add_deadline()	添加一个新的 DDL 任务。
Read (List)	list	(无)	view.render_list()	静态打印所有任务列表并退出。
Update	edit	name, new_date	model.update_deadline()	修改现有任务的日期。
Delete	remove	name	model.delete_deadline()	根据名称删除任务。
5. 数据流与存储 (Data Flow & Storage)
5.1 数据存储

格式: JSON。

路径: 优先查找用户配置目录（如 ~/.config/due/data.json），如果不存在则自动创建。

初始化策略 (Copy-on-Write): 程序初次运行时，若未检测到用户数据，将自动从源码包中复制一份包含示例数据（如 ARR Deadlines）的模板文件到用户目录。

5.2 数据流向示例 (以 "Add Task" 为例)

User: 输入 due add "NeurIPS" "2026-05-15"。

Controller (main.py): * 解析 sys.argv，识别动词 add。

提取参数 "NeurIPS" 和 "2026-05-15"。

调用 utils.parse_datetime 验证格式。

Model (model.py):

读取 data.json 到内存字典。

将新任务追加到字典中。

将更新后的字典序列化回写至 data.json。

View (view.py):

Controller 调用 View 输出成功提示：“Successfully added NeurIPS”。

6. 工程约束与决策 (Constraints & Decisions)
6.1 依赖管理

决策: 坚持 Zero-Dependency（零第三方依赖）。

理由: 为了让该工具极其容易安装（Copy-paste 或简单的 pip install），不给用户的 Python 环境增加负担。

6.2 错误处理 (Error Handling)

策略: Fail Fast, Print Friendly。

实现: * 对于用户输入错误（如日期格式不对），捕获异常并打印清晰的提示信息（"Invalid date format, please use YYYY-MM-DD"），而不是打印 Python Traceback。

对于数据损坏（JSON Decode Error），自动备份坏文件并初始化新文件，防止程序崩溃。

6.3 国际化 (i18n)

当前状态: 代码注释与 CLI 输出目前以英文为主。

文档: 架构文档提供中英双语版本，以支持更广泛的开发者社区。

7. 未来规划 (Future Work)
交互增强: 在 TUI 模式下引入 keyboard 监听，支持按键直接删除/添加任务（无需退出看板）。

参数解析升级: 引入 argparse 以支持 --help 和更复杂的参数选项（如 --urgent 标记）。

测试覆盖: 为核心的时间计算逻辑（utils.py）和数据读写逻辑（model.py）添加单元测试。