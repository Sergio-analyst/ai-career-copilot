from urllib.parse import quote

from playwright.sync_api import sync_playwright

from config.settings import (
    HEADLESS,
    LINKEDIN_URL,
    PROFILE_DIR,
    SEARCH_KEYWORDS,
    SEARCH_LOCATION,
)


def search_jobs():

    search_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote(SEARCH_KEYWORDS)}"
        f"&location={quote(SEARCH_LOCATION)}"
    )

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=HEADLESS,
        )

        page = context.new_page()

        print("Opening LinkedIn...")

        page.goto(
            LINKEDIN_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(3000)

        print("Opening Jobs Search...")

        page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print(f"\nOpened:\n{search_url}")

        input("\nPress ENTER to close browser...")

        context.close()

    return []