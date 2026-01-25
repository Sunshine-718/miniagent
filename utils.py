import re
import json
from constants import Tags


def get_tag_regex(open_tag, close_tag):
    return re.escape(open_tag) + r'(.*?)(' + re.escape(close_tag) + r'|$)'


def parse_agent_response(response: str):
    """
    基于 XML 标签 [TAG]...[/TAG] 的解析器，边界严格，无歧义。
    """
    result = {
        "plan": None,
        "thought": None,
        "action": None,
        'action_input': None,
        'final_answer': None,
        'is_refresh': False,
        'retry': False
    }
    
    # 1. 提取 [PLAN] (新增)
    plan_match = re.search(get_tag_regex(*Tags.plan_tag), response, re.DOTALL)
    if plan_match:
        result['plan'] = plan_match.group(1).strip()

    # 2. 提取 [ANSWER]
    answer_match = re.search(get_tag_regex(*Tags.answer_tag), response, re.DOTALL)
    if answer_match:
        result['final_answer'] = answer_match.group(1).strip()

    # 3. 提取 [THOUGHT]
    thought_match = re.search(get_tag_regex(*Tags.thought_tag), response, re.DOTALL)
    if thought_match:
        result['thought'] = thought_match.group(1).strip()

    # 4. 提取 [ACTION]
    action_match = re.search(get_tag_regex(*Tags.action_tag), response, re.DOTALL)
    if action_match:
        result['action'] = action_match.group(1).strip()
        
        if '[REFRESH]' in result['action']:
            result['is_refresh'] = True
            return result

        # 5. 提取 [ARGS]
        args_match = re.search(get_tag_regex(*Tags.args_tag), response, re.DOTALL)
        if args_match:
            raw_input = args_match.group(1).strip()
            raw_input = re.sub(r'^```\w*\s*', '', raw_input)
            raw_input = re.sub(r'\s*```$', '', raw_input)
            try:
                result['action_input'] = json.loads(raw_input)
            except json.JSONDecodeError:
                result['action_input'] = None
                result['retry'] = True

    return result