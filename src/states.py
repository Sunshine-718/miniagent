from dataclasses import dataclass
from typing import Optional, Dict, Any


class Tags:
    PLAN = "<PLAN>"
    THOUGHT = "<THOUGHT>"
    ACTION = "<ACTION>"
    ARGS = "<ARGS>"
    ANSWER = "<ANSWER>"

    ALL = [PLAN, THOUGHT, ACTION, ARGS, ANSWER]


@dataclass
class AgentState:
    plan: Optional[str] = None
    thought: Optional[str] = None
    action_name: Optional[str] = None
    action_args: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None
    is_refresh: bool = False
    error: Optional[str] = None

    @property
    def has_action(self):
        return bool(self.action_name)
    
    @property
    def is_finished(self):
        return bool(self.final_answer)