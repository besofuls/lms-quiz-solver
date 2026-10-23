import asyncio
import os
import socket
import subprocess
import sys
import time
from dotenv import load_dotenv

# Đảm bảo in UTF-8 không bị lỗi ký tự tiếng Việt trên Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from browser_use import Agent, Browser
from browser_use.llm.base import BaseChatModel
from browser_use.llm.google.chat import ChatGoogle

load_dotenv()

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9222
DEFAULT_URL = "https://lms-hcm.fpt.edu.vn/mod/quiz/attempt.php?attempt=227238&cmid=12365"

# Danh sách API Keys được nạp từ biến môi trường (.env)
API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1", os.getenv("GOOGLE_API_KEY", "")),
    os.getenv("GOOGLE_API_KEY_2", ""),
    os.getenv("GOOGLE_API_KEY_3", ""),
]
API_KEYS = [k.strip() for k in API_KEYS if k and k.strip()]

class MultiKeyChatGoogle(BaseChatModel):
    def __init__(self, api_keys: list[str], model="gemini-3.5-flash-lite"):
        self.api_keys = api_keys
        self.model = model
        self.clients = [ChatGoogle(model=model, api_key=k) for k in api_keys]
        self.current_idx = 0
        print(f"🔑 Đã kích hoạt chế độ ĐA API KEYS: Tổng cộng {len(self.clients)} tài khoản Google xoay tua liên tục!")

    @property
    def provider(self) -> str:
        return "google"

    @property
    def name(self) -> str:
        return self.model

    async def ainvoke(self, messages, output_format=None, **kwargs):
        attempts = 0
        total_keys = len(self.clients)
        
        while attempts < total_keys:
            client = self.clients[self.current_idx]
            key_num = self.current_idx + 1
            try:
                res = await client.ainvoke(messages, output_format=output_format, **kwargs)
                self.current_idx = (self.current_idx + 1) % total_keys
                return res
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    next_idx = (self.current_idx + 1) % total_keys
                    print(f"\n⚡ [Key {key_num}] Chạm hạn mức phút! LẬP TỨC chuyển sang Key {next_idx + 1} không cần chờ...")
                    self.current_idx = next_idx
                    attempts += 1
                else:
                    raise e
        
        return await self.clients[self.current_idx].ainvoke(messages, output_format=output_format, **kwargs)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def get_browser_executable(preferred="edge"):
    if preferred == "edge" and os.path.exists(EDGE_PATH):
        return EDGE_PATH, "Microsoft Edge"
    if os.path.exists(CHROME_PATH):
        return CHROME_PATH, "Google Chrome"
    if os.path.exists(EDGE_PATH):
        return EDGE_PATH, "Microsoft Edge"
    raise FileNotFoundError("Không tìm thấy trình duyệt Edge hoặc Chrome trên máy.")

def launch_browser_with_debug_port(url: str, browser_type="edge"):
    browser_path, browser_name = get_browser_executable(preferred=browser_type)
    
    if is_port_in_use(CDP_PORT):
        print(f"✅ Phát hiện {browser_name} đang mở sẵn với cổng điều khiển ({CDP_PORT})!")
        return None, browser_name

    user_data_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"{browser_type}_debug_profile")
    os.makedirs(user_data_dir, exist_ok=True)

    cmd = [
        browser_path,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        url
    ]
    print(f"🌐 Đang mở trình duyệt {browser_name}: {url}")
    proc = subprocess.Popen(cmd)
    time.sleep(2)
    return proc, browser_name

