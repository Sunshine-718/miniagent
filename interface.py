from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.theme import Theme
from rich.syntax import Syntax
from states import Tags, AgentState
import json


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
    
    def print_tool_call(self, name, args):
        self.console.print(f"[tool]🛠️  Calling Tool:[/tool] [bold white]{name}[/bold white]")
        json_str = json.dumps(args, indent=2, ensure_ascii=False)
        self.console.print(Syntax(json_str, "json", theme="monokai", word_wrap=True))
    
    def print_observation(self, obs):
        text = obs if len(obs) < 500 else obs[:500] + "...(truncated)"
        self.console.print(Panel(text, title="👀 Observation", border_style="blue"))
    
    def print_error(self, msg):
        self.console.print(f"[error]❌ {msg}[/error]")
    
    def render_stream_loop(self, generator):
        """核心渲染逻辑：处理流式输出并更新面板"""
        full_text = ""
        plan_panel = Panel("...", title="📅 Plan", style="dim")
        
        ui_group = Group(plan_panel)
        with Live(ui_group, console=self.console, refresh_per_second=5, vertical_overflow='visible') as live:
            for chunk in generator:
                full_text += chunk
                
                panels = []

                if Tags.PLAN[0] in full_text:
                    plan_content = "..."
                    parts = full_text.split(Tags.PLAN[0])
                    if len(parts) > 1:
                        content_part = parts[1].split(Tags.PLAN[1])[0]
                        plan_content = content_part.strip()
                    if plan_content:
                        plan_panel = Panel(Markdown(plan_content), title="📅 Plan", border_style="magenta")
                    panels.append(plan_panel)
                
                if Tags.THOUGHT[0] in full_text:
                    thought_content = "..."
                    parts = full_text.split(Tags.THOUGHT[0])
                    if len(parts) > 1:
                        content_part = parts[1].split(Tags.THOUGHT[1])[0]
                        thought_content = content_part.strip()
                    thought_panel = Panel(Markdown(thought_content), title="🤖 Thinking", border_style="yellow")
                    panels.append(thought_panel)
                
                if Tags.ACTION[0] in full_text:
                    action_section = full_text.split(Tags.ACTION[0])[-1]

                    tool_name = '...'
                    display_content = ""
                    panel_title = "🛠️ Generating Tool Call..."

                    if Tags.ACTION[1] in action_section:
                        name_parts = action_section.split(Tags.ACTION[1])
                        tool_name = name_parts[0].strip()
                        remaining_after_name = name_parts[1]

                        panel_title = f"🛠️ Calling Tool: [bold white]{tool_name}[/bold white]"
                        if Tags.ARGS[0] in remaining_after_name:
                            args_raw = remaining_after_name.split(Tags.ARGS[0])[-1]

                            if Tags.ARGS[1] in args_raw:
                                args_raw = args_raw.split(Tags.ARGS[1])[0]
                            
                            display_content = Markdown(f"```json\n{args_raw}```")
                        else:
                            display_content = "Preparing arguments..."
                    else:
                        tool_name = action_section.strip()
                        display_content = tool_name
                    
                    action_panel = Panel(
                        display_content,
                        title=panel_title,
                        border_style='blue',
                        style='white'
                    )
                    panels.append(action_panel)

                if Tags.ANSWER[0] in full_text:
                    answer_part = full_text.split(Tags.ANSWER[0])[-1].split(Tags.ANSWER[1])[0]
                    answer_panel = Panel(Markdown(answer_part), title="✅ Final Answer", border_style="green")
                    panels.append(answer_panel)
                
                # 只有当面板列表不为空时才更新
                if panels:
                    live.update(Group(*panels))
        return full_text