"""
Автотести сторінки Events (GreenCity).

Вимоги курсу: Python + Selenium + unittest (без pytest / Page Object); setUp/tearDown;
очікування через WebDriverWait; без time.sleep у тестах.

Фіналізовано: TC1–TC4.

TC1: test_tc1_verify_filter_by_past_events — фільтр Past.
TC2: test_tc2_verify_reset_past_events_filter — скидання фільтра Past (хрестик img.cross-img).
TC3: test_tc3_verify_change_view_between_card_and_list_layout — List view / Card view.
TC4: test_tc4_search_non_existing_value — пошук → `.active-filter-list p` (0 items) + empty message.

Запуск одного тесту:
  python -m unittest tests.test_events_page.TestEventsPage.test_tc1_verify_filter_by_past_events -v
  python -m unittest tests.test_events_page.TestEventsPage.test_tc2_verify_reset_past_events_filter -v
  python -m unittest tests.test_events_page.TestEventsPage.test_tc3_verify_change_view_between_card_and_list_layout -v
  python -m unittest tests.test_events_page.TestEventsPage.test_tc4_search_non_existing_value -v
Усі тести класу:
  python -m unittest discover tests -v
"""
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestEventsPage(unittest.TestCase):
    """
    UI tests for GreenCity Events page.
    Preconditions shared by all tests are applied in setUp() (browser, URL, overlays, language).
    """

    BASE_URL = "https://www.greencity.cx.ua/#/greenCity/events"
    # Set True only when debugging (pauses before closing browser).
    DEBUG_HOLD_BROWSER_OPEN = False

    def setUp(self):
        """
        Preconditions (for all tests in this class):
        - Chrome is launched with a fixed window size.
        - The Events page URL is opened.
        - Cookie / simple overlays are closed if present.
        - Language is switched to English when possible (site may show Uk in header).
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1440,1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.implicitly_wait(2)
        self.driver.get(self.BASE_URL)
        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self._close_popups_if_present()
        self._switch_language_to_en()
        self._save_step_screenshot("step_00_after_setup")

    def tearDown(self):
        if self.driver:
            if self.DEBUG_HOLD_BROWSER_OPEN:
                input("Debug mode: press Enter to close browser...")
            self.driver.quit()

    def _find(self, locators):
        for by, value in locators:
            elements = self.driver.find_elements(by, value)
            if elements:
                return elements[0]
        return None

    def _close_popups_if_present(self):
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

    def _save_step_screenshot(self, name):
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        file_path = artifacts_dir / f"{name}.png"
        self.driver.save_screenshot(str(file_path))
        print(f"[DEBUG] Screenshot saved: {file_path}")

    def _switch_language_to_en(self):
        """Site shows Ukrainian as 'Uk' in header. Open menu and pick En."""
        en_header = self._find(
            [
                (By.XPATH, "//span[normalize-space()='En']"),
                (By.XPATH, "//button[normalize-space()='En']"),
                (By.XPATH, "//*[contains(@class,'lang') or contains(@class,'language')][.//span[normalize-space()='En']]"),
            ]
        )
        if en_header is not None:
            print("[DEBUG] Language already EN")
            return

        open_menu = self._find(
            [
                (By.XPATH, "//span[normalize-space()='Uk']"),
                (By.XPATH, "//button[.//span[normalize-space()='Uk']]"),
                (By.XPATH, "//a[.//span[normalize-space()='Uk']]"),
                (By.XPATH, "//*[contains(@class,'lang') or contains(@class,'language')][.//*[normalize-space()='Uk']]"),
                (By.XPATH, "//span[normalize-space()='Ua' or normalize-space()='UA']"),
                (By.XPATH, "//span[normalize-space()='Укр']"),
            ]
        )
        if open_menu is None:
            print("[DEBUG] Language switcher not found, skipping EN")
            return

        try:
            open_menu.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", open_menu)

        # Один WebDriverWait замість 7×5 с на окремі локатори (раніше могло бути до ~35 с).
        en_xpath = (
            "//mat-option[.//span[normalize-space()='En']]"
            " | //*[contains(@class,'cdk-overlay-pane')]//span[normalize-space()='En']"
            " | //*[contains(@class,'cdk-overlay-pane')]//button[normalize-space()='En']"
            " | //li[.//*[normalize-space()='En']]"
            " | //button[normalize-space()='En']"
            " | //a[normalize-space()='En']"
        )
        try:
            en_option = WebDriverWait(self.driver, 8).until(
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
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                try:
                    element.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", element)
                print(f"[DEBUG] Event time opened ({lang})")
                self._save_step_screenshot("step_01_event_time_clicked")
                return
            except TimeoutException:
                continue
        self.fail("Event time dropdown was not found.")

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
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", past_option)
            try:
                past_option.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", past_option)
            self._save_step_screenshot("step_02_past_selected")
        except TimeoutException:
            self._save_step_screenshot("step_02_past_not_found")
            self.fail("Past filter option was not found.")

    def _apply_past_filter_and_scroll(self):
        """Спільні кроки TC1/TC2: застосувати Past і проскролити сторінку."""
        self.wait.until(lambda d: "events" in d.current_url.lower())
        self._enable_past_filter()
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")

    def _counter_element(self):
        counter_xpath = (
            "//div[contains(@class,'active-filter-container')]//p"
            " | //*[contains(., 'Items found')]"
            " | //*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'items found')]"
            " | //*[contains(., 'знайдено')]"
        )
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, counter_xpath))
        )

    def _click_close_past_filter_chip(self):
        """Клік по хрестику: img.cross-img у div.cross-container (зелений чіп Past)."""
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
            # fallback: кнопка / mat-chip, якщо верстка зміниться
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
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                return
            except TimeoutException:
                continue
        self.fail("Close icon for Past filter chip was not found.")

    def _click_events_view_mode(self, mode):
        """
        mode: 'list' | 'card'
        Розмітка сайту: div.change-view — button.list (aria-label list view),
        button.gallery (aria-label table view) — сітка / «картки».
        """
        locators = []
        if mode == "list":
            locators = [
                (By.CSS_SELECTOR, "div.change-view button.list"),
                (By.CSS_SELECTOR, "button[aria-label='list view']"),
                (By.XPATH, "//button[contains(@class,'list')][contains(@aria-label,'list view')]"),
            ]
        else:
            # У тест-кейсі «Card view»; на сайті — gallery / table view
            locators = [
                (By.CSS_SELECTOR, "div.change-view button.gallery"),
                (By.CSS_SELECTOR, "button[aria-label='table view']"),
                (By.XPATH, "//button[contains(@class,'gallery')][contains(@aria-label,'table view')]"),
            ]
        last_error = None
        for by, value in locators:
            try:
                btn = WebDriverWait(self.driver, 12).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                return
            except TimeoutException as e:
                last_error = e
                continue
        self.fail(f"Could not find or click '{mode}' view button: {last_error!r}")

    def _assert_list_layout_active(self):
        """Кнопка List активна: aria-pressed=true на button.list."""
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'change-view')]//button[contains(@class,'list')][@aria-pressed='true']"
                    " | //button[contains(@class,'list')][@aria-pressed='true']",
                )
            )
        )

    def _assert_card_layout_active(self):
        """Сітка (gallery): aria-pressed=true на button.gallery (aria-label table view)."""
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'change-view')]//button[contains(@class,'gallery')][@aria-pressed='true']"
                    " | //button[contains(@class,'gallery')][@aria-pressed='true']",
                )
            )
        )

    def test_tc1_verify_filter_by_past_events(self):
        """
        Test case: Verify Filter by Past events (TC1).

        Preconditions: applied in setUp() — browser, Events URL, overlays, EN where possible.

        Steps:
        1. Open "Event time" filter and select "Past".
        2. Scroll the page down and up.

        Assertions:
        - Active Past filter is visible (chip / label).
        - Events counter text is visible (e.g. in .active-filter-container).
        """
        self._save_step_screenshot("tc1_step_before_actions")
        self._apply_past_filter_and_scroll()
        self._save_step_screenshot("tc1_step_after_scroll")

        chip_xpath = (
            "//*[contains(., 'Past') and contains(@class, 'filter')]"
            " | //*[contains(., 'Минул') and contains(@class, 'filter')]"
            " | //*[contains(., 'Past')]"
            " | //*[contains(., 'Минул')]"
        )
        active_past_chip = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, chip_xpath))
        )
        self.assertIsNotNone(active_past_chip, "Past filter chip/text is not displayed.")

        counter_xpath = (
            "//div[contains(@class,'active-filter-container')]//p"
            " | //*[contains(., 'Items found')]"
            " | //*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'items found')]"
            " | //*[contains(., 'знайдено')]"
        )
        counter = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, counter_xpath))
        )
        self.assertTrue(
            len((counter.text or "").strip()) > 0,
            "Events counter text is empty.",
        )
        self._save_step_screenshot("tc1_assertions_passed")

    def test_tc2_verify_reset_past_events_filter(self):
        """
        Test case 2 (фінальна версія): Verify Reset Past events Filter.

        Preconditions: як у setUp() (браузер, сторінка Events, EN за можливості).

        Steps:
        1–3. Як у TC1: відкрити Event time → Past → скрол вниз/вгору (переконатися, що Past застосовано).
        4. Клік по іконці закриття на зеленому чіпі Past.
        5. Скрол вниз і вгору.
        6. Перевірити список / стан фільтрів.

        Expected:
        - чіп Past знято;
        - лічильник оновився (інший текст, ніж зі ввімкненим Past);
        - у блоці активних фільтрів немає Past.
        """
        self._save_step_screenshot("tc2_step_before_actions")

        self._apply_past_filter_and_scroll()
        self._save_step_screenshot("tc2_after_tc1_steps_past_applied")

        chip_xpath = (
            "//*[contains(., 'Past') and contains(@class, 'filter')]"
            " | //*[contains(., 'Минул') and contains(@class, 'filter')]"
            " | //*[contains(., 'Past')]"
            " | //*[contains(., 'Минул')]"
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, chip_xpath))
        )
        counter_with_past = self._counter_element()
        text_with_past = (counter_with_past.text or "").strip()
        self.assertTrue(len(text_with_past) > 0, "Counter should be visible with Past filter on.")

        # 1. Close Past chip
        self._click_close_past_filter_chip()
        self._save_step_screenshot("tc2_after_close_past_chip")

        # 2–3. Scroll and observe
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self._save_step_screenshot("tc2_after_scroll")

        # Past filter removed: only the green chip row (.chips > .active-filter), not any nested text
        chip_past_xpath = (
            "//div[contains(@class,'active-filter-list')]//div[contains(@class,'chips')]"
            "//div[contains(@class,'active-filter')][contains(.,'Past') or contains(.,'Минул')]"
        )
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: len(
                    d.find_elements(By.XPATH, chip_past_xpath)
                )
                == 0
            )
        except TimeoutException:
            self.fail("Past filter chip should be removed from active filters (still present after close).")

        counter_after = self._counter_element()
        text_after = (counter_after.text or "").strip()
        self.assertTrue(len(text_after) > 0, "Counter should still show items count after reset.")
        self.assertNotEqual(
            text_with_past,
            text_after,
            "Counter text should change after removing Past filter (all events vs past-only).",
        )

        self._save_step_screenshot("tc2_assertions_passed")

    def test_tc3_verify_change_view_between_card_and_list_layout(self):
        """
        Test case 3: Verify Change View Between Card and List Layout.

        UI: div.change-view — button.list (aria-label list view), button.gallery (aria-label table view).
        Перевірка стану: aria-pressed на активній кнопці.

        Steps:
        1. List view — клік button.list, перевірка aria-pressed.
        2. Скрол, знову перевірка list.
        3. Сітка (картки) — клік button.gallery, перевірка aria-pressed.
        4. Скрол, знову перевірка gallery.

        Assertions: той самий origin URL (без повного переходу з сайту).
        """
        self.wait.until(lambda d: "events" in d.current_url.lower())
        url_before = self.driver.current_url
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "app-events, .events-list, .events-container, [class*='events']")
            )
        )
        self._save_step_screenshot("tc3_before_view_toggle")

        # 1–2: List view + scroll
        self._click_events_view_mode("list")
        self._assert_list_layout_active()
        self._save_step_screenshot("tc3_list_view")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self._save_step_screenshot("tc3_list_after_scroll")
        self._assert_list_layout_active()

        # 3–4: Card view + scroll
        self._click_events_view_mode("card")
        self._assert_card_layout_active()
        self._save_step_screenshot("tc3_card_view")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self._save_step_screenshot("tc3_card_after_scroll")
        self._assert_card_layout_active()

        self.assertEqual(
            self.driver.current_url.split("#")[0],
            url_before.split("#")[0],
            "Page origin should stay the same (no full navigation away from Events).",
        )
        self._save_step_screenshot("tc3_assertions_passed")

    def _events_search_input_locators(self):
        """Поле після розгортання: input.place-input у div.container-input (create-container / top-header)."""
        return [
            (By.CSS_SELECTOR, "div.create-container input.place-input"),
            (By.CSS_SELECTOR, "input.place-input"),
            (By.CSS_SELECTOR, "div.container-input input[type='text']"),
            (By.CSS_SELECTOR, "div.top-header input.place-input"),
            (By.XPATH, "//div[contains(@class,'container-input')]//input[@placeholder='Search' or @placeholder='Пошук']"),
            (By.CSS_SELECTOR, "app-events-list input.place-input"),
            (By.CSS_SELECTOR, "app-events input.place-input"),
        ]

    def _expand_events_search_field(self):
        """
        Спочатку показується лише іконка лупи (div.container-img); після кліку розгортається input.place-input.
        """
        icon_locators = [
            (By.CSS_SELECTOR, "div.create-container div.container-img"),
            (By.CSS_SELECTOR, "div.top-header div.create-container div.container-img"),
            (By.XPATH, "//div[contains(@class,'top-header')]//div[contains(@class,'create-container')]//div[contains(@class,'container-img')]"),
            (By.CSS_SELECTOR, "div.event-header div.container-img"),
            (By.CSS_SELECTOR, "div.top-header div.container-img"),
        ]
        for by, value in icon_locators:
            try:
                icon = WebDriverWait(self.driver, 6).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
                try:
                    icon.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", icon)
                return
            except TimeoutException:
                continue
        self.fail(
            "Search icon not found: expected clickable div.container-img inside div.create-container / top-header."
        )

    def _wait_interactable_search_input(self):
        """Після кліку по іконці поле має стати клікабельним; інакше send_keys дає ElementNotInteractableException."""
        last_error = None
        for by, value in self._events_search_input_locators():
            try:
                inp = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                return inp
            except TimeoutException as e:
                last_error = e
                continue
        self.fail(f"Search input not interactable after expanding (place-input): {last_error!r}")

    def _open_search_and_type(self, query):
        """Клік по іконці лупи → розгортання поля → ввід тексту → Enter."""
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

    def _wait_tc4_zero_counter_paragraph(self):
        """
        Лічильник над списком: зазвичай div.active-filter-container → div.active-filter-list → p
        з текстом на кшталт «0 items found» (у DOM можуть бути відступи в класах — перебираємо p у блоці).
        """
        def _pick(d):
            for el in d.find_elements(
                By.CSS_SELECTOR,
                "div.active-filter-container p, div.active-filter-list p",
            ):
                t = (el.text or "").strip().lower()
                if "0" not in t:
                    continue
                if "items found" in t or "item found" in t:
                    return el
                if "знайдено" in t:
                    return el
            return False

        return WebDriverWait(self.driver, 15).until(_pick)

    def test_tc4_search_non_existing_value(self):
        """
        Test case 4: Search not existing value.

        Steps:
        1. Клік по іконці пошуку (div.container-img у create-container).
        2. У розгорнуте поле input.place-input ввести `-12!@#$%^&*`.

        Expected:
        - лічильник над списком: `div.active-filter-container` → `div.active-filter-list` → `p` (0 items);
        - повідомлення в контенті, що за цим пошуком нічого не знайдено.
        """
        self.wait.until(lambda d: "events" in d.current_url.lower())
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "app-events, .events-list, .events-container, [class*='events']")
            )
        )
        self._save_step_screenshot("tc4_before_search")

        self._open_search_and_type("-12!@#$%^&*")
        self._save_step_screenshot("tc4_after_typing")

        # 1) Спочатку центральне повідомлення (Angular оновлює лічильник трохи пізніше)
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

        # 2) Лічильник прив’язаний до .active-filter-container / .active-filter-list (див. DevTools — <p> 0 items found)
        counter_p = self._wait_tc4_zero_counter_paragraph()
        counter_text = (counter_p.text or "").strip().lower()
        self.assertIn("0", counter_text, "Counter <p> should show zero.")
        self.assertTrue(
            ("items found" in counter_text or "item found" in counter_text)
            or ("знайдено" in counter_text and "0" in counter_text),
            f"Counter should look like '0 items found'; got: {counter_p.text!r}",
        )

        self._save_step_screenshot("tc4_assertions_passed")


if __name__ == "__main__":
    unittest.main()
