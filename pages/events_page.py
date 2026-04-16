from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class EventsPage:
    BASE_URL = "https://www.greencity.cx.ua/#/greenCity/events"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(self.BASE_URL)
        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return self

    def prepare(self):
        self.close_popups_if_present()
        self.switch_language_to_en()
        return self

    def save_step_screenshot(self, name):
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        file_path = artifacts_dir / f"{name}.png"
        self.driver.save_screenshot(str(file_path))
        print(f"[DEBUG] Screenshot saved: {file_path}")

    def _find_first(self, locators):
        for by, value in locators:
            elements = self.driver.find_elements(by, value)
            if elements:
                return elements[0]
        return None

    def close_popups_if_present(self):
        popup_close_locators = [
            (By.XPATH, "//button[contains(., 'Accept')]"),
            (By.XPATH, "//button[contains(., 'Прийняти')]"),
            (By.XPATH, "//button[contains(@class, 'close')]"),
            (By.XPATH, "//button[contains(@aria-label, 'Close')]"),
        ]
        for by, value in popup_close_locators:
            elements = self.driver.find_elements(by, value)
            if elements:
                try:
                    elements[0].click()
                    print("[DEBUG] Closed popup/cookie dialog")
                except Exception:
                    pass

    def switch_language_to_en(self):
        # Use combined XPath to avoid N sequential misses with implicit wait.
        en_header_xpath = (
            "//span[normalize-space()='En']"
            " | //button[normalize-space()='En']"
            " | //*[contains(@class,'lang') or contains(@class,'language')][.//span[normalize-space()='En']]"
        )
        if self.driver.find_elements(By.XPATH, en_header_xpath):
            print("[DEBUG] Language already EN")
            return

        open_menu_xpath = (
            "//span[normalize-space()='Uk']"
            " | //button[.//span[normalize-space()='Uk']]"
            " | //a[.//span[normalize-space()='Uk']]"
            " | //*[contains(@class,'lang') or contains(@class,'language')][.//*[normalize-space()='Uk']]"
            " | //span[normalize-space()='Ua' or normalize-space()='UA']"
            " | //span[normalize-space()='Укр']"
        )
        try:
            open_menu = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, open_menu_xpath))
            )
        except TimeoutException:
            open_menu = None
        if open_menu is None:
            print("[DEBUG] Language switcher not found, skipping EN")
            return

        try:
            open_menu.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", open_menu)

        en_xpath = (
            "//mat-option[.//span[normalize-space()='En']]"
            " | //*[contains(@class,'cdk-overlay-pane')]//span[normalize-space()='En']"
            " | //*[contains(@class,'cdk-overlay-pane')]//button[normalize-space()='En']"
            " | //li[.//*[normalize-space()='En']]"
            " | //button[normalize-space()='En']"
            " | //a[normalize-space()='En']"
        )
        try:
            en_option = WebDriverWait(self.driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, en_xpath))
            )
        except TimeoutException:
            print("[DEBUG] EN option not found after opening language menu")
            return

        try:
            en_option.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", en_option)
        print("[DEBUG] Switched language to EN")

    def _open_filters_and_event_time(self):
        print("[DEBUG] Step: open Event time filter")
        for lang, xpath in (
            ("EN", "//*[normalize-space()='Event time']"),
            ("UA", "//*[normalize-space()='Час події']"),
        ):
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                try:
                    element.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", element)
                print(f"[DEBUG] Event time opened ({lang})")
                self.save_step_screenshot("step_01_event_time_clicked")
                return
            except TimeoutException:
                continue
        raise AssertionError("Event time dropdown was not found.")

    def _enable_past_filter(self):
        self._open_filters_and_event_time()
        print("[DEBUG] Step: select Past option")
        past_locator = (
            By.XPATH,
            "//mat-option[.//span[normalize-space()='Past'] or contains(@id,'Past') or contains(@id,'past')]"
            " | //mat-option[.//span[contains(.,'Минул')] or contains(@id,'past')]"
            " | //div[contains(@class,'cdk-overlay-pane')]//*[contains(@class,'mdc-list-item__primary-text') and normalize-space()='Past']"
            " | //div[contains(@class,'cdk-overlay-pane')]//*[contains(@class,'mdc-list-item__primary-text') and contains(.,'Минул')]"
            " | //div[contains(@class,'dropdown')]//span[normalize-space()='Past']"
            " | //span[contains(@class,'mdc-list-item__primary-text') and normalize-space()='Past']"
            " | //span[contains(@class,'mdc-list-item__primary-text') and contains(.,'Минул')]",
        )
        try:
            past_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(past_locator)
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", past_option
            )
            try:
                past_option.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", past_option)
            self.save_step_screenshot("step_02_past_selected")
        except TimeoutException:
            self.save_step_screenshot("step_02_past_not_found")
            raise AssertionError("Past filter option was not found.")

    def apply_past_filter_and_scroll(self):
        self.wait.until(lambda d: "events" in d.current_url.lower())
        self._enable_past_filter()
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")

    def get_counter_text(self):
        counter_xpath = (
            "//div[contains(@class,'active-filter-container')]//p"
            " | //*[contains(., 'Items found')]"
            " | //*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'items found')]"
            " | //*[contains(., 'знайдено')]"
        )
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, counter_xpath))
        )
        return (el.text or "").strip()

    def assert_past_chip_visible(self):
        chip_xpath = (
            "//*[contains(., 'Past') and contains(@class, 'filter')]"
            " | //*[contains(., 'Минул') and contains(@class, 'filter')]"
            " | //*[contains(., 'Past')]"
            " | //*[contains(., 'Минул')]"
        )
        chip = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, chip_xpath))
        )
        if chip is None:
            raise AssertionError("Past filter chip/text is not displayed.")

    def close_past_filter_chip(self):
        close_locators = [
            (By.CSS_SELECTOR, "div.active-filter-container img.cross-img"),
            (By.CSS_SELECTOR, "div.active-filter-container img[alt='cross']"),
            (
                By.XPATH,
                "//div[contains(@class,'active-filter-list')]//div[contains(@class,'chips')]"
                "//div[contains(@class,'cross-container')]//img[contains(@class,'cross-img') or @alt='cross']",
            ),
            (
                By.XPATH,
                "//div[contains(@class,'cross-container')]//img[@alt='cross' or contains(@class,'cross-img')]",
            ),
            (
                By.CSS_SELECTOR,
                "div.active-filter-container div.chips div.active-filter button",
            ),
            (
                By.XPATH,
                "//div[contains(@class,'active-filter-list')]//div[contains(@class,'chips')]"
                "//div[contains(@class,'active-filter')][contains(.,'Past') or contains(.,'Минул')]//button",
            ),
            (By.XPATH, "//mat-chip[.//*[contains(.,'Past')] or .//*[contains(.,'Минул')]]//button"),
        ]
        for by, value in close_locators:
            try:
                btn = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", btn
                )
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                return
            except TimeoutException:
                continue
        raise AssertionError("Close icon for Past filter chip was not found.")

    def assert_past_chip_removed(self):
        chip_past_xpath = (
            "//div[contains(@class,'active-filter-list')]//div[contains(@class,'chips')]"
            "//div[contains(@class,'active-filter')][contains(.,'Past') or contains(.,'Минул')]"
        )
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: len(d.find_elements(By.XPATH, chip_past_xpath)) == 0
            )
        except TimeoutException:
            raise AssertionError(
                "Past filter chip should be removed from active filters (still present after close)."
            )

    def click_events_view_mode(self, mode):
        if mode == "list":
            locators = [
                (By.CSS_SELECTOR, "div.change-view button.list"),
                (By.CSS_SELECTOR, "button[aria-label='list view']"),
                (
                    By.XPATH,
                    "//button[contains(@class,'list')][contains(@aria-label,'list view')]",
                ),
            ]
        else:
            locators = [
                (By.CSS_SELECTOR, "div.change-view button.gallery"),
                (By.CSS_SELECTOR, "button[aria-label='table view']"),
                (
                    By.XPATH,
                    "//button[contains(@class,'gallery')][contains(@aria-label,'table view')]",
                ),
            ]
        last_error = None
        for by, value in locators:
            try:
                btn = WebDriverWait(self.driver, 12).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", btn
                )
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                return
            except TimeoutException as error:
                last_error = error
                continue
        raise AssertionError(f"Could not find or click '{mode}' view button: {last_error!r}")

    def assert_list_layout_active(self):
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'change-view')]//button[contains(@class,'list')][@aria-pressed='true']"
                    " | //button[contains(@class,'list')][@aria-pressed='true']",
                )
            )
        )

    def assert_card_layout_active(self):
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'change-view')]//button[contains(@class,'gallery')][@aria-pressed='true']"
                    " | //button[contains(@class,'gallery')][@aria-pressed='true']",
                )
            )
        )

    def _events_search_input_locators(self):
        return [
            (By.CSS_SELECTOR, "div.create-container input.place-input"),
            (By.CSS_SELECTOR, "input.place-input"),
            (By.CSS_SELECTOR, "div.container-input input[type='text']"),
            (By.CSS_SELECTOR, "div.top-header input.place-input"),
            (
                By.XPATH,
                "//div[contains(@class,'container-input')]//input[@placeholder='Search' or @placeholder='Пошук']",
            ),
            (By.CSS_SELECTOR, "app-events-list input.place-input"),
            (By.CSS_SELECTOR, "app-events input.place-input"),
        ]

    def _expand_events_search_field(self):
        icon_locators = [
            (By.CSS_SELECTOR, "div.create-container div.container-img"),
            (By.CSS_SELECTOR, "div.top-header div.create-container div.container-img"),
            (
                By.XPATH,
                "//div[contains(@class,'top-header')]//div[contains(@class,'create-container')]//div[contains(@class,'container-img')]",
            ),
            (By.CSS_SELECTOR, "div.event-header div.container-img"),
            (By.CSS_SELECTOR, "div.top-header div.container-img"),
        ]
        for by, value in icon_locators:
            try:
                icon = WebDriverWait(self.driver, 6).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", icon
                )
                try:
                    icon.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", icon)
                return
            except TimeoutException:
                continue
        raise AssertionError(
            "Search icon not found: expected clickable div.container-img inside div.create-container / top-header."
        )

    def _wait_interactable_search_input(self):
        last_error = None
        for by, value in self._events_search_input_locators():
            try:
                inp = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", inp
                )
                return inp
            except TimeoutException as error:
                last_error = error
                continue
        raise AssertionError(
            f"Search input not interactable after expanding (place-input): {last_error!r}"
        )

    def search_for_text(self, query):
        self._expand_events_search_field()
        inp = self._wait_interactable_search_input()
        try:
            inp.click()
        except Exception:
            self.driver.execute_script("arguments[0].focus();", inp)
        try:
            inp.clear()
        except Exception:
            pass
        inp.send_keys(query)
        inp.send_keys(Keys.ENTER)

    def _wait_zero_counter_paragraph(self):
        def _pick(d):
            for el in d.find_elements(
                By.CSS_SELECTOR, "div.active-filter-container p, div.active-filter-list p"
            ):
                text = (el.text or "").strip().lower()
                if "0" not in text:
                    continue
                if "items found" in text or "item found" in text:
                    return el
                if "знайдено" in text:
                    return el
            return False

        return WebDriverWait(self.driver, 15).until(_pick)

    def assert_empty_state_message(self):
        empty_msg_xpath = (
            "//*[contains(., 'matching to this search')]"
            " | //*[contains(., 'find any results')]"
            " | //*[contains(., \"didn't find\") and contains(., 'results')]"
            " | //*[contains(., 'не знайшли') or contains(., 'нічого не знайдено')]"
            " | //*[contains(., 'no results') or contains(., 'No results')]"
        )
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, empty_msg_xpath))
        )

    def assert_zero_counter(self):
        counter_p = self._wait_zero_counter_paragraph()
        counter_text = (counter_p.text or "").strip().lower()
        if "0" not in counter_text:
            raise AssertionError("Counter <p> should show zero.")
        if not (
            ("items found" in counter_text or "item found" in counter_text)
            or ("знайдено" in counter_text and "0" in counter_text)
        ):
            raise AssertionError(
                f"Counter should look like '0 items found'; got: {counter_p.text!r}"
            )
