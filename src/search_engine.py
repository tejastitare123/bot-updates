import json
import random
import time
import socket
import urllib.parse
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, 
    StaleElementReferenceException, 
    WebDriverException
)
from selenium.webdriver.common.by import By

from .utils import human_typing
from .human_behavior import HumanBehavior

# 🟢 Live News Fetcher Import
try:
    from .news_keywords import get_smart_queries
except ImportError:
    try:
        from news_keywords import get_smart_queries
    except ImportError:
        get_smart_queries = None

def is_online():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def wait_until_online(logger=None, account_name="Bot"):
    first = True
    while not is_online():
        if first:
            if logger:
                logger(f"🌐 [{account_name}] Internet disconnected (ERR_NAME_NOT_RESOLVED). Waiting for reconnect...")
            first = False
        time.sleep(3)
    if not first and logger:
        logger(f"✅ [{account_name}] Connection restored! Resuming...")

class SearchEngine:
    def __init__(self, logger=None, history=None):
        self._logger = logger
        self._history = history

    def _log(self, message):
        if self._logger:
            self._logger(message)

    def _add_to_history(self, query_text, status, account_name=None):
        if self._history:
            try:
                if account_name and status == "Success" and hasattr(self._history, 'update_progress'):
                    self._history.update_progress(account_name, 1)
                elif hasattr(self._history, 'add_to_history'):
                    self._history.add_to_history(query_text, status)
            except Exception as e:
                self._log(f"[WARNING] History tracking error: {e}")

    def load_queries_from_json(self, filepath, num_needed):
        """
        Pehle Multi-Source Live APIs se exact (num_needed + 1) queries fetch karta hai:
        1 Query Trigger ke liye + baaki num_needed actual searches ke liye.
        """
        total_fetch = num_needed + 1

        if get_smart_queries:
            try:
                live_queries = get_smart_queries(needed_count=total_fetch)
                if live_queries:
                    self._log(f"📰 Loaded {len(live_queries)} Live Trending Queries ({num_needed} Goal + 1 Free Trigger).")
                    return live_queries
            except Exception as e:
                self._log(f"[WARNING] Live API fetch error ({e}). Shifting to backup.")

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                all_queries = data.get("queries", [])
                if len(all_queries) < total_fetch:
                    self._log(f"[WARNING] Only {len(all_queries)} queries in local JSON.")
                    return all_queries
                self._log(f"📁 Loaded {total_fetch} queries from local JSON backup.")
                return random.sample(all_queries, total_fetch)
        except Exception:
            self._log(f"[ERROR] File {filepath} not found, generating dynamic fallback.")
            return [f"trending topic {random.randint(100, 999)}" for _ in range(total_fetch)]

    def perform_searches(self, driver, queries, account_name=None):
        human = HumanBehavior(driver, show_cursor=True)
        acc_str = account_name if account_name else "Bot"

        if not queries:
            self._log("[WARNING] No queries passed to perform_searches.")
            return

        # 🟢 Internet Guard before Trigger
        wait_until_online(self._log, acc_str)

        # 🚀 STEP 1: Extra Trigger Query Extraction (Zero Search Counting)
        query_list = list(queries)
        if len(query_list) > 1:
            trigger_kw = query_list.pop(0)  # Pehli query pop karo trigger ke liye
            target_queries = query_list     # Bachi hui exact goal queries
        else:
            trigger_kw = query_list[0]
            target_queries = query_list

        try:
            encoded_trigger = urllib.parse.quote(trigger_kw)
            dynamic_trigger_url = f"https://www.bing.com/search?PC=U316&FORM=SBIHMP&q={encoded_trigger}"

            self._log(f"⚡ Triggering Initial Search with Live Topic: '{trigger_kw}' (Uncounted)")
            driver.get(dynamic_trigger_url)
            time.sleep(1.2)

            try:
                human.scroll_page()
            except Exception:
                pass
            time.sleep(0.3)
        except Exception as e:
            err_msg = str(e).lower()
            if any(x in err_msg for x in ["invalid session id", "target window already closed", "no such window", "session deleted"]):
                self._log("[INFO] Process stopped by user during trigger URL.")
                return
            if "net::err" in err_msg or "name_not_resolved" in err_msg:
                wait_until_online(self._log, acc_str)
            else:
                self._log(f"[WARNING] Trigger URL initial load issue: {str(e)[:40]}")

        self._log(f"Starting {len(target_queries)} goal searches...")

        # 🚀 STEP 2: Loop Through Queries with Stale-Element Auto-Recovery
        for i, query in enumerate(target_queries):
            search_success = False

            # Micro-retry loop (Max 3 attempts per search to prevent 19/20 incomplete drops)
            for attempt in range(3):
                try:
                    wait_until_online(self._log, acc_str)

                    if "bing.com/search" not in driver.current_url:
                        driver.get("https://www.bing.com")
                        time.sleep(1.2)

                    # --- Locate Search Box Robustly ---
                    search_box = None
                    for selector in ["q", "sb_form_q"]:
                        try:
                            search_box = driver.find_element(By.NAME, selector)
                            if search_box:
                                break
                        except NoSuchElementException:
                            continue

                    if not search_box:
                        driver.get("https://www.bing.com")
                        time.sleep(1.2)
                        search_box = driver.find_element(By.NAME, "q")

                    # Clear existing text securely
                    driver.execute_script("arguments[0].value = '';", search_box)
                    search_box.send_keys(Keys.CONTROL + "a")
                    search_box.send_keys(Keys.DELETE)
                    time.sleep(0.1)

                    # 🛡️ Fresh Reference Fetch before typing to kill StaleElementReferenceException
                    search_box = driver.find_element(By.NAME, "q")

                    self._log(f"Search #{i + 1}/{len(target_queries)}: {query}")
                    human_typing(search_box, query)
                    search_box.send_keys(Keys.RETURN)

                    # --- ⏳ REWARDS DEBOUNCE GAP & COOLDOWN (5.5s - 7.5s for 100% points credit) ---
                    time.sleep(random.uniform(3, 4))

                    # --- Tab Switching (Quick Random Interaction) ---
                    tabs_config = [
                        {"name": "All", "priority": 75, "id": None},
                        {"name": "Images", "priority": 9, "id": "b-scopeListItem-images"},
                        {"name": "Videos", "priority": 8, "id": "b-scopeListItem-video"},
                        {"name": "News", "priority": 8, "id": "b-scopeListItem-news"},
                    ]
                    weights = [tab["priority"] for tab in tabs_config]
                    chosen_tab = random.choices(tabs_config, weights=weights, k=1)[0]

                    if chosen_tab["name"] != "All":
                        try:
                            xpath = f"//li[@id='{chosen_tab['id']}']//a"
                            tab_element = driver.find_element(By.XPATH, xpath)
                            human.click_element(tab_element)
                            time.sleep(random.uniform(1.2, 1.8))
                        except (NoSuchElementException, StaleElementReferenceException):
                            chosen_tab["name"] = "All"

                    # --- Fast Page Interaction ---
                    if chosen_tab["name"] == "All":
                        try:
                            human.scroll_page()
                        except Exception:
                            pass

                    time.sleep(random.uniform(0.4, 0.7))

                    self._add_to_history(query, "Success", account_name=account_name)
                    search_success = True
                    break  # Success, next query par jao

                except StaleElementReferenceException:
                    time.sleep(0.4)
                    continue  # Retry same query attempt
                except Exception as e:
                    err_msg = str(e).lower()
                    if any(x in err_msg for x in ["invalid session id", "target window already closed", "no such window", "session deleted"]):
                        self._log("[INFO] Process stopped by user. Exiting cleanly.")
                        return
                    if "net::err" in err_msg or "name_not_resolved" in err_msg:
                        wait_until_online(self._log, acc_str)
                    else:
                        time.sleep(0.8)

            if not search_success:
                self._log(f"[ERROR] Search failed permanently on attempt #{i+1}")
                self._add_to_history(query, "Failed", account_name=account_name)