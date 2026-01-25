import tools
from system_instructions import REACT_SYSTEM_PROMPT
from constants import Tags
import os
import re
import json
from openai import OpenAI, BadRequestError
import inspect
import time
import importlib
import config  # 导入配置模块

# --- 引入 Rich 库进行美化 ---
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.theme import Theme
from rich.table import Table
from rich.live import Live
from rich.console import Group

# 自定义配色主题
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "thought": "yellow",
    "tool": "bold blue"
})
console = Console(theme=custom_theme)

# 从配置中读取API密钥
client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def get_tag_regex(open_tag, close_tag):
    return re.escape(open_tag) + r'(.*?)(' + re.escape(close_tag) + r'|$)'


def parse_agent_response(response: str):
    """
    基于 XML 标签 [TAG]...[/TAG] 的解析器，边界严格，无歧义。
    """
    result = {
        "plan": None,
        "thought": None,
        "action": None,
        'action_input': None,
        'final_answer': None,
        'is_refresh': False,
        'retry': False
    }
    
    # 1. 提取 [PLAN] (新增)
    plan_match = re.search(get_tag_regex(*Tags.plan_tag), response, re.DOTALL)
    if plan_match:
        result['plan'] = plan_match.group(1).strip()

    # 2. 提取 [ANSWER]
    answer_match = re.search(get_tag_regex(*Tags.answer_tag), response, re.DOTALL)
    if answer_match:
        result['final_answer'] = answer_match.group(1).strip()

    # 3. 提取 [THOUGHT]
    thought_match = re.search(get_tag_regex(*Tags.thought_tag), response, re.DOTALL)
    if thought_match:
        result['thought'] = thought_match.group(1).strip()

    # 4. 提取 [ACTION]
    action_match = re.search(get_tag_regex(*Tags.action_tag), response, re.DOTALL)
    if action_match:
        result['action'] = action_match.group(1).strip()
        
        if '[REFRESH]' in result['action']:
            result['is_refresh'] = True
            return result

        # 5. 提取 [ARGS]
        args_match = re.search(get_tag_regex(*Tags.args_tag), response, re.DOTALL)
        if args_match:
            raw_input = args_match.group(1).strip()
            raw_input = re.sub(r'^```\w*\s*', '', raw_input)
            raw_input = re.sub(r'\s*```$', '', raw_input)
            try:
                result['action_input'] = json.loads(raw_input)
            except json.JSONDecodeError:
                result['action_input'] = None
                result['retry'] = True

    return result


