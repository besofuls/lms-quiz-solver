import asyncio
import http.server
import os
import socket
import socketserver
import sys
import threading
from dotenv import load_dotenv

# Đảm bảo UTF-8 trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from browser_use import Agent, Browser, ChatGoogle

load_dotenv()

def start_local_server_if_needed(target: str):
    """
    Nếu người dùng truyền vào đường dẫn file HTML cục bộ, tự động khởi động
    server HTTP cục bộ (localhost) để browser-use truy cập an toàn.
    """
    clean_target = target.replace("file:///", "").replace("file://", "").strip()
    if os.path.exists(clean_target) and clean_target.endswith(".html"):
        directory = os.path.dirname(os.path.abspath(clean_target))
        filename = os.path.basename(clean_target)
        
        # Tìm port trống
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            port = s.getsockname()[1]

        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
            def log_message(self, format, *args):
                pass  # Tắt log stdout của server

        server = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        
        url = f"http://127.0.0.1:{port}/{filename}"
        print(f"📦 Đã tạo máy chủ nội bộ: {url}")
        return url, server
    return target, None

async def run_quiz(target_url: str, custom_instruction: str = ""):
    url, server = start_local_server_if_needed(target_url)

    # 1. Khởi tạo Gemini model tốc độ cao
    # gemini-3.5-flash-lite / gemini-flash-lite-latest phản hồi < 1 giây
    llm = ChatGoogle(model="gemini-3.5-flash-lite")

    # 2. Khởi tạo Trình duyệt trực quan (headless=False để xem trực tiếp)
    browser = Browser(
        headless=False,
        disable_security=True,
    )

    # 3. Yêu cầu tác vụ giải quiz
    task_prompt = f"""
    1. Truy cập vào trang: {url}
    2. Đọc kỹ tất cả câu hỏi và các lựa chọn đáp án trên màn hình.
    3. Chọn đáp án chính xác nhất cho từng câu hỏi (click vào radio button hoặc checkbox tương ứng).
    4. Nhấn nút "Nộp bài" hoặc "Submit" khi đã chọn xong.
    5. Đọc kết quả / số điểm hiển thị trên màn hình và báo cáo lại chi tiết câu nào đúng câu nào sai nếu có.

    Yêu cầu bổ sung:
    {custom_instruction}
    """

    print("\n" + "="*50)
    print("🚀 Đang khởi động AI Agent để giải Quiz...")
    print(f"🎯 URL: {url}")
    print("="*50 + "\n")

    agent = Agent(
        task=task_prompt,
        llm=llm,
        browser=browser,
        use_vision=True,
        use_thinking=False,  # Tắt thinking mode để phản hồi nhanh tức thì
    )

    try:
        history = await agent.run()
        print("\n" + "="*50)
        print("🏁 Báo cáo kết quả của Agent:")
        print(history.final_result())
        print("="*50 + "\n")
    finally:
        await browser.close()
        if server:
            server.shutdown()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("👉 Nhập link bài Quiz (Web URL hoặc file HTML): ").strip()
    
    if target:
        asyncio.run(run_quiz(target))
    else:
        print("❌ Chưa nhập link.")
