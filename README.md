# greencity-tests

## Project description

This repository contains **manual test cases** (Markdown) and **automated UI tests** for the **GreenCity Events** page.

Manual test cases follow a consistent structure (number, title, preconditions, steps, data, expected result) and are stored in `test-cases/events-page-tests.md`.

Automated tests use **Python**,and **Selenium WebDriver**
The repository contains:

- **Manual test cases**: `test-cases/events-page-tests.md`
- **Automated tests**: `tests/test_events_page.py`
- **Dependencies**: `requirements.txt`

## Testing page

[GreenCity Events](https://www.greencity.cx.ua/#/greenCity/events)

## How to run tests

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the full test suite:

   ```bash
   python -m unittest discover tests
   ```

4. Run with verbose output:

   ```bash
   python -m unittest discover tests -v
   ```

5. Run a single test class:

   ```bash
   python -m unittest tests.test_events_page.TestEventsPage -v
   ```

6. Run one test method (example — TC1):

   ```bash
   python -m unittest tests.test_events_page.TestEventsPage.test_tc1_verify_filter_by_past_events -v
   ```

**Prerequisites:** Google Chrome and a matching ChromeDriver (Selenium 4 manages the driver automatically in typical setups).

## Author

**Duda Nataliia**
