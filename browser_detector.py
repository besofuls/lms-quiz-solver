import os
import socket
import subprocess
import time

CDP_PORT = 9222

KNOWN_BROWSERS = {
    "Microsoft Edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ],
    "Google Chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ],
    "Cốc Cốc": [
        os.path.expandvars(r"%LOCALAPPDATA%\CocCoc\Browser\Application\browser.exe"),
        r"C:\Program Files\CocCoc\Browser\Application\browser.exe",
        r"C:\Program Files (x86)\CocCoc\Browser\Application\browser.exe"
    ],
    "Brave Browser": [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
    ],
    "Opera / Opera GX": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX\launcher.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\launcher.exe"),
        r"C:\Program Files\Opera GX\launcher.exe",
        r"C:\Program Files\Opera\launcher.exe"
    ]
}

def scan_installed_browsers():
    """
    Quét và trả về danh sách các trình duyệt thực tế có trên máy tính của người dùng.
    """
    installed = {}
    for name, paths in KNOWN_BROWSERS.items():
        for p in paths:
            if os.path.exists(p):
                installed[name] = p
                break
    return installed

def is_cdp_port_active():
    """
    Kiểm tra xem cổng Remote Debugging 9222 đã có trình duyệt nào đang mở hay chưa.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', CDP_PORT)) == 0

def launch_selected_browser(browser_name: str, target_url: str, custom_path: str = ""):
    """
    Khởi động trình duyệt được chọn kèm cờ --remote-debugging-port=9222.
    """
    browser_exe = None
    
    if browser_name == "Tùy chọn file .exe..." and custom_path and os.path.exists(custom_path):
        browser_exe = custom_path
    else:
        installed = scan_installed_browsers()
        browser_exe = installed.get(browser_name)
        if not browser_exe:
            # Lấy trình duyệt đầu tiên tìm thấy
            if installed:
                browser_exe = list(installed.values())[0]

    if not browser_exe or not os.path.exists(browser_exe):
        raise FileNotFoundError(f"Không tìm thấy file thực thi của trình duyệt: {browser_name}")

    if is_cdp_port_active():
        return True, "Trình duyệt đã có sẵn cổng kết nối, AI sẽ dùng luôn tab hiện tại."

    # Tạo thư mục profile debug riêng biệt
    clean_name = "".join(c for c in browser_name if c.isalnum())
    user_data_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"{clean_name}_debug_profile")
    os.makedirs(user_data_dir, exist_ok=True)

    cmd = [
        browser_exe,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        target_url
    ]

    subprocess.Popen(cmd)
    time.sleep(2)
    return True, f"Đã mở {browser_name} thành công!"
