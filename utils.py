import os
import re
import json
import importlib
import inspect
from states import AgentState, Tags
import tools
import datetime


class Parser:
    @staticmethod
    def _get_tag_content(text: str, tag_pair: tuple):
        pattern = re.escape(tag_pair[0]) + r'(.*?)(' + re.escape(tag_pair[1]) + r'|$)'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None

    @classmethod
    def parse_response(cls, response):
        state = AgentState()

        state.plan = cls._get_tag_content(response, Tags.PLAN)
        state.thought = cls._get_tag_content(response, Tags.THOUGHT)
        state.final_answer = cls._get_tag_content(response, Tags.ANSWER)
        state.action_name = cls._get_tag_content(response, Tags.ACTION)

        if state.action_name == "[REFRESH]":
            state.is_refresh = True
            return state

        args_text = cls._get_tag_content(response, Tags.ARGS)
        if args_text:
            # 清理 Markdown 代码块符号
            clean_json = re.sub(r'^```\w*\s*|\s*```$', '', args_text.strip())
            try:
                state.action_args = json.loads(clean_json)
            except json.JSONDecodeError:
                state.error = "Invalid JSON in arguments"
        return state


class ToolManager:
    def __init__(self):
        self.tools = {}
        self.reload()

    def reload(self):
        importlib.reload(tools)
        self.tools = {
            name: {'func': obj, 'desc': (obj.__doc__ or "No description").strip()}
            for name, obj in inspect.getmembers(tools) if inspect.isfunction(obj)
        }

    def get_descriptions(self) -> str:
        return "\n".join([f"- {n}: {d['desc']}" for n, d in self.tools.items()])

    def execute(self, name, args):
        if name not in self.tools:
            return f"[ERROR] Tool '{name}' not found"
        try:
            return str(self.tools[name]['func'](**args))
        except Exception as e:
            return f"Error executing {name}: {str(e)}"


class LogManager:
    def __init__(self, config):
        self.config = config
        self.log_file = self.init_log()

    def init_log(self, path=None):
        if path is None:
            os.makedirs(self.config.LOG_DIR, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(self.config.LOG_DIR, f'chat_{ts}.md')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f'# Session {ts}\n\n')
        else:
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(path, 'a', encoding='utf-8') as f:
                f.write(f'\n\n# Session {ts}\n\n')
        return path

    def log(self, role: str, content: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = ""
        if role == "User":
            log_entry = f"\n\n## 👤 User ({timestamp})\n\n{content}\n"
        elif role == "Agent":
            log_entry = f"\n\n### 🤖 Agent ({timestamp})\n\n```xml\n{content}\n```\n"
        elif role == "System":  # 通常是 Observation
            log_entry = f"\n\n> 🛠️ **System/Observation** ({timestamp})\n\n```\n{content}\n```\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[Log Error] Could not write to log file: {e}")
