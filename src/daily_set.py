import time
import re
from selenium.webdriver.common.by import By

class DailySet:
    def __init__(self, logger=None):
        self.logger = logger

    def _log(self, message):
        if self.logger: 
            self.logger(message)

    def should_perform_daily_set(self):
        return True

    def perform_daily_set(self, driver, human=None):
        """
        Regular /earn daily tasks ko full scan aur complete karta hai.
        """
        from src.history import HistoryManager
        h_mgr = HistoryManager()

        try:
            user_data = driver.capabilities['chrome']['userDataDir']
            profile_name = user_data.replace('\\', '/').split('/')[-1]
        except Exception: 
            profile_name = "Unknown"

        self._log(f"🛡️ Daily Set Scanner Active: {profile_name}")

        try:
            main_tab = driver.current_window_handle
            processed_urls = set()
            consecutive_misses = 0

            # 🟢 Extended 20 Passes to click ALL tasks without leaving any behind
            for pass_idx in range(20):
                candidate_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='rewards'], a.ds-card-sec, a[class*='card'], a[href*='bing.com'], mee-card a, div[role='button']")
                if not candidate_links:
                    candidate_links = driver.find_elements(By.TAG_NAME, "a")

                target = None
                pts = 0

                for link in candidate_links:
                    try:
                        inner_text = link.text.strip()
                        inner_html = link.get_attribute("innerHTML").lower()

                        if "checkmark" in inner_html or "completed" in inner_html or "mee-icon-checkmark" in inner_html:
                            continue

                        # Scan for point triggers (+5, +10, +15 etc.)
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

                if target:
                    consecutive_misses = 0
                    try:
                        self._log(f"🖱️ Clicking Task (+{pts} pts)")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                        time.sleep(0.4)
                        driver.execute_script("arguments[0].click();", target)

                        h_mgr.add_task_points(profile_name, pts)

                        tab_opened = False
                        for _ in range(8):
                            if len(driver.window_handles) > 1:
                                tab_opened = True
                                break
                            time.sleep(0.3)

                        # 🟢 Full 2.5s - 3s telemetry handshake wait
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
                    time.sleep(0.4)
                    if consecutive_misses >= 4:
                        break

            driver.execute_script("window.scrollTo(0, 0);")
            return True

        except Exception as e:
            self._log(f"Error: {e}")
            return False

    def perform_app_exclusive_cards(self, driver, profile_name, h_mgr=None):
        """
        Store-App exclusive cards ko DOM ke andar unlock karta hai,
        rnoreward strip karke real click event dispatch karta hai,
        aur background telemetry execute hone tak wait karke points credit karwata hai.
        """
        try:
            main_tab = driver.current_window_handle

            # 1. Force Store App User-Agent & Client Platform Signature
            STORE_UA = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/152.0.0.0 Safari/537.36 Edg/152.0.0.0 MSRewards/Desktop/1.2.0"
            )
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": STORE_UA,
                "platform": "Windows"
            })

            # Dashboard refresh to unlock cards
            driver.get("https://rewards.bing.com/earn")
            time.sleep(4)

            # 2. Count uncompleted Store App promo tasks on dashboard (Strict Filter)
            pending_count = driver.execute_script("""
                let count = 0;
                let cards = document.querySelectorAll('span[role="link"], a, [class*="card"], div[role="button"]');
                cards.forEach(el => {
                    let href = el.getAttribute('href') || el.href || '';
                    let text = el.innerText || '';
                    let html = el.innerHTML.toLowerCase();
                    let isCompleted = html.includes('checkmark') || html.includes('completed') || text.includes('Completed');
                    
                    if ((href.includes('rnoreward=1') || text.includes('Rewards App only') || text.includes('Rewards App exclusive')) && !isCompleted) {
                        count++;
                    }
                });
                return count;
            """)

            if not pending_count or pending_count == 0:
                self._log("ℹ️ No pending App-exclusive promo cards found.")
                return

            self._log(f"🎁 Found {pending_count} pending Store App Exclusive Task(s)")

            # 3. Direct DOM Click Loop with Full Dynamic Telemetry Execution (Strict Filter)
            for idx in range(pending_count):
                try:
                    self._log(f"🔓 Auto-Clicking Store Card [{idx + 1}/{pending_count}]")

                    # Strip rnoreward parameter & dispatch direct synthetic click
                    clicked = driver.execute_script("""
                        let found = false;
                        let elements = Array.from(document.querySelectorAll('span[role="link"], a, [class*="card"], div[role="button"]'));
                        for (let el of elements) {
                            let href = el.getAttribute('href') || el.href || '';
                            let text = el.innerText || '';
                            let html = el.innerHTML.toLowerCase();
                            let isCompleted = html.includes('checkmark') || html.includes('completed') || text.includes('Completed');

                            if ((href.includes('rnoreward=1') || text.includes('Rewards App only') || text.includes('Rewards App exclusive')) && !isCompleted && !el.dataset.botDone) {
                                if (href) {
                                    let cleanHref = href.replace(/&?rnoreward=1/g, '');
                                    el.setAttribute('href', cleanHref);
                                    if (el.href) el.href = cleanHref;
                                }
                                el.removeAttribute('aria-disabled');
                                el.removeAttribute('data-disabled');
                                el.dataset.botDone = 'true';

                                el.scrollIntoView({block: 'center'});
                                el.click();
                                found = true;
                                break;
                            }
                        }
                        return found;
                    """)

                    if not clicked:
                        break

                    # Wait for tab open
                    tab_opened = False
                    for _ in range(8):
                        if len(driver.window_handles) > 1:
                            tab_opened = True
                            break
                        time.sleep(0.3)

                    # Dynamic JS Telemetry & Handshake Execution Wait
                    if tab_opened:
                        time.sleep(3.5)
                        for h in driver.window_handles:
                            if h != main_tab:
                                driver.switch_to.window(h)
                                driver.execute_script("window.scrollBy(0, 300);")
                                time.sleep(1)
                                driver.close()
                        driver.switch_to.window(main_tab)
                    else:
                        time.sleep(3)

                    if h_mgr:
                        h_mgr.add_task_points(profile_name, 10)

                    time.sleep(1)

                except Exception as ex:
                    self._log(f"⚠️ Store card click issue: {ex}")
                    if len(driver.window_handles) > 1:
                        for h in driver.window_handles:
                            if h != main_tab:
                                driver.switch_to.window(h)
                                driver.close()
                        driver.switch_to.window(main_tab)

            self._log("✅ All Store exclusive tasks auto-clicked successfully.")

        except Exception as e:
            self._log(f"⚠️ App exclusive handler bypassed: {e}")