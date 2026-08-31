import customtkinter as ctk
import json
import os
import time
import threading
import shutil
import psutil
import sys
import subprocess
import requests
import traceback
from tkinter import messagebox, Tk

# 🟢 Direct Import of Bot Module
try:
    import chrome_isolate
except Exception as e:
    chrome_isolate = None

# 🟢 CURRENT BOT VERSION
CURRENT_VERSION = "13.5"

# 🟢 CONFIG LINKS
LICENSE_URL = "https://api.npoint.io/a42f92a3f4e8ab158488"
UPDATE_JSON_URL = "https://api.npoint.io/6376be033bccb601a69f"

def get_hwid():
    """Windows PC ka Unique Motherboard/System Hardware ID nikaalta hai (Win 10/11 Compatible)."""
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

    import platform
    return platform.node()

def verify_hwid_license():
    user_hwid = get_hwid().strip()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
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
                        cmd = f'echo {user_hwid}| clip'
                        os.system(cmd)
                    except Exception:
                        pass
                
                messagebox.showerror(
                    "License Key Required",
                    f"Your Hardware ID (HWID) is not registered!\n\n"
                    f"Your HWID:\n{user_hwid}\n\n"
                    f"(HWID has been copied to your clipboard. Send it to Admin for access!)"
                )
                sys.exit(0)
        else:
            messagebox.showerror(
                "Server Error", 
                f"Could not verify license. Server returned status code: {response.status_code}\nURL: {LICENSE_URL}"
            )
            sys.exit(0)
            
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to connect to license server.\nPlease check your internet connection.\n\nDetails: {e}")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Security Error", f"License check error: {e}")
        sys.exit(0)

def auto_update_bot():
    """Server se check karke compiled .pyc files auto download aur replace karta hai."""
    try:
        fresh_url = f"{UPDATE_JSON_URL}?t={int(time.time())}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cache-Control': 'no-cache', 
            'Pragma': 'no-cache'
        }
        response = requests.get(fresh_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            remote_version = str(data.get("latest_version", CURRENT_VERSION)).strip()
            
            if remote_version != CURRENT_VERSION:
                files_to_update = data.get("update_files", {})
                updated_count = 0
                base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
                
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
                        f"Bot updated to v{remote_version} successfully!\nPlease restart the bot."
                    )
                    sys.exit(0)
    except Exception as e:
        print(f"Update Check Skipped/Failed: {e}")

