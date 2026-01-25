import tools
from system_instructions import REACT_SYSTEM_PROMPT
from constants import Tags
import os
import re
from openai import OpenAI
import inspect
import datetime
import importlib
import config  # 导入配置模块
from utils import *

# --- 引入 Rich 库进行美化 ---
from rich.console import Console
from rich.theme import Theme

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

class ReactAgent:
    def __init__(self):
        self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)
        self.history = []
        self.tools = {}
        self.token_limit = 100000
        self.retain_recent = 4
        self.log_dir = 'logs'
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = os.path.join(self.log_dir, f'chat_{timestamp}.md')
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f'# Chat Session: {timestamp}\n\n')
        self.clear_history()
    
    def append_log(self, role: str, text: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = ""
        if role == "User":
            log_entry = f"\n\n## 👤 User ({timestamp})\n\n{text}\n"
        elif role == "Agent":
            log_entry = f"\n\n### 🤖 Agent ({timestamp})\n\n```xml\n{text}\n```\n"
        elif role == "System": # 通常是 Observation
            log_entry = f"\n\n> 🛠️ **System/Observation** ({timestamp})\n\n```\n{text}\n```\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[Log Error] Could not write to log file: {e}")

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
