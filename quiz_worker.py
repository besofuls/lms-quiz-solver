import asyncio
import sys
import threading
import time
from browser_use import Agent, Browser
from browser_use.llm.base import BaseChatModel
from browser_use.llm.google.chat import ChatGoogle

CDP_PORT = 9222

class MultiKeyChatGoogle(BaseChatModel):
    def __init__(self, api_keys: list[str], model="gemini-3.5-flash-lite", log_callback=None):
        self.api_keys = api_keys
        self.model = model
        self.log_callback = log_callback
        self.clients = [ChatGoogle(model=model, api_key=k) for k in api_keys]
        self.current_idx = 0

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

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
                # Tự động xoay sang key tiếp theo
                self.current_idx = (self.current_idx + 1) % total_keys
                return res
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    next_idx = (self.current_idx + 1) % total_keys
                    self.log(f"⚡ [Key {key_num}] Chạm hạn mức phút -> Lập tức chuyển sang Key {next_idx + 1}...")
                    self.current_idx = next_idx
                    attempts += 1
                else:
                    raise e
        
        return await self.clients[self.current_idx].ainvoke(messages, output_format=output_format, **kwargs)


class QuizWorker:
    def __init__(self, api_keys: list[str], target_url: str, speed_mode="turbo", log_callback=None, status_callback=None):
        self.api_keys = api_keys
        self.target_url = target_url
        self.speed_mode = speed_mode
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.is_running = False
        self._thread = None
        self._agent = None
        self._browser = None

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)

    def set_status(self, status: str):
        if self.status_callback:
            self.status_callback(status)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        self.log("🛑 Đã gửi tín hiệu dừng tới AI...")
        self.set_status("Đang dừng...")

    def _run_async_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._execute_agent())
        except Exception as e:
            self.log(f"❌ Lỗi thực thi: {e}")
        finally:
            self.is_running = False
            self.set_status("Đã dừng")
            loop.close()

    async def _execute_agent(self):
        self.log("🚀 Đang khởi động AI và kết nối vào trình duyệt...")
        self.set_status("Đang kết nối...")

        # Cấu hình LLM đa key
        llm = MultiKeyChatGoogle(api_keys=self.api_keys, model="gemini-3.5-flash-lite", log_callback=self.log_callback)

        # Cấu hình độ trễ theo speed_mode
        if self.speed_mode == "turbo":
            wait_action = 0.8
            wait_page = 2.0
        else:
            wait_action = 1.8
            wait_page = 2.5

        self._browser = Browser(
            cdp_url=f"http://localhost:{CDP_PORT}",
            minimum_wait_page_load_time=wait_page,
            wait_for_network_idle_page_load_time=1.5,
            wait_between_actions=wait_action,
        )

        task_prompt = """
        Bạn là trợ lý AI giải bài trắc nghiệm. Hãy tiếp tục giải từ trang câu hỏi đang mở trên màn hình.

        QUY TẮC CỰC KỲ QUAN TRỌNG:
        1. Giữ nguyên trên trang web bài thi hiện tại, KHÔNG tự ý nhập URL hay điều hướng đi trang khác.
        2. Nếu nhìn thấy màn hình trắng hoặc đang tải: ĐÓ LÀ MẠNG ĐANG CHUYỂN CÂU, KHÔNG ĐƯỢC COI LÀ HẾT BÀI và TUYỆT ĐỐI CẤM GỌI 'done'!
        3. Ở thanh bên phải (Quiz navigation) có chữ 'Finish attempt', đó chỉ là menu điều hướng, KHÔNG PHẢI HẾT BÀI! Cấm click vào và không dừng lại.
        4. Miễn là ở giữa màn hình VẪN CÒN CÂU HỎI thì BẮT BUỘC PHẢI TIẾP TỤC GIẢI.

        Quy trình cho từng câu:
        - Đọc kỹ nội dung câu hỏi (chữ, code, hình ảnh, sơ đồ).
        - Chọn đáp án đúng nhất bằng cách click vào nút tròn (radio) hoặc ô vuông (checkbox).
        - Click nút chuyển trang ('Next page', 'Next', 'Trang tiếp') để sang câu tiếp theo.
        - Lặp lại liên tục cho đến khi không còn câu hỏi nào.

        ĐIỀU KIỆN DUY NHẤT ĐỂ ĐƯỢC DỪNG BÀI:
        - Chỉ dừng lại khi màn hình hiển thị BẢNG TỔNG KẾT TẤT CẢ CÂU HỎI (Summary of attempt) và HOÀN TOÀN KHÔNG CÒN CÂU HỎI NÀO NỮA.
        - Lúc này gọi action 'done' và TUYỆT ĐỐI KHÔNG bấm nút nộp bài chính thức.
        """

        self._agent = Agent(
            task=task_prompt,
            llm=llm,
            browser=self._browser,
            use_vision=True,
            use_thinking=False,
            use_judge=False,
            max_history_items=8,
            max_steps=500,
            directly_open_url=False,
        )

        self.log(f"✅ Đã kết nối thành công! Đang tiến hành giải tự động...")
        self.set_status("Đang giải bài...")

        try:
            history = await self._agent.run()
            self.log("\n" + "=" * 50)
            self.log("🏁 BÁO CÁO KẾT QUẢ TỪ AI:")
            self.log(str(history.final_result()))
            self.log("=" * 50 + "\n")
            self.set_status("Hoàn thành!")
        except Exception as e:
            self.log(f"⚠️ Quá trình thực hiện gặp lỗi: {e}")
            self.set_status("Có lỗi xảy ra")
