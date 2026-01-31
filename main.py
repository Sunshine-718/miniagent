from prepare import prepare
import asyncio

async def main():
    from pathlib import Path
    from src import ToolManager, Parser, ReactAgent, ConsoleUI
    from openai import APIConnectionError, AuthenticationError
    from datetime import datetime

    # 依赖注入
    tools = ToolManager()
    agent = ReactAgent(tools)
    ui = ConsoleUI()

    ui.rule("ReAct Agent Started")
    paused = ""

    while True:
        try:
            ui.rule("New Round")
            # 处理用户输入
            user_input = ui.input("Prompt > ")
            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit']:
                break
            
            # 命令处理
            if user_input.lower() == 'reset':
                agent.reset()
                ui.console.print("[yellow]Memory Cleared[/yellow]")
                continue
            elif user_input.lower() == 'reload':
                ui.console.print("[yellow]Reloading History[/yellow]")
                fname = input("请输入历史记录文件名 chat_**.md: ").strip()
                path = Path(f'./logs/{fname}')
                if path.exists():
                    agent.load_history(path)
                    ui.console.print("[yellow]History Reloaded[/yellow]")
                    continue
                else:
                    ui.console.print("[Red]History not exists[/Red]")
                    continue

            # --- ReAct 循环 ---
            current_prompt = paused + user_input
            paused = ""
            step = 0
            
            while True:
                step += 1
                ui.console.print(f"[dim]Step {step}[/dim]")

                # 构造 Prompt，直接读取 agent.usage (如果是第一轮则为 None)
                prompt_content = current_prompt + f"[CURRENT STEP: {step}]\n[CURRENT TIME: {datetime.now()}]\n[TOTAL TOKEN USAGE: {agent.total_tokens}]"

                # 1. 创建生成任务 (允许打断)
                # agent.step_stream 现在直接 yield 字符串
                gen_coro = ui.render_stream_loop(agent.step_stream(prompt_content))
                task = asyncio.create_task(gen_coro)

                full_response = ""
                try:
                    # 等待 UI 渲染完成
                    full_response = await task
                except KeyboardInterrupt:
                    # 【核心功能】捕获 Ctrl+C
                    task.cancel() # 取消正在进行的流式任务
                    try:
                        await task # 等待任务真正结束
                    except asyncio.CancelledError:
                        pass # 忽略取消异常
                    
                    ui.console.print("\n[yellow][System] Generation Interrupted by User.[/yellow]")
                    paused = "System Hint: User Interrupted the thought process manually.\n\n"
                    # 这里选择 break 跳出 ReAct 循环回到 Prompt 输入，还是 continue 取决于你想保留多少上下文
                    # 这里选择回到用户输入
                    break
                except Exception as e:
                    ui.print_error(f"Runtime Error: {e}")
                    break

                # 2. 解析响应
                state = Parser.parse_response(full_response)

                if state.plan:
                    agent.update_plan(state.plan)

                # 3. 分支处理
                if state.final_answer:
                    # 打印最终 Token 使用量
                    ui.console.print(f"[dim green]Total Tokens: {agent.total_tokens}[/dim green]")
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
                    agent.add_observation(result)
                    current_prompt = "Observation: (See history for result)"
                    ui.print_observation(current_prompt)

                if not state.has_action and not state.final_answer:
                    current_prompt = f"System Hint: You stopped without an Action or Answer. Please continue."
                    ui.print_observation(current_prompt)

        except KeyboardInterrupt:
            # 外层捕获：如果在输入阶段按 Ctrl+C
            ui.console.print("\n[yellow]Paused. Type 'quit' to exit.[/yellow]")
            continue
        except APIConnectionError:
            ui.print_error("无网络连接，正在退出...")
            break
        except AuthenticationError:
            ui.print_error("API key错误，请检查环境变量...")
            break

if __name__ == "__main__":
    prepare()
    asyncio.run(main())