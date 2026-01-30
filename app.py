import chainlit as cl
from src import settings, ToolManager, Parser, ReactAgent
from datetime import datetime
import os
import sys
import shutil
import asyncio


UPLOAD_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(UPLOAD_DIR, exist_ok=True)
tools = ToolManager()
agent = ReactAgent(tools)


async def setup_wizard():
    """Web版配置向导"""
    await cl.Message(content="👋 **欢迎使用 Axiom Agent！**\n\n检测到您是首次运行，我们需要进行一些简单的初始化配置。\n\n请在下方对话框输入API key", author="System").send()

    config_data = {}

    # 1. DeepSeek Key (必填)
    res = await cl.AskUserMessage(content="请配置 **DeepSeek API Key** (必填)\n您可以访问 [Deepseek 控制台](https://platform.deepseek.com/api_keys) 获取。", timeout=600).send()
    if not res:
        await cl.Message(content="❌ 配置超时或取消，请刷新页面重试。").send()
        return False
    config_data["DEEPSEEK_API_KEY"] = res["output"].strip()

    # 2. Jina Token (可选)
    res = await cl.AskUserMessage(content="请配置 **Jina API Token** (可选，强烈推荐)\n用于联网搜索功能。如果不需要，请直接回复 `skip` 或 `跳过`。", timeout=600).send()
    if res and res["output"].strip().lower() not in ["skip", "跳过"]:
        config_data["JINA_API_TOKEN"] = res["output"].strip()
    else:
        config_data["JINA_API_TOKEN"] = "<Replace me>"  # 或者你的模板默认值

    # 3. QQ Email (可选)
    res = await cl.AskUserMessage(content="请配置 **QQ 邮箱** (可选)\n用于发送邮件通知。如果不配置，请回复 `skip`。", timeout=600).send()
    if res and res["output"].strip().lower() not in ["skip", "跳过"]:
        config_data["QQ_EMAIL"] = res["output"].strip()

        # 如果填了邮箱，接着问授权码
        res_code = await cl.AskUserMessage(content="请输入 **QQ 邮箱授权码**", timeout=600).send()
        if res_code:
            config_data["QQ_EMAIL_AUTH_CODE"] = res_code["output"].strip()
    else:
        config_data["QQ_EMAIL"] = "<Replace me>"
        config_data["QQ_EMAIL_AUTH_CODE"] = "<Replace me>"

    # 4. 生成 .env 文件
    env_content = ""
    # 读取模板（如果存在）来保持格式，或者直接写入
    try:
        # 这里为了简单直接生成，你也可以读取 .env.template 做替换
        for key, value in config_data.items():
            env_content += f"{key}={value}\n"

        # 写入文件
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        await cl.Message(content="✅ `.env` 配置文件生成成功！", author="System").send()


        msg = cl.Message(
            content="✅ **环境配置已完成！**\n\n为了确保配置文件生效，请点击下方链接刷新页面：\n\n👉 [**🔄 点击此处刷新页面 (Refresh)**](/)\n\n(刷新后将直接进入对话界面)", 
            author="System"
        )
        await msg.send()

        return True

    except Exception as e:
        await cl.Message(content=f"❌ 写入配置失败: {str(e)}", author="System").send()
        return False


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="介绍自己",
            message="你好，请介绍一下你自己，以及你可以使用哪些工具？",
            # icon="/public/learn.svg",
        ),
        cl.Starter(
            label="查询余额",
            message="帮我检查一下当前 DeepSeek API 的余额。",
        ),
        cl.Starter(
            label="今天新闻",
            message="请帮我看看今天有什么新闻。",
        ),
        cl.Starter(
            label="查询记忆",
            message="查询一下你记忆数据库中关于我的信息。",
        ),
        cl.Starter(
            label="查看缓存日志",
            message="看看现在有多少条日志缓存"
        ),
        cl.Starter(
            label="玩游戏",
            message="我们来玩游戏吧！"
        ),
        cl.Starter(
            label="塔罗牌",
            message="帮我用三张塔罗牌占卜一下"
        ),
    ]


@cl.on_chat_start
async def start():
    if not os.path.exists(".env"):
        success = await setup_wizard()
        return

    try:
        import src
        src.config.settings.validate()
    except Exception as e:
        await cl.Message(content=f"⚠️ **配置验证失败**: {str(e)}\n\n请检查 `.env` 文件格式，或删除该文件后刷新页面重新配置。", author="System").send()
        return
    try:
        agent.reset()
        cl.user_session.set("agent", agent)
        cl.user_session.set("tools", tools)
    except Exception as e:
        await cl.Message(content=f"❌ Agent 初始化失败: {str(e)}", author="System").send()


