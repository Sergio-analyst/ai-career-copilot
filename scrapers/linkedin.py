import random
from urllib.parse import quote
from playwright.sync_api import sync_playwright, TimeoutError

from config.settings import (
    LINKEDIN_URL,
    SEARCH_KEYWORDS,
    SEARCH_LOCATIONS,
    PROFILE_DIR,
    HEADLESS,
)

MAX_JOBS_PER_LOCATION = 10


def human_delay(min_seconds: float, max_seconds: float) -> None:
    """Sleep for a randomized amount of time to avoid constant, bot-like pacing."""
    import time
    time.sleep(random.uniform(min_seconds, max_seconds))


def search_jobs():
    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=HEADLESS,
        )

        page = browser.new_page()

        print("Opening LinkedIn...")
        page.goto(LINKEDIN_URL, wait_until="domcontentloaded", timeout=60000)

        input("Press ENTER after login/verification...")

        for location in SEARCH_LOCATIONS:
            search_url = (
                "https://www.linkedin.com/jobs/search/"
                f"?keywords={quote(SEARCH_KEYWORDS)}"
                f"&location={quote(location)}"
            )

            print(f"\nOpening Jobs Search for: {location}...")
            page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            human_delay(1.5, 4.0)

            try:
                page.wait_for_selector("div.job-card-container", timeout=20000)
            except TimeoutError:
                print(f"\nNo vacancies found for {location}.")
                continue

            print(f"\nSearch page loaded for {location}. Extracting job cards...\n")

            cards = page.locator("div.job-card-container")
            total = min(cards.count(), MAX_JOBS_PER_LOCATION)

            location_jobs = []

            # 1. Собираем базовую информацию (ссылки, названия, компании)
            for i in range(total):
                card = cards.nth(i)
                try:
                    link = card.locator("a.job-card-container__link").first
                    title = link.inner_text().strip()
                    url = link.get_attribute("href")

                    if url and url.startswith("/"):
                        url = "https://www.linkedin.com" + url

                    company = card.locator(".artdeco-entity-lockup__subtitle span").first.inner_text().strip()
                    card_location = card.locator(".artdeco-entity-lockup__caption span").first.inner_text().strip()

                    location_jobs.append({
                        "title": title,
                        "company": company,
                        "location": card_location,
                        "url": url,
                    })
                except Exception as e:
                    print(f"Error parsing card #{i}: {e}")

                human_delay(0.3, 1.2)

            print(f"Found {len(location_jobs)} jobs in {location}. Getting FULL descriptions...\n")

            # 2. Переходим на страницу каждой вакансии за полным описанием
            for idx, job in enumerate(location_jobs, 1):
                print("=" * 70)
                print(f"[{idx}/{len(location_jobs)}] {job['title']}")
                print(f"URL: {job['url']}")

                try:
                    human_delay(2.0, 6.0)

                    page.goto(job["url"], wait_until="domcontentloaded", timeout=30000)
                    human_delay(1.5, 3.5)

                    # Плавная прокрутка документа вниз через JS
                    page.evaluate("""
                        window.scrollTo({
                            top: document.body.scrollHeight,
                            behavior: 'smooth'
                        })
                    """)
                    human_delay(2.0, 4.0)

                    # Нажимаем "Show more", если кнопка присутствует
                    try:
                        show_more_btn = page.get_by_role("button", name="Show more")
                        if show_more_btn.is_visible(timeout=2000):
                            show_more_btn.click()
                            human_delay(0.8, 1.8)
                    except Exception:
                        pass

                    selectors = [
                        ".jobs-description",
                        ".jobs-description-content__text",
                        ".jobs-box__html-content",
                        ".jobs-description__content",
                        ".jobs-description-content",
                        ".jobs-box__container",
                        ".jobs-details",
                        ".jobs-search__job-details--container",
                        "#job-details",
                        "main",
                    ]

                    # Поиск самого длинного текста с печатью селекторов
                    best_text = ""
                    for selector in selectors:
                        try:
                            loc = page.locator(selector)

                            if loc.count() == 0:
                                continue

                            text = loc.first.inner_text().strip()
                            print(f"{selector} {len(text)}")

                            if len(text) > len(best_text):
                                best_text = text

                        except Exception:
                            pass

                    description = best_text
                    job["description"] = description

                    if description:
                        print(f"Description length: {len(description)} chars")
                        print(description[:300] + "...\n")
                    else:
                        print("DESCRIPTION NOT FOUND\n")

                except Exception as e:
                    print(f"Failed to fetch description for {job['title']}: {e}\n")
                    job["description"] = ""

            all_jobs.extend(location_jobs)

        browser.close()
        return all_jobs