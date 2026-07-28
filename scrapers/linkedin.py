"""
LinkedIn Job Scraper

Версия: v0.1.1

Проверяем работу Playwright.
"""

from playwright.sync_api import sync_playwright


def search_jobs(query: str):
    """
    Пока просто открывает браузер
    и переходит на Google.
    """

    print(f"Searching LinkedIn for: {query}")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto("https://www.google.com")

        print("✅ Browser opened successfully!")

        input("Press ENTER to close browser...")

        browser.close()

    return []