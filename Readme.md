# miniagent

一个轻量级、模块化、具备自我进化能力的 ReAct（Reasoning + Acting）AI 代理系统。

miniagent - 从单文件脚本进化为现代化的 AI Agent 框架。它拥有结构化的记忆、有状态的任务规划以及即插即用的工具系统。

## ✨ 核心特性

🧩 **即插即用工具库**：工具按功能分类存储（file_ops, web_ops 等），支持递归自动扫描。只需放入 tools 文件夹，Agent 即可立即获得新能力。

🧠 **长期记忆系统**：内置 JSON 索引的记忆库（memory_ops），支持记忆的分类存储、模糊搜索与自动管理。

📝 **有状态计划 (Stateful Plan)**：Agent 能够维护当前计划状态，仅在必要时更新计划，大幅节省 Token 消耗并保持上下文连贯。

🔄 **深度热重载**：支持运行时的"深度刷新"，不仅重载工具列表，还能强制刷新 Python 模块缓存，开发新工具无需重启。

🎨 **现代化 UI**：基于 Rich 库构建的流式控制台，支持 Markdown 渲染、代码高亮和实时思考过程展示。

## 📋 系统架构

```plaintext
┌─────────────────────────────────────────────────────────────┐
│                    Console UI (Rich)                        │
│   [Stream Renderer]  [Stateful Panel]  [Error Handler]      │
├─────────────────────────────────────────────────────────────┤
│                    ReAct Agent Core                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐     │
│  │  Planner    │◄─│ Context Mgr │─►│  Memory System   │     │
│  └─────────────┘  └─────────────┘  └──────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Tool Manager (Dynamic)                   │
│          (Auto-Discovery & Recursive Loading)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ file_ops │  │ web_ops  │  │ sys_ops  │  │ mem_ops  │ ... │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- [DeepSeek API Key](https://platform.deepseek.com/api_keys)
- [Jina API Token](https://jina.ai/zh-CN/) (用于联网搜索)
- [QQ邮箱](https://wx.mail.qq.com/)授权码 (可选，用于邮件功能)

### 安装步骤

1. **克隆项目并安装依赖**

```bash
git clone https://github.com/Sunshine-718/miniagent.git
cd miniagent
pip install -r requirements.txt
```

2. **配置环境变量**

项目根目录已包含 .env.template，请复制为 .env 并填入密钥：

```bash
cp .env.template .env
```

编辑 .env 文件：

```bash
# 核心配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 增强功能配置
JINA_API_TOKEN=jina_xxxxxxxxxxxx
QQ_EMAIL=your_email@qq.com
QQ_EMAIL_AUTH_CODE=your_auth_code
```

3. **启动 Agent**

```bash
python main.py
```

## 🛠️ 工具集概览 (src/tools/)

工具库已按功能分类到不同文件夹：

### 📂 file_ops (文件系统)

- `create_file` / `read_file` / `delete_file` - 基础操作
- `edit_file_by_replace` / `edit_file_by_line` - 精准文件编辑 (节省 Token)
- `check_file_diff` - 修改前差异预览
- `regex_search_in_file` - 正则搜索
- `rename_file` / `rename_dir` - 文件/文件夹重命名
- `replace_file` - 原子文件替换 (使用 os.replace)
- `move_file` - 文件/文件夹移动

### 🌐 web_ops (网络能力)

- `search_jina` - 联网搜索 (SERP)
- `scrape_web_page` / `read_url_jina` - 网页内容读取与 Markdown 转换
- `get_weather` - 实时天气查询
- `send_email_via_qq` - 邮件发送

### 💻 system_ops (系统控制)

- `run_terminal_command` - 执行 Shell 命令
- `python_repl` - Python 代码执行沙箱
- `upload_to_github` - 自动 Git 提交与推送
- `get_source_code` - Agent 自我内省 (读取自身源码)

### 🧠 memory_ops (记忆管理)

- `save_memory` - 保存关键信息到长期记忆
- `search_memory` - 模糊/精确搜索记忆库
- `get_all_memories` - 记忆库概览

### 🧮 math_ops (计算)

- `calculator` - 安全的数学表达式计算器

## 📁 项目结构

```plaintext
miniagent/
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
├── .env                     # 环境变量 (不要提交到Git)
├── logs/                    # 运行日志
├── memory/                  # [自动生成] 长期记忆存储库 (JSON索引)
├── storage/                 # [自动生成] Agent 的工作区
└── src/                     # 源代码包
    ├── agent.py             # ReAct Agent 核心逻辑 (含状态计划)
    ├── config.py            # 配置加载器 (兼容对象与模块级变量)
    ├── interface.py         # Rich UI 渲染层
    ├── states.py            # 状态定义 (Plan/Thought/Action)
    ├── system_instructions.py # System Prompt 模板
    ├── utils.py             # 通用工具类 (LogManager, ToolManager)
    └── tools/               # 工具包根目录
        ├── __init__.py      # 核心：动态递归扫描器
        ├── file_ops/        # 文件工具分类
        ├── web_ops/         # 网络工具分类
        ├── system_ops/      # 系统工具分类
        ├── memory_ops/      # 记忆工具分类
        └── math_ops/        # 计算工具分类
```

## 🔧 开发与扩展

### 如何添加新工具？

得益于动态扫描机制，添加工具非常简单：

1. **选择分类**：在 `src/tools/` 下找到合适的文件夹（如 `web_ops`），或者新建一个文件夹。
2. **创建文件**：新建一个 `.py` 文件，例如 `get_btc_price.py`。
3. **编写函数**：

```python
# src/tools/web_ops/get_btc_price.py
import requests

def get_btc_price(currency: str = "USD") -> str:
    """
    获取比特币当前价格。
    参数:
        currency: 货币单位 (USD/CNY)
    """
    # 实现逻辑...
    return "价格信息..."
```

4. **完成！** 无需注册，无需修改配置。 Agent 在下一次启动或触发 `[REFRESH]` 时会自动加载该工具。

## 🎮 交互指令

- `quit` / `exit` - 退出
- `reset` - 重置当前对话上下文（清空短期记忆）
- `reload` - 从日志文件回放历史对话

## ⚠️ 免责声明

本系统具有执行系统命令和修改文件的能力。虽然内置了 `check_file_diff` 等安全机制，但在生产环境中使用 `run_terminal_command` 时请务必谨慎。建议在沙箱或受控环境中运行。