class ReactAgent:
    def __init__(self):
        self.client = client
        self.history = []
        self.tools = {}
        self.token_limit = 100000
        self.retain_recent = 4
        self.clear_history()

    def _estimate_tokens(self, text: str):
        if not text:
            return 0
        return len(text) // 3

    def clear_history(self):
        # 初始化时，确保 tools 已经加载
        self.history = [{'role': 'system', 'content': self.system_prompt}]

    def reload_tools(self):
        try:
            importlib.reload(tools)
            self.tools = {}
            tool_list = [obj for _, obj in inspect.getmembers(tools) if inspect.isfunction(obj)]
            self.register_tool(tool_list)
            self.history[0] = {'role': 'system', 'content': self.system_prompt}
        except Exception as e:
            print(f"Reload failed: {e}")
            exit()

    @property
    def system_prompt(self):
        prompt = REACT_SYSTEM_PROMPT
        tool_descriptions = ''
        for name, d in self.tools.items():
            tool_descriptions += f'- {name}: {d["desc"]}\n'
        prompt = prompt.replace('{tool_descriptions}', tool_descriptions)
        return prompt

    def _register_tool(self, tool):
        name = tool.__name__
        doc = tool.__doc__
        if not doc:
            print(f"[Warning] Tool '{name}' has no docstring. Agent may not use it correctly.")
            description = "No description available."
        else:
            description = doc.strip()
        self.tools[name] = {'func': tool, 'desc': description}

    def register_tool(self, tool):
        if isinstance(tool, (list, tuple)):
            for t in tool:
                self._register_tool(t)
        else:
            self._register_tool(tool)

    def _compress_history(self):
        total_tokens = sum(self._estimate_tokens(m['content']) for m in self.history)
        if total_tokens < self.token_limit:
            return

        console.print(f"[warning]⚠️  Token limit reached ({total_tokens}/{self.token_limit}). Compressing...[/warning]")

        sys_prompt = self.history[0]
        msgs_to_compress = self.history[1:-self.retain_recent]
        recent_msgs = self.history[-self.retain_recent:]

        compressed_batch = []
        thought_pattern = get_tag_regex(*Tags.thought_tag)
        for msg in msgs_to_compress:
            if msg['role'] == 'assistant':
                content = msg['content']

                new_content = re.sub(thought_pattern, '', content, flags=re.DOTALL)
                new_content = new_content.strip()
                if new_content:
                    msg['content'] = new_content
                    compressed_batch.append(msg)
            elif msg['role'] == 'user':
                if msg['content'].startswith("Observation:"):
                    msg['content'] = "Observation: [History Compressed]"
                    compressed_batch.append(msg)
            else:
                compressed_batch.append(msg)

        self.history = [sys_prompt] + compressed_batch + recent_msgs

        current_tokens = sum(self._estimate_tokens(m['content']) for m in self.history)
        while current_tokens > self.token_limit and len(self.history) > 1:
            dropped_msg = self.history.pop(1)
            current_tokens -= self._estimate_tokens(dropped_msg['content'])

        if len(self.history) <= 1:
            console.print(
                "[bold red]🚨 Alert: History wiped due to extreme token usage. Only System Prompt remains.[/bold red]")

    def generate(self, prompt):
        messages = [{'role': 'user', 'content': prompt}]
        self.history.extend(messages)

        # === 在调用 API 前，先检查并修剪历史 ===
        self._compress_history()

        # 发起请求
        response_stream = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=self.history,
            stream=True
        )
        full_content = ""
        for chunk in response_stream:
            content = chunk.choices[0].delta.content
            if content:
                full_content += content
                yield content
        self.history.append({'role': 'assistant', 'content': full_content})

# --- 优化后的 Server 类 ---