# 🔒 Run Security and Auto-Update Checks Before Launching GUI
verify_hwid_license()
auto_update_bot()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SuperDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"MS Bot Ultra Dashboard v{CURRENT_VERSION}")
        self.geometry("1420x920")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Paths
        self.history_path = os.path.join("bot_data", "history.json")
        self.accounts_path = os.path.join("config", "accounts.json")
        self.settings_path = os.path.join("config", "settings.json")
        self.session_path = os.path.abspath("chrome_sessions")

        os.makedirs("config", exist_ok=True)
        os.makedirs("bot_data", exist_ok=True)

        self.account_cards = {}
        self.is_running = False
        self.daily_goal = 20
        self.cached_dir_size = "Calculating..."

        # Layout Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🤖 MS BOT ULTRA", font=("Arial", 22, "bold")).pack(pady=15)

        # Add Account Section
        self.add_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b")
        self.add_frame.pack(fill="x", padx=15, pady=5)
        self.new_name = ctk.CTkEntry(self.add_frame, placeholder_text="Profile Name")
        self.new_name.pack(pady=5, padx=10, fill="x")
        self.new_email = ctk.CTkEntry(self.add_frame, placeholder_text="Email Address")
        self.new_email.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.add_frame, text="Add Account", command=self.add_account_logic).pack(pady=8, padx=10, fill="x")

        # 🟢 Control 1: Daily Searches Dropdown Selector
        ctk.CTkLabel(self.sidebar, text="🔍 Daily Searches:", font=("Arial", 12, "bold")).pack(pady=(8, 0))
        self.search_goal_opt = ctk.CTkOptionMenu(
            self.sidebar, 
            values=["5", "10", "15", "20", "25", "30", "35", "40"], 
            command=self.save_settings
        )
        self.search_goal_opt.pack(pady=4, padx=20, fill="x")

        # Control 2: Batch Size
        ctk.CTkLabel(self.sidebar, text="⚡ Parallel Batch Size:", font=("Arial", 12)).pack(pady=(6, 0))
        self.batch_opt = ctk.CTkOptionMenu(self.sidebar, values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], command=self.save_settings)
        self.batch_opt.pack(pady=4, padx=20, fill="x")
        
        # --- 🟢 SWITCHES CONTAINER (Clean Left Alignment) ---
        self.switches_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.switches_frame.pack(fill="x", padx=25, pady=8)

        # Control 3: Headless Switch
        self.headless_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            self.switches_frame, 
            text="Headless Mode", 
            variable=self.headless_var, 
            command=self.save_settings
        ).pack(anchor="w", pady=4)

        # Control 4: Dashboard Tasks Switch (/dashboard cards)
        self.dashboard_tasks_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            self.switches_frame, 
            text="Daily Set (Cards)", 
            variable=self.dashboard_tasks_var, 
            command=self.save_settings
        ).pack(anchor="w", pady=4)

        # Control 5: Daily App Check-In Switch
        self.app_checkin_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            self.switches_frame, 
            text="App Daily Check-In", 
            variable=self.app_checkin_var, 
            command=self.save_settings
        ).pack(anchor="w", pady=4)

        # Control 6: App Promotions (Weather / Quests) Switch
        self.weather_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            self.switches_frame, 
            text="App Promotions (Weather)", 
            variable=self.weather_var, 
            command=self.save_settings
        ).pack(anchor="w", pady=4)

        # Control 7: Read To Earn News Switch
        self.read_earn_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            self.switches_frame, 
            text="Read to Earn (30 Pts)", 
            variable=self.read_earn_var, 
            command=self.save_settings
        ).pack(anchor="w", pady=4)

        self.ram_lbl = ctk.CTkLabel(self.sidebar, text="RAM Usage: 0%", font=("Arial", 13, "bold"), text_color="#2ecc71")
        self.ram_lbl.pack(pady=6)

        # 🚀 START BOT
        self.run_btn = ctk.CTkButton(self.sidebar, text="🚀 START BOT", fg_color="#2ecc71", font=("Arial", 14, "bold"), command=self.safe_launch_sequence)
        self.run_btn.pack(pady=6, padx=20, fill="x")

        self.stop_btn = ctk.CTkButton(self.sidebar, text="🛑 STOP ALL", fg_color="#e74c3c", command=self.stop_bot)
        self.stop_btn.pack(pady=4, padx=20, fill="x")

        self.storage_lbl = ctk.CTkLabel(self.sidebar, text="Disk Usage: 0 MB", font=("Arial", 11), text_color="gray")
        self.storage_lbl.pack(side="bottom", pady=10)

        self.initial_load()

        # --- MAIN VIEW ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Safety & Stability Monitor")
        self.scroll_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.bind_scroll_events()

        # Start Loops
        self.async_disk_calc_loop()
        self.update_loop()

    def bind_scroll_events(self):
        try:
            canvas = self.scroll_frame._parent_canvas
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        except Exception:
            pass

    def initial_load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f: 
                    cfg = json.load(f)
                    self.batch_opt.set(str(cfg.get("batch_size", 4)))
                    self.headless_var.set(cfg.get("headless", True))
                    self.dashboard_tasks_var.set(cfg.get("enable_dashboard_tasks", True))
                    self.app_checkin_var.set(cfg.get("enable_app_checkin", True))
                    self.weather_var.set(cfg.get("enable_weather_check", True))
                    self.read_earn_var.set(cfg.get("enable_read_to_earn", True))
                    self.daily_goal = int(cfg.get("daily_search_goal", 20))
                    self.search_goal_opt.set(str(self.daily_goal))
            except Exception: 
                self.daily_goal = 20
                self.search_goal_opt.set("20")

    def save_settings(self, *args):
        os.makedirs("config", exist_ok=True)
        try:
            self.daily_goal = int(self.search_goal_opt.get())
        except Exception:
            self.daily_goal = 20

        new_cfg = {
            "daily_search_goal": self.daily_goal, 
            "batch_size": int(self.batch_opt.get()), 
            "headless": self.headless_var.get(),
            "enable_dashboard_tasks": self.dashboard_tasks_var.get(),
            "enable_app_checkin": self.app_checkin_var.get(),
            "enable_weather_check": self.weather_var.get(),
            "enable_read_to_earn": self.read_earn_var.get()
        }
        with open(self.settings_path, 'w') as f: 
            json.dump(new_cfg, f, indent=4)
        
        self.refresh_logic()

    def safe_launch_sequence(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Bot is already running in background!")
            return

        current_ram = psutil.virtual_memory().percent
        if current_ram >= 95:
            messagebox.showerror("CRITICAL: High RAM", f"PC RAM is at {current_ram}%. Bot blocked!")
            return

        self.is_running = True
        threading.Thread(target=self.run_bot_thread, daemon=True).start()

    def run_bot_thread(self):
        try:
            if chrome_isolate and hasattr(chrome_isolate, "main"):
                chrome_isolate.main()
            else:
                messagebox.showerror("Error", "Could not import 'chrome_isolate' module!")
        except Exception:
            error_details = traceback.format_exc()
            messagebox.showerror("Bot Crash Error", f"Bot crashed with error:\n\n{error_details}")
        finally:
            self.is_running = False

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
                messagebox.showerror("Launch Error", f"Could not launch Chrome for {name}:\n{e}")

        threading.Thread(target=launch, daemon=True).start()

    def add_account_logic(self):
        name = self.new_name.get().strip()
        email = self.new_email.get().strip()
        if not name or not email:
            messagebox.showwarning("Error", "Name and Email are required!")
            return
        try:
            os.makedirs("config", exist_ok=True)

            if os.path.exists(self.accounts_path):
                with open(self.accounts_path, 'r') as f: 
                    accounts = json.load(f)
            else: 
                accounts = []

            if any(acc['name'] == name for acc in accounts):
                messagebox.showwarning("Error", "Profile name already exists!")
                return

            accounts.append({"name": name, "email": email})

            with open(self.accounts_path, 'w') as f: 
                json.dump(accounts, f, indent=4)

            self.new_name.delete(0, 'end')
            self.new_email.delete(0, 'end')
            self.force_refresh() 
        except Exception as e:
            messagebox.showerror("Error", f"Could not add account: {e}")

    def delete_account(self, name):
        if messagebox.askyesno("Confirm", f"Delete Profile: {name}?"):
            try:
                if os.path.exists(self.accounts_path):
                    with open(self.accounts_path, 'r') as f: 
                        accounts = json.load(f)
                    updated = [acc for acc in accounts if acc['name'] != name]
                    with open(self.accounts_path, 'w') as f: 
                        json.dump(updated, f, indent=4)
                    self.force_refresh()
            except Exception as e: 
                print(f"Delete Error: {e}")

    def force_refresh(self):
        for widget in self.scroll_frame.winfo_children(): 
            widget.destroy()
        self.account_cards = {}
        self.refresh_logic()

    def async_disk_calc_loop(self):
        def calc():
            total = 0
            if os.path.exists(self.session_path):
                try:
                    for dirpath, dirnames, filenames in os.walk(self.session_path):
                        for f in filenames: 
                            total += os.path.getsize(os.path.join(dirpath, f))
                except Exception: 
                    pass
            self.cached_dir_size = f"{total / (1024 * 1024):.1f} MB"
            self.after(30000, self.async_disk_calc_loop)

        threading.Thread(target=calc, daemon=True).start()

    def update_loop(self):
        self.refresh_logic()
        ram_usage = psutil.virtual_memory().percent
        self.ram_lbl.configure(text=f"RAM Usage: {ram_usage}%")
        if ram_usage >= 95: 
            self.ram_lbl.configure(text_color="#e74c3c")
        elif ram_usage >= 85: 
            self.ram_lbl.configure(text_color="#e67e22")
        else: 
            self.ram_lbl.configure(text_color="#2ecc71")
        
        self.storage_lbl.configure(text=f"Disk Usage: {self.cached_dir_size}")
        self.after(2000, self.update_loop)

    def refresh_logic(self):
        try:
            if not os.path.exists(self.accounts_path): 
                return
            with open(self.accounts_path, 'r') as f: 
                accounts = json.load(f)
            try:
                with open(self.history_path, 'r') as f: 
                    history = json.load(f)
            except Exception: 
                history = {}
            
            today = time.strftime("%Y-%m-%d")
            today_data = history.get(today, {}) 

            for acc in accounts:
                name = acc['name']
                email = acc.get('email', 'N/A')
                clean_name = name.replace(" ", "_")
                data = today_data.get(clean_name, {"searches": 0, "total_points": 0, "total_balance": 0})
                
                if name not in self.account_cards:
                    self.create_card(name, email, data)
                else:
                    self.update_card_ui(name, data)
        except Exception as e: 
            print(f"UI Refresh Error: {e}")

    def create_card(self, name, email, data):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
        card.pack(fill="x", pady=6, padx=5)
        card.grid_columnconfigure(1, minsize=230) 
        card.grid_columnconfigure(2, weight=1)

        dot = ctk.CTkLabel(card, text="●", font=("Arial", 22), text_color="gray")
        dot.grid(row=0, column=0, padx=10)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, padx=8, pady=8, sticky="w")
        ctk.CTkLabel(info, text=name, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=email, font=("Arial", 11), text_color="gray70", wraplength=210, justify="left").pack(anchor="w")

        prog_frame = ctk.CTkFrame(card, fg_color="transparent")
        prog_frame.grid(row=0, column=2, padx=12, pady=8, sticky="ew")
        done = data.get('searches', 0)
        
        stat_lbl = ctk.CTkLabel(prog_frame, text=f"Searches: {done}/{self.daily_goal}", font=("Arial", 12, "bold"), text_color="#3498db")
        stat_lbl.pack(anchor="w", pady=(0, 4))
        
        pb = ctk.CTkProgressBar(prog_frame, height=12)
        pb.pack(fill="x")
        pb_val = min(done / self.daily_goal, 1.0) if self.daily_goal > 0 else 0
        pb.set(pb_val)

        pts = ctk.CTkFrame(card, fg_color="#1a1a1a", corner_radius=8, width=130, height=55)
        pts.grid(row=0, column=3, padx=10)
        pts.pack_propagate(False)
        day = ctk.CTkLabel(pts, text=f"+{data.get('total_points', 0)} Today", font=("Arial", 11, "bold"), text_color="#2ecc71")
        day.pack(pady=(6, 0))
        wal = ctk.CTkLabel(pts, text=f"Bal: {data.get('total_balance', 0)}", font=("Arial", 11, "bold"))
        wal.pack()

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=10)

        view_btn = ctk.CTkButton(
            btn_frame, 
            text="👁️ View", 
            width=65, 
            height=32, 
            fg_color="#2980b9", 
            hover_color="#3498db", 
            font=("Arial", 11, "bold"),
            command=lambda n=name: self.open_account_browser(n)
        )
        view_btn.pack(side="left", padx=4)

        del_btn = ctk.CTkButton(
            btn_frame, 
            text="🗑️", 
            width=32, 
            height=32, 
            fg_color="#c0392b", 
            hover_color="#e74c3c", 
            command=lambda n=name: self.delete_account(n)
        )
        del_btn.pack(side="left", padx=4)

        self.account_cards[name] = {"pb": pb, "day": day, "wal": wal, "dot": dot, "stat": stat_lbl}

    def update_card_ui(self, name, data):
        ui = self.account_cards[name]
        done = data.get('searches', 0)
        
        pb_val = min(done / self.daily_goal, 1.0) if self.daily_goal > 0 else 0
        ui["pb"].set(pb_val)
        ui["stat"].configure(text=f"Searches: {done}/{self.daily_goal}") 
        
        ui["day"].configure(text=f"+{data.get('total_points', 0)} Today")
        ui["wal"].configure(text=f"Bal: {data.get('total_balance', 0)}")
        
        if done >= self.daily_goal: 
            ui["dot"].configure(text_color="#2ecc71")
        elif done > 0: 
            ui["dot"].configure(text_color="#3498db")
        else: 
            ui["dot"].configure(text_color="gray")

    def stop_bot(self, show_msg=True):
        self.is_running = False

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
                'ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"'
            )
            try:
                subprocess.run(ps_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        try:
            subprocess.run('taskkill /F /IM chromedriver.exe /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
            
        if show_msg:
            messagebox.showinfo("Stopped", "Bot fully stopped. Personal Chrome remained untouched!")

    def on_closing(self):
        self.stop_bot(show_msg=False)
        self.destroy()

if __name__ == "__main__":
    app = SuperDashboard()
    app.mainloop()