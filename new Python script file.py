import subprocess
import time
import re
import os
import sys

# ========================= 配置区 =========================
# 1. 你的 cf.exe 所在路径
CF_EXE_PATH = "../cf.exe"

# 2. 你的 GitHub 本地仓库文件夹路径
REPO_PATH = "E:/cf/网站方案"

# 3. 你的 GitHub 分支名
BRANCH_NAME = "main"

# 4. 如果系统找不到 git，请在这里填入你电脑上 git.exe 的准确路径
# 常用路径通常是 C:/Program Files/Git/bin/git.exe
CUSTOM_GIT_PATH = r"C:\Program Files\Git\bin\git.exe"
# =========================================================

def get_git_command():
    """检测系统中可用的 git 指令"""
    try:
        # 尝试直接运行 git
        subprocess.run(["git", "--version"], capture_output=True)
        return "git"
    except FileNotFoundError:
        # 如果直接运行失败，尝试使用手动指定的路径
        if os.path.exists(CUSTOM_GIT_PATH):
            return CUSTOM_GIT_PATH
        else:
            print("❌ 错误：在系统 Path 和指定路径中都找不到 git.exe")
            print("请确认是否安装了 Git，或者在配置区修改 CUSTOM_GIT_PATH")
            sys.exit()

def start_tunnel():
    print(">>> [步骤 1/2] 正在启动 Cloudflare 隧道...")
    if os.path.exists("tunnel.log"):
        try: os.remove("tunnel.log")
        except: pass
    
    try:
        log_file = open("tunnel.log", "w", encoding="utf-8")
        cmd = [CF_EXE_PATH, "tunnel", "--url", "http://127.0.0.1:1145", "--protocol", "http2"]
        process = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
    except Exception as e:
        print(f"❌ 启动 cf.exe 失败: {e}")
        sys.exit()

    print(">>> 正在等待隧道分配地址...")
    start_time = time.time()
    while True:
        time.sleep(1)
        if os.path.exists("tunnel.log"):
            with open("tunnel.log", "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', content)
                if match:
                    url = match.group(0)
                    print(f"✅ 成功捕获地址: {url}")
                    return url, process, log_file
        
        if time.time() - start_time > 30:
            print("❌ 隧道启动超时！")
            process.terminate()
            sys.exit()

def sync_to_github(target_url):
    print(f"\n>>> [步骤 2/2] 正在同步到 GitHub Pages...")
    git_cmd = get_git_command()
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url={target_url}">
    <script>window.location.replace("{target_url}");</script>
    <title>跳转中...</title>
</head>
<body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;font-family:sans-serif;">
    <div style="border:3px solid #333;border-top:3px solid #3498db;border-radius:50%;width:30px;height:30px;animation:spin 1s linear infinite;"></div>
    <p>正在进入 1050 Ti 影院...</p>
    <style>@keyframes spin {{0% {{transform:rotate(0deg);}} 100% {{transform:rotate(360deg);}}}}</style>
</body>
</html>"""

    try:
        if not os.path.exists(REPO_PATH):
            print(f"❌ 仓库路径不存在: {REPO_PATH}")
            return
            
        # 记录原始目录，执行完后切回来
        original_dir = os.getcwd()
        os.chdir(REPO_PATH)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_template)
        print("✅ 本地 index.html 已更新")

        print(f">>> 正在通过 {git_cmd} 推送到 GitHub...")
        # 执行 Git 指令
        subprocess.run([git_cmd, "add", "index.html"], check=True, capture_output=True)
        # 使用时间戳作为 commit 信息防止重复提交报错
        commit_msg = f"update tunnel: {time.strftime('%H:%M:%S')}"
        subprocess.run([git_cmd, "commit", "-m", commit_msg], check=True, capture_output=True)
        subprocess.run([git_cmd, "push", "origin", BRANCH_NAME], check=True, capture_output=True)
        
        print("🚀 GitHub 推送成功！")
        os.chdir(original_dir)

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败！可能是网络问题或未登录 Git。")
        if e.stderr:
            print(f"详情: {e.stderr.decode('gbk', errors='ignore')}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    try:
        new_url, proc, log_f = start_tunnel()
        sync_to_github(new_url)
        print("\n影院运行中... (保持此窗口开启，按 Ctrl+C 停止)")
        proc.wait()
    except KeyboardInterrupt:
        print("\n正在关闭影院服务...")
        proc.terminate()
        log_f.close()
