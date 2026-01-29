<div align="center">
  <img src="assets/logo.jpg" alt="miniagent logo" width="200" height="200">

# miniagent

  一个轻量级、模块化、具备**自我进化**能力的 ReAct（Reasoning + Acting）+ Plan-and-solve + self-Reflection 的AI 代理系统。

</div>

## 📢 最新更新

<details>
<summary><strong>🚀 2026-01-29 - 综合功能增强与用户体验全面优化</strong></summary>

### 🆕 新增功能

1. **智能Dashboard系统**

   - Agent首次打招呼时自动显示Dashboard信息
   - 包含API余额、当前时间、系统状态等关键信息
   - 实时监控日志文件数量，超过阈值自动提醒
2. **文本转PDF工具**

   - 新增 `file_to_pdf` 工具，支持将文本文件（.txt, .md）转换为PDF
   - 支持中文字体渲染，避免乱码问题
   - 可自定义字体、字号和页面尺寸
3. **系统监控增强**

   - 启动时自动监测日志文件数量，超过20个时提醒用户清理
   - 实时跟踪API token使用量，接近128K限制时主动预警

### 🎨 UI与交互优化

1. **动态视觉反馈**

   - 在配置向导、工具加载、网络请求等操作中添加动态Spinner动画
   - 为长时操作添加进度条，显示进度百分比和预计时间
   - 优化控制台刷新机制，减少界面闪烁，改进错误信息显示
2. **交互提示改进**

   - 为所有链接添加"Ctrl+鼠标左键点击访问"提示

</details>

<details>
<summary><strong>🔄 2026-01-28 - 交互式配置引导集成与 Prompt 增强</strong></summary>

### 新增功能

1. **一键启动配置引导**

   - `main.py` 现已集成 `prepare()` 函数，首次运行自动检测并启动配置向导
   - 用户只需运行 `python main.py` 即可完成从环境配置到启动 Agent 的全过程
2. **智能环境检测**

   - 自动检测 `.env` 文件是否存在
   - 缺失配置时自动启动交互式配置向导
   - 配置完成后自动安装所有依赖包
3. **三种配置方式**

   - **一键启动**：`python main.py`（推荐）
   - **独立配置**：`python prepare.py`
   - **手动配置**：传统方式，保留灵活性
4. **配置优化**

   - 移除了 `DEEPSEEK_BASE_URL` 配置项
   - 简化 `.env` 文件，现在只需配置4个关键项
5. **Prompt 增强**

   - 每个 ReAct 步骤现在自动添加 `[CURRENT STEP: {step}]` 标签
   - 每个步骤自动添加 `[CURRENT TIME: {datetime.now()}]` 时间戳
   - 增强调试能力，便于跟踪对话流程和时间线
6. **Agent 控制指令增强**

   - 新增 `[QUIT]` 指令：终止 Agent 程序，安全退出
   - 新增 `[CLEAR]` 指令：清除历史对话记录，重置对话状态
   - 完善的特殊指令系统，支持更精细的 Agent 控制
7. **Token使用量实时监控**

   - 系统实时监控对话的 token 使用量，每个步骤都会在系统提示中显示当前已使用的 token 估计数量
   - 当 token 使用量接近上下文限制（128K）时，系统会主动提醒用户
   - 有效避免上下文溢出问题，确保对话的稳定性和连续性

### 用户体验提升

- 🎨 基于 Rich 库的现代化交互界面
- 🔑 逐步引导配置所有必要的 API Key
- 📦 自动安装依赖，无需手动操作
- 🤖 配置完成后无缝进入 Agent 交互界面
- ⏱️ 增强的调试信息，每个步骤都有时间戳和步骤编号
- 🎮 增强的交互控制，支持忘记历史和退出程序
- 💰 实时余额查询和告知，随时掌握 API 使用情况

### 技术改进

- 导入 `datetime` 模块支持实时时间戳
- 改进的 prompt 构造逻辑，确保步骤和时间信息准确传递
- 更好的对话流程跟踪和调试支持
- 增强的 Agent 状态管理，支持安全退出和对话重置

</details>

## ✨ 核心特性

🧩 **即插即用工具库**：工具按功能分类存储（file_ops, web_ops 等），支持递归自动扫描。只需放入 tools 文件夹，Agent 即可立即获得新能力。

🧠 **长期记忆系统**：内置 JSON 索引的记忆库（memory_ops），支持记忆的分类存储、模糊搜索与自动管理。

🔄 **深度热重载**：支持运行时的"深度刷新"，不仅重载工具列表，还能强制刷新 Python 模块缓存，开发新工具无需重启。

🧬 **自我进化能力**：Agent 能够分析自身不足，主动创建新工具、优化现有功能，实现能力的持续增长和系统自我完善。

🎨 **现代化 UI**：基于 Rich 库构建的流式控制台，支持 Markdown 渲染、代码高亮和实时思考过程展示。

🔌 **MCP协议集成**：内置完整的MCP客户端，支持连接外部MCP服务器，实现工具能力的无限扩展。

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

