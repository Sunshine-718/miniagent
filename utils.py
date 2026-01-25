import os
import re
import json
import importlib
import inspect
from states import AgentState, Tags
import tools
import datetime


class Parser:
    @classmethod
    def parse_response(cls, text: str):
        state = AgentState()

        text = text.replace('\r\n', '\n')

        # 一次性提取所有 "## Title" -> "Content" 的键值对
        pattern = re.compile(
            r'(?m)^##\s*(?P<header>.+?)\s*$(?P<content>[\s\S]*?)(?=^##|\Z)'
        )

        sections = {
            m.group('header').strip().lower(): m.group('content').strip()
            for m in pattern.finditer(text)
        }

        state.plan = sections.get('plan')
        state.thought = sections.get('thought')
        state.final_answer = sections.get('answer')

        action_raw = sections.get('action')
        if action_raw:
            state.action_name = action_raw.split('\n')[0].strip()
            if state.action_name == "[REFRESH]":
                state.is_refresh = True

        args_raw = sections.get('args')
        if args_raw and state.action_name:
            code_match = re.search(r'```(?:json|python)?\s*(.*?)```', args_raw, re.DOTALL)
            if code_match:
                content = code_match.group(1).strip()
                if state.action_name == "python_repl":
                    state.action_args = {"code": content}
                else:
                    try:
                        state.action_args = json.loads(content)
                    except json.JSONDecodeError:
                        state.error = "Args JSON 解析失败"
            else:
                if state.action_name == 'python_repl':
                    state.action_args = {"code": args_raw}
                elif not args_raw.strip():
                    state.action_args = {}
                else:
                    try:
                        state.action_args = json.loads(args_raw)
                    except:
                        state.error = "未找到代码块 (```) 且无法解析JSON"
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
        self.init_log()

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
        self.log_file = path
        return self

    def log(self, role: str, content: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = ""
        if role == "User":
            log_entry = f"\n\n## 👤 User ({timestamp})\n\n{content}\n"
        elif role == "Agent":
            log_entry = f"\n\n### 🤖 Agent ({timestamp})\n\n```\n{content}\n```\n"
        elif role == "System":  # 通常是 Observation
            log_entry = f"\n\n> 🛠️ **System/Observation** ({timestamp})\n\n```\n{content}\n```\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[Log Error] Could not write to log file: {e}")