@cl.on_message
async def main(message: cl.Message):

    agent: ReactAgent = cl.user_session.get("agent")
    tools: ToolManager = cl.user_session.get("tools")

    if not agent:
        await cl.Message(content="⚠️ Agent 未初始化，请检查配置或刷新页面。", author="System").send()
        return

    current_prompt = message.content

    if message.elements:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_notifications = []

        async with cl.Step(name="File Upload", type="system") as step:
            step.input = f"Received {len(message.elements)} file(s)"

            for element in message.elements:
                if hasattr(element, "path") and element.path:
                    target_path = os.path.join(UPLOAD_DIR, element.name)
                    shutil.copy(element.path, target_path)
                    info = f"File: '{element.name}' saved to: '{target_path}'"
                    file_notifications.append(info)
            step.output = "\n".join(file_notifications)

        if file_notifications:
            system_note = (
                "\n\n[SYSTEM NOTIFICATION]\n"
                "User has uploaded the following files to your workspace.\n"
                "You can inspect/read them using your file tools:\n"
            )
            for note in file_notifications:
                system_note += f"- {note}\n"

            current_prompt += system_note

            if not message.content:
                current_prompt += "\nPlease analyze the uploaded files(s)."

    step_count = 0
    try:
        while True:
            step_count += 1

            system_injection = (
                f"\n[CURRENT STEP: {step_count}]"
                f"\n[CURRENT TIME: {datetime.now()}]"
                f"\n[ESTIMATED NUM TOKEN USED: {agent.est_num_token}]"
            )

            full_response = ""
            answer_marker = "@@@ Answer"
            has_sent_answer_msg = False
            previous_answer_len = 0

            msg = cl.Message(content="", author="Axiom")

            async with cl.Step(name=f"Step {step_count}: Reasoning", type="process") as step:
                async for chunk in agent.step_stream(current_prompt + system_injection):
                    full_response += chunk

                    marker_index = full_response.find(answer_marker)

                    if marker_index != -1:
                        cleaning_reasoning = full_response[:marker_index].strip()
                        step.output = cleaning_reasoning
                        await step.update()

                        # 提取答案内容并发送给主聊天框
                        content_start_index = marker_index + len(answer_marker)
                        full_answer_text = full_response[content_start_index:].lstrip()
                        new_content = full_answer_text[previous_answer_len:]
                        if new_content:
                            if not has_sent_answer_msg:
                                await msg.send()    # 第一次有答案时才发送消息框
                                has_sent_answer_msg = True
                            await msg.stream_token(new_content)  # 流式传输
                            previous_answer_len += len(new_content)
                    elif "@@@ Action" in full_response and "@@@ Args" in full_response:
                        args_index = full_response.find("@@@ Args")
                        next_marker_index = full_response.find("@@@", args_index + len("@@@ Args"))
                        if next_marker_index != -1:
                            full_response = full_response[:next_marker_index].strip()
                            break
                    else:
                        await step.stream_token(chunk)  # 还在思考阶段，输出到step

            if has_sent_answer_msg:
                await msg.update()

            state = Parser.parse_response(full_response)

            if state.plan:
                agent.update_plan(state.plan)

            if state.final_answer:
                break

            if state.is_quit:
                break

            if state.is_clear:
                agent.reset()
                await cl.Message(content="🧹 记忆已清除", author="System").send()
                break

            if state.is_refresh:
                agent.reload_toolset()
                info_msg = "Observation: Tools reloaded successfully."
                async with cl.Step(name="System", type="system") as step:
                    step.output = info_msg
                current_prompt = info_msg
                continue

            if state.error:
                error_msg = f"Observation: Error: {state.error}. Please reflect and retry."
                async with cl.Step(name="Error", type='error') as step:
                    step.output = state.error
                current_prompt = error_msg
                continue

            if state.has_action:
                action_result = ""
                async with cl.Step(name=state.action_name, type="tool") as step:
                    step.input = state.action_args or {}

                    action_result = await cl.make_async(tools.execute)(
                        state.action_name,
                        state.action_args or {}
                    )
                    step.output = action_result

                async with cl.Step(name="Observation", type="tool") as step:
                    step.output = action_result

                agent.add_observation(action_result)

                current_prompt = "Observation: (see history for result)"

            if not state.has_action and not state.final_answer:
                hint_msg = "System Hint: You stopped without an Action or Answer. Please continue properly using '## Thought' or '## Action' sections."
                async with cl.Step(name="System Hint", type="error") as step:
                    step.output = hint_msg
                current_prompt = hint_msg
    except asyncio.CancelledError:
        agent.add_observation(
            f"\n[SYSTEM]: The user interrupted the process at step {step_count}. "
            "Waiting for new instructions."
        )
        await cl.Message(
            content="⏸️ **操作已暂停**。您可以直接输入新的指令，我会基于当前的上下文继续。",
            author="System"
        ).send()
        return
