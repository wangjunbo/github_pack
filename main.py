import webview
import threading
import time
import os
import sys

def resource_path(relative_path):
    """获取 PyInstaller 打包后的资源路径"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

# 定义 Python API，供 JS 调用
class Api:
    def say_hello(self, name):
        print(f"[Python] JS 调用了 say_hello('{name}')")
        return f"Hello, {name}! (from Python)"

def run_js(window):
    # 等待窗口初始化完成
    time.sleep(3)
    # 主动执行 JS
    print("[Python] 调用 JS 函数 showMessage()")
    window.evaluate_js("showMessage('Python 主动发来的消息！')")

if __name__ == "__main__":
    api = Api()
    html_file = resource_path("index.html")

    window = webview.create_window("PyWebView 双向通信 Demo", html_file, js_api=api)

    # 启动后台线程，模拟 Python 主动发消息
    threading.Thread(target=run_js, args=(window,), daemon=True).start()

    webview.start()
