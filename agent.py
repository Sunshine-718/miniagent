from openai import OpenAI
from config import settings
from system_instructions import REACT_SYSTEM_PROMPT
from utils import LogManager


class ReactAgent:
    def __init__(self, tool_manager):
        self.client = OpenAI(api_key=settings.API_KEY, base_url=settings.BASE_URL)
        self.tool_manager = tool_manager
        self.logger = LogManager(settings)
        self.history = []
        self.reset()

    def reset(self):
        self.history = [{'role': 'system', 'content': self._build_system_prompt()}]
        self.logger.init_log()
        self.reload_toolset()

    def reload_toolset(self):
        self.tool_manager.reload()
        if self.history:
            self.history[0] = {'role': 'system', 'content': self._build_system_prompt()}
        else:
            self.history = [{'role': 'system', 'content': self._build_system_prompt()}]

    def load_history(self, history_path):
        self.reset()
        with open(history_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = ''.join(lines)
        self.history.append({'role': 'user', 'content': f'以下是对话记录：\n{str(lines)}'})
        self.logger.init_log(history_path)

    def _build_system_prompt(self):
        return REACT_SYSTEM_PROMPT.replace('{tool_descriptions}', self.tool_manager.get_descriptions())

    def _compress_history(self):
        total_len = sum(len(m['content']) for m in self.history) // 3
        if total_len < settings.TOKEN_LIMIT:
            return

        sys_msg = self.history[0]
        first_round = []
        if len(self.history) >= 3:
            first_round = self.history[1:3]  # User + Agent
        retain_count = settings.RETAIN_RECENT * 2
        recent = self.history[-retain_count:]

        if len(self.history) > 3 + retain_count:
            omission_hint = {'role': 'system',
                             'content': '[System Note: Middle conversation history compressed/omitted to save memory]'}
            self.history = [sys_msg] + first_round + [omission_hint] + recent
        else:
            self.history = [sys_msg] + self.history[-retain_count:]

        self.logger.log("System", "History compressed.")

    def step_stream(self, user_input):
        self.history.append({'role': 'user', 'content': user_input})
        self.logger.log("User", user_input)
        self._compress_history()

        response_stream = self.client.chat.completions.create(
            model='deepseek-chat', messages=self.history, stream=True
        )

        full_content = ""

        for chunk in response_stream:
            text = chunk.choices[0].delta.content
            if text:
                full_content += text
                yield text

        self.history.append({'role': 'assistant', 'content': full_content})
        self.logger.log("Agent", full_content)
        return full_content

    def add_observation(self, content):
        msg = f'Observation: {content}'
        self.history.append({'role': 'user', 'content': msg})
        self.logger.log("System", msg)
