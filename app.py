import datetime
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from browser_detector import is_cdp_port_active, launch_selected_browser, scan_installed_browsers
from config_manager import load_config, save_config
from quiz_worker import QuizWorker

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LMSQuizSolverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LMS Quiz Solver Pro - AI Trợ Lý Tự Động")
        self.geometry("900, 680")
        self.minsize(800, 600)

        # Nạp cấu hình
        self.config_data = load_config()
        self.installed_browsers = scan_installed_browsers()
        self.worker = None

        self._build_ui()
        self._load_saved_values()

    def _build_ui(self):
        # 1. Header
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a24")
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎓 LMS QUIZ SOLVER PRO", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#4da6ff"
        )
        title_label.pack(side="left", padx=20, pady=12)

        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="v2.0 • Hỗ Trợ Mọi Trình Duyệt • Đa API Keys", 
            font=ctk.CTkFont(size=12),
            text_color="#888899"
        )
        subtitle_label.pack(side="right", padx=20, pady=12)

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_dashboard = self.tabview.add("🚀 Bảng Điều Khiển")
        self.tab_keys = self.tabview.add("🔑 Quản Lý API Keys")
        self.tab_help = self.tabview.add("ℹ️ Hướng Dẫn & Mẹo")

        self._setup_dashboard_tab()
        self._setup_keys_tab()
        self._setup_help_tab()

    def _setup_dashboard_tab(self):
        tab = self.tab_dashboard

        # Khung cài đặt bài thi & trình duyệt
        control_card = ctk.CTkFrame(tab, corner_radius=8, fg_color="#21212e")
        control_card.pack(fill="x", padx=10, pady=8)

        # Hàng 1: URL bài Quiz
        url_label = ctk.CTkLabel(control_card, text="🔗 URL Bài Thi:", font=ctk.CTkFont(weight="bold"))
        url_label.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))

        self.url_entry = ctk.CTkEntry(
            control_card, 
            placeholder_text="Dán link bài kiểm tra vào đây (FPT LMS, Google Forms, Canvas, v.v.)...",
            width=580,
            height=35
        )
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(0, 15), pady=(12, 4))

        # Hàng 2: Chọn trình duyệt & Tốc độ
        browser_label = ctk.CTkLabel(control_card, text="🌐 Trình Duyệt:", font=ctk.CTkFont(weight="bold"))
        browser_label.grid(row=1, column=0, sticky="w", padx=15, pady=(4, 12))

        browser_options = list(self.installed_browsers.keys())
        if not browser_options:
            browser_options = ["Microsoft Edge", "Google Chrome"]
        browser_options.append("Tùy chọn file .exe...")

        self.browser_dropdown = ctk.CTkOptionMenu(
            control_card, 
            values=browser_options,
            command=self._on_browser_changed,
            width=220,
            height=32
        )
        self.browser_dropdown.grid(row=1, column=1, sticky="w", padx=0, pady=(4, 12))

        # Tùy chọn tốc độ
        speed_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        speed_frame.grid(row=1, column=2, sticky="e", padx=15, pady=(4, 12))

        ctk.CTkLabel(speed_frame, text="⚡ Chế độ:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 5))
        self.speed_var = ctk.StringVar(value="turbo")
        self.speed_turbo = ctk.CTkRadioButton(speed_frame, text="Siêu tốc (Turbo)", variable=self.speed_var, value="turbo")
        self.speed_turbo.pack(side="left", padx=5)
        self.speed_safe = ctk.CTkRadioButton(speed_frame, text="Tiêu chuẩn (Safe)", variable=self.speed_var, value="safe")
        self.speed_safe.pack(side="left", padx=5)

        control_card.columnconfigure(1, weight=1)

        # Khung các nút hành động (Buttons)
        action_frame = ctk.CTkFrame(tab, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=5)

        self.btn_open_browser = ctk.CTkButton(
            action_frame,
            text="1. 🌐 Mở Trình Duyệt & Đăng Nhập",
            command=self._action_open_browser,
            fg_color="#3366cc",
            hover_color="#254e99",
            height=38,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_open_browser.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_start = ctk.CTkButton(
            action_frame,
            text="2. 🚀 BẮT ĐẦU GIẢI QUIZ",
            command=self._action_start_solving,
            fg_color="#00994d",
            hover_color="#007a3d",
            height=38,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_start.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_stop = ctk.CTkButton(
            action_frame,
            text="⏹ DỪNG LẠI",
            command=self._action_stop,
            fg_color="#cc3333",
            hover_color="#992626",
            width=120,
            height=38,
            font=ctk.CTkFont(weight="bold"),
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=(5, 0))

        # Thanh trạng thái (Status Banner)
        status_card = ctk.CTkFrame(tab, corner_radius=6, fg_color="#181822", height=32)
        status_card.pack(fill="x", padx=10, pady=(8, 4))

        self.status_label = ctk.CTkLabel(
            status_card, 
            text="● Sẵn sàng. Nhấn '1. Mở Trình Duyệt' để chuẩn bị bài thi.", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00cc66"
        )
        self.status_label.pack(side="left", padx=12, pady=5)

        # Khung Log đầu ra (Console Output)
        log_label_frame = ctk.CTkFrame(tab, fg_color="transparent")
        log_label_frame.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(log_label_frame, text="📋 Nhật Ký Hoạt Động (Live Logs):", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(log_label_frame, text="Xóa Log", width=65, height=22, fg_color="#333344", command=self._clear_logs).pack(side="right")

        self.log_textbox = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), corner_radius=6)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    def _setup_keys_tab(self):
        tab = self.tab_keys

        info_card = ctk.CTkFrame(tab, corner_radius=8, fg_color="#21212e")
        info_card.pack(fill="x", padx=10, pady=8)

        info_text = (
            "💡 HƯỚNG DẪN ĐA API KEYS:\n"
            "• Thêm 2 đến 3 API Keys từ các tài khoản Google khác nhau để không bao giờ bị nghẽn hạn mức (429 Rate Limit).\n"
            "• Lấy Key miễn phí 100% tại: https://aistudio.google.com/app/apikey\n"
            "• Dán mỗi API Key trên MỘT DÒNG bên dưới rồi nhấn nút 'Lưu Danh Sách Keys'."
        )
        ctk.CTkLabel(info_card, text=info_text, justify="left", font=ctk.CTkFont(size=12)).pack(padx=15, pady=10, anchor="w")

        # Khung nhập Keys
        ctk.CTkLabel(tab, text="Danh Sách API Keys (Mỗi key một dòng):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 2))

        self.keys_textbox = ctk.CTkTextbox(tab, height=220, font=ctk.CTkFont(family="Consolas", size=13))
        self.keys_textbox.pack(fill="x", padx=10, pady=(0, 10))

        # Nút Lưu và Test Keys
        keys_btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        keys_btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_save_keys = ctk.CTkButton(
            keys_btn_frame, 
            text="💾 Lưu Danh Sách Keys", 
            command=self._save_keys, 
            fg_color="#00994d", 
            hover_color="#007a3d",
            height=36
        )
        self.btn_save_keys.pack(side="left", padx=(0, 10))

        self.btn_test_keys = ctk.CTkButton(
            keys_btn_frame, 
            text="🔍 Kiểm Tra Kết Nối Các Keys", 
            command=self._test_keys, 
            fg_color="#3366cc", 
            hover_color="#254e99",
            height=36
        )
        self.btn_test_keys.pack(side="left")

    def _setup_help_tab(self):
        tab = self.tab_help
        help_card = ctk.CTkFrame(tab, corner_radius=8, fg_color="#21212e")
        help_card.pack(fill="both", expand=True, padx=10, pady=10)

        help_content = """
        📖 QUY TRÌNH SỬ DỤNG 3 BƯỚC ĐƠN GIẢN:

        1️⃣ BƯỚC 1: Chọn trình duyệt & Dán Link bài Quiz
           - Chọn Microsoft Edge, Google Chrome hoặc Cốc Cốc.
           - Dán link bài Quiz của bạn vào ô URL.
           - Bấm nút "1. Mở Trình Duyệt & Đăng Nhập".

        2️⃣ BƯỚC 2: Đăng nhập & Vào bài thi
           - Cửa sổ trình duyệt của bạn sẽ hiện ra.
           - Tự đăng nhập tài khoản trường (FPT SSO, Google,...) nếu trang yêu cầu.
           - Mở đến đúng trang câu hỏi bạn muốn AI bắt đầu giải.

        3️⃣ BƯỚC 3: Bấm Bắt Đầu
           - Quay lại phần mềm này và bấm nút "2. BẮT ĐẦU GIẢI QUIZ".
           - AI sẽ tự động đọc câu hỏi, chọn đáp án đúng và bấm 'Next page' liên tục!
           - Khi đến trang tổng kết (Summary of attempt), AI sẽ tự động DỪNG LẠI để bạn kiểm tra lại trước khi bấm nộp bài thật.

        --------------------------------------------------------------------------------

        ✨ ĐIỂM NỔI BẬT:
        • Hỗ trợ câu hỏi có HÌNH ẢNH / SƠ ĐỒ / BẢNG BIỂU nhờ mô hình Gemini Multimodal Vision.
        • Tự động xoay tua đa API Keys để đạt tốc độ tối đa không bị gián đoạn.
        • Tương thích hoàn toàn với LMS FPT (Moodle), Google Forms, Canvas, Quizizz,...
        """
        textbox = ctk.CTkTextbox(help_card, font=ctk.CTkFont(size=12), fg_color="transparent")
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", help_content)
        textbox.configure(state="disabled")

    def _load_saved_values(self):
        # Nạp URL
        self.url_entry.insert(0, self.config_data.get("default_url", ""))
        # Nạp Trình duyệt đã chọn
        saved_browser = self.config_data.get("selected_browser", "Microsoft Edge")
        if saved_browser in self.browser_dropdown.cget("values"):
            self.browser_dropdown.set(saved_browser)
        # Nạp Tốc độ
        self.speed_var.set(self.config_data.get("speed_mode", "turbo"))
        # Nạp Keys
        keys = self.config_data.get("api_keys", [])
        self.keys_textbox.insert("1.0", "\n".join(keys))

    def _on_browser_changed(self, choice):
        if choice == "Tùy chọn file .exe...":
            file_path = filedialog.askopenfilename(
                title="Chọn file trình duyệt (.exe)",
                filetypes=[("Executable Files", "*.exe")]
            )
            if file_path:
                self.config_data["custom_browser_path"] = file_path
            else:
                self.browser_dropdown.set("Microsoft Edge")

    def log(self, text: str):
        def _append():
            timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
            self.log_textbox.insert("end", timestamp + text + "\n")
            self.log_textbox.see("end")
        self.after(0, _append)

    def set_status(self, text: str, color="#00cc66"):
        def _set():
            self.status_label.configure(text=f"● {text}", text_color=color)
        self.after(0, _set)

    def _clear_logs(self):
        self.log_textbox.delete("1.0", "end")

    def _save_keys(self):
        content = self.keys_textbox.get("1.0", "end").strip()
        keys = [k.strip() for k in content.splitlines() if k.strip()]
        if not keys:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất 1 API Key!")
            return
        self.config_data["api_keys"] = keys
        save_config(self.config_data)
        messagebox.showinfo("Thành công", f"Đã lưu thành công {len(keys)} API Keys!")
        self.log(f"💾 Đã lưu cấu hình {len(keys)} API Keys vào hệ thống.")

    def _test_keys(self):
        content = self.keys_textbox.get("1.0", "end").strip()
        keys = [k.strip() for k in content.splitlines() if k.strip()]
        if not keys:
            messagebox.showwarning("Cảnh báo", "Không có key nào để kiểm tra!")
            return

        self.log("🔍 Đang kiểm tra trạng thái hoạt động của các API Keys...")
        self.set_status("Đang kiểm tra Keys...", color="#ffcc00")

        def _run_test():
            from google import genai
            results = []
            for i, k in enumerate(keys, 1):
                try:
                    c = genai.Client(api_key=k)
                    res = c.models.generate_content(model="gemini-3.5-flash-lite", contents="Ping")
                    results.append(f"✅ Key {i}: Hoạt động TỐT")
                    self.log(f"✅ Key {i} ({k[:12]}...): KẾT NỐI TỐT")
                except Exception as e:
                    results.append(f"❌ Key {i}: Lỗi ({e})")
                    self.log(f"❌ Key {i}: LỖI -> {e}")
            self.set_status("Kiểm tra hoàn tất", color="#00cc66")
            messagebox.showinfo("Kết quả kiểm tra", "\n".join(results))

        threading.Thread(target=_run_test, daemon=True).start()

    def _action_open_browser(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập link bài Quiz!")
            return

        browser_choice = self.browser_dropdown.get()
        custom_path = self.config_data.get("custom_browser_path", "")

        self.log(f"🌐 Đang khởi động trình duyệt {browser_choice}...")
        self.set_status(f"Đang mở {browser_choice}...", color="#3399ff")

        try:
            _, msg = launch_selected_browser(browser_choice, url, custom_path=custom_path)
            self.log(f"✅ {msg}")
            self.set_status("Trình duyệt đã mở. Hãy đăng nhập và vào đúng trang câu hỏi.", color="#00cc66")
            # Lưu lại URL
            self.config_data["default_url"] = url
            self.config_data["selected_browser"] = browser_choice
            save_config(self.config_data)
        except Exception as e:
            self.log(f"❌ Lỗi mở trình duyệt: {e}")
            self.set_status("Lỗi mở trình duyệt", color="#ff3333")
            messagebox.showerror("Lỗi", f"Không thể mở trình duyệt: {e}")

    def _action_start_solving(self):
        keys = self.config_data.get("api_keys", [])
        if not keys:
            messagebox.showerror("Thiếu API Key", "Chưa có API Key nào được cài đặt. Hãy chuyển sang tab 'Quản Lý API Keys' để thêm key!")
            return

        url = self.url_entry.get().strip()
        speed = self.speed_var.get()

        # Cập nhật trạng thái nút
        self.btn_start.configure(state="disabled")
        self.btn_open_browser.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        self.log("=" * 45)
        self.log(f"🚀 BẮT ĐẦU TIẾN TRÌNH GIẢI QUIZ TỰ ĐỘNG...")
        self.log(f"🔑 Số lượng Keys xoay tua: {len(keys)}")
        self.log(f"⚡ Tốc độ: {speed.upper()}")
        self.log("=" * 45)

        def on_finished_callback(status):
            self.set_status(status)
            self.btn_start.configure(state="normal")
            self.btn_open_browser.configure(state="normal")
            self.btn_stop.configure(state="disabled")

        self.worker = QuizWorker(
            api_keys=keys,
            target_url=url,
            speed_mode=speed,
            log_callback=self.log,
            status_callback=lambda s: self.set_status(s)
        )
        self.worker.start()

    def _action_stop(self):
        if self.worker and self.worker.is_running:
            self.worker.stop()
            self.log("⏹ Đã yêu cầu dừng giải bài.")
            self.btn_start.configure(state="normal")
            self.btn_open_browser.configure(state="normal")
            self.btn_stop.configure(state="disabled")

if __name__ == "__main__":
    app = LMSQuizSolverApp()
    app.mainloop()
