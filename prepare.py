import os
import subprocess
import sys

try:
    import rich
except ModuleNotFoundError:
    result = subprocess.run(["pip", "install", "rich", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"安装失败！\n{result.stdout}\n{result.stderr}")

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.text import Text

# 初始化 Rich 控制台
console = Console()


def pip_install():
    install_cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", "requirements.txt",
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
    ]

    print()  # 空一行
    # 使用 rich 的 status 显示动态转圈效果
    with console.status("[bold green]正在初始化 Python 环境 (pip install)...[/]", spinner="dots") as status:
        try:
            # 使用 Popen 而不是 run，以便实时获取输出
            process = subprocess.Popen(
                install_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 确保 Windows 下中文不乱码
                bufsize=1          # 行缓冲
            )

            # 实时读取 stdout 更新状态栏文字
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # 去掉换行符，截取一部分长度防止刷屏太乱
                    clean_line = output.strip()[:80]
                    if clean_line:
                        # 动态更新状态栏文字，显示当前 pip 正在干什么
                        status.update(f"[bold green]正在安装依赖库...[/] [dim]{clean_line}[/]")

            # 等待进程完全结束
            return_code = process.poll()

            if return_code == 0:
                console.print(Panel("[bold green]所有环境配置及安装已成功完成！[/]", border_style="green"))
            else:
                # 获取错误日志
                stderr_output = process.stderr.read()
                console.print(Panel(f"[bold red]环境安装失败[/]\n错误详情:\n{stderr_output}", border_style="red"))

        except Exception as e:
            console.print(f"[bold red]执行 pip 安装时发生异常: {e}[/]")


def prepare():
    # 1. 检查文件是否存在
    if os.path.exists('.env'):
        # 这一步可以静默返回，也可以提示一下
        # console.print("[dim]环境配置文件 .env 已存在，跳过配置向导。[/]")
        return

    # 2. 显示欢迎面板
    welcome_text = Text("欢迎使用环境配置向导\n检测到首次运行，我们将协助您创建 .env 配置文件", justify="center")
    console.print(Panel(welcome_text, title="[bold green]初始化设置[/]", border_style="green", padding=(1, 2)))
    lines = []
    # 3. 读取模板并生成配置文件
    try:
        with open('.env.template', 'r', encoding='utf-8') as template:

            while True:
                line = template.readline()
                if not line:
                    break

                # 只处理包含 '=' 的行，保留注释和空行
                if '=' in line:
                    tmp = line.split('=')
                    key_name = tmp[0].strip()
                    user_value = ""

                    # 根据不同的 Key 进行美化询问
                    if key_name == 'DASHSCOPE_API_KEY':
                        console.print(f"\n[bold cyan]配置 {key_name}[/]")
                        console.print("请访问 [link=https://help.aliyun.com/zh/model-studio/get-api-key?spm=a2c4g.11186623.help-menu-2400256.d_2_0_0.1def6a1b9yDjg6]阿里云[/] 获取 Key")
                        user_value = Prompt.ask("请输入 API Key")  # password=True 可以隐藏输入内容

                    elif key_name == "JINA_API_TOKEN":
                        console.print(f"\n[bold cyan]配置 {key_name} (可选)[/]")
                        console.print("激活便捷 Agent 搜索功能: [link=https://jina.ai/zh-CN/]Jina AI 官网[/]")
                        user_value = Prompt.ask("请输入 Key [dim](按 Enter 跳过)[/]")

                    elif key_name == "QQ_EMAIL":
                        console.print(f"\n[bold cyan]配置 {key_name} (可选)[/]")
                        user_value = Prompt.ask("请输入 QQ 邮箱地址 [dim](按 Enter 跳过)[/]")

                    elif key_name == "QQ_EMAIL_AUTH_CODE":
                        console.print(f"\n[bold cyan]配置 {key_name} (可选)[/]")
                        console.print("请在 [link=https://wx.mail.qq.com/]QQ 邮箱设置[/] 中获取授权码")
                        user_value = Prompt.ask("请输入授权码 [dim](按 Enter 跳过)[/]")

                    else:
                        # 对于模板中未知的 Key，抛出异常或询问
                        console.print(f"[bold red]警告: 模板中存在未知配置项 {key_name}[/]")
                        raise ValueError(f"Unknown key: {key_name}")

                    # 处理空值（用户跳过的情况）
                    final_value = user_value.strip() if user_value.strip() else "<Replace me>"

                    # 写入文件
                    lines.append(f'{key_name}={final_value}\n')
                    console.print(f"[green]✔ {key_name} 已保存[/]")
                else:
                    # 非配置行直接写入（如注释）
                    lines.append(line)
        with open('.env', 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(line)
        console.print(Panel("配置文件的生成已完成，即将开始安装依赖...", style="bold blue"))
        pip_install()
    except FileNotFoundError:
        console.print("[bold red]错误：未找到 .env.template 模板文件！[/]")
        return
    except Exception as e:
        console.print(f"[bold red]配置过程中发生错误: {e}[/]")
        # 发生错误删除可能损坏的 .env
        if os.path.exists('.env'):
            os.remove('.env')
        return


if __name__ == "__main__":
    prepare()
