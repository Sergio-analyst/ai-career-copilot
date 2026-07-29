from urllib.parse import quote

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError

from config.settings import (
    LINKEDIN_URL,
    SEARCH_KEYWORDS,
    SEARCH_LOCATION,
    PROFILE_DIR,
    HEADLESS,
)

MAX_JOBS = 10


def search_jobs():
    jobs = []

    search_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote(SEARCH_KEYWORDS)}"
        f"&location={quote(SEARCH_LOCATION)}"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=HEADLESS,
        )

        page = browser.new_page()

        print("Opening LinkedIn...")

        page.goto(
            LINKEDIN_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )
        print(page.title())
        print(page.url)

        input("Press ENTER...")

        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=10000,
            )
        except TimeoutError:
            pass

        print("Opening Jobs Search...")

        page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )
        print(page.title())
        print(page.url)

        input("Press ENTER...")

        try:
            page.wait_for_selector(
                "div.job-card-container",
                timeout=20000,
            )
        except TimeoutError:
            print("\nNo vacancies found.")
            browser.close()
            return []

        print()
        print("Search page loaded.")
        print()

        cards = page.locator("div.job-card-container")

        total = cards.count()

        if total > MAX_JOBS:
            total = MAX_JOBS

        for i in range(total):

            card = cards.nth(i)

            try:
                link = card.locator("a.job-card-container__link").first

                title = link.inner_text().strip()

                url = link.get_attribute("href")

                if url.startswith("/"):
                    url = "https://www.linkedin.com" + url

                company = card.locator(
                    ".artdeco-entity-lockup__subtitle span"
                ).first.inner_text().strip()

                location = card.locator(
                    ".artdeco-entity-lockup__caption span"
                ).first.inner_text().strip()

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": url,
                    }
                )

            except Exception as e:
                print(e)

        print(f"Jobs found: {len(jobs)}")
        print(f"New jobs: {len(jobs)}\n")

        for idx, job in enumerate(jobs, 1):
            print(f"[{idx}] {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}\n")

        browser.close()
        return jobs