async def run_lms_quiz(target_url: str, browser_type="edge"):
    print("\n" + "=" * 65)
    print("🎓 HỆ THỐNG TỰ ĐỘNG GIẢI QUIZ BẰNG AI (EDGE + 3 GEMINI KEYS)")
    print(f"🎯 URL bài thi: {target_url}")
    print("=" * 65)

    launch_browser_with_debug_port(target_url, browser_type=browser_type)

    print("\n" + "!" * 65)
    print("👉 BƯỚC 1: Kiểm tra cửa sổ trình duyệt Edge.")
    print("👉 BƯỚC 2: Vào đúng trang câu hỏi bạn đang làm dở.")
    print("!" * 65)
    input("\n👉 Khi đã ở đúng câu hỏi trên màn hình, NHẤN ENTER ĐỂ AI BẮT ĐẦU: ")

    print("\n🚀 AI đang kết nối vào tab hiện tại và bắt đầu giải bài hết tốc lực...")

    # 1. Khởi tạo LLM đa Keys (Xoay tua 3 tài khoản Google)
    llm = MultiKeyChatGoogle(api_keys=API_KEYS, model="gemini-3.5-flash-lite")

    # 2. Cấu hình thời gian chờ chuẩn để chống trang trắng (Blank screen) khi mạng chậm
    browser = Browser(
        cdp_url=f"http://localhost:{CDP_PORT}",
        minimum_wait_page_load_time=2.2,     # Đợi 2.2 giây để server LMS tải xong câu hỏi mới 100%
        wait_for_network_idle_page_load_time=1.5, # Đợi mọi request mạng hoàn tất
        wait_between_actions=1.0,            # Nghỉ 1 giây giữa các thao tác
    )

    # 3. Prompt nghiêm ngặt: Tuyệt đối cấm hiểu nhầm trang trắng là hết bài
    task_prompt = """
    Bạn là trợ lý AI giải bài trắc nghiệm. Hãy tiếp tục giải từ trang câu hỏi đang mở trên màn hình.

    CẢNH BÁO CỰC KỲ QUAN TRỌNG VỀ TRANG TRẮNG / ĐANG TẢI (BLANK PAGE / LOADING):
    - Sau khi bấm 'Next page', mạng LMS FPT cần khoảng 1 đến 2 giây để tải câu hỏi tiếp theo.
    - NẾU NHÌN THẤY MÀN HÌNH TRẮNG, KHÔNG CÓ NỘI DUNG HOẶC ĐANG TẢI: ĐÓ LÀ TRANG ĐANG CHUYỂN TIẾP, KHÔNG PHẢI LÀ HẾT BÀI!
    - TUYỆT ĐỐI CẤM GỌI ACTION 'done' KHI MÀN HÌNH ĐANG TRẮNG HOẶC ĐANG TẢI! Hãy đợi hoặc nếu cần thì click nhẹ để trang hiển thị.

    CẢNH BÁO VỀ THANH MENU ĐIỀU HƯỚNG BÊN PHẢI:
    - Ở thanh bên phải (Quiz navigation) có dòng chữ 'Finish attempt', đó chỉ là menu điều hướng, KHÔNG PHẢI HẾT BÀI! Cấm click vào và không dừng lại.
    - Chừng nào vẫn còn câu hỏi (chứa nội dung câu hỏi, ô chọn A, B, C, D) thì BẮT BUỘC PHẢI TIẾP TỤC GIẢI.

    Quy trình từng câu:
    1. Đọc kỹ câu hỏi và các đáp án A, B, C, D.
    2. Chọn đáp án đúng nhất bằng cách click vào nút tròn (radio) hoặc ô vuông (checkbox).
    3. Click nút chuyển trang ('Next page', 'Next', 'Trang tiếp') để sang câu tiếp theo.
    4. Lặp lại liên tục cho đến câu cuối cùng.

    ĐIỀU KIỆN DUY NHẤT ĐỂ ĐƯỢC DỪNG BÀI:
    - Chỉ được dừng khi màn hình hiển thị BẢNG TỔNG KẾT TẤT CẢ CÂU HỎI (Summary of attempt) và HOÀN TOÀN KHÔNG CÒN CÂU HỎI NÀO NỮA.
    - Lúc này gọi action 'done' và TUYỆT ĐỐI KHÔNG bấm nút nộp bài chính thức.
    """

    agent = Agent(
        task=task_prompt,
        llm=llm,
        browser=browser,
        use_vision=True,
        use_thinking=False,
        use_judge=False,
        max_history_items=8,
        max_steps=500,           # Thoải mái giải xuyên suốt 191 câu
        directly_open_url=False, # Không tự ý mở URL trong prompt, làm trực tiếp trên tab hiện tại
    )

    try:
        history = await agent.run()
        print("\n" + "=" * 65)
        print("🏁 AI ĐÃ HOÀN THÀNH CÁC CÂU HỎI:")
        print(history.final_result())
        print("=" * 65)
    except Exception as e:
        print(f"❌ Có lỗi trong quá trình thực thi: {e}")
    finally:
        print("\n✅ Quá trình kết thúc. Bạn có thể kiểm tra lại trên trình duyệt Edge và tự nộp bài.")

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("   CHƯƠNG TRÌNH TỰ ĐỘNG GIẢI QUIZ TRẮC NGHIỆM AI (3 KEYS)")
    print("=" * 65)

    if len(sys.argv) > 1 and sys.argv[1].strip():
        quiz_url = sys.argv[1].strip()
    else:
        print(f"📌 Link FPT LMS mẫu: {DEFAULT_URL}\n")
        user_url = input("👉 Dán LINK bài Quiz của bạn (hoặc nhấn ENTER để dùng link FPT mẫu): ").strip()
        quiz_url = user_url if user_url else DEFAULT_URL

    asyncio.run(run_lms_quiz(quiz_url, browser_type="edge"))
