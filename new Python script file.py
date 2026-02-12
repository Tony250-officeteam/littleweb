import os
import subprocess

def push_to_github(new_url, repo_path):
    # 1. 生成新的 index.html (覆盖旧的)
    html_content = f'<html><head><meta http-equiv="refresh" content="0;url={new_url}"></head>' \
                   f'<body><script>window.location.replace("{new_url}");</script></body></html>'
    
    with open(os.path.join(repo_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 2. 自动 Git 推送
    try:
        os.chdir(repo_path)
        # 强制添加 index.html 并提交
        subprocess.run(["git", "add", "index.html"], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update tunnel URL"], check=True)
        # 推送到主分支 (可能是 main 或 master)
        subprocess.run(["git", "push", "origin", "main"], check=True) 
        print("✅ GitHub 传送门已更新！")
    except Exception as e:
        print(f"❌ 推送失败: {e}")