class Server:
    def __init__(self, agent):
        self.agent = agent

    def execute(self, prompt):
        for i in range(1000):
            console.rule(f"[bold white]Step {i + 1}[/bold white]")

            response = self._stream_and_render(prompt)

            parse_res = parse_agent_response(response)

            # 1. 结束条件：检测到 Final Answer
            if parse_res['final_answer']:
                break
            # 2. 热重载
            if parse_res['is_refresh']:
                self._handle_refresh()
                prompt = "Observation: 工具库重载成功。"
                continue
            # 3. 工具调用
            if parse_res['action']:
                prompt = self._handle_tool_call(parse_res)
            # 4. 错误处理
            elif parse_res['retry']:
                prompt = self._handle_error(f"JSON format error in {Tags.ARGS_OPEN}.")
            elif not parse_res['thought']:
                # 如果连 Thought 都没有，且没有 Answer，说明格式严重错误
                prompt = self._handle_error(f"Invalid format. Please use {Tags.THOUGHT_OPEN}...{Tags.THOUGHT_CLOSE} tags.")

    def _clean_tags(self, text: str) -> str:
        """
        UI 辅助函数：去除文本中的 [TAG] 标签，让显示更干净
        """
        for tag in Tags.ALL_TAGS:
            text = re.sub(re.escape(tag), '', text)
        return text.strip()

    def _stream_and_render(self, prompt) -> str:
        """
        流式渲染：能够识别 [ANSWER] 标签并切换面板
        """
        full_response = ""

        plan_panel = Panel("...", title="📅 Mission Plan", style="dim", border_style="blue")
        thought_panel = Panel("", title="🤖 AI Thinking...", style='thought', border_style='yellow')

        # 初始只显示思考面板
        ui_group = Group(thought_panel)

        # 调整刷新率，防止闪烁
        with Live(ui_group, console=console, refresh_per_second=5, vertical_overflow="visible") as live:
            for chunk in self.agent.generate(prompt):
                full_response += chunk

                plan_match = re.search(get_tag_regex(*Tags.plan_tag), full_response, re.DOTALL)
                if plan_match:
                    plan_text = plan_match.group(1).strip()
                    if plan_text:
                        plan_panel = Panel(Markdown(plan_text), title="📅 Mission Plan", style="white", border_style="magenta")
                
                thought_text = "..."
                if Tags.PLAN_CLOSE in full_response:
                    parts = full_response.split(Tags.PLAN_CLOSE)
                    if len(parts) > 1:
                        remaining = parts[1]
                        thought_text = self._clean_tags(remaining)
                        if Tags.ANSWER_OPEN in remaining:
                            thought_text = remaining.split(Tags.ANSWER_OPEN)[0].replace(Tags.THOUGHT_OPEN, "").replace(Tags.THOUGHT_CLOSE, "").strip()
                
                thought_panel = Panel(Markdown(thought_text), title="🤖 AI Thinking...", style="thought", border_style="yellow")

                panels = [plan_panel, thought_panel]

                if Tags.ANSWER_OPEN in full_response:
                    ans_match = re.search(get_tag_regex(*Tags.answer_tag), full_response, re.DOTALL)
                    if ans_match:
                        ans_text = ans_match.group(1).strip()
                        panels.append(Panel(Markdown(ans_text), title="✅ Final Answer", style="success", border_style="green"))
                live.update(Group(*panels))
        return full_response
                
                
    def _handle_tool_call(self, parse_res) -> str:
        tool_name = parse_res['action']
        args = parse_res['action_input'] or {}

        console.print(f"[tool]🛠️  Calling Tool:[/tool] [bold white]{tool_name}[/bold white]")
        self._print_json_args(args)

        if tool_name not in self.agent.tools:
            return self._handle_error(f"Tool '{tool_name}' not found.")

        try:
            with console.status(f"[bold blue]Running {tool_name}...[/bold blue]", spinner="bouncingBar"):
                func_return = str(self.agent.tools[tool_name]['func'](**args))

            if "error" in func_return.lower() or "exception" in func_return.lower():
                self._print_observation(func_return)
                return f'Observation: {func_return}\nSystem Hint: Execution failed? If so, please REFLECT on the arguments.'
            self._print_observation(func_return)
            return f'Observation: Function return: {func_return}\n'

        except Exception as e:
            return self._handle_error(f"Tool execution error: {str(e)}")

    def _handle_refresh(self):
        self.agent.reload_tools()
        console.print(Panel("System: Tools Reloaded", style="warning"))

    def _handle_error(self, msg) -> str:
        console.print(f"[danger]❌ {msg}[/danger]")
        return f"Observation: Error: {msg}\nSystem Hint: Previous action failed. Please starts your next {Tags.THOUGHT_OPEN} with 'Reflection:' to analyze the cause."

    def _print_json_args(self, args):
        args_str = json.dumps(args, indent=2, ensure_ascii=False)
        display_args = args_str if len(args_str) < 500 else args_str[:500] + "\n..."
        console.print(Syntax(display_args, "json", theme="monokai", word_wrap=True))

    def _print_observation(self, content):
        display = content if len(content) < 800 else content[:800] + " ... (truncated)"
        console.print(Panel(display, title="👀 Observation", border_style="blue", expand=False))


if __name__ == '__main__':
    agent = ReactAgent()
    agent.reload_tools()  # 启动时加载
    server = Server(agent)

    console.print(Panel.fit("[bold white]ReAct Agent[/bold white]", style="blue"))

    i = 0
    try:
        while True:
            i += 1
            console.rule(f"[bold magenta]Round {i}[/bold magenta]")
            user_input = console.input("[bold green]User:[/bold green] ")
            if user_input.strip().upper() == "RESET":
                agent.clear_history()
                console.print("[bold yellow]History Cleared![/bold yellow]")
                continue
            elif user_input.strip().upper() == "QUIT":
                break
            if user_input:
                try:
                    server.execute(user_input)
                except BadRequestError:
                    agent.clear_history()
                    server.execute(user_input)
    except KeyboardInterrupt:
        pass
    console.print("🛑STOPPED🛑", style="red")