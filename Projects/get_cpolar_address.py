import subprocess
import re
import time
import signal
import sys
# 定义 tmux 会话和窗口名称
session_name = "cpolar_session"
window_name = "cpolar_window"
def signal_handler(sig, frame):
    print('Terminating tmux session...')
    subprocess.run(['tmux', 'kill-session', '-t', session_name])
    sys.exit(0)
# 注册信号处理函数，以便在脚本终止时关闭 tmux 会话
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
def run_cpolar_and_extract_url():
    # 打开一个新的终端窗口并启动 tmux 会话
    terminal_command = [
        'gnome-terminal', '--', 'tmux', 'new-session', '-s', session_name, '-n', window_name, './cpolar http 5000'
    ]
    # 使用 Popen 启动终端
    subprocess.Popen(terminal_command)
    # 定义正则表达式模式，匹配以 http 或 https 开头的网址
    url_pattern = re.compile(r'https?://[^\s]+')
    # 打印提示信息
    print("Attempting to extract URL...")
    url = None
    # 循环检查 tmux 窗口的输出，直到找到 URL 为止
    for _ in range(20):  # 尝试 20 次，每次间隔 1 秒
        time.sleep(1)
        # 使用 tmux capture-pane 命令获取 tmux 窗口的输出
        result = subprocess.run(['tmux', 'capture-pane', '-pt', f'{session_name}:{window_name}'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        # 使用正则表达式匹配 URL
        match = url_pattern.search(output)
        if match:
            url = match.group(0)
            break
    if url:
        print(f"Extracted URL: {url}")
    else:
        print("Failed to extract URL")
while True:
    run_cpolar_and_extract_url()
    print("Waiting for 5 minutes before next check...")
    time.sleep(5 * 60)  # 等待 5 分钟
