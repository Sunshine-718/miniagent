from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.theme import Theme
from rich.syntax import Syntax
import re
import json


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
    
    def render_stream_loop(self, generator):
        full_text = ""

        ui_group = Group(Panel("Waiting for response...", style='dim'))

        with Live(ui_group, console=self.console, refresh_per_second=3, vertical_overflow='auto') as live:
            for chunk in generator:
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
                    panels.append(Panel(Markdown(thought), title="🤖 Thinking", border_style="yellow"))
                
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
                    action_panel = Panel(
                        Markdown(display_content),
                        title=f"🛠️ Action: [bold white]{action}[/bold white]",
                        border_style="blue"
                    )
                    panels.append(action_panel)

                if answer:
                    panels.append(Panel(Markdown(answer), title="✅ Final Answer", border_style="green"))
                
                if panels:
                    live.update(Group(*panels))
                    
        return full_text