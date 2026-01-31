import os
import re
import json
import importlib
import inspect
from src.states import AgentState
import datetime
from src import tools


class Parser:
    @classmethod
    def parse_response(cls, text: str):
        state = AgentState()

        text = text.replace('\r\n', '\n')

        # 一次性提取所有 "@@@ Title" -> "Content" 的键值对
        pattern = re.compile(
            r'(?m)^@@@\s*(?P<header>.+?)\s*$(?P<content>[\s\S]*?)(?=^@@@\s|\Z)'
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
            elif state.action_name == "[QUIT]":
                state.is_quit = True
            elif state.action_name == "[CLEAR]":
                state.is_clear = True

        args_raw = sections.get('args')
        if args_raw and state.action_name:
            content = args_raw.strip()
            if state.action_name == "python_repl":
                match = re.search(r'~~~\s*(?:python)?\s*(.*?)~~~', content, re.DOTALL)
                if match:
                    state.action_args = {"code": match.group(1).strip()}
                else:
                    clean_code = content.strip()
                    
                    if clean_code.startswith("~~~"):
                        clean_code = clean_code[3:]
                    if clean_code.endswith("~~~"):
                        clean_code = clean_code[:-3]
                    
                    clean_code = clean_code.strip()

                    if clean_code.lower().startswith("python"):
                        clean_code = clean_code[6:].strip()
                    state.action_args = {'code': clean_code}
            else:
                if not content:
                    state.action_args = {}
                else:
                    try:
                        state.action_args = json.loads(content)
                    except Exception as e:
                        state.error = f"Args Parse Failed: {str(e)}"
                    
        return state


class Context:
    def __init__(self, config):
        self.config = config
        self.context = {"messages": []}
    
    def __len__(self):
        return len(self.context["messages"])
    
    def __call__(self):
        return self.context["messages"]
    
    def reset(self, system_prompt):
        self.context = {"messages": [{"role": "system", "content": system_prompt}]}
    
    def refresh(self, system_prompt):
        self.append("system", system_prompt)
    
    def append(self, role, content):
        self.context["messages"].append(dict(role=role, content=content))
    
    def compress(self):
        total_len = sum(len(m['content']) for m in self.context["messages"]) // 3
        self.est_num_token = total_len
        if total_len < self.config.TOKEN_LIMIT:
            return False

        sys_msg = self.context["messages"][0]
        first_round = []
        if len(self.context["messages"]) >= 3:
            first_round = self.context["messages"][1:3]  # User + Agent
        retain_count = self.config.RETAIN_RECENT * 2
        recent = self.context["messages"][-retain_count:]

        if len(self.context["messages"]) > 3 + retain_count:
            omission_hint = {'role': 'system',
                             'content': '[System Note: Middle conversation history compressed/omitted to save memory]'}
            self.context["messages"] = [sys_msg] + first_round + [omission_hint] + recent
        else:
            self.context["messages"] = [sys_msg] + recent
        return True
                        

class ToolManager:
    def __init__(self):
        self.tools = {}
        self.refresh_list()

    def refresh_list(self):
        """只更新工具列表，不重载模块文件"""
        self.tools = {
            name: {'func': obj, 'desc': (obj.__doc__ or "No description").strip()}
            for name, obj in inspect.getmembers(tools) if inspect.isfunction(obj)
        }
    
    def reload(self):
        """强制从磁盘重载代码"""
        importlib.reload(tools)
        self.refresh_list()

    def get_descriptions(self) -> str:
        return "\n".join([f"- {n}: {d['desc']}" for n, d in self.tools.items()])
    
    def get_tools_structure(self):
        base_path = os.path.join(os.path.dirname(__file__), 'tools')
        tree_str = 'src/tools/\n'

        for root, dirs, files in os.walk(base_path):
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            
            level = root.replace(base_path, "").count(os.sep)
            indent = " " * 4 * (level + 1)

            if root != base_path:
                folder_name = os.path.basename(root)
                tree_str += f"{" " * 4 * level}|-- {folder_name}/\n"
            
            for f in files:
                if f.endswith('.py') and f != "__init__.py":
                    tree_str += f"{indent}|-- {f}\n"
        return tree_str.strip()
            

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

    def init_log(self, path=None):
        if path is None:
            os.makedirs("logs", exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join("logs", f'chat_{ts}.md')
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
            if not os.path.exists("logs"):
                os.mkdir("logs")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[Log Error] Could not write to log file: {e}")
