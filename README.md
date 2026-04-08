# greencity-tests

## Project description

This repository contains 4 **manual test cases** (Markdown) and 4 **automated UI tests** for the **GreenCity Events** page.

| Location | Content |
|----------|---------|
| `test-cases/events-page-tests.md` | Manual test cases (table: preconditions, steps, data, expected result) |
| `tests/test_events_page.py` | Four automated tests (`unittest` + Selenium) |
| `requirements.txt` | Python dependencies |

**Testing page:** [GreenCity Events](https://www.greencity.cx.ua/#/greenCity/events)


## How to run tests

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the full suite:

   ```bash
   python -m unittest discover tests
   ```

4. Verbose:

   ```bash
   python -m unittest discover tests -v
   ```

5. Run the whole test class:

   ```bash
   python -m unittest tests.test_events_page.TestEventsPage -v
   ```

6. Run a single test (examples):

   ```bash
   python -m unittest tests.test_events_page.TestEventsPage.test_tc1_verify_filter_by_past_events -v
   python -m unittest tests.test_events_page.TestEventsPage.test_tc2_verify_reset_past_events_filter -v
   python -m unittest tests.test_events_page.TestEventsPage.test_tc3_verify_change_view_between_card_and_list_layout -v
   python -m unittest tests.test_events_page.TestEventsPage.test_tc4_search_non_existing_value -v
   ```

**Prerequisites:** Google Chrome installed; Selenium 4 typically resolves the matching driver automatically.

---

## Author

**Duda Nataliia**
