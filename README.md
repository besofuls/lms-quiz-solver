# 🎓 LMS Quiz Solver Pro - AI Trợ Lý Giải Trắc Nghiệm Tự Động

Ứng dụng tự động hóa giải bài trắc nghiệm (Moodle LMS, Google Forms, Canvas, Quizizz,...) sử dụng **Google Gemini Vision AI** và **Browser-Use**, hỗ trợ đa trình duyệt và cơ chế xoay tua đa API Keys chống lỗi hạn mức (429 Rate Limit).

---

## ⚡ DÀNH CHO NGƯỜI DÙNG PHỔ THÔNG

Bạn **không cần biết lập trình**, **không cần cài Python**, chọn 1 trong 3 cách siêu nhanh dưới đây:

### 🟢 Cách 1: Tải về là dùng ngay (Khuyên dùng - 0 Giây cài đặt)
1. Bấm vào link này để tải file thực thi: 👉 **[Tải LMS_Quiz_Solver_Pro.exe (Bản Mới Nhất)](https://github.com/besofuls/lms-quiz-solver/releases/latest)**
2. Nhấp đúp chuột vào file **`LMS_Quiz_Solver_Pro.exe`** vừa tải về là phần mềm mở lên ngay lập tức!

---

### ⚡ Cách 2: Chạy 1 lệnh duy nhất trong PowerShell
Mở **PowerShell** trên Windows và dán dòng lệnh sau rồi nhấn **Enter**:
```powershell
irm https://raw.githubusercontent.com/besofuls/lms-quiz-solver/main/install.ps1 | iex
```
*(Lệnh này sẽ tự động tải file `.exe` về máy và mở phần mềm lên cho bạn)*

---

### 📁 Cách 3: Tải mã nguồn ZIP về và nhấp đúp `QuickStart.bat`
Nếu bạn tải file **Source code (zip)** về máy:
* Chỉ cần **nhấp đúp chuột vào file `QuickStart.bat`**.
* File này sẽ **tự động làm hết từ A-Z**: tự kiểm tra Python, tự tạo môi trường, tự tải thư viện và tự mở app lên!

---

## 🛠️ DÀNH CHO LẬP TRÌNH VIÊN (DEVELOPERS)

Nếu bạn muốn chỉnh sửa mã nguồn hoặc tự build lại ứng dụng:

```bash
# 1. Clone repository
git clone https://github.com/besofuls/lms-quiz-solver.git
cd lms-quiz-solver

# 2. Tạo môi trường ảo & cài đặt
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# 3. Chạy giao diện mã nguồn
python app.py

# 4. Tự đóng gói thành file .exe độc lập
# Nhấp đúp build_exe.bat hoặc chạy:
pyinstaller --noconsole --onefile --name "LMS_Quiz_Solver_Pro" --collect-all customtkinter --hidden-import=browser_use --hidden-import=google.genai --hidden-import=dotenv app.py
```

---

## ✨ Các Tính Năng Nổi Bật

- 🌐 **Hỗ trợ mọi trình duyệt:** Tự động nhận diện và kết nối trực tiếp với **Microsoft Edge, Google Chrome, Cốc Cốc, Brave, Opera,...** qua cổng CDP (giữ nguyên phiên đăng nhập và cookie cá nhân).
- 🔑 **Đa API Keys Xoay Tua (Round-Robin):** Tự động luân phiên nhiều tài khoản Google Gemini, loại bỏ hoàn toàn lỗi nghẽn hạn mức 250k token/phút.
- 👁️ **Thị giác máy tính (Multimodal Vision):** Đọc và phân tích được cả câu hỏi bằng **hình ảnh, sơ đồ, bảng biểu, đoạn code chụp lại**.
- 🖥️ **Giao diện Desktop hiện đại (GUI):** Xây dựng bằng `CustomTkinter` với Dark Mode đẹp mắt.
- 🛡️ **An toàn tuyệt đối:** Tự động dừng tại trang tổng kết bài làm (*Summary of attempt*), không tự ý nộp bài.

---

## 📖 Hướng Dẫn Sử Dụng 3 Bước

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
