from pathlib import Path
from src.config import settings
from src.utils import ToolManager, Parser
from src.agent import ReactAgent
from src.interface import ConsoleUI


def main():
    settings.validate()

    # 依赖注入
    tools = ToolManager()
    agent = ReactAgent(tools)
    ui = ConsoleUI()

    ui.rule("ReAct Agent Started")

    while True:
        try:
            ui.rule("New Round")
            user_input = ui.input()
            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit']:
                break
            if user_input.lower() == 'reset':
                agent.reset()
                ui.console.print("[yellow]Memory Cleared[/yellow]")
                continue
            elif user_input.lower() == 'reload':
                ui.console.print("[yellow]Reloading History[/yellow]")
                path = Path(f'./logs/{input("请输入历史记录文件名 chat_**.md: ").strip()}')
                if path.exists():
                    agent.load_history(path)
                    ui.console.print("[yellow]History Reloded[/yellow]")
                    continue
                else:
                    ui.console.print("[Red]History not exists[/Red]")
                    continue

            # 处理一轮对话中的多次 ReAct 循环
            current_prompt = user_input
            MAX_STEPS = 10000

            for step in range(MAX_STEPS):
                ui.console.print(f"[dim]Step {step + 1}[/dim]")

                # 1. Agent 思考并生成流
                response_stream = agent.step_stream(current_prompt)
                full_response = ui.render_stream_loop(response_stream)

                # 2. 解析响应
                state = Parser.parse_response(full_response)
                
                if state.plan:
                    agent.update_plan(state.plan)

                # 3. 各种分支处理
                if state.final_answer:
                    break

                if state.is_refresh:
                    agent.reload_toolset()
                    current_prompt = "Observation: Tools reloaded successfully."
                    ui.print_observation(current_prompt)
                    continue

                if state.error:
                    ui.print_error(state.error)
                    current_prompt = f"Observation: Error: {state.error}. Please reflect and retry."
                    ui.print_observation(current_prompt)
                    continue

                if state.has_action:
                    result = tools.execute(state.action_name, state.action_args or {})
                    ui.print_observation(result)
                    agent.add_observation(result)  # 写入历史
                    # 下一轮循环自动开始，无需修改 prompt，因为历史记录里已经有了 Observation
                    current_prompt = "Observation: (See history for result)"
                    ui.print_observation(current_prompt)

                if not state.has_action and not state.final_answer:
                    current_prompt = f"System Hint: You stopped without an Action or Answer. Please continue properly using '## Thought' or '## Action' sections."
                    ui.print_observation(current_prompt)

        except KeyboardInterrupt:
            ui.console.print("\n[yellow]Paused. Type 'quit' to exit or Enter to continue.[/yellow]")
            continue


if __name__ == "__main__":
    main()
