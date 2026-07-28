"""
LinkedIn Job Scraper

Версия: v0.1.2

Используем постоянный профиль браузера.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright


PROFILE_DIR = Path("browser_profile")


def search_jobs(query: str):
    """
    Открывает браузер с постоянным профилем.
    """

    print(f"Searching LinkedIn for: {query}")

    PROFILE_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
        )

        page = context.new_page()

        page.goto("https://www.linkedin.com")

        print("✅ LinkedIn opened!")

        print("Если это первый запуск — войди в свой аккаунт вручную.")

        input("\nPress ENTER to close browser...")

        context.close()

    return []