import concurrent.futures
import csv
import datetime
import json
import math
import os
import platform
import psutil
import requests
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import traceback
from tkinter import Tk, messagebox, filedialog
import customtkinter as ctk

# 🟢 Direct Import of Bot Module[cite: 6]
try:
    import chrome_isolate
except Exception:
    chrome_isolate = None

# 🟢 CURRENT BOT VERSION[cite: 6]
CURRENT_VERSION = "15.4"

# 🟢 CONFIG LINKS (GitHub Raw CDN)[cite: 6]
LICENSE_URL = "https://raw.githubusercontent.com/tejastitare123/bot-config/refs/heads/main/licenses.json"
UPDATE_JSON_URL = "https://raw.githubusercontent.com/tejastitare123/bot-config/refs/heads/main/version.json"

def get_hwid():
    """Windows PC Unique System Motherboard Hardware ID (Win 10/11 Compatible).[cite: 6]"""
    try:
        cmd = 'powershell -Command "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"'
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        if output:
            return output
    except Exception:
        pass

    try:
        cmd = 'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid'
        output = subprocess.check_output(cmd, shell=True).decode()
        for line in output.splitlines():
            if "MachineGuid" in line:
                return line.split()[-1].strip()
    except Exception:
        pass

    return platform.node()

def verify_hwid_license():
    user_hwid = get_hwid().strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    try:
        fresh_url = f"{LICENSE_URL}?t={int(time.time())}"
        response = requests.get(fresh_url, headers=headers, timeout=12)

        if response.status_code == 200:
            data = response.json()
            if data.get("global_kill_switch", False) is True:
                messagebox.showerror("Access Revoked", "This bot version has been globally disabled by Admin.")
                sys.exit(0)

            allowed_hwids = [str(h).strip().lower() for h in data.get("allowed_hwids", [])]

            if user_hwid.lower() not in allowed_hwids:
                try:
                    import pyperclip
                    pyperclip.copy(user_hwid)
                except Exception:
                    try:
                        cmd = f"echo {user_hwid}| clip"
                        os.system(cmd)
                    except Exception:
                        pass

                messagebox.showerror(
                    "License Key Required",
                    f"Your Hardware ID (HWID) is not registered!\n\nYour HWID:\n{user_hwid}\n\n(Copied to clipboard. Send to Admin for access!)"
                )
                sys.exit(0)
        else:
            messagebox.showerror(
                "Server Error",
                f"Could not verify license. Server status: {response.status_code}\nURL: {LICENSE_URL}"
            )
            sys.exit(0)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to connect to license server.\nDetails: {e}")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Security Error", f"License check error: {e}")
        sys.exit(0)

def auto_update_bot():
    """Server checks and auto-downloads compiled .pyc files if newer version available.[cite: 6]"""
    try:
        fresh_url = f"{UPDATE_JSON_URL}?t={int(time.time())}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        response = requests.get(fresh_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            remote_version = str(data.get("latest_version", CURRENT_VERSION)).strip()

            if remote_version != CURRENT_VERSION:
                files_to_update = data.get("update_files", {})
                updated_count = 0
                base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

                for filename, download_url in files_to_update.items():
                    sep = "&" if "?" in download_url else "?"
                    file_url = f"{download_url}{sep}t={int(time.time())}"

                    r = requests.get(file_url, headers=headers, timeout=15)
                    if r.status_code == 200:
                        target_file_path = os.path.join(base_dir, filename)
                        file_dir = os.path.dirname(target_file_path)
                        if file_dir:
                            os.makedirs(file_dir, exist_ok=True)

                        with open(target_file_path, "wb") as f:
                            f.write(r.content)
                        updated_count += 1

                if updated_count > 0:
                    messagebox.showinfo(
                        "Update Installed",
                        f"Bot updated to v{remote_version} successfully!\nPlease restart."
                    )
                    sys.exit(0)
    except Exception as e:
        print(f"Update Check Skipped: {e}")

# 🔒 Run Security & Auto-Update Checks[cite: 6]
verify_hwid_license()
auto_update_bot()

ctk.set_default_color_theme("blue")


# ==========================================
# 🌌 3D HOLOGRAPHIC CYBER CORE (MATHEMATICAL 3D ENGINE)
# ==========================================
class Hologram3DCore(tk.Canvas):
    """Real-time 3D projected wireframe hypercube engine inside Tkinter Canvas.[cite: 6]"""
    def __init__(self, master, width=160, height=130, **kwargs):
        super().__init__(master, width=width, height=height, bg="#0d0f1a", highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.active_status = False

        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1],  [1, -1, 1],  [1, 1, 1],  [-1, 1, 1]
        ]

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        self.render_frame()

    def set_active(self, active=True):
        self.active_status = active

    def render_frame(self):
        self.delete("all")
        scale = 32
        cx, cy = self.w // 2, self.h // 2

        if self.active_status:
            self.angle_x += 0.04
            self.angle_y += 0.06
            self.angle_z += 0.03
            edge_color = "#10b981"
            node_color = "#34d399"
        else:
            self.angle_x += 0.015
            self.angle_y += 0.02
            self.angle_z += 0.01
            edge_color = "#00f0ff"
            node_color = "#38bdf8"

        cos_x, sin_x = math.cos(self.angle_x), math.sin(self.angle_x)
        cos_y, sin_y = math.cos(self.angle_y), math.sin(self.angle_y)
        cos_z, sin_z = math.cos(self.angle_z), math.sin(self.angle_z)

        projected = []
        for x, y, z in self.vertices:
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x

            x2 = x * cos_y + z1 * sin_y
            z2 = -x * sin_y + z1 * cos_y

            x3 = x2 * cos_z - y1 * sin_z
            y3 = x2 * sin_z + y1 * cos_z

            distance = 3.5
            f = scale * (distance / (distance + z2))
            px = int(cx + x3 * f)
            py = int(cy + y3 * f)
            projected.append((px, py))

        for edge in self.edges:
            p1 = projected[edge[0]]
            p2 = projected[edge[1]]
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill=edge_color, width=2)

        for px, py in projected:
            self.create_oval(px - 3, py - 3, px + 3, py + 3, fill=node_color, outline="")

        core_r = 4 if not self.active_status else 6
        core_c = "#f59e0b" if self.active_status else "#00f0ff"
        self.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill=core_c, outline="")

        self.after(33, self.render_frame)


# ==========================================
# 📈 7-DAY CYBER SPARKLINE CANVAS (LEVEL 4)
# ==========================================
class CyberSparkline(tk.Canvas):
    """Vector Sparkline Graph for 7-Day Performance trend visualization.[cite: 6]"""
    def __init__(self, master, width=155, height=38, bg_color="#121420", **kwargs):
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height

    def set_bg(self, bg_color):
        self.configure(bg=bg_color)

    def draw_sparkline(self, points_list):
        self.delete("all")
        if not points_list or len(points_list) < 2:
            points_list = [0] * 7

        max_val = max(points_list) if max(points_list) > 0 else 100
        min_val = min(points_list) if min(points_list) >= 0 else 0
        val_range = max(max_val - min_val, 1)

        padding_x = 8
        padding_y = 6
        avail_w = self.w - 2 * padding_x
        avail_h = self.h - 2 * padding_y
        step_x = avail_w / (len(points_list) - 1)

        coords = []
        for i, val in enumerate(points_list):
            cx = padding_x + i * step_x
            normalized = (val - min_val) / val_range
            cy = (self.h - padding_y) - (normalized * avail_h)
            coords.append((cx, cy))

        poly = [padding_x, self.h]
        for cx, cy in coords:
            poly.extend([cx, cy])
        poly.extend([self.w - padding_x, self.h])
        try:
            self.create_polygon(poly, fill="#0c231f", outline="")
        except Exception:
            pass

        for i in range(len(coords) - 1):
            p1 = coords[i]
            p2 = coords[i + 1]
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill="#047857", width=3)
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill="#10b981", width=1.5)

        for i, (cx, cy) in enumerate(coords):
            is_last = (i == len(coords) - 1)
            color = "#00f0ff" if is_last else "#34d399"
            r = 3 if is_last else 2
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")


