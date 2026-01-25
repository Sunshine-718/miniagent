from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.console import Group

from constants import Tags
import re
import json
from openai import BadRequestError
from utils import *
from agent import console, ReactAgent


class Server:
    def __init__(self, agent):
        self.agent = agent

    def execute(self, prompt):
        current_prompt = prompt
        self.agent.append_log("User", prompt)
        for i in range(1000):
            try:
                console.rule(f"[bold white]Step {i + 1}[/bold white]")

                response = self._stream_and_render(current_prompt)
                
                self.agent.append_log("Agent", response)

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
                    current_prompt = self._handle_tool_call(parse_res)
                # 4. 错误处理
                elif parse_res['retry']:
                    current_prompt = self._handle_error(f"JSON format error in {Tags.ARGS_OPEN}.")
                elif not parse_res['thought']:
                    # 如果连 Thought 都没有，且没有 Answer，说明格式严重错误
                    current_prompt = self._handle_error(f"Invalid format. Please use {Tags.THOUGHT_OPEN}...{Tags.THOUGHT_CLOSE} tags.")
            except KeyboardInterrupt:
                console.print("\n[bold yellow]⏸️  Process Paused by User (Ctrl+C)[/bold yellow]")
                action = console.input("[bold cyan]Choose Action: (c)ontinue / (i)ntervene / (q)uit task:[/bold cyan] ").strip().lower()

                if action == 'q':
                    console.print("[bold red]Task Aborted by User.[/bold red]")
                    break
                elif action == 'i':
                    # 允许用户插入新的 Observation 或 System Hint
                    new_instruction = console.input("[bold green]Enter intervention/hint:[/bold green] ")
                    # 将用户的干预伪装成 System Hint 强行注入
                    current_prompt = f"Observation: [User Intervention] {new_instruction}\nSystem Hint: The user paused execution to provide the above correction. Please adapt your plan."
                    console.print("[bold magenta]Intervention injected into context.[/bold magenta]")
                    continue
                else:
                    console.print("[dim]Resuming...[/dim]")
                    # 如果刚才被打断的是 _stream_and_render，response 可能不完整
                    # 这里简单的处理是让 Agent 基于当前历史继续（可能需要重试）
                    current_prompt = "System Hint: Execution was paused briefly. Please continue."
                    continue

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
                result = f'Observation: {func_return}\nSystem Hint: Execution failed? If so, please REFLECT on the arguments.'
            else:
                self._print_observation(func_return)
                result = f'Observation: Function return: {func_return}\n'
            self.agent.append_log("System", result)
            return result
        except Exception as e:
            return self._handle_error(f"Tool execution error: {str(e)}")

    def _handle_refresh(self):
        self.agent.reload_tools()
        console.print(Panel("System: Tools Reloaded", style="warning"))

    def _handle_error(self, msg) -> str:
        console.print(f"[danger]❌ {msg}[/danger]")
        error_msg = f"Observation: Error: {msg}\nSystem Hint: Previous action failed. Please starts your next {Tags.THOUGHT_OPEN} with 'Reflection:' to analyze the cause."
        self.agent.append_log("System", error_msg)
        return error_msg

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
    except (EOFError, KeyboardInterrupt):
        pass
    print("🛑STOPPED🛑")