from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.theme import Theme
from rich.syntax import Syntax
import re


class ConsoleUI:
    def __init__(self):
        self.console = Console(theme=Theme({
            "info": "dim cyan",
            "thought": "yellow",
            "tool": "bold blue",
            "error": "bold red"
        }))
    
    def input(self, prompt="User: "):
        return self.console.input(f'[bold green]{prompt}[/bold green]')
    
    def rule(self, title):
        self.console.rule(f'[bold white]{title}[/bold white]')
    
    def print_observation(self, obs):
        text = obs if len(obs) < 500 else obs[:500] + "...(truncated)"
        self.console.print(Panel(text, title="👀 Observation", border_style="blue"))
    
    def print_error(self, msg):
        self.console.print(f"[error]❌ {msg}[/error]")
    
    def render_stream_loop(self, generator):
        full_text = ""

        ui_group = Group(Panel("Waiting for response...", style='dim'))

        with Live(ui_group, console=self.console, refresh_per_second=5, vertical_overflow='visible') as live:
            for chunk in generator:
                full_text += chunk

                panels = []
                
                def get_section(name):
                    pattern = f"##\\s*{name}\\s*(.*?)(?=\n##\\s|$)"
                    match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
                    return match.group(1) .strip() if match else None
                
                plan = get_section("Plan")
                thought = get_section("Thought")
                action = get_section("Action")
                args = get_section("Args")
                answer = get_section("Answer")

                if plan:
                    panels.append(Panel(Markdown(plan), title="📅 Plan", border_style="magenta"))
                
                if thought:
                    panels.append(Panel(Markdown(thought), title="🤖 Thinking", border_style="yellow"))
                
                if action:
                    display_args = args if args else "..."

                    if args:
                        code_match = re.search(r'```(\w+)?\s*(.*?)```', args, re.DOTALL)
                        if code_match:
                            lang = code_match.group(1) or ('python' if 'python' in action.lower() else "json")
                            code_content = code_match.group(2)
                            display_args = Syntax(code_content, lang, theme="monokai", word_wrap=True)
                        else:
                            # 如果还没输完代码块，暂时显示纯文本
                            pass
                    action_panel = Panel(
                        display_args,
                        title=f"🛠️ Action: [bold white]{action}[/bold white]",
                        border_style="blue"
                    )
                    panels.append(action_panel)

                if answer:
                    panels.append(Panel(Markdown(answer), title="✅ Final Answer", border_style="green"))
                
                if panels:
                    live.update(Group(*panels))
                    
        return full_text