from openai import AsyncOpenAI
from src.config import settings
from src.utils import LogManager, Context
from copy import deepcopy
import importlib
import os


class ReactAgent:
    def __init__(self, tool_manager):
        self.client = AsyncOpenAI(api_key=os.environ["DASHSCOPE_API_KEY"],
                                  base_url=r"https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.tool_manager = tool_manager
        self.context = Context(settings)
        self.logger = LogManager('logs')
        self.current_plan = "暂无计划 (No Plan Yet)"
        self.total_tokens = 0
        self.reset(False)

    def reset(self, reload_tools=True):
        self.context.reset(self._build_system_prompt())
        self.current_plan = "暂无计划 (No Plan Yet)"
        self.logger.init_log()
        if reload_tools:
            self.reload_toolset()

    def reload_toolset(self):
        self.tool_manager.reload()
        if self.context():
            self.context.append("system", self._build_system_prompt())
        else:
            self.context.append("system", self._build_system_prompt())

    def load_history(self, history_path):
        self.reset()
        with open(history_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = ''.join(lines)
        self.context.append(role='user', content=f'以下是对话记录：\n{str(lines)}')
        self.logger.init_log(history_path)

    def update_plan(self, new_plan: str):
        self.current_plan = new_plan
        if self.context() and self.context()[0]['role'] == 'system':
            self.context()[0]['content'] = self._build_system_prompt()

    def _build_system_prompt(self):
        from src import system_instructions
        importlib.reload(system_instructions)
        REACT_SYSTEM_PROMPT = system_instructions.sys_prompt
        descriptions = self.tool_manager.get_descriptions()
        structure = self.tool_manager.get_tools_structure()
        return deepcopy(REACT_SYSTEM_PROMPT).replace('{tool_descriptions}', descriptions)\
            .replace('{tool_structure}', structure)\
            .replace('{current_plan}', self.current_plan)
    
    async def model(self, user_input, name='qwen-plus', stream=True):
        if len(self.context) % 50 == 0:
            self.context.refresh(self._build_system_prompt())
        self.context.append(role="user", content=user_input)
        self.logger.log("User", user_input)
        if self.context.compress():
            self.logger.log("System", "History compressed.")
        return await self.client.chat.completions.create(model=name, messages=self.context(), stream=stream, stream_options={"include_usage": True})

    async def step_stream(self, user_input):
        response_stream = await self.model(user_input)
        full_content = ""

        async for chunk in response_stream:
            text = ""
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
            
            if text:
                full_content += text
                yield text
            
            if hasattr(chunk, 'usage') and chunk.usage is not None:
                self.total_tokens += chunk.usage.total_tokens

        self.context.append(role="assistant", content=full_content)
        self.logger.log("Agent", full_content)
        # return full_content

    def add_observation(self, content):
        msg = f'[Observation]: {content}'
        self.context.append(role="user", content=msg)
        self.logger.log("System", msg)
