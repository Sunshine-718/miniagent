from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.theme import Theme
from rich.spinner import Spinner
from rich.align import Align
import re
import json
import asyncio


class ConsoleUI:
    def __init__(self):
        self.console = Console(theme=Theme({
            "info": "dim cyan",
            "thought": "yellow",
            "tool": "bold blue",
            "error": "bold red"
        }), force_terminal=True)

    def input(self, prompt="User: "):
        return self.console.input(f'[bold green]{prompt}[/bold green]')

    def rule(self, title):
        self.console.rule(f'[bold white]{title}[/bold white]')

    def print_observation(self, obs):
        text = obs if len(obs) < 500 else obs[:500] + "...(truncated)"
        self.console.print(Panel(text, title="👀 Observation", border_style="blue"))

    def print_error(self, msg):
        self.console.print(f"[error]❌ {msg}[/error]")

    async def render_stream_loop(self, generator):
        full_text = ""
        waiting_spinner = Spinner("dots", text="[bold cyan] 正在连接Axiom...[/]", style='cyan')
        initial_panel = Panel(Align.center(waiting_spinner), title="⚡ System Status", border_style="dim")

        with Live(initial_panel, console=self.console, refresh_per_second=5, vertical_overflow='auto') as live:
            async for chunk in generator:
                full_text += chunk

                panels = []

                def get_section(name):
                    pattern = f"(?i)@@@\\s*{name}\\s*(.*?)(?=\\n@@@\\s|$)"
                    matches = list(re.finditer(pattern, full_text, re.DOTALL))
                    return matches[-1].group(1).strip() if matches else None

                plan = get_section("Plan")
                thought = get_section("Thought")
                action = get_section("Action")
                args = get_section("Args")
                answer = get_section("Answer")

                if plan:
                    panels.append(Panel(Markdown(plan), title="📅 Plan", border_style="magenta"))

                if thought:
                    if not action and not answer:
                        spinner = Spinner("moon", text=" [bold yellow]Reasoning...[/]", style="yellow")
                        title = "🤖 Thought Process"
                        content = Group(Markdown(thought), Align.right(spinner))
                    else:
                        title = "🤖 Thought History"
                        content = Markdown(thought)
                    panels.append(Panel(content, title=title, border_style="yellow"))
                if action:
                    display_content = "..."

                    if args:
                        stripped = args.strip()
                        if action == 'python_repl':
                            match = re.search(r'~~~\s*(?:python)?\s*(.*?)~~~', stripped, re.DOTALL)
                            if match:
                                code_content = match.group(1).strip()
                                display_content = f"```python\n{code_content}\n```"
                            else:
                                clean_code = stripped
                                if clean_code.startswith("~~~"):
                                    clean_code = clean_code[3:]
                                if clean_code.endswith("~~~"):
                                    clean_code = clean_code[:-3]
                                clean_code = clean_code.strip()
                                if clean_code.lower().startswith("python"):
                                    clean_code = clean_code[6:].strip()
                                display_content = f"```python\n{clean_code}\n```"
                        else:
                            try:
                                parsed_json = json.loads(stripped)
                                pretty_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                                display_content = f"```json\n{pretty_json}\n```"
                            except:
                                display_content = f"```json\n{stripped}\n```"
                    tool_spinner = Spinner("earth", text=f" Executing [bold]{action}[/]...", style="blue")
                    action_content = Group(Markdown(display_content), Align.right(tool_spinner))
                    action_panel = Panel(
                        action_content,
                        title=f"🛠️ Action: [bold white]{action}[/bold white]",
                        border_style="blue"
                    )
                    panels.append(action_panel)

                if answer:
                    result_spinner = Spinner("aesthetic", text=" [bold green]Finalizing Output...[/]", style="green")
                    answer_content = Group(Markdown(answer), Align.right(result_spinner))
                    panels.append(Panel(answer_content, title="✅ Final Result", border_style="green"))

                if not panels:
                    panels.append(Panel(full_text, title="⚡ Streaming...", border_style="dim"))
                live.update(Group(*panels))
        return full_text
