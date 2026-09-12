import time
import re
from selenium.webdriver.common.by import By

class DashboardSet:
    def __init__(self, logger=None):
        self.logger = logger

    def _log(self, message):
        if self.logger: 
            self.logger(message)
        else: 
            print(message)

    def perform_dashboard_tasks(self, driver):
        """rewards.bing.com/dashboard page par sabhi activities ko deeply scan aur complete karta hai"""
        from src.history import HistoryManager
        h_mgr = HistoryManager()

        try:
            user_data = driver.capabilities['chrome']['userDataDir']
            profile_name = user_data.replace('\\', '/').split('/')[-1]
        except Exception: 
            profile_name = "Unknown"

        self._log(f"🛡️ Dashboard Tasks Scanner Active: {profile_name}")

        try:
            driver.get("https://rewards.bing.com/dashboard")
            time.sleep(3)

            # Lazy load elements trigger karne ke liye smooth scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)

            main_tab = driver.current_window_handle
            processed_urls = set()
            consecutive_misses = 0

            # 🟢 Extended 15 Passes Loop for complete grid coverage
            for pass_idx in range(15):
                candidate_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='rewards'], a.ds-card-sec, a[class*='card'], a[href*='bing.com'], mee-card a, div[role='button']")
                if not candidate_links:
                    candidate_links = driver.find_elements(By.TAG_NAME, "a")

                target = None
                pts = 0

                for link in candidate_links:
                    try:
                        inner_text = link.text.strip()
                        inner_html = link.get_attribute("innerHTML").lower()

                        # Completed check
                        if "checkmark" in inner_html or "completed" in inner_html or "mee-icon-checkmark" in inner_html:
                            continue

                        # Active points check (+5, +10, +15, +30 etc.)
                        pts_match = re.search(r'\+(\d+)', inner_text)
                        if pts_match:
                            pts = int(pts_match.group(1))
                            if pts in [50, 100, 200]:
                                continue
                            
                            href = link.get_attribute("href")
                            if not href or href in processed_urls or "javascript:" in href:
                                continue

                            target = link
                            processed_urls.add(href)
                            break
                    except Exception:
                        continue

                # Agar task mila toh click karo
                if target:
                    consecutive_misses = 0
                    try:
                        self._log(f"🖱️ Clicking Dashboard Task (+{pts} pts)")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                        time.sleep(0.4)
                        driver.execute_script("arguments[0].click();", target)

                        h_mgr.add_task_points(profile_name, pts)

                        # Tab handling
                        tab_opened = False
                        for _ in range(8):
                            if len(driver.window_handles) > 1:
                                tab_opened = True
                                break
                            time.sleep(0.3)

                        # 🟢 Wait 2.5s for Microsoft rewards telemetry registration
                        if tab_opened:
                            time.sleep(2.5)
                            for h in driver.window_handles:
                                if h != main_tab:
                                    driver.switch_to.window(h)
                                    driver.execute_script("window.scrollBy(0, 300);")
                                    time.sleep(1)
                                    driver.close()
                            driver.switch_to.window(main_tab)
                            time.sleep(1)
                        else:
                            time.sleep(1.5)

                    except Exception:
                        continue
                else:
                    consecutive_misses += 1
                    driver.execute_script("window.scrollBy(0, 450);")
                    time.sleep(0.5)
                    if consecutive_misses >= 4:
                        break

            driver.execute_script("window.scrollTo(0, 0);")
            return True

        except Exception as e:
            self._log(f"Error: {e}")
            return False