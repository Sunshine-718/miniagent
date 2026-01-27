<div align="center">
  <img src="assets/logo.jpg" alt="miniagent logo" width="200" height="200">

# miniagent

  一个轻量级、模块化、具备**自我进化**能力的 ReAct（Reasoning + Acting）+ Plan-and-solve  + self-Reflection 的AI 代理系统。

</div>

## ✨ 核心特性

🧩 **即插即用工具库**：工具按功能分类存储（file_ops, web_ops 等），支持递归自动扫描。只需放入 tools 文件夹，Agent 即可立即获得新能力。

🧠 **长期记忆系统**：内置 JSON 索引的记忆库（memory_ops），支持记忆的分类存储、模糊搜索与自动管理。

🔄 **深度热重载**：支持运行时的"深度刷新"，不仅重载工具列表，还能强制刷新 Python 模块缓存，开发新工具无需重启。

🧬 **自我进化能力**：Agent 能够分析自身不足，主动创建新工具、优化现有功能，实现能力的持续增长和系统自我完善。

🎨 **现代化 UI**：基于 Rich 库构建的流式控制台，支持 Markdown 渲染、代码高亮和实时思考过程展示。

🔌 **MCP协议集成**：内置完整的MCP客户端，支持连接外部MCP服务器，实现工具能力的无限扩展。

### 🔄 自我进化实例

**示例：文件操作能力的自我扩展**

```
1. 识别需求：用户需要批量文件操作功能
2. 分析现状：现有工具库缺少批量处理能力
3. 创建工具：开发 batch_rename_files.py
4. 测试验证：在storage目录创建原型并测试
5. 集成部署：添加到正式工具库并[REFRESH]
6. 能力增长：系统获得新的批量重命名能力
```

**实际应用场景**

- 🔍 **项目代码分析**：搜索特定代码模式，统计行数
- 📝 **文档批量处理**：重命名文档，替换内容
- 🗂️ **文件系统整理**：批量整理文件，权限管理
- 🔧 **开发辅助**：代码重构，配置文件管理

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

工具库已按功能分类到不同文件夹，支持动态热重载：

### 🎮 toys (娱乐游戏)

- `roll_dices` - 掷骰子游戏
- `flip_coins` - 投硬币游戏
- `rock_paper_scissors` - 石头剪刀布游戏
- `number_guessing_game` - 数字猜谜游戏
- `draw_cards` - 抽牌游戏（支持扑克、塔罗、UNO牌）
- `tic_tac_toe_game` - 井字棋游戏

### 📂 file_ops (文件系统操作)

- `list_files` / `list_dir` - 列出目录内容
- `create_file` / `read_file` / `delete_file` - 基础文件操作
- `edit_file_by_replace` / `edit_file_by_line` - 精准文件编辑（节省Token）
- `append_to_file` - 在文件特定位置追加内容
- `regex_search_in_file` - 正则表达式搜索
- `search_files_by_content` - 按内容搜索文件
- `rename_file` / `rename_dir` - 文件/文件夹重命名
- `batch_rename_files` - 批量文件重命名
- `move_file` / `copy` - 文件移动和复制
- `replace_file` - 原子文件替换（使用os.replace）
- `make_dir` / `delete_dir` - 目录创建和删除
- `get_file_info` - 获取文件详细信息
- `compare_files` - 比较两个文件差异
- `count_file_lines` - 统计文件行数信息
- `change_file_permissions` - 修改文件权限

### 🌐 web_ops (网络操作)

- `search_jina` - 联网搜索（SERP）
- `scrape_web_page` / `read_url_jina` - 网页内容读取与Markdown转换
- `get_weather` - 实时天气查询
- `send_email_via_qq` - 邮件发送（支持附件）
- `check_deepseek_balance` - 查询DeepSeek API账户余额

### 💻 system_ops (系统操作)

- `run_terminal_command` - 执行Shell命令（支持实时输出）
- `python_repl` - Python代码执行沙箱（变量持续保持）
- `upload_to_github` - 自动Git提交与推送
- `get_source_code` - Agent自我内省（读取工具源码）
- `get_current_time` - 获取当前日期时间
- `get_os_info` - 获取操作系统信息

### 🧠 memory_ops (记忆管理)

- `save_memory` - 保存关键信息到长期记忆
- `search_memory` - 模糊/精确搜索记忆库
- `get_all_memories` - 记忆库概览
- `delete_memory` - 删除指定记忆

### 🧮 math_ops (数学计算)

- `calculator` - 安全的数学表达式计算器（支持科学计算）
- `sympy_tool` - 符号计算工具（支持积分、微分、极限、方程求解、线性代数矩阵运算等）

### 🔌 mcp_ops (MCP协议支持)

- `connect_mcp_server` - 连接外部MCP服务器（支持Stdio协议）
- `list_mcp_tools` - 列出MCP服务器提供的所有工具
- `call_mcp_tool` - 调用MCP服务器上的特定工具

**MCP (Model Context Protocol) 支持**：miniagent 内置了完整的MCP客户端，可以连接和调用任何符合MCP标准的服务器。这使得系统能够：

- 扩展外部工具能力，无需修改核心代码
- 连接数据库、API服务、文件系统等外部资源
- 实现模块化的工具生态系统

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
    ├── mcp_manager.py       # MCP客户端集成
    └── tools/               # 工具包根目录
        ├── __init__.py      # 核心：动态递归扫描器
        ├── file_ops/        # 文件工具分类
        ├── math_ops/        # 计算工具分类
        ├── mcp_ops/        # MCP协议工具分类
        ├── memory_ops/      # 记忆工具分类
        ├── system_ops/      # 系统工具分类
        └── web_ops/         # 网络工具分类
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

本系统具有执行系统命令和修改文件的能力。虽然内置了 `修改前备份`等安全机制，但在生产环境中使用  `run_terminal_command` 时请务必谨慎。建议在沙箱或受控环境中运行。
