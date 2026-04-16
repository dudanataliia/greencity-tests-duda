"""GreenCity Events tests implemented with Page Object pattern (TC1–TC4)."""

import unittest

from selenium import webdriver

from pages.events_page import EventsPage


class TestEventsPage(unittest.TestCase):
    """UI tests for GreenCity Events page via EventsPage object."""

    DEBUG_HOLD_BROWSER_OPEN = False

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1440,1080")
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(1)

        self.events_page = EventsPage(self.driver)
        self.events_page.open().prepare()
        self.events_page.save_step_screenshot("step_00_after_setup")

    def tearDown(self):
        if self.driver:
            if self.DEBUG_HOLD_BROWSER_OPEN:
                input("Debug mode: press Enter to close browser...")
            self.driver.quit()

    def test_tc1_verify_filter_by_past_events(self):
        """TC1: Apply Past filter and verify active chip and counter text."""
        self.events_page.save_step_screenshot("tc1_step_before_actions")
        self.events_page.apply_past_filter_and_scroll()
        self.events_page.save_step_screenshot("tc1_step_after_scroll")

        self.events_page.assert_past_chip_visible()
        counter_text = self.events_page.get_counter_text()
        self.assertTrue(len(counter_text) > 0, "Events counter text is empty.")

        self.events_page.save_step_screenshot("tc1_assertions_passed")

    def test_tc2_verify_reset_past_events_filter(self):
        """TC2: Apply Past, close Past chip, verify removal and counter update."""
        self.events_page.save_step_screenshot("tc2_step_before_actions")

        self.events_page.apply_past_filter_and_scroll()
        self.events_page.save_step_screenshot("tc2_after_tc1_steps_past_applied")

        self.events_page.assert_past_chip_visible()
        counter_with_past = self.events_page.get_counter_text()
        self.assertTrue(
            len(counter_with_past) > 0, "Counter should be visible with Past filter on."
        )

        self.events_page.close_past_filter_chip()
        self.events_page.save_step_screenshot("tc2_after_close_past_chip")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self.events_page.save_step_screenshot("tc2_after_scroll")

        self.events_page.assert_past_chip_removed()
        counter_after = self.events_page.get_counter_text()
        self.assertTrue(
            len(counter_after) > 0, "Counter should still show items count after reset."
        )
        self.assertNotEqual(
            counter_with_past,
            counter_after,
            "Counter text should change after removing Past filter.",
        )

        self.events_page.save_step_screenshot("tc2_assertions_passed")

    def test_tc3_verify_change_view_between_card_and_list_layout(self):
        """TC3: Toggle list/card views and verify active state with scroll."""
        self.events_page.wait.until(lambda d: "events" in d.current_url.lower())
        url_before = self.driver.current_url
        self.events_page.save_step_screenshot("tc3_before_view_toggle")

        self.events_page.click_events_view_mode("list")
        self.events_page.assert_list_layout_active()
        self.events_page.save_step_screenshot("tc3_list_view")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self.events_page.save_step_screenshot("tc3_list_after_scroll")
        self.events_page.assert_list_layout_active()

        self.events_page.click_events_view_mode("card")
        self.events_page.assert_card_layout_active()
        self.events_page.save_step_screenshot("tc3_card_view")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self.events_page.save_step_screenshot("tc3_card_after_scroll")
        self.events_page.assert_card_layout_active()

        self.assertEqual(
            self.driver.current_url.split("#")[0],
            url_before.split("#")[0],
            "Page origin should stay the same (no full navigation away from Events).",
        )
        self.events_page.save_step_screenshot("tc3_assertions_passed")

    def test_tc4_search_non_existing_value(self):
        """TC4: Search nonsense value and verify empty state + zero counter."""
        self.events_page.wait.until(lambda d: "events" in d.current_url.lower())
        self.events_page.save_step_screenshot("tc4_before_search")

        self.events_page.search_for_text("-12!@#$%^&*")
        self.events_page.save_step_screenshot("tc4_after_typing")

        self.events_page.assert_empty_state_message()
        self.events_page.assert_zero_counter()

        self.events_page.save_step_screenshot("tc4_assertions_passed")


if __name__ == "__main__":
    unittest.main()
