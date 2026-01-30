from prepare import prepare
import asyncio


async def main():
    from pathlib import Path
    from src import settings, ToolManager, Parser, ReactAgent, ConsoleUI
    from openai import APIConnectionError, AuthenticationError
    from datetime import datetime
    settings.validate()

    # 依赖注入
    tools = ToolManager()
    agent = ReactAgent(tools)
    ui = ConsoleUI()

    ui.rule("ReAct Agent Started")
    paused = ""

    while True:
        try:
            ui.rule("New Round")
            user_input = ui.input("Prompt > ")
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
            current_prompt = paused + user_input
            paused = ""
            step = 0
            while True:
                step += 1
                ui.console.print(f"[dim]Step {step + 1}[/dim]")

                # 1. Agent 思考并生成流
                response_stream = agent.step_stream(current_prompt + f"[CURRENT STEP: {step}]\n[CURRENT TIME: {datetime.now()}]\n[ESTIMATED NUM TOKEN USED: {agent.est_num_token}]")
                full_response = await ui.render_stream_loop(response_stream)

                # 2. 解析响应
                state = Parser.parse_response(full_response)

                if state.plan:
                    agent.update_plan(state.plan)

                # 3. 各种分支处理
                if state.final_answer:
                    break

                if state.is_quit:
                    exit()

                if state.is_clear:
                    agent.reset()
                    ui.print_observation("对话记录已清除")
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
            paused = "System Hint: User Interrupted.\n\n"
            continue
        except APIConnectionError:
            ui.print_error("无网络连接，正在退出...")
            break
        except AuthenticationError:
            ui.print_error("API key错误，请检查 .env 文件的 DEEPSEEK_API_KEY 行，正在退出")
            break


if __name__ == "__main__":
    prepare()
    asyncio.run(main())