## 🎯 能力展示示例

miniagent 已成功完成多个实际项目，展示了其强大的多领域能力。所有示例代码和报告均可在 `examples/` 目录中找到。

### 🎮 示例1：尼姆游戏开发

**位置**: `examples/Agent开发新的小游戏示例/`

**项目概述**: 从零开始设计和实现经典的数学策略游戏——尼姆游戏（Nim Game）。

**展示能力**:

- ✅ **需求分析**: 从模糊需求中准确识别游戏类型
- ✅ **系统设计**: 完整的游戏架构设计，支持两种游戏模式（标准/反尼姆）
- ✅ **算法实现**: 基于模运算的数学必胜策略算法
- ✅ **AI系统**: 三种难度级别的AI对手（简单/普通/困难）
- ✅ **完整测试**: 单元测试、集成测试和边界测试
- ✅ **工具集成**: 成功集成到 `src/tools/toys/nim_game.py`

**关键文件**:

- `尼姆游戏开发过程报告.md` - 完整开发文档
- `聊天记录.md` - 开发过程对话记录

### 📊 示例2：Iris数据集数据分析

**位置**: `examples/Agent数据分析示例/`

**项目概述**: 对经典的Iris鸢尾花数据集进行全面的探索性数据分析（EDA）。

**展示能力**:

- ✅ **数据处理**: 数据加载、清洗和预处理
- ✅ **统计分析**: 描述性统计、相关性分析
- ✅ **可视化**: 多种图表生成（箱线图、直方图、散点图矩阵、热力图）
- ✅ **洞察发现**: 识别关键特征和类别可分性
- ✅ **报告生成**: 专业的分析报告和可视化展示

**生成文件**:

- `Iris数据分析报告.md` - 完整分析报告
- `描述性统计.txt` - 数值统计摘要
- `特征相关性矩阵.txt` - 相关系数矩阵
- 5种可视化图表（PNG格式）
- 原始数据集 `iris_data.csv`

### 🔤 示例3：Python代码字母频率分析

**位置**: `examples/Python代码字母频率分析/`

**项目概述**: 分析项目所有Python源代码的字母频率分布，生成统计报告和可视化。

**展示能力**:

- ✅ **代码分析**: 递归扫描66个Python文件，统计56,378个字母
- ✅ **频率统计**: 区分大小写/不区分大小写的完整字母频率排名
- ✅ **高级可视化**: 5种专业图表（条形图、饼图、热力图、大小写对比图）
- ✅ **深度洞察**: 发现代码字母分布规律（如'E'最常见占13.10%，'Q'最罕见占0.12%）
- ✅ **完整报告**: 包含方法、结果、结论和建议的详细报告

**生成文件**:

- `Python代码字母频率分析报告.md` - 完整分析报告
- `letter_frequency_stats.json` - 详细统计数据
- `analysis_script.py` - 可复用的分析脚本
- 5种可视化图表（PNG格式）

### 🏆 综合能力总结

通过这些实际项目，miniagent 展示了其作为全能型ReAct Agent的全面能力：

| 能力维度           | 具体表现                       |
| ------------------ | ------------------------------ |
| **需求理解** | 从模糊需求到具体方案的分析能力 |
| **系统设计** | 完整的架构设计和模块划分       |
| **算法实现** | 数学算法和逻辑的正确实现       |
| **数据处理** | 数据清洗、统计分析和可视化     |
| **代码分析** | 大规模代码库的分析和统计       |
| **测试验证** | 全面的功能测试和边界测试       |
| **文档生成** | 专业的报告和文档编写能力       |
| **工具集成** | 新功能的工具化集成能力         |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- [DeepSeek API Key](https://platform.deepseek.com/api_keys)
- [Jina API Token](https://jina.ai/zh-CN/) (用于联网搜索)
- [QQ邮箱](https://wx.mail.qq.com/)授权码 (可选，用于邮件功能)

### 安装步骤

#### 方法一：一键启动（推荐）

最简单的启动方式，系统会自动检测并引导您完成首次配置：

```bash
git clone https://github.com/Sunshine-718/miniagent.git
cd miniagent
python main.py
```

首次运行时，系统将自动：

1. 🔍 检测环境配置状态
2. 🎨 启动交互式配置向导（如果需要配置）
3. 🔑 引导您逐步配置所有必要的 API Key
4. 📝 自动生成 `.env` 配置文件
5. 📦 自动安装所有依赖包
6. 🤖 直接进入 Agent 交互界面

#### 方法二：独立配置

如果您希望先单独完成配置，再启动 Agent：

```bash
git clone https://github.com/Sunshine-718/miniagent.git
cd miniagent
python prepare.py
```

配置完成后，再运行：

```bash
python main.py
```

#### 方法三：手动配置

如果您更喜欢完全手动配置，可以按照以下步骤操作：

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
- `check_deepseek_balance` - 查询DeepSeek API账户余额（实时监控使用成本）

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
├── prepare.py               # 交互式环境配置向导
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
