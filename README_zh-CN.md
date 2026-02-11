“项目巧思”、“主打简洁”、“设计哲学”都放在这里:

What: 这是什么？（终端倒计时工具）

Why: 为什么要做？（市面上的太复杂，我就要一个能闪烁、有紧迫感、极简的工具）

How: 怎么用？（安装、快捷键说明）

# DDL Countdown Dashboard

会议/项目截止日期倒计时小工具，可在终端实时显示 DDL 剩余时间。

## 功能

- **实时大盘**：按剩余时间排序展示所有未过期 DDL
- **单目标模式**：`countdown icml` 只追踪指定会议
- **独立数据存储**：DDL 存储在 `deadlines.json`，与代码分离
- **自动重载**：手动编辑 JSON 后，仪表盘会自动检测并更新
- **初始化与扩展**：`add` 子命令添加新 DDL，或直接编辑 JSON

## 安装

```bash
# 克隆后直接运行
git clone https://github.com/YOUR_USERNAME/countdown.git
cd countdown
python countdown.py
```

或通过 pip（若已发布）：

```bash
pip install countdown-dashboard
countdown
```

## 使用

```bash
# 全员大盘模式（默认）
python countdown.py

# 单目标模式
python countdown.py icml

# 添加新 DDL
python countdown.py add "ACL 2026" "2026-02-15 19:59"
python countdown.py add "CVPR" "2026-03-15 23:59" --estimated

# 列出当前所有 DDL
python countdown.py list
```

## 数据文件

- **位置**：优先使用脚本同目录下的 `deadlines.json`，否则使用 `~/.countdown_deadlines.json`
- **格式**：JSON，可手动编辑

```json
{
  "conferences": {
    "ICML": {"datetime": "2026-01-29 19:59", "estimated": false},
    "NeurIPS": {"datetime": "2026-05-20 19:59", "estimated": true}
  }
}
```

- `datetime`：北京时间的截止时刻，格式 `YYYY-MM-DD HH:MM`
- `estimated`：是否为估计日期（会显示 E 标记）

编辑保存后，正在运行的仪表盘会在下次刷新时自动加载新数据。

## 颜色说明

- 红色：距截止 < 2 天
- 橙色：2–14 天
- 绿色：> 14 天

底部红字会随当前最紧急的 DDL 动态更新；当所有 DDL 过期后显示 `All deadlines passed.`

## 依赖

仅需 Python 3.6+ 标准库，无额外依赖。

## License

MIT
