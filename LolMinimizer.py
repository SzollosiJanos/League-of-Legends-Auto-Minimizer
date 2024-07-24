import time
import ctypes
import psutil
import win32gui
import win32process
import win32con
from pynput import keyboard, mouse
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as Item
import ctypes
import tkinter as tk
from tkinter import messagebox
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
monitoring_enabled = True
previous_window = None
last_user_action_time = time.time()
FORBIDDEN_PROCESS = 'LeagueClientUx.exe'
ALLOWED_PROCESS = 'League of Legends.exe'
adapter='Disable Program'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False
        
def show_error_message_box(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message)
    
    
if not is_admin():
    show_error_message_box("Please run the program with administrator privileges.")
    exit()
def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            return True
    return False

def enum_windows_callback(hwnd, windows):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    windows.append((hwnd, pid))

def get_hwnd_by_process_name(process_name):
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    for hwnd, pid in windows:
        try:
            process = psutil.Process(pid)
            if process.name().lower() == process_name.lower():
                return hwnd
        except psutil.NoSuchProcess:
            continue
    return None
def is_window_minimized(hwnd):
    if hwnd:
        placement = win32gui.GetWindowPlacement(hwnd)
        return  placement[2]==(-1, -1)
    return False

def minimize_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def on_press(key):
    global last_user_action_time
    last_user_action_time = time.time()
    
def on_release(key):
    global last_user_action_time
    last_user_action_time = time.time()

def on_click(x, y, button, pressed):
    global last_user_action_time
    last_user_action_time = time.time()
    
def toggle_monitoring(icon, item):
    global monitoring_enabled,adapter
    monitoring_enabled = not monitoring_enabled
    if monitoring_enabled:
        adapter='Disable Program'
    else:
        adapter='Enable Program'
    icon.update_menu()
    
def create_image():
    width = 64
    height = 64
    color1 = (0, 0, 0)
    color2 = (255, 255, 255)

    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

def quit_program(icon, item):
    icon.stop()
    keyboard_listener.stop()
    mouse_listener.stop()

def monitor_processes():
    global previous_window, last_user_action_time,monitoring_enabled
    while True:
        try:
            if monitoring_enabled:
                if is_process_running(ALLOWED_PROCESS):
                    time.sleep(10)
                else:
                    hwnd = get_hwnd_by_process_name(FORBIDDEN_PROCESS)
                    if hwnd:
                        if not is_window_minimized(hwnd):
                            current_time = time.time()
                            user_active = (current_time - last_user_action_time) < 0.3
                            if not user_active and (hwnd != previous_window):
                                minimize_window(hwnd)
                        
                            previous_window = win32gui.GetForegroundWindow()
                    else:
                        time.sleep(60)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(0.1)


keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()


icon = pystray.Icon("Lol Popup")
icon.icon = create_image()
menu =(
    Item('League of Legends Auto-Minimizer', None, enabled=False),
    Item('Made by: 爪εℊøłtЄłεҝ', None, enabled=False),
    Item('-----------------------', None, enabled=False),
    Item(lambda text: adapter, toggle_monitoring),
    Item('Quit', quit_program)
)

icon.menu = pystray.Menu(*menu)
monitor_thread = threading.Thread(target=monitor_processes)
monitor_thread.daemon = True
monitor_thread.start()

icon.run()