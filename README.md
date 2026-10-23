# 🎓 LMS Quiz Solver Pro - AI Trợ Lý Giải Trắc Nghiệm Tự Động

Ứng dụng tự động hóa giải bài trắc nghiệm (Moodle LMS, Google Forms, Canvas, Quizizz,...) sử dụng **Google Gemini Vision AI** và **Browser-Use**, hỗ trợ đa trình duyệt và cơ chế xoay tua đa API Keys chống lỗi giới hạn hạn mức (429 Rate Limit).

---

## ✨ Tính Năng Nổi Bật

- 🌐 **Hỗ trợ mọi trình duyệt:** Tự động nhận diện và kết nối trực tiếp với **Microsoft Edge, Google Chrome, Cốc Cốc, Brave, Opera,...** qua cổng CDP (giữ nguyên phiên đăng nhập và cookie cá nhân).
- 🔑 **Đa API Keys Xoay Tua (Round-Robin):** Tự động luân phiên nhiều tài khoản Google Gemini, loại bỏ hoàn toàn lỗi nghẽn hạn mức 250k token/phút.
- 👁️ **Thị giác máy tính (Multimodal Vision):** Đọc và phân tích được cả câu hỏi bằng **hình ảnh, sơ đồ, bảng biểu, đoạn code chụp lại**.
- 🖥️ **Giao diện Desktop hiện đại (GUI):** Xây dựng bằng `CustomTkinter` với Dark Mode đẹp mắt, không cần mở dòng lệnh terminal.
- 🛡️ **An toàn tuyệt đối:** Tự động dừng tại trang tổng kết bài làm (*Summary of attempt*), không tự ý nộp bài.

---

## 🚀 Cài Đặt & Chạy Ứng Dụng

### 1. Yêu cầu hệ thống
- Python >= 3.11
- Hệ điều hành: Windows 10/11

### 2. Cài đặt các thư viện cần thiết
```bash
# Tạo môi trường ảo
python -m venv .venv
.\.venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
playwright install
```

### 3. Khởi chạy giao diện
```bash
python app.py
# Hoặc nhấp đúp file run_app.bat
```

### 4. Đóng gói thành file .exe độc lập
```bash
# Nhấp đúp file build_exe.bat
# Hoặc chạy lệnh:
pyinstaller --noconsole --onefile --name "LMS_Quiz_Solver_Pro" --collect-all customtkinter --hidden-import=browser_use --hidden-import=google.genai --hidden-import=dotenv app.py
```

---

## 📖 Hướng Dẫn Sử Dụng

1. Mở ứng dụng `LMS_Quiz_Solver_Pro`.
2. Vào tab **🔑 Quản Lý API Keys** để dán danh sách API Key Gemini (lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/)).
3. Trở lại tab **🚀 Bảng Điều Khiển**:
   - Chọn trình duyệt của bạn (Edge, Chrome, Cốc Cốc,...).
   - Dán link bài thi.
   - Bấm **"1. Mở Trình Duyệt & Đăng Nhập"** để mở trình duyệt và đăng nhập bài thi.
   - Bấm **"2. BẮT ĐẦU GIẢI QUIZ"** để AI tự động làm bài đến câu cuối cùng.

---

## ⚠️ Lưu ý miễn trừ trách nhiệm
Dự án được phát triển nhằm mục đích nghiên cứu công nghệ tự động hóa trình duyệt và AI Agent thị giác. Người dùng tự chịu trách nhiệm khi sử dụng công cụ này trên các nền tảng giáo dục hoặc bài thi thực tế.