class TextRedirector:
    """Intercepts standard terminal stdout/stderr and mirrors it live to the GUI Console.[cite: 6]"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout

    def write(self, string):
        try:
            self.original_stdout.write(string)
            if string.strip():
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                formatted = f"[{now_str}] {string.strip()}\n"
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", formatted)
                lines = int(self.text_widget.index('end-1c').split('.')[0])
                if lines > 500:
                    self.text_widget.delete("1.0", "100.0")
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")
        except Exception:
            pass

    def flush(self):
        try:
            self.original_stdout.flush()
        except Exception:
            pass


class SuperDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"MS BOT ULTRA • CYBER COMMAND CENTER v{CURRENT_VERSION}")
        self.geometry("1500x920")
        self.minsize(1300, 820)
        self.configure(fg_color=("#e5eaf2", "#0b0c13"))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # File Paths[cite: 6]
        self.history_path = os.path.join("bot_data", "history.json")
        self.accounts_path = os.path.join("config", "accounts.json")
        self.settings_path = os.path.join("config", "settings.json")
        self.session_path = os.path.abspath("chrome_sessions")

        os.makedirs("config", exist_ok=True)
        os.makedirs("bot_data", exist_ok=True)

        self.account_cards = {}
        self.suspended_cards = {}
        
        self._cached_history_data = {}
        self._last_history_mtime = 0
        
        # 🟢 Multi-Profile Concurrent Execution State[cite: 6]
        self.is_batch_running = False
        self.active_running_profiles = set()

        # 🟢 Search & Filter State[cite: 6]
        self.search_filter_text = ""
        self.active_category_filter = "All"

        # 🟢 Auto-Scheduler State[cite: 6]
        self.scheduler_time = "05:30"
        self.last_scheduled_date = None

        self.daily_goal = 20
        self.target_points = 8150
        self.tg_token = ""
        self.tg_chat_id = ""
        self.cached_dir_size = "Calculating..."
        self.cached_ping = "Calculating..."
        self.pulse_state = False

        self.net_baseline = psutil.net_io_counters()
        self.data_date = datetime.datetime.now().date()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_main_view()

        sys.stdout = TextRedirector(self.console_text)

        self.initial_load()
        self.select_tab("monitor")

        self.async_disk_calc_loop()
        self.async_ping_calc_loop()
        self.update_loop()
        self.pulse_animation_loop()

    @property
    def is_running(self):
        return self.is_batch_running or len(self.active_running_profiles) > 0

    # ==========================================
    # 🌐 SIDEBAR WITH 3D HOLO CORE
    # ==========================================
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=290, corner_radius=0,
            fg_color=("#d6dee8", "#10111a"),
            border_width=1,
            border_color=("#b6c2d1", "#191c2b")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        holo_pod = ctk.CTkFrame(
            self.sidebar,
            fg_color="#0d0f1a",
            corner_radius=12,
            border_width=1,
            border_color="#1f2438"
        )
        holo_pod.pack(fill="x", padx=15, pady=(14, 8))

        self.holo_3d = Hologram3DCore(holo_pod, width=150, height=105)
        self.holo_3d.pack(pady=4)

        ctk.CTkLabel(
            holo_pod,
            text="⚡ QUANTUM CORE 3D",
            font=("Segoe UI", 9, "bold"),
            text_color="#00f0ff"
        ).pack(pady=(0, 4))

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(2, 10))
        ctk.CTkLabel(
            brand_frame,
            text="MS BOT ULTRA",
            font=("Segoe UI", 18, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_frame,
            text="Cyber Automation Cluster",
            font=("Segoe UI", 10),
            text_color=("#475569", "#64748b")
        ).pack(anchor="w")

        # Tab Navigation[cite: 6]
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=15, pady=2)

        self.btn_tab_monitor = self.create_nav_btn("📊  Live Monitor", lambda: self.select_tab("monitor"))
        self.btn_tab_console = self.create_nav_btn("💻  Matrix Terminal", lambda: self.select_tab("console"))
        self.btn_tab_accounts = self.create_nav_btn("👥  Profiles Manager", lambda: self.select_tab("accounts"))
        self.btn_tab_suspended = self.create_nav_btn("⛔  Suspended Nodes", lambda: self.select_tab("suspended"))
        self.btn_tab_settings = self.create_nav_btn("⚙️  Engine Settings", lambda: self.select_tab("settings"))

        # Execution Controls[cite: 6]
        ctl_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=("#e9f0f8", "#161824"),
            corner_radius=12,
            border_width=2,
            border_color=("#b9c9dc", "#24293e")
        )
        ctl_frame.pack(fill="x", padx=15, pady=10)

        self.run_btn = ctk.CTkButton(
            ctl_frame,
            text="🚀  INITIALIZE ENGINE",
            fg_color="#059669",
            hover_color="#10b981",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            command=self.safe_launch_sequence
        )
        self.run_btn.pack(fill="x", padx=12, pady=(10, 4))

        self.stop_btn = ctk.CTkButton(
            ctl_frame,
            text="🛑  EMERGENCY STOP",
            fg_color="#dc2626",
            hover_color="#ef4444",
            height=34,
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            command=self.stop_bot
        )
        self.stop_btn.pack(fill="x", padx=12, pady=(2, 10))

        # Hardware & Network Telemetry Pod[cite: 6]
        tele_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=("#e4ecf5", "#131520"),
            corner_radius=10,
            border_width=1,
            border_color=("#bfd0e2", "#1d2133")
        )
        tele_frame.pack(side="bottom", fill="x", padx=15, pady=12)

        self.cpu_lbl = ctk.CTkLabel(
            tele_frame,
            text="CPU Load: 0%",
            font=("Segoe UI", 10, "bold"),
            text_color=("#0284c7", "#00f0ff")
        )
        self.cpu_lbl.pack(anchor="w", padx=12, pady=(6, 1))

        self.ram_lbl = ctk.CTkLabel(
            tele_frame,
            text="RAM Usage: 0%",
            font=("Segoe UI", 10, "bold"),
            text_color="#10b981"
        )
        self.ram_lbl.pack(anchor="w", padx=12, pady=(0, 1))

        self.ram_bar = ctk.CTkProgressBar(
            tele_frame,
            height=5,
            fg_color=("#c8d6e5", "#0b0c13"),
            progress_color="#10b981",
            corner_radius=3
        )
        self.ram_bar.pack(fill="x", padx=12, pady=(0, 4))
        self.ram_bar.set(0.1)

        self.ping_lbl = ctk.CTkLabel(
            tele_frame,
            text="Latency: Calculating...",
            font=("Segoe UI", 10, "bold"),
            text_color=("#334155", "#94a3b8")
        )
        self.ping_lbl.pack(anchor="w", padx=12, pady=(0, 1))

        self.storage_lbl = ctk.CTkLabel(
            tele_frame,
            text="Disk Vault: 0 MB",
            font=("Segoe UI", 9),
            text_color=("#64748b", "#64748b")
        )
        self.storage_lbl.pack(anchor="w", padx=12, pady=(0, 3))

        self.theme_opt = ctk.CTkOptionMenu(
            tele_frame,
            values=["Light", "Dark", "System"],
            command=self.change_theme_mode,
            height=24,
            corner_radius=6,
            fg_color=("#d0dbe7", "#1a1d2d"),
            button_color=("#b6ccdf", "#25293f"),
            text_color=("#0f172a", "#f8fafc"),
            font=("Segoe UI", 9, "bold")
        )
        self.theme_opt.pack(fill="x", padx=12, pady=(2, 6))

    def change_theme_mode(self, theme_choice):
        ctk.set_appearance_mode(theme_choice.lower())
        bg = "#f4f8fc" if theme_choice.lower() == "light" else "#121420"
        if hasattr(self, "sparkline_canvas"):
            self.sparkline_canvas.set_bg(bg)
        self.save_settings()

    def create_nav_btn(self, text, command):
        btn = ctk.CTkButton(
            self.nav_frame,
            text=text,
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#c8d5e4", "#1a1d2b"),
            text_color=("#334155", "#94a3b8"),
            font=("Segoe UI", 11, "bold"),
            command=command
        )
        btn.pack(fill="x", pady=1)
        return btn

    # ==========================================
    # 💻 MAIN CONTENT VIEWS & DASHBOARD LAYOUT
    # ==========================================
    def build_main_view(self):
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=18)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # 1. Top Analytics Bar (With Level 4 Sparkline Pod)[cite: 6]
        self.metrics_bar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.metrics_bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.metrics_bar.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.card_pts_today = self.create_metric_pod(self.metrics_bar, 0, "TODAY EARNED", "+0 Pts", "#10b981", "✨")
        self.card_total_vault = self.create_metric_pod(self.metrics_bar, 1, "WALLET VAULT", "0 Pts", ("#0284c7", "#00f0ff"), "💎")
        self.card_active_profiles = self.create_metric_pod(self.metrics_bar, 2, "ACTIVE NODES", "0 Ready", "#8b5cf6", "🤖")
        self.card_completed_searches = self.create_metric_pod(self.metrics_bar, 3, "TOTAL QUERIES", "0 Goal", "#f59e0b", "🔍")
        self.card_countdown = self.create_metric_pod(self.metrics_bar, 4, "NEXT CYCLE", "Ready Now", "#ec4899", "⏳")

        # 📈 Level 4 Sparkline Pod[cite: 6]
        self.build_sparkline_pod(self.metrics_bar, 5)

        # 2. View Containers[cite: 6]
        self.tab_monitor_view = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.tab_console_view = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.tab_accounts_view = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.tab_suspended_view = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.tab_settings_view = ctk.CTkFrame(self.main_content, fg_color="transparent")

        self.build_monitor_tab()
        self.build_console_tab()
        self.build_accounts_tab()
        self.build_suspended_tab()
        self.build_settings_tab()

    def create_metric_pod(self, parent, col, title, value, color, icon):
        frame = ctk.CTkFrame(
            parent,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=11,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032"),
            height=84
        )
        frame.grid(row=0, column=col, padx=3, sticky="ew")
        frame.pack_propagate(False)

        top_row = ctk.CTkFrame(frame, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(top_row, text=title, font=("Segoe UI", 9, "bold"), text_color=("#64748b", "#64748b")).pack(side="left")
        ctk.CTkLabel(top_row, text=icon, font=("Segoe UI", 12)).pack(side="right")

        val_lbl = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 15, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=10)
        return val_lbl

    def build_sparkline_pod(self, parent, col):
        frame = ctk.CTkFrame(
            parent,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=11,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032"),
            height=84
        )
        frame.grid(row=0, column=col, padx=3, sticky="ew")
        frame.pack_propagate(False)

        top_row = ctk.CTkFrame(frame, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(6, 0))
        ctk.CTkLabel(top_row, text="7-DAY TREND", font=("Segoe UI", 9, "bold"), text_color=("#64748b", "#64748b")).pack(side="left")
        
        self.spark_avg_lbl = ctk.CTkLabel(top_row, text="Avg: +0 Pts/d", font=("Segoe UI", 9, "bold"), text_color="#10b981")
        self.spark_avg_lbl.pack(side="right")

        self.sparkline_canvas = CyberSparkline(frame, width=160, height=44, bg_color="#121420")
        self.sparkline_canvas.pack(fill="both", expand=True, padx=8, pady=(2, 4))

    # --- TAB 1: LIVE MONITOR ---
    def build_monitor_tab(self):
        batch_bar = ctk.CTkFrame(
            self.tab_monitor_view,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=10,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032"),
            height=48
        )
        batch_bar.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            batch_bar,
            text="⚡ QUICK ACTIONS:",
            font=("Segoe UI", 11, "bold"),
            text_color=("#334155", "#94a3b8")
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            batch_bar,
            text="🌐 Open All Profiles",
            height=30,
            fg_color=("#0284c7", "#1e293b"),
            hover_color=("#0369a1", "#334155"),
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.open_all_profiles
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            batch_bar,
            text="🧹 Purge Cache",
            height=30,
            fg_color=("#d97706", "#78350f"),
            hover_color=("#b45309", "#92400e"),
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.purge_junk_cache
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            batch_bar,
            text="🔁 Reset Searches",
            height=30,
            fg_color=("#6366f1", "#4338ca"),
            hover_color=("#4f46e5", "#3730a3"),
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.reset_all_searches_today
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            batch_bar,
            text="📥 Export CSV",
            height=30,
            fg_color="#059669",
            hover_color="#10b981",
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.export_history_csv
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            batch_bar,
            text="🔄 Refresh Grid",
            height=30,
            fg_color=("#64748b", "#374151"),
            hover_color=("#475569", "#4b5563"),
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.force_refresh
        ).pack(side="right", padx=15)

        # 🟢 SMART FILTER & SEARCH BAR[cite: 6]
        filter_bar = ctk.CTkFrame(
            self.tab_monitor_view,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=10,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032"),
            height=46
        )
        filter_bar.pack(fill="x", pady=(0, 6))

        search_pod = ctk.CTkFrame(filter_bar, fg_color="transparent")
        search_pod.pack(side="left", padx=(10, 10), pady=6)

        self.search_entry = ctk.CTkEntry(
            search_pod,
            placeholder_text="🔍 Filter Profile or Email...",
            width=230,
            height=30,
            corner_radius=6,
            fg_color=("#ffffff", "#0b0c13"),
            border_color=("#cbd9e8", "#24283d"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.search_entry.pack(side="left", padx=(0, 4))
        self.search_entry.bind("<KeyRelease>", self.on_search_filter_changed)

        ctk.CTkButton(
            search_pod,
            text="✕",
            width=26,
            height=30,
            fg_color=("#e2ecf7", "#1a1d2d"),
            hover_color=("#cbd9e8", "#25293f"),
            text_color=("#64748b", "#94a3b8"),
            font=("Segoe UI", 10, "bold"),
            command=self.clear_search_filter
        ).pack(side="left")

        self.category_seg = ctk.CTkSegmentedButton(
            filter_bar,
            values=["All", "🎁 Ready", "⏳ Incomplete", "✅ Done", "▶️ Running"],
            command=self.on_category_filter_changed,
            height=30,
            corner_radius=6,
            selected_color="#0284c7",
            selected_hover_color="#0369a1",
            unselected_color=("#e2ecf7", "#141724"),
            unselected_hover_color=("#cbd9e8", "#1c2032"),
            text_color=("#0f172a", "#f8fafc"),
            font=("Segoe UI", 10, "bold")
        )
        self.category_seg.set("All")
        self.category_seg.pack(side="right", padx=(0, 10), pady=6)

        data_bar = ctk.CTkFrame(
            self.tab_monitor_view,
            fg_color=("#e8edf5", "#0f1a1a"),
            corner_radius=8,
            border_width=1,
            border_color=("#0284c7", "#006688"),
            height=28
        )
        data_bar.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            data_bar,
            text="📊 TODAY'S DATA USAGE:",
            font=("Segoe UI", 10, "bold"),
            text_color=("#475569", "#94a3b8")
        ).pack(side="left", padx=12)

        self.data_download_lbl = ctk.CTkLabel(
            data_bar,
            text="⬇️ Download: 0 MB",
            font=("Segoe UI", 10, "bold"),
            text_color=("#0284c7", "#00aaff")
        )
        self.data_download_lbl.pack(side="left", padx=8)

        self.data_upload_lbl = ctk.CTkLabel(
            data_bar,
            text="⬆️ Upload: 0 MB",
            font=("Segoe UI", 10, "bold"),
            text_color=("#d97706", "#ff8844")
        )
        self.data_upload_lbl.pack(side="left", padx=8)

        self.data_total_lbl = ctk.CTkLabel(
            data_bar,
            text="📦 Total: 0 MB",
            font=("Segoe UI", 10, "bold"),
            text_color=("#059669", "#10b981")
        )
        self.data_total_lbl.pack(side="left", padx=8)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.tab_monitor_view,
            fg_color=("#edf3f9", "#0f1018"),
            corner_radius=12,
            border_width=2,
            border_color=("#c7d6e5", "#1a1d2d"),
            label_text="🚀 Active Cluster Node Grid (Click on ✏️ Edit to customize target goal)",
            label_font=("Segoe UI", 11, "bold"),
            label_text_color=("#334155", "#94a3b8")
        )
        self.scroll_frame.pack(fill="both", expand=True)
        self.bind_scroll_events(self.scroll_frame)

    def on_search_filter_changed(self, event=None):
        self.search_filter_text = self.search_entry.get().strip().lower()
        self.force_refresh()

    def on_category_filter_changed(self, selected_val=None):
        if selected_val:
            self.active_category_filter = selected_val
        else:
            self.active_category_filter = self.category_seg.get()
        self.force_refresh()

    def clear_search_filter(self):
        self.search_entry.delete(0, "end")
        self.search_filter_text = ""
        self.force_refresh()

    def reset_all_searches_today(self):
        if messagebox.askyesno("Reset Searches", "Are you sure you want to reset today's search count to 0 for ALL profiles?\n\n(Total Vault balance and points remain intact)[cite: 4]"):
            try:
                if os.path.exists(self.history_path):
                    with open(self.history_path, "r", encoding="utf-8") as f:
                        history = json.load(f)
                    today = time.strftime("%Y-%m-%d")
                    if today in history and isinstance(history[today], dict):
                        for clean_name in history[today]:
                            if isinstance(history[today][clean_name], dict):
                                history[today][clean_name]["searches"] = 0
                        with open(self.history_path, "w", encoding="utf-8") as f:
                            json.dump(history, f, indent=4)
                self.force_refresh()
                messagebox.showinfo("Reset Complete", "All search counters reset to 0 for today!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset searches: {e}")

    def reset_single_profile_searches(self, name):
        clean_name = name.replace(" ", "_")
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                today = time.strftime("%Y-%m-%d")
                if today in history and clean_name in history[today] and isinstance(history[today][clean_name], dict):
                    history[today][clean_name]["searches"] = 0
                    with open(self.history_path, "w", encoding="utf-8") as f:
                        json.dump(history, f, indent=4)
            self.force_refresh()
        except Exception as e:
            print(f"Error resetting search for {name}: {e}")

    # --- TAB 2: LIVE MATRIX TERMINAL ---
    def build_console_tab(self):
        console_bar = ctk.CTkFrame(
            self.tab_console_view,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=10,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032"),
            height=45
        )
        console_bar.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            console_bar,
            text="💻 LIVE PROCESS STDOUT STREAM",
            font=("Segoe UI", 11, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            console_bar,
            text="🧹 Clear Terminal",
            height=28,
            width=110,
            fg_color=("#64748b", "#374151"),
            hover_color=("#475569", "#4b5563"),
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.clear_console
        ).pack(side="right", padx=15)

        self.console_text = ctk.CTkTextbox(
            self.tab_console_view,
            fg_color=("#0b0f19", "#08090f"),
            text_color="#10b981",
            font=("Consolas", 11),
            corner_radius=10,
            border_width=2,
            border_color=("#1e293b", "#1a1d2d")
        )
        self.console_text.pack(fill="both", expand=True)
        self.console_text.configure(state="disabled")

    def clear_console(self):
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")

    # --- TAB 3: PROFILES MANAGER ---
    def build_accounts_tab(self):
        acc_box = ctk.CTkFrame(
            self.tab_accounts_view,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=14,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032")
        )
        acc_box.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(
            acc_box,
            text="➕ Register Profile Node",
            font=("Segoe UI", 16, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            acc_box,
            text="Add unique Microsoft account profiles with custom gift voucher goals.",
            font=("Segoe UI", 11),
            text_color=("#475569", "#64748b")
        ).pack(anchor="w", padx=20, pady=(0, 15))

        input_grid = ctk.CTkFrame(acc_box, fg_color="transparent")
        input_grid.pack(fill="x", padx=20, pady=(0, 20))
        input_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self.new_name = ctk.CTkEntry(
            input_grid,
            placeholder_text="Profile Alias (e.g. Account 1)",
            height=42,
            corner_radius=8,
            fg_color=("#ffffff", "#0b0c13"),
            border_color=("#cbd9e8", "#24283d"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.new_name.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.new_email = ctk.CTkEntry(
            input_grid,
            placeholder_text="Microsoft Email Address",
            height=42,
            corner_radius=8,
            fg_color=("#ffffff", "#0b0c13"),
            border_color=("#cbd9e8", "#24283d"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.new_email.grid(row=0, column=1, padx=4, sticky="ew")

        self.new_target_pts = ctk.CTkEntry(
            input_grid,
            placeholder_text="Custom Goal (e.g. 8150)",
            height=42,
            corner_radius=8,
            fg_color=("#ffffff", "#0b0c13"),
            border_color=("#cbd9e8", "#24283d"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.new_target_pts.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        ctk.CTkButton(
            acc_box,
            text="Provision Profile Node",
            height=42,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#3b82f6",
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold"),
            command=self.add_account_logic
        ).pack(fill="x", padx=20, pady=(0, 20))

    # --- TAB: SUSPENDED ACCOUNTS VIEW ---
    def build_suspended_tab(self):
        sus_top_bar = ctk.CTkFrame(
            self.tab_suspended_view,
            fg_color=("#fef2f2", "#181014"),
            corner_radius=10,
            border_width=2,
            border_color=("#fecaca", "#4c1d24"),
            height=48
        )
        sus_top_bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            sus_top_bar,
            text="⛔ SUSPENDED NODES VAULT",
            font=("Segoe UI", 11, "bold"),
            text_color="#ef4444"
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            sus_top_bar,
            text="🗑️ Authorize Purge (All)",
            height=30,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.purge_all_suspended
        ).pack(side="right", padx=15)

        self.sus_scroll_frame = ctk.CTkScrollableFrame(
            self.tab_suspended_view,
            fg_color=("#edf3f9", "#0f1018"),
            corner_radius=12,
            border_width=2,
            border_color=("#fca5a5", "#3b171c"),
            label_text="⚠️ Quarantined / Suspended Microsoft Accounts",
            label_font=("Segoe UI", 12, "bold"),
            label_text_color="#ef4444"
        )
        self.sus_scroll_frame.pack(fill="both", expand=True)
        self.bind_scroll_events(self.sus_scroll_frame)

    # --- TAB 4: ENGINE SETTINGS ---
    def build_settings_tab(self):
        sett_container = ctk.CTkScrollableFrame(
            self.tab_settings_view,
            fg_color=("#edf3f9", "#0f1018"),
            corner_radius=12,
            border_width=2,
            border_color=("#c7d6e5", "#1a1d2d")
        )
        sett_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            sett_container,
            text="⚡ ENGINE & TIMING CONTROLS",
            font=("Segoe UI", 13, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        ctrl_grid = ctk.CTkFrame(
            sett_container,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=12,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032")
        )
        ctrl_grid.pack(fill="x", padx=15, pady=5)
        ctrl_grid.grid_columnconfigure((0, 1, 2), weight=1)

        c1 = ctk.CTkFrame(ctrl_grid, fg_color="transparent")
        c1.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        ctk.CTkLabel(c1, text="🔍 Daily Searches:", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(anchor="w")
        
        # 🟢 Dynamic 1 to 50 Searches Dropdown
        self.search_goal_opt = ctk.CTkOptionMenu(
            c1,
            values=[str(i) for i in range(1, 51)],
            command=self.save_settings,
            height=36,
            corner_radius=8,
            fg_color=("#d6e3f0", "#1a1d2d"),
            button_color=("#b6ccdf", "#25293f"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.search_goal_opt.pack(fill="x", pady=6)

        c2 = ctk.CTkFrame(ctrl_grid, fg_color="transparent")
        c2.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        ctk.CTkLabel(c2, text="⚡ Parallel Batch Size:", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(anchor="w")
        self.batch_opt = ctk.CTkOptionMenu(
            c2,
            values=[str(i) for i in range(1, 16)],
            command=self.save_settings,
            height=36,
            corner_radius=8,
            fg_color=("#d6e3f0", "#1a1d2d"),
            button_color=("#b6ccdf", "#25293f"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.batch_opt.pack(fill="x", pady=6)

        c3 = ctk.CTkFrame(ctrl_grid, fg_color="transparent")
        c3.grid(row=0, column=2, padx=15, pady=15, sticky="ew")
        ctk.CTkLabel(c3, text="⏱️ Search Delay (Gap):", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(anchor="w")
        self.delay_opt = ctk.CTkOptionMenu(
            c3,
            values=["1-2s", "2-3s", "3-4s", "4-5s", "5-6s", "6-7s", "7-8s", "8-9s", "9-10s"],
            command=self.save_settings,
            height=36,
            corner_radius=8,
            fg_color=("#d6e3f0", "#1a1d2d"),
            button_color=("#b6ccdf", "#25293f"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.delay_opt.pack(fill="x", pady=6)

        # 🎯 INDEPENDENT GLOBAL DEFAULT TARGET BOX[cite: 6]
        ctk.CTkLabel(
            sett_container,
            text="🎯 GLOBAL DEFAULT REWARD GOAL",
            font=("Segoe UI", 13, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w", padx=15, pady=(20, 10))

        target_box = ctk.CTkFrame(
            sett_container,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=12,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032")
        )
        target_box.pack(fill="x", padx=15, pady=5)

        t_row = ctk.CTkFrame(target_box, fg_color="transparent")
        t_row.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(t_row, text="🎁 Default Milestone Target Points (Applies if profile has no custom goal):", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(side="left", padx=(0, 10))
        
        self.target_pts_entry = ctk.CTkEntry(t_row, placeholder_text="e.g. 8150", width=120, height=36, corner_radius=8)
        self.target_pts_entry.insert(0, str(self.target_points))
        self.target_pts_entry.pack(side="left", padx=5)

        ctk.CTkButton(t_row, text="💾 Save Goal", width=100, height=36, fg_color="#059669", hover_color="#10b981", font=("Segoe UI", 10, "bold"), command=self.save_settings).pack(side="left", padx=8)

        # ⏰ BACKGROUND AUTO-LAUNCH SCHEDULER[cite: 6]
        ctk.CTkLabel(
            sett_container,
            text="⏰ BACKGROUND AUTO-LAUNCH SCHEDULER",
            font=("Segoe UI", 13, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w", padx=15, pady=(20, 10))

        sched_box = ctk.CTkFrame(
            sett_container,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=12,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032")
        )
        sched_box.pack(fill="x", padx=15, pady=5)

        self.auto_sched_var = ctk.BooleanVar(value=False)
        s_row = ctk.CTkFrame(sched_box, fg_color="transparent")
        s_row.pack(fill="x", padx=15, pady=12)

        self.sched_switch = ctk.CTkSwitch(
            s_row,
            text="Enable Daily Auto-Launch",
            font=("Segoe UI", 12, "bold"),
            text_color=("#1e293b", "#e2e8f0"),
            variable=self.auto_sched_var,
            command=self.save_settings,
            progress_color=("#0284c7", "#00f0ff")
        )
        self.sched_switch.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(s_row, text="Target Time (24h HH:MM):", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(side="left", padx=(0, 8))

        self.sched_time_entry = ctk.CTkEntry(s_row, placeholder_text="05:30", width=100, height=36, corner_radius=8)
        self.sched_time_entry.insert(0, self.scheduler_time)
        self.sched_time_entry.pack(side="left", padx=5)

        ctk.CTkButton(s_row, text="💾 Save Timer", width=100, height=36, fg_color="#059669", hover_color="#10b981", font=("Segoe UI", 10, "bold"), command=self.save_settings).pack(side="left", padx=8)

        # 📱 OPTIONAL TELEGRAM NOTIFICATIONS[cite: 6]
        ctk.CTkLabel(
            sett_container,
            text="📱 TELEGRAM NOTIFICATIONS (100% OPTIONAL)",
            font=("Segoe UI", 13, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w", padx=15, pady=(20, 10))

        tg_grid = ctk.CTkFrame(
            sett_container,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=12,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032")
        )
        tg_grid.pack(fill="x", padx=15, pady=5)
        tg_grid.grid_columnconfigure((0, 1), weight=1)

        tg_c1 = ctk.CTkFrame(tg_grid, fg_color="transparent")
        tg_c1.grid(row=0, column=0, padx=15, pady=12, sticky="ew")
        ctk.CTkLabel(tg_c1, text="🤖 Telegram Bot Token (Optional):", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(anchor="w")
        self.tg_token_entry = ctk.CTkEntry(tg_c1, placeholder_text="123456:ABC-DEF... (Leave blank if not used)", height=36, corner_radius=8, show="•")
        self.tg_token_entry.insert(0, self.tg_token)
        self.tg_token_entry.pack(fill="x", pady=6)

        tg_c2 = ctk.CTkFrame(tg_grid, fg_color="transparent")
        tg_c2.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        ctk.CTkLabel(tg_c2, text="💬 Telegram Chat ID (Optional):", font=("Segoe UI", 11, "bold"), text_color=("#334155", "#94a3b8")).pack(anchor="w")
        
        chat_box_row = ctk.CTkFrame(tg_c2, fg_color="transparent")
        chat_box_row.pack(fill="x", pady=6)
        self.tg_chat_entry = ctk.CTkEntry(chat_box_row, placeholder_text="e.g. 987654321", height=36, corner_radius=8)
        self.tg_chat_entry.insert(0, self.tg_chat_id)
        self.tg_chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            chat_box_row,
            text="🔔 Test",
            width=60,
            height=36,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=("Segoe UI", 10, "bold"),
            command=self.send_test_telegram
        ).pack(side="right")

        # Switches Section[cite: 6]
        ctk.CTkLabel(
            sett_container,
            text="🛡️ REWARDS MODULE SWITCHES",
            font=("Segoe UI", 13, "bold"),
            text_color=("#0284c7", "#00f0ff")
        ).pack(anchor="w", padx=15, pady=(20, 10))

        switches_box = ctk.CTkFrame(
            sett_container,
            fg_color=("#f4f8fc", "#121420"),
            corner_radius=12,
            border_width=2,
            border_color=("#cbd9e8", "#1c2032")
        )
        switches_box.pack(fill="x", padx=15, pady=5)
        switches_box.grid_columnconfigure((0, 1), weight=1)

        self.headless_var = ctk.BooleanVar(value=True)
        self.daily_set_var = ctk.BooleanVar(value=True)
        self.dashboard_tasks_var = ctk.BooleanVar(value=True)
        self.app_exclusive_var = ctk.BooleanVar(value=True)
        self.app_checkin_var = ctk.BooleanVar(value=True)
        self.weather_var = ctk.BooleanVar(value=True)
        self.read_earn_var = ctk.BooleanVar(value=True)
        self.tg_alerts_var = ctk.BooleanVar(value=False)

        self.create_switch_tile(switches_box, 0, 0, "Headless Mode", "Runs Chrome completely invisible in background", self.headless_var)
        self.create_switch_tile(switches_box, 0, 1, "Daily Set (/earn Cards)", "Solves Quiz, True/False, and Standard Cards", self.daily_set_var)
        self.create_switch_tile(switches_box, 1, 0, "Dashboard Tasks (/dashboard)", "Scrapes & executes cards from root dashboard", self.dashboard_tasks_var)
        self.create_switch_tile(switches_box, 1, 1, "Store App Promos (+50 Pts)", "Executes Bing App mobile promotional bonus", self.app_exclusive_var)
        self.create_switch_tile(switches_box, 2, 0, "App Daily Check-In", "Executes 7-day progressive check-in cycle", self.app_checkin_var)
        self.create_switch_tile(switches_box, 2, 1, "App Promotions (Weather)", "Solves wallpaper, dynamic quests, and weather", self.weather_var)
        self.create_switch_tile(switches_box, 3, 0, "Read to Earn (30 Pts)", "Automates MSN News article consumption", self.read_earn_var)
        self.create_switch_tile(switches_box, 3, 1, "Telegram Push Alerts", "Sends completion summary & alerts to Telegram", self.tg_alerts_var)

    def create_switch_tile(self, parent, row, col, title, desc, variable):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=15, pady=12, sticky="ew")

        switch = ctk.CTkSwitch(
            frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color=("#1e293b", "#e2e8f0"),
            variable=variable,
            command=self.save_settings,
            progress_color=("#0284c7", "#00f0ff")
        )
        switch.pack(anchor="w")
        ctk.CTkLabel(frame, text=desc, font=("Segoe UI", 10), text_color=("#64748b", "#64748b")).pack(anchor="w", padx=(45, 0))

    def select_tab(self, tab_name):
        self.btn_tab_monitor.configure(fg_color="transparent", text_color=("#334155", "#94a3b8"))
        self.btn_tab_console.configure(fg_color="transparent", text_color=("#334155", "#94a3b8"))
        self.btn_tab_accounts.configure(fg_color="transparent", text_color=("#334155", "#94a3b8"))
        self.btn_tab_suspended.configure(fg_color="transparent", text_color=("#334155", "#94a3b8"))
        self.btn_tab_settings.configure(fg_color="transparent", text_color=("#334155", "#94a3b8"))

        self.tab_monitor_view.grid_forget()
        self.tab_console_view.grid_forget()
        self.tab_accounts_view.grid_forget()
        self.tab_suspended_view.grid_forget()
        self.tab_settings_view.grid_forget()

        active_btn_color = ("#c2d5e8", "#181a28")
        active_txt_color = ("#0284c7", "#00f0ff")

        if tab_name == "monitor":
            self.btn_tab_monitor.configure(fg_color=active_btn_color, text_color=active_txt_color)
            self.tab_monitor_view.grid(row=1, column=0, sticky="nsew")
        elif tab_name == "console":
            self.btn_tab_console.configure(fg_color=active_btn_color, text_color=active_txt_color)
            self.tab_console_view.grid(row=1, column=0, sticky="nsew")
        elif tab_name == "accounts":
            self.btn_tab_accounts.configure(fg_color=active_btn_color, text_color=active_txt_color)
            self.tab_accounts_view.grid(row=1, column=0, sticky="nsew")
        elif tab_name == "suspended":
            self.btn_tab_suspended.configure(fg_color=("#fee2e2", "#2d1217"), text_color="#ef4444")
            self.tab_suspended_view.grid(row=1, column=0, sticky="nsew")
        elif tab_name == "settings":
            self.btn_tab_settings.configure(fg_color=active_btn_color, text_color=active_txt_color)
            self.tab_settings_view.grid(row=1, column=0, sticky="nsew")

    def bind_scroll_events(self, widget):
        try:
            canvas = widget._parent_canvas
            
            def _on_mousewheel(event):
                try:
                    if platform.system() == "Windows":
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    elif platform.system() == "Darwin":
                        canvas.yview_scroll(int(-1 * event.delta), "units")
                    else:
                        if event.num == 4:
                            canvas.yview_scroll(-1, "units")
                        elif event.num == 5:
                            canvas.yview_scroll(1, "units")
                except Exception:
                    pass

            def _bind_recursive(node):
                node.bind("<MouseWheel>", _on_mousewheel, add="+")
                node.bind("<Button-4>", _on_mousewheel, add="+")
                node.bind("<Button-5>", _on_mousewheel, add="+")
                for child in node.winfo_children():
                    _bind_recursive(child)

            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)
            
            _bind_recursive(widget)
        except Exception:
            pass

    # ==========================================
    # ⚙️ EXPORT, MASS TOOLS & AUTOMATION LOGIC
    # ==========================================
    def purge_junk_cache(self):
        if self.is_running:
            messagebox.showwarning("Engine Active", "Please stop or wait for bot engine before clearing cache.")
            return

        freed_bytes = 0
        junk_dirs = ['cache', 'code cache', 'gpucache', 'blob_storage', 'service worker', 'crashpad', 'dawncachedir', 'shadercache']
        
        if os.path.exists(self.session_path):
            for root, dirs, files in os.walk(self.session_path, topdown=False):
                for d in dirs:
                    if d.lower() in junk_dirs:
                        dp = os.path.join(root, d)
                        try:
                            for r, _, fs in os.walk(dp):
                                freed_bytes += os.path.getsize(os.path.join(r, f))
                            shutil.rmtree(dp, ignore_errors=True)
                        except Exception:
                            pass

        self.async_disk_calc_loop()
        mb_freed = freed_bytes / (1024 * 1024)
        messagebox.showinfo("Purge Complete", f"Purged {mb_freed:.1f} MB of junk browser cache!\nLogin cookies and sessions are 100% intact.")

    def edit_profile_target_dialog(self, account_name):
        dialog = ctk.CTkInputDialog(text=f"Enter Custom Reward Goal Points for '{account_name}':", title="Set Custom Goal")
        val = dialog.get_input()
        if val:
            try:
                new_tgt = int(val.strip())
                if os.path.exists(self.accounts_path):
                    with open(self.accounts_path, "r") as f:
                        accounts = json.load(f)
                    for acc in accounts:
                        if acc["name"] == account_name:
                            acc["target"] = new_tgt
                            break
                    with open(self.accounts_path, "w") as f:
                        json.dump(accounts, f, indent=4)
                    self.force_refresh()
            except Exception:
                messagebox.showerror("Error", "Please enter a valid numeric points value!")

    def send_telegram_msg(self, text):
        token = self.tg_token
        chat_id = self.tg_chat_id
        
        if not token or not chat_id:
            return False

        def _send():
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
                requests.post(url, json=payload, timeout=8)
            except Exception as e:
                print(f"Telegram Webhook Error: {e}")

        threading.Thread(target=_send, daemon=True).start()
        return True

    def send_test_telegram(self):
        self.save_settings()
        if not self.tg_token or not self.tg_chat_id:
            messagebox.showwarning("Telegram Setup", "Please enter both Telegram Bot Token and Chat ID first!")
            return
        msg = "🔔 <b>MS BOT ULTRA • TEST ALERT</b>\n\n✅ Telegram Webhook Connected Successfully!\nYou will receive completion reports and alerts here."
        if self.send_telegram_msg(msg):
            messagebox.showinfo("Alert Dispatched", "Test message sent to Telegram successfully!")

    def export_history_csv(self):
        try:
            if not os.path.exists(self.history_path):
                messagebox.showwarning("Export Failed", "No history data logged yet.")
                return

            save_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Document", "*.csv")],
                initialfile=f"Rewards_Audit_Report_{time.strftime('%Y%m%d')}.csv"
            )
            if not save_file:
                return

            with open(self.history_path, "r") as f:
                hist_data = json.load(f)

            with open(save_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Date", "Account Profile", "Searches Completed", "Daily Goal", "Today Points Earned", "Total Points Vault"])

                for dt, accs in hist_data.items():
                    for name, d in accs.items():
                        writer.writerow([
                            dt,
                            name,
                            d.get("searches", 0),
                            self.daily_goal,
                            d.get("total_points", 0),
                            d.get("total_balance", 0)
                        ])

            messagebox.showinfo("Export Complete", f"Audit report successfully exported to:\n{save_file}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

    def open_all_profiles(self):
        if not os.path.exists(self.accounts_path):
            return
        with open(self.accounts_path, "r") as f:
            accounts = json.load(f)

        if not accounts:
            messagebox.showinfo("Empty Profiles", "No profiles configured.")
            return

        if messagebox.askyesno("Launch All", f"Open Chromium browser sessions for all {len(accounts)} profiles?"):
            for acc in accounts:
                self.open_account_browser(acc["name"])
                time.sleep(0.5)

    def recover_account(self, name):
        """Quarantined suspended account ko wapas active profile me restore karta hai."""
        if messagebox.askyesno("Recover Node", f"Un-quarantine and restore profile '{name}' back to active cluster?[cite: 6]"):
            clean_name = name.replace(" ", "_")
            try:
                if os.path.exists(self.history_path):
                    with open(self.history_path, "r", encoding="utf-8") as f:
                        history = json.load(f)
                    for dt in history:
                        if isinstance(history[dt], dict) and clean_name in history[dt]:
                            if "status" in history[dt][clean_name]:
                                del history[dt][clean_name]["status"]
                    with open(self.history_path, "w", encoding="utf-8") as f:
                        json.dump(history, f, indent=4)

                self.force_refresh()
                self.select_tab("monitor")
                messagebox.showinfo("Node Restored", f"Profile '{name}' has been removed from quarantine and returned to active cluster grid![cite: 6]")
            except Exception as e:
                messagebox.showerror("Recovery Error", f"Failed to recover account: {e}")

    def purge_all_suspended(self):
        try:
            if not os.path.exists(self.history_path) or not os.path.exists(self.accounts_path):
                return
            with open(self.history_path, "r") as f:
                history = json.load(f)
            with open(self.accounts_path, "r") as f:
                accounts = json.load(f)

            today = time.strftime("%Y-%m-%d")
            today_data = history.get(today, {})

            suspended_list = []
            for acc in accounts:
                clean_name = acc["name"].replace(" ", "_")
                if today_data.get(clean_name, {}).get("status") == "SUSPENDED":
                    suspended_list.append(acc["name"])

            if not suspended_list:
                messagebox.showinfo("Clean Vault", "No suspended accounts found to purge.")
                return

            if messagebox.askyesno("Authorize Purge", f"Permanently delete {len(suspended_list)} suspended accounts & their session data?"):
                for name in suspended_list:
                    clean_name = name.replace(" ", "_")
                    accounts = [acc for acc in accounts if acc["name"] != name]
                    profile_dir = os.path.join(self.session_path, clean_name)
                    if os.path.exists(profile_dir):
                        shutil.rmtree(profile_dir, ignore_errors=True)

                with open(self.accounts_path, "w") as f:
                    json.dump(accounts, f, indent=4)

                self.force_refresh()
                messagebox.showinfo("Purge Complete", f"Successfully wiped {len(suspended_list)} suspended accounts.")
        except Exception as e:
            messagebox.showerror("Purge Error", f"Failed to purge suspended accounts: {e}")

    def initial_load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r") as f:
                    cfg = json.load(f)
                    self.batch_opt.set(str(cfg.get("batch_size", 4)))
                    self.delay_opt.set(str(cfg.get("search_delay", "3-4s")))
                    self.headless_var.set(cfg.get("headless", True))
                    self.daily_set_var.set(cfg.get("enable_daily_set", True))
                    self.dashboard_tasks_var.set(cfg.get("enable_dashboard_tasks", True))
                    self.app_exclusive_var.set(cfg.get("enable_app_exclusive", True))
                    self.app_checkin_var.set(cfg.get("enable_app_checkin", True))
                    self.weather_var.set(cfg.get("enable_weather_check", True))
                    self.read_earn_var.set(cfg.get("enable_read_to_earn", True))
                    self.tg_alerts_var.set(cfg.get("enable_telegram_alerts", False))
                    self.target_points = int(cfg.get("target_gift_points", 8150))
                    self.tg_token = cfg.get("telegram_bot_token", "")
                    self.tg_chat_id = cfg.get("telegram_chat_id", "")
                    self.daily_goal = int(cfg.get("daily_search_goal", 20))
                    self.search_goal_opt.set(str(self.daily_goal))
                    self.auto_sched_var.set(cfg.get("enable_auto_scheduler", False))
                    self.scheduler_time = str(cfg.get("auto_scheduler_time", "05:30")).strip()
                    if hasattr(self, "sched_time_entry"):
                        self.sched_time_entry.delete(0, "end")
                        self.sched_time_entry.insert(0, self.scheduler_time)
                    theme = cfg.get("theme_mode", "Dark")
                    self.theme_opt.set(theme)
                    ctk.set_appearance_mode(theme.lower())
            except Exception:
                self.daily_goal = 20
                self.target_points = 8150
                self.search_goal_opt.set("20")
                self.delay_opt.set("3-4s")
                self.theme_opt.set("Dark")
                ctk.set_appearance_mode("dark")

    def save_settings(self, *args):
        os.makedirs("config", exist_ok=True)
        try:
            self.daily_goal = int(self.search_goal_opt.get())
        except Exception:
            self.daily_goal = 20

        if hasattr(self, "tg_token_entry"):
            self.tg_token = self.tg_token_entry.get().strip()
        if hasattr(self, "tg_chat_entry"):
            self.tg_chat_id = self.tg_chat_entry.get().strip()
        if hasattr(self, "target_pts_entry"):
            try:
                self.target_points = int(self.target_pts_entry.get().strip())
            except Exception:
                self.target_points = 8150
        if hasattr(self, "sched_time_entry"):
            self.scheduler_time = self.sched_time_entry.get().strip() or "05:30"

        new_cfg = {
            "daily_search_goal": self.daily_goal,
            "target_gift_points": self.target_points,
            "batch_size": int(self.batch_opt.get()),
            "search_delay": self.delay_opt.get(),
            "headless": self.headless_var.get(),
            "enable_daily_set": self.daily_set_var.get(),
            "enable_dashboard_tasks": self.dashboard_tasks_var.get(),
            "enable_app_exclusive": self.app_exclusive_var.get(),
            "enable_app_checkin": self.app_checkin_var.get(),
            "enable_weather_check": self.weather_var.get(),
            "enable_read_to_earn": self.read_earn_var.get(),
            "enable_telegram_alerts": self.tg_alerts_var.get(),
            "enable_auto_scheduler": self.auto_sched_var.get(),
            "auto_scheduler_time": self.scheduler_time,
            "telegram_bot_token": self.tg_token,
            "telegram_chat_id": self.tg_chat_id,
            "theme_mode": self.theme_opt.get()
        }
        with open(self.settings_path, "w") as f:
            json.dump(new_cfg, f, indent=4)

        self.refresh_logic()

    def safe_launch_sequence(self):
        if self.is_batch_running:
            messagebox.showwarning("Warning", "Batch engine is already executing in background!")
            return

        current_ram = psutil.virtual_memory().percent
        if current_ram >= 95:
            messagebox.showerror("Critical RAM State", f"System RAM saturated at {current_ram}%. Safety lockout engaged!")
            return

        self.is_batch_running = True
        self.holo_3d.set_active(True)
        threading.Thread(target=self.run_bot_thread, daemon=True).start()

    def run_bot_thread(self):
        try:
            if chrome_isolate and hasattr(chrome_isolate, "main"):
                chrome_isolate.main()
            else:
                messagebox.showerror("Module Error", "Could not locate 'chrome_isolate' module!")
        except Exception:
            error_details = traceback.format_exc()
            messagebox.showerror("Runtime Failure", f"Engine crash trace:\n\n{error_details}")
        finally:
            self.is_batch_running = False
            if not self.active_running_profiles:
                self.holo_3d.set_active(False)
            if self.tg_alerts_var.get():
                self.send_completion_telegram_report()

    # 🟢 CONCURRENT INDIVIDUAL RUN HANDLER
    def run_single_profile_threaded(self, name):
        if self.is_batch_running:
            messagebox.showwarning("Busy", "Full cluster batch is actively running! Please wait for it to finish.")
            return

        if name in self.active_running_profiles:
            messagebox.showinfo("Running", f"Profile '{name}' is already executing in background!")
            return

        current_ram = psutil.virtual_memory().percent
        if current_ram >= 95:
            messagebox.showerror("Critical RAM State", f"System RAM saturated at {current_ram}%. Safety lockout engaged!")
            return

        if not os.path.exists(self.accounts_path):
            return
        with open(self.accounts_path, "r") as f:
            accounts = json.load(f)
            
        target_acc = next((acc for acc in accounts if acc["name"] == name), None)
        if not target_acc:
            return

        self.active_running_profiles.add(name)
        self.holo_3d.set_active(True)
        self.force_refresh()

        def _run():
            try:
                if chrome_isolate and hasattr(chrome_isolate, "run_single_account"):
                    chrome_isolate.run_single_account(target_acc)
                else:
                    messagebox.showerror("Module Error", "Could not locate 'run_single_account' in chrome_isolate module!")
            except Exception:
                error_details = traceback.format_exc()
                messagebox.showerror("Runtime Failure", f"Engine crash trace:\n\n{error_details}")
            finally:
                self.active_running_profiles.discard(name)
                if not self.active_running_profiles and not self.is_batch_running:
                    self.holo_3d.set_active(False)
                    if self.tg_alerts_var.get():
                        self.send_completion_telegram_report()
                self.force_refresh()

        threading.Thread(target=_run, daemon=True).start()

    # 🟢 INDIVIDUAL PROFILE PAUSE/STOP HANDLER
    def stop_single_profile(self, name):
        if chrome_isolate and hasattr(chrome_isolate, "stop_single_account"):
            chrome_isolate.stop_single_account(name)
        self.active_running_profiles.discard(name)
        if not self.active_running_profiles and not self.is_batch_running:
            self.holo_3d.set_active(False)
        self.force_refresh()

    def send_completion_telegram_report(self):
        try:
            with open(self.history_path, "r") as f:
                history = json.load(f)
            today = time.strftime("%Y-%m-%d")
            today_data = history.get(today, {})
            tot_pts = sum(d.get("total_points", 0) for d in today_data.values() if isinstance(d, dict))
            tot_bal = sum(d.get("total_balance", 0) for d in today_data.values() if isinstance(d, dict))
            msg = (
                f"🏁 <b>MS BOT ULTRA • MISSION COMPLETE</b>\n\n"
                f"✨ <b>Today Earned:</b> +{tot_pts:,} Pts\n"
                f"💎 <b>Total Vault:</b> {tot_bal:,} Pts\n"
                f"🤖 <b>Active Nodes:</b> {len(today_data)}\n"
                f"📅 <b>Date:</b> {today}"
            )
            self.send_telegram_msg(msg)
        except Exception:
            pass

    def open_account_browser(self, name):
        clean_name = name.replace(" ", "_")
        profile_dir = os.path.join(self.session_path, clean_name)
        os.makedirs(profile_dir, exist_ok=True)

        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]

        chrome_bin = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_bin = path
                break

        if not chrome_bin:
            chrome_bin = "chrome"

        cmd = [
            chrome_bin,
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "https://rewards.bing.com"
        ]

        def launch():
            try:
                subprocess.Popen(cmd)
            except Exception as e:
                messagebox.showerror("Launch Failure", f"Failed to instantiate browser for {name}:\n{e}")

        threading.Thread(target=launch, daemon=True).start()

    def add_account_logic(self):
        name = self.new_name.get().strip()
        email = self.new_email.get().strip()
        target_str = self.new_target_pts.get().strip()
        
        try:
            custom_target = int(target_str) if target_str else self.target_points
        except ValueError:
            custom_target = self.target_points

        if not name or not email:
            messagebox.showwarning("Input Validation", "Both Profile Alias and Email Address required!")
            return
        try:
            os.makedirs("config", exist_ok=True)
            if os.path.exists(self.accounts_path):
                with open(self.accounts_path, "r") as f:
                    accounts = json.load(f)
            else:
                accounts = []

            if any(acc["name"] == name for acc in accounts):
                messagebox.showwarning("Duplicate Alias", "A profile with this alias already exists!")
                return

            accounts.append({"name": name, "email": email, "target": custom_target})
            with open(self.accounts_path, "w") as f:
                json.dump(accounts, f, indent=4)

            self.new_name.delete(0, "end")
            self.new_email.delete(0, "end")
            self.new_target_pts.delete(0, "end")
            self.force_refresh()
            self.select_tab("monitor")
            messagebox.showinfo("Profile Registered", f"Profile '{name}' successfully provisioned with Goal: {custom_target:,} Pts![cite: 6]")
        except Exception as e:
            messagebox.showerror("Provisioning Error", f"Could not register account: {e}")

    def delete_account(self, name):
        if messagebox.askyesno(
            "Authorize Wipe",
            f"Permanently wipe profile: '{name}'?\n\nThis will purge all Chromium session tokens, cookies, and local database records.[cite: 6]"
        ):
            try:
                if os.path.exists(self.accounts_path):
                    with open(self.accounts_path, "r") as f:
                        accounts = json.load(f)
                    updated = [acc for acc in accounts if acc["name"] != name]
                    with open(self.accounts_path, "w") as f:
                        json.dump(updated, f, indent=4)

                clean_name = name.replace(" ", "_")
                profile_dir = os.path.join(self.session_path, clean_name)

                if os.path.exists(profile_dir):
                    try:
                        shutil.rmtree(profile_dir, ignore_errors=True)
                    except Exception as err:
                        print(f"⚠️ Failed to remove session vault: {err}")

                self.force_refresh()
            except Exception as e:
                print(f"Wipe Error: {e}")

    def force_refresh(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.sus_scroll_frame.winfo_children():
            widget.destroy()
        self.account_cards = {}
        self.suspended_cards = {}
        self._cached_history_data = {}
        self._last_history_mtime = 0
        self.refresh_logic()

    def async_disk_calc_loop(self):
        def scan():
            total = 0
            if os.path.exists(self.session_path):
                try:
                    for dirpath, dirnames, filenames in os.walk(self.session_path):
                        dirpath_lower = dirpath.lower()
                        if any(skip in dirpath_lower for skip in ['cache', 'code cache', 'gpucache', 'blob_storage', 'service worker']):
                            continue
                        for f in filenames:
                            if f in ['Cookies', 'Preferences', 'Login Data', 'Local Storage', 'Bookmarks']:
                                try:
                                    total += os.path.getsize(os.path.join(dirpath, f))
                                except Exception:
                                    pass
                except Exception:
                    pass
            try:
                self._update_disk_size(total)
            except Exception:
                pass
        
        threading.Thread(target=scan, daemon=True).start()
    
    def _update_disk_size(self, total):
        self.cached_dir_size = f"{total / (1024 * 1024):.1f} MB"
        self.after(30000, self.async_disk_calc_loop)

    def async_ping_calc_loop(self):
        def ping():
            while True:
                try:
                    t0 = time.time()
                    requests.get("https://www.bing.com", timeout=3)
                    latency = int((time.time() - t0) * 1000)
                    self.cached_ping = f"{latency} ms 🟢" if latency < 150 else f"{latency} ms 🟡"
                except Exception:
                    self.cached_ping = "Timeout 🔴"
                time.sleep(10)

        threading.Thread(target=ping, daemon=True).start()

    def pulse_animation_loop(self):
        self.pulse_state = not self.pulse_state
        if self.is_running:
            for name, ui in self.account_cards.items():
                if ui.get("status_text") in ["ACTIVE", "RUNNING"]:
                    border_c = "#00f0ff" if self.pulse_state else ("#cbd9e8", "#1e2238")
                    ui["card"].configure(border_color=border_c)
        self.after(800, self.pulse_animation_loop)

    def update_loop(self):
        self.refresh_logic()

        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_hm = now.strftime("%H:%M")

        # 🟢 AUTO-SCHEDULER TRIGGER CHECK[cite: 6]
        if self.auto_sched_var.get() and current_hm == self.scheduler_time:
            if self.last_scheduled_date != today_str and not self.is_running:
                self.last_scheduled_date = today_str
                print(f"\n⏰ [AUTO-SCHEDULER] Triggering scheduled batch run at {current_hm} ({today_str})...")
                self.safe_launch_sequence()

        try:
            current = psutil.net_io_counters()
            today = now.date()
            if today != self.data_date:
                self.net_baseline = current
                self.data_date = today

            sent_mb = (current.bytes_sent - self.net_baseline.bytes_sent) / (1024 * 1024)
            recv_mb = (current.bytes_recv - self.net_baseline.bytes_recv) / (1024 * 1024)
            total_mb = sent_mb + recv_mb

            if total_mb > 1024:
                self.data_total_lbl.configure(text=f"📦 Total: {total_mb/1024:.2f} GB")
                self.data_download_lbl.configure(text=f"⬇️ Download: {recv_mb/1024:.2f} GB")
                self.data_upload_lbl.configure(text=f"⬆️ Upload: {sent_mb/1024:.2f} GB")
            else:
                self.data_total_lbl.configure(text=f"📦 Total: {total_mb:.1f} MB")
                self.data_download_lbl.configure(text=f"⬇️ Download: {recv_mb:.1f} MB")
                self.data_upload_lbl.configure(text=f"⬆️ Upload: {sent_mb:.1f} MB")
        except Exception:
            pass

        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        self.cpu_lbl.configure(text=f"CPU Core Load: {cpu_usage}%")
        self.ram_lbl.configure(text=f"RAM Telemetry: {ram_usage}%")
        self.ram_bar.set(ram_usage / 100.0)

        if ram_usage >= 90:
            self.ram_lbl.configure(text_color="#ef4444")
            self.ram_bar.configure(progress_color="#ef4444")
        elif ram_usage >= 75:
            self.ram_lbl.configure(text_color="#f59e0b")
            self.ram_bar.configure(progress_color="#f59e0b")
        else:
            self.ram_lbl.configure(text_color="#10b981")
            self.ram_bar.configure(progress_color="#10b981")

        self.ping_lbl.configure(text=f"Network Ping: {self.cached_ping}")
        self.storage_lbl.configure(text=f"Disk Vault: {self.cached_dir_size}")

        # 🟢 SMART COUNTDOWN TIMER[cite: 6]
        if self.auto_sched_var.get():
            try:
                sched_h, sched_m = map(int, self.scheduler_time.split(":"))
                target_dt = now.replace(hour=sched_h, minute=sched_m, second=0, microsecond=0)
                if target_dt <= now:
                    target_dt += datetime.timedelta(days=1)
                delta = target_dt - now
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                self.card_countdown.configure(text=f"⏰ {hours:02d}h {minutes:02d}m")
            except Exception:
                tomorrow = now.date() + datetime.timedelta(days=1)
                midnight = datetime.datetime.combine(tomorrow, datetime.time.min)
                delta = midnight - now
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                self.card_countdown.configure(text=f"{hours:02d}h {minutes:02d}m")
        else:
            tomorrow = now.date() + datetime.timedelta(days=1)
            midnight = datetime.datetime.combine(tomorrow, datetime.time.min)
            delta = midnight - now
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            self.card_countdown.configure(text=f"{hours:02d}h {minutes:02d}m")

        self.after(2000, self.update_loop)

    def refresh_logic(self):
        try:
            if not os.path.exists(self.accounts_path):
                return
            with open(self.accounts_path, "r", encoding="utf-8") as f:
                accounts = json.load(f)

            if os.path.exists(self.history_path):
                current_mtime = os.path.getmtime(self.history_path)
                if current_mtime != self._last_history_mtime:
                    try:
                        with open(self.history_path, "r", encoding="utf-8") as f:
                            self._cached_history_data = json.load(f)
                        self._last_history_mtime = current_mtime
                    except Exception:
                        pass
            history = self._cached_history_data

            today = time.strftime("%Y-%m-%d")
            today_data = history.get(today, {})

            tot_pts_today = 0
            tot_vault = 0
            tot_completed = 0
            active_count = 0
            suspended_count = 0

            for acc in accounts:
                name = acc["name"]
                email = acc.get("email", "N/A")
                custom_target = acc.get("target", self.target_points)
                clean_name = name.replace(" ", "_")
                data = today_data.get(clean_name, {"searches": 0, "total_points": 0, "total_balance": 0, "streak": 0, "level": 2})
                is_suspended = (data.get("status") == "SUSPENDED")

                if is_suspended:
                    suspended_count += 1
                    if name in self.account_cards:
                        self.account_cards[name]["card"].destroy()
                        del self.account_cards[name]
                    if name not in self.suspended_cards:
                        self.create_suspended_card(name, email, data)
                else:
                    active_count += 1
                    if name in self.suspended_cards:
                        self.suspended_cards[name]["card"].destroy()
                        del self.suspended_cards[name]

                    tot_pts_today += data.get("total_points", 0)
                    tot_vault += data.get("total_balance", 0)
                    
                    done = data.get("searches", 0)
                    cur_bal = data.get("total_balance", 0)
                    target = int(custom_target) if (custom_target and int(custom_target) > 0) else getattr(self, "target_points", 8150)
                    if target <= 0:
                        target = 8150

                    is_complete = (done >= self.daily_goal and self.daily_goal > 0)
                    is_claim_ready = (cur_bal >= target)
                    is_running_now = (name in self.active_running_profiles)

                    if is_complete:
                        tot_completed += 1

                    # 🔍 Real-Time Filter & Search Matching[cite: 6]
                    matches_search = True
                    if self.search_filter_text:
                        q = self.search_filter_text
                        matches_search = (q in name.lower()) or (q in email.lower())

                    matches_category = True
                    cat = self.active_category_filter
                    if cat in ["🎁 Ready", "Ready"]:
                        matches_category = is_claim_ready
                    elif cat in ["⏳ Incomplete", "Incomplete"]:
                        matches_category = not is_complete
                    elif cat in ["✅ Done", "Done"]:
                        matches_category = is_complete
                    elif cat in ["▶️ Running", "Running"]:
                        matches_category = is_running_now

                    if matches_search and matches_category:
                        if name not in self.account_cards:
                            self.create_card(name, email, data, custom_target)
                        else:
                            self.update_card_ui(name, data, custom_target)
                    else:
                        if name in self.account_cards:
                            self.account_cards[name]["card"].destroy()
                            del self.account_cards[name]

            # 🟢 LEVEL 4: 7-DAY SPARKLINE COMPUTE & DRAW[cite: 6]
            try:
                seven_days_pts = []
                now_dt = datetime.datetime.now().date()
                for i in range(6, -1, -1):
                    d_str = (now_dt - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                    day_hist = history.get(d_str, {})
                    day_tot = sum(d.get("total_points", 0) for d in day_hist.values() if isinstance(d, dict))
                    seven_days_pts.append(day_tot)

                avg_7d = sum(seven_days_pts) // 7
                self.spark_avg_lbl.configure(text=f"Avg: +{avg_7d:,} Pts/d")
                self.sparkline_canvas.draw_sparkline(seven_days_pts)
            except Exception:
                pass

            self.btn_tab_suspended.configure(text=f"⛔  Suspended Nodes ({suspended_count})")
            self.card_pts_today.configure(text=f"+{tot_pts_today:,} Pts")
            self.card_total_vault.configure(text=f"{tot_vault:,} Pts")
            self.card_active_profiles.configure(text=f"{active_count} Ready")
            self.card_completed_searches.configure(text=f"{tot_completed} / {active_count} Done")

        except Exception as e:
            print(f"UI Refresh Error: {e}")

    # ==========================================
    # 🎴 3D HOLO / CYBER DUAL-LAYER CARD (ACTIVE)
    # ==========================================
    def create_card(self, name, email, data, target_pts):
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=("#f8fafc", "#10121d"),
            corner_radius=12,
            border_width=2,
            border_color=("#cbd9e8", "#1a1e30")
        )
        card.pack(fill="x", pady=5, padx=6)

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=0)
        card.grid_columnconfigure(2, weight=1)
        card.grid_columnconfigure(3, weight=0)
        card.grid_columnconfigure(4, weight=0)

        # 1. Status Pill[cite: 6]
        badge_frame = ctk.CTkFrame(
            card,
            fg_color=("#e2ecf7", "#161928"),
            corner_radius=18,
            border_width=1,
            border_color=("#c1d4e8", "#24293f"),
            width=80,
            height=28
        )
        badge_frame.grid(row=0, column=0, padx=(12, 6), pady=12)
        badge_frame.pack_propagate(False)

        status_pill = ctk.CTkLabel(
            badge_frame,
            text="READY",
            font=("Segoe UI", 10, "bold"),
            text_color=("#334155", "#94a3b8")
        )
        status_pill.pack(expand=True)

        # 2. Profile Info (With Level & Streak Badges)[cite: 6]
        info = ctk.CTkFrame(card, fg_color="transparent", width=220, height=48)
        info.grid(row=0, column=1, padx=(6, 12), pady=10, sticky="w")
        info.pack_propagate(False)

        name_row = ctk.CTkFrame(info, fg_color="transparent")
        name_row.pack(fill="x", anchor="w")

        ctk.CTkLabel(
            name_row, 
            text=name, 
            font=("Segoe UI", 13, "bold"), 
            text_color=("#0f172a", "#f8fafc")
        ).pack(side="left")

        lvl_val = data.get("level", 2)
        stk_val = data.get("streak", 0)

        lvl_badge = ctk.CTkLabel(
            name_row,
            text=f"⚡ L{lvl_val}",
            font=("Segoe UI", 8, "bold"),
            text_color=("#0284c7", "#00f0ff"),
            fg_color=("#e0f2fe", "#083344"),
            corner_radius=4,
            padx=4, pady=0
        )
        lvl_badge.pack(side="left", padx=(5, 2))

        stk_badge = ctk.CTkLabel(
            name_row,
            text=f"🔥 {stk_val}d",
            font=("Segoe UI", 8, "bold"),
            text_color="#f59e0b",
            fg_color=("#fef3c7", "#2e1a05"),
            corner_radius=4,
            padx=4, pady=0
        )
        stk_badge.pack(side="left", padx=(1, 0))

        ctk.CTkLabel(
            info, 
            text=email, 
            font=("Segoe UI", 10), 
            text_color=("#475569", "#64748b"), 
            wraplength=215, 
            justify="left"
        ).pack(anchor="w", pady=(1, 0))

        # 3. Dual Cyber Gauges[cite: 6]
        gauges_frame = ctk.CTkFrame(card, fg_color="transparent")
        gauges_frame.grid(row=0, column=2, padx=(4, 15), pady=8, sticky="ew")

        # --- Gauge 1: Search Queries ---[cite: 6]
        q_row = ctk.CTkFrame(gauges_frame, fg_color="transparent")
        q_row.pack(fill="x", pady=(0, 2))
        
        done = data.get("searches", 0)
        stat_lbl = ctk.CTkLabel(
            q_row,
            text=f"🔍 Queries: {done}/{self.daily_goal}",
            font=("Segoe UI", 10, "bold"),
            text_color=("#0284c7", "#00f0ff")
        )
        stat_lbl.pack(side="left")

        pb_queries = ctk.CTkProgressBar(
            gauges_frame,
            height=6,
            fg_color=("#d6e3f0", "#090a10"),
            progress_color=("#0284c7", "#00f0ff"),
            corner_radius=3
        )
        pb_queries.pack(fill="x", pady=(0, 6))
        pb_val = min(done / self.daily_goal, 1.0) if self.daily_goal > 0 else 0
        pb_queries.set(pb_val)

        # --- Gauge 2: Target Milestone ---[cite: 6]
        cur_bal = data.get("total_balance", 0)
        try:
            target = int(target_pts) if (target_pts and int(target_pts) > 0) else getattr(self, "target_points", 8150)
        except Exception:
            target = getattr(self, "target_points", 8150)
        if target <= 0:
            target = 8150

        pct = min(100.0, (cur_bal / target * 100))

        g_row = ctk.CTkFrame(gauges_frame, fg_color="transparent")
        g_row.pack(fill="x", pady=(0, 2))

        goal_title_lbl = ctk.CTkLabel(
            g_row,
            text=f"🎯 Target: {cur_bal:,} / {target:,} Pts ({pct:.0f}%)" if pct < 100 else f"🎁 MILESTONE REACHED ({cur_bal:,} Pts)",
            font=("Segoe UI", 10, "bold"),
            text_color=("#7c3aed", "#a78bfa") if pct < 100 else "#10b981"
        )
        goal_title_lbl.pack(side="left")

        edit_btn = ctk.CTkButton(
            g_row,
            text="✏️ Edit",
            width=42,
            height=16,
            fg_color=("#e2ecf7", "#181b2a"),
            hover_color=("#cbd9e8", "#252b42"),
            font=("Segoe UI", 8, "bold"),
            text_color=("#0284c7", "#38bdf8"),
            command=lambda n=name: self.edit_profile_target_dialog(n)
        )
        edit_btn.pack(side="right")

        pb_goal = ctk.CTkProgressBar(
            gauges_frame,
            height=6,
            fg_color=("#d6e3f0", "#090a10"),
            progress_color=("#8b5cf6", "#a855f7") if pct < 100 else "#10b981",
            corner_radius=3
        )
        pb_goal.pack(fill="x")
        pb_goal.set(min(pct / 100.0, 1.0))

        # 4. Points Vault Pod[cite: 6]
        pts = ctk.CTkFrame(
            card,
            fg_color=("#eaf2fa", "#0c0e18"),
            corner_radius=10,
            border_width=1,
            border_color=("#bfd3e6", "#20253d"),
            width=130,
            height=50
        )
        pts.grid(row=0, column=3, padx=(6, 10), pady=12)
        pts.pack_propagate(False)

        day = ctk.CTkLabel(
            pts, 
            text=f"+{data.get('total_points', 0)} Today", 
            font=("Segoe UI", 9, "bold"), 
            text_color="#10b981"
        )
        day.pack(pady=(4, 0))

        wal = ctk.CTkLabel(
            pts, 
            text=f"💎 {cur_bal:,} Pts", 
            font=("Segoe UI", 12, "bold"), 
            text_color=("#0284c7", "#00f0ff")
        )
        wal.pack(pady=(0, 4))

        # 5. Action Controls (WITH DYNAMIC RUN/PAUSE/RESET)[cite: 6]
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=(4, 14))

        run_single_btn = ctk.CTkButton(
            btn_frame,
            text="▶️",
            width=34,
            height=32,
            fg_color=("#059669", "#064e3b"),
            hover_color=("#10b981", "#047857"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            command=lambda n=name: self.run_single_profile_threaded(n)
        )
        run_single_btn.pack(side="left", padx=2)

        reset_single_btn = ctk.CTkButton(
            btn_frame,
            text="🔁",
            width=34,
            height=32,
            fg_color=("#6366f1", "#312e81"),
            hover_color=("#4f46e5", "#3730a3"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            command=lambda n=name: self.reset_single_profile_searches(n)
        )
        reset_single_btn.pack(side="left", padx=2)

        view_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Open",
            width=65,
            height=32,
            fg_color=("#0284c7", "#1e293b"),
            hover_color=("#0369a1", "#334155"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            command=lambda n=name: self.open_account_browser(n)
        )
        view_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=34,
            height=32,
            fg_color=("#ef4444", "#450a0a"),
            hover_color=("#dc2626", "#7f1d1d"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 11),
            command=lambda n=name: self.delete_account(n)
        )
        del_btn.pack(side="left", padx=2)

        # 🟢 Bind MouseWheel to card and all its child widgets for seamless scrolling
        def _card_scroll(e):
            try:
                canvas = self.scroll_frame._parent_canvas
                if platform.system() == "Windows":
                    canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
                else:
                    canvas.yview_scroll(int(-1 * e.delta), "units")
            except Exception:
                pass

        def _bind_all_children(widget):
            widget.bind("<MouseWheel>", _card_scroll, add="+")
            for child in widget.winfo_children():
                _bind_all_children(child)

        _bind_all_children(card)

        self.account_cards[name] = {
            "card": card,
            "pb_queries": pb_queries,
            "pb_goal": pb_goal,
            "day": day,
            "wal": wal,
            "goal_lbl": goal_title_lbl,
            "pill": status_pill,
            "badge_frame": badge_frame,
            "stat": stat_lbl,
            "run_btn": run_single_btn,
            "lvl_badge": lvl_badge,
            "stk_badge": stk_badge,
            "status_text": "READY"
        }

    def update_card_ui(self, name, data, target_pts):
        ui = self.account_cards[name]
        done = data.get("searches", 0)

        # Queries Update[cite: 6]
        pb_val = min(done / self.daily_goal, 1.0) if self.daily_goal > 0 else 0
        ui["pb_queries"].set(pb_val)
        ui["stat"].configure(text=f"🔍 Queries: {done}/{self.daily_goal}")

        # Target Milestone Update[cite: 6]
        cur_bal = data.get('total_balance', 0)
        try:
            target = int(target_pts) if (target_pts and int(target_pts) > 0) else getattr(self, "target_points", 8150)
        except Exception:
            target = getattr(self, "target_points", 8150)
        if target <= 0:
            target = 8150

        pct = min(100.0, (cur_bal / target * 100))

        ui["day"].configure(text=f"+{data.get('total_points', 0)} Today")
        ui["wal"].configure(text=f"💎 {cur_bal:,} Pts")

        # Update Level & Streak Badges[cite: 6]
        if "lvl_badge" in ui:
            lvl_val = data.get("level", 2)
            ui["lvl_badge"].configure(text=f"⚡ L{lvl_val}")
        if "stk_badge" in ui:
            stk_val = data.get("streak", 0)
            ui["stk_badge"].configure(text=f"🔥 {stk_val}d")

        if "goal_lbl" in ui:
            if pct >= 100:
                ui["goal_lbl"].configure(
                    text=f"🎁 MILESTONE REACHED ({cur_bal:,} Pts)",
                    text_color="#10b981"
                )
                ui["pb_goal"].configure(progress_color="#10b981")
            else:
                ui["goal_lbl"].configure(
                    text=f"🎯 Target: {cur_bal:,} / {target:,} Pts ({pct:.0f}%)",
                    text_color=("#7c3aed", "#a78bfa")
                )
                ui["pb_goal"].configure(progress_color=("#8b5cf6", "#a855f7"))

            ui["pb_goal"].set(min(pct / 100.0, 1.0))

        # Dynamic Status & Action Button Toggle (▶️ Run vs ⏸️ Pause)[cite: 6]
        if name in self.active_running_profiles:
            ui["status_text"] = "RUNNING"
            ui["pill"].configure(text="RUNNING", text_color=("#0284c7", "#00f0ff"))
            ui["badge_frame"].configure(fg_color=("#e0f2fe", "#083344"), border_color=("#7dd3fc", "#0e7490"))
            ui["pb_queries"].configure(progress_color=("#0284c7", "#00f0ff"))
            ui["card"].configure(border_color=("#00f0ff", "#0284c7"))
            
            ui["run_btn"].configure(
                text="⏸️",
                fg_color=("#d97706", "#78350f"),
                hover_color=("#b45309", "#92400e"),
                command=lambda n=name: self.stop_single_profile(n)
            )
        else:
            ui["run_btn"].configure(
                text="▶️",
                fg_color=("#059669", "#064e3b"),
                hover_color=("#10b981", "#047857"),
                command=lambda n=name: self.run_single_profile_threaded(n)
            )

            if done >= self.daily_goal and self.daily_goal > 0:
                ui["status_text"] = "COMPLETE"
                ui["pill"].configure(text="COMPLETE", text_color="#10b981")
                ui["badge_frame"].configure(fg_color=("#d1fae5", "#064e3b"), border_color=("#6ee7b7", "#059669"))
                ui["pb_queries"].configure(progress_color="#10b981")
                ui["card"].configure(border_color=("#10b981", "#064e3b"))
            elif done > 0:
                ui["status_text"] = "ACTIVE"
                ui["pill"].configure(text="ACTIVE", text_color=("#0284c7", "#00f0ff"))
                ui["badge_frame"].configure(fg_color=("#e0f2fe", "#083344"), border_color=("#7dd3fc", "#0e7490"))
                ui["pb_queries"].configure(progress_color=("#0284c7", "#00f0ff"))
            else:
                ui["status_text"] = "READY"
                ui["pill"].configure(text="READY", text_color=("#334155", "#94a3b8"))
                ui["badge_frame"].configure(fg_color=("#e2ecf7", "#161928"), border_color=("#c1d4e8", "#24293f"))
                ui["pb_queries"].configure(progress_color=("#0284c7", "#00f0ff"))
                ui["card"].configure(border_color=("#cbd9e8", "#1a1e30"))

    # ==========================================
    # ⛔ SUSPENDED ACCOUNT CARD
    # ==========================================
    def create_suspended_card(self, name, email, data):
        card = ctk.CTkFrame(
            self.sus_scroll_frame,
            fg_color=("#fff1f2", "#1f0d12"),
            corner_radius=12,
            border_width=2,
            border_color=("#fecdd3", "#5c1320")
        )
        card.pack(fill="x", pady=5, padx=6)

        card.grid_columnconfigure(1, minsize=240)
        card.grid_columnconfigure(2, weight=1)

        badge_frame = ctk.CTkFrame(
            card,
            fg_color=("#fee2e2", "#450a0a"),
            corner_radius=20,
            border_width=1,
            border_color=("#fca5a5", "#7f1d1d"),
            width=96,
            height=28
        )
        badge_frame.grid(row=0, column=0, padx=(14, 8), pady=12)
        badge_frame.pack_propagate(False)

        status_pill = ctk.CTkLabel(
            badge_frame,
            text="SUSPENDED",
            font=("Segoe UI", 9, "bold"),
            text_color="#ef4444"
        )
        status_pill.pack(expand=True)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, padx=10, pady=12, sticky="w")
        ctk.CTkLabel(info, text=name, font=("Segoe UI", 14, "bold"), text_color=("#991b1b", "#fca5a5")).pack(anchor="w")
        ctk.CTkLabel(info, text=email, font=("Segoe UI", 11), text_color=("#64748b", "#94a3b8"), wraplength=220, justify="left").pack(anchor="w")

        warn_frame = ctk.CTkFrame(card, fg_color="transparent")
        warn_frame.grid(row=0, column=2, padx=15, pady=12, sticky="w")
        ctk.CTkLabel(
            warn_frame,
            text="⚠️ Quarantined: Rewards Account Suspended by Microsoft",
            font=("Segoe UI", 11, "bold"),
            text_color="#ef4444"
        ).pack(anchor="w")
        ctk.CTkLabel(
            warn_frame,
            text="Skipped automatically from batch executions.",
            font=("Segoe UI", 10),
            text_color=("#64748b", "#64748b")
        ).pack(anchor="w")

        pts = ctk.CTkFrame(
            card,
            fg_color=("#fde8e8", "#2a0d13"),
            corner_radius=8,
            border_width=1,
            border_color=("#fbd5d5", "#4c1d24"),
            width=145,
            height=54
        )
        pts.grid(row=0, column=3, padx=10)
        pts.pack_propagate(False)

        day = ctk.CTkLabel(pts, text="Locked", font=("Segoe UI", 10, "bold"), text_color="#ef4444")
        day.pack(pady=(2, 0))
        wal = ctk.CTkLabel(pts, text=f"Bal: {data.get('total_balance', 0):,}", font=("Segoe UI", 10, "bold"), text_color=("#64748b", "#94a3b8"))
        wal.pack()

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=(8, 14))

        recover_btn = ctk.CTkButton(
            btn_frame,
            text="♻️ Recover",
            width=75,
            height=32,
            fg_color=("#059669", "#064e3b"),
            hover_color=("#10b981", "#047857"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 10, "bold"),
            command=lambda n=name: self.recover_account(n)
        )
        recover_btn.pack(side="left", padx=2)

        view_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Open",
            width=65,
            height=32,
            fg_color=("#64748b", "#334155"),
            hover_color=("#475569", "#475569"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            command=lambda n=name: self.open_account_browser(n)
        )
        view_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Wipe",
            width=65,
            height=32,
            fg_color=("#dc2626", "#7f1d1d"),
            hover_color=("#b91c1c", "#991b1b"),
            text_color="#ffffff",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            command=lambda n=name: self.delete_account(n)
        )
        del_btn.pack(side="left", padx=2)

        def _card_scroll(e):
            try:
                canvas = self.sus_scroll_frame._parent_canvas
                if platform.system() == "Windows":
                    canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
                else:
                    canvas.yview_scroll(int(-1 * e.delta), "units")
            except Exception:
                pass

        def _bind_all_children(widget):
            widget.bind("<MouseWheel>", _card_scroll, add="+")
            for child in widget.winfo_children():
                _bind_all_children(child)

        _bind_all_children(card)

        self.suspended_cards[name] = {"card": card}

    def stop_bot(self, show_msg=True):
        self.is_batch_running = False
        self.active_running_profiles.clear()
        self.holo_3d.set_active(False)
        try:
            if chrome_isolate and hasattr(chrome_isolate, "stop_all_execution"):
                chrome_isolate.stop_all_execution()
        except Exception:
            pass

        if sys.platform == "win32":
            ps_cmd = (
                'powershell -Command "'
                "Get-CimInstance Win32_Process -Filter \\\"Name = 'chrome.exe'\\\" | "
                "Where-Object { $_.CommandLine -like '*chrome_sessions*' -or $_.CommandLine -like '*remote-debugging-port*' } | "
                "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }\""
            )
            try:
                subprocess.run(ps_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        try:
            subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        if show_msg:
            messagebox.showinfo("Stopped", "Bot engine disengaged safely. Personal sessions intact!")

    def on_closing(self):
        self.stop_bot(show_msg=False)
        self.destroy()


if __name__ == "__main__":
    app = SuperDashboard()
    app.mainloop()