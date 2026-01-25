class Tags:
    # 定义标签样式，想改的时候只需要改这里
    PLAN_OPEN = "<PLAN>"
    PLAN_CLOSE = "</PLAN>"
    plan_tag = (PLAN_OPEN, PLAN_CLOSE)
    
    THOUGHT_OPEN = "<THOUGHT>"
    THOUGHT_CLOSE = "</THOUGHT>"
    thought_tag = (THOUGHT_OPEN, THOUGHT_CLOSE)
    
    ACTION_OPEN = "<ACTION>"
    ACTION_CLOSE = "</ACTION>"
    action_tag = (ACTION_OPEN, ACTION_CLOSE)
    
    ARGS_OPEN = "<ARGS>"
    ARGS_CLOSE = "</ARGS>"
    args_tag = (ARGS_OPEN, ARGS_CLOSE)
    
    ANSWER_OPEN = "<ANSWER>"
    ANSWER_CLOSE = "</ANSWER>"
    answer_tag = (ANSWER_OPEN, ANSWER_CLOSE)

    # 汇总所有标签列表，方便做清理
    ALL_TAGS = [
        PLAN_OPEN, PLAN_CLOSE,
        THOUGHT_OPEN, THOUGHT_CLOSE,
        ACTION_OPEN, ACTION_CLOSE,
        ARGS_OPEN, ARGS_CLOSE,
        ANSWER_OPEN, ANSWER_CLOSE
    ]