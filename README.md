# greencity-tests

## Project description

This repository contains **manual test cases** (Markdown) and **automated UI tests** for the **GreenCity Events** page.

| Location | Content |
|----------|---------|
| `test-cases/events-page-tests.md` | Manual test cases (table: preconditions, steps, data, expected result) |
| `tests/test_events_page.py` | Four automated tests (`unittest` + Selenium) |
| `requirements.txt` | Python dependencies |

**Stack:** Python, Selenium WebDriver, standard **`unittest`** (no `pytest`, no Page Object).  
Tests use **`setUp` / `tearDown`**, **`WebDriverWait`** / explicit waits, and avoid `time.sleep` in test code.

**Testing page:** [GreenCity Events](https://www.greencity.cx.ua/#/greenCity/events)

---

## Automated tests (4)

| ID | Test method | What it checks |
|----|-------------|----------------|
| TC1 | `test_tc1_verify_filter_by_past_events` | **Event time** → **Past** filter, scroll; Past chip visible; items counter text visible |
| TC2 | `test_tc2_verify_reset_past_events_filter` | Same as TC1 to apply Past, then close Past chip (`img.cross-img`), scroll; chip gone; counter text changes |
| TC3 | `test_tc3_verify_change_view_between_card_and_list_layout` | **List** vs **gallery/card** (`div.change-view`), `aria-pressed` on active button, scroll, same page origin |
| TC4 | `test_tc4_search_non_existing_value` | Expand search (`div.container-img` → `input.place-input`), type `-12!@#$%^&*`, empty-state message + **0 items** in `.active-filter-list p` |

**Shared preconditions (`setUp`):** Chrome (fixed window), open Events URL, close cookie/popups if present, switch UI to **English** when possible.  
**Screenshots (debug):** saved under `artifacts/` when tests run (folder is gitignored).

---

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
