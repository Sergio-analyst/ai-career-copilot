import random
from playwright.sync_api import sync_playwright, TimeoutError

from config.settings import (
    LINKEDIN_URL,
    SEARCH_KEYWORDS,
    SEARCH_LOCATIONS,
    PROFILE_DIR,
    HEADLESS,
)
from models import Job
from utils.linkedin_filters import build_search_url
from parsers.job_parser import JobParser

MAX_JOBS_PER_LOCATION = 2 


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
            search_url = build_search_url(
                SEARCH_KEYWORDS,
                location
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

            # 1. Собираем базовую информацию
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

                    job = Job()
                    job.title = title
                    job.company = company
                    job.location = card_location
                    job.url = url

                    location_jobs.append(job)
                except Exception as e:
                    print(f"Error parsing card #{i}: {e}")

                human_delay(0.3, 1.2)

            print(f"Found {len(location_jobs)} jobs in {location}. Getting FULL descriptions...\n")

            # 2. Кликаем по карточкам прямо в результатах поиска
            for idx, job in enumerate(location_jobs, 1):
                card = cards.nth(idx - 1)
                card.click()
                page.wait_for_timeout(2500)

                # Раскрываем блок описания
                try:
                    page.locator(
                        "button[aria-label*='Show more']"
                    ).first.click(timeout=3000)
                except Exception:
                    pass

                # Извлекаем текст описания
                description = ""
                possible = [
                    ".jobs-description-content",
                    ".jobs-description",
                    ".jobs-box__html-content",
                    ".jobs-description__content"
                ]

                for s in possible:
                    try:
                        txt = page.locator(s).inner_text().strip()
                        if len(txt) > len(description):
                            description = txt
                    except Exception:
                        pass

                job.description = description

                # Вывод сырого текста вакансии в консоль
                print()
                print("=" * 80)
                print(description[:2500])
                print("=" * 80)

                # Проверка Easy Apply
                job.easy_apply = False
                try:
                    apply_btn = page.locator("button.jobs-apply-button")
                    if apply_btn.count():
                        text = apply_btn.first.inner_text().lower()
                        if "easy apply" in text:
                            job.easy_apply = True
                except Exception:
                    pass

                # Проверка длины описания перед парсингом
                if len(description) < 300:
                    print("❌ Description too short.")
                    continue

                # ---------------- AI PARSER ----------------
                try:
                    from ai.gemini_job_parser import parse_job_with_gemini

                    ai_result = parse_job_with_gemini(description)

                    job.salary = ai_result.get("salary", "")
                    job.requirements = ai_result.get("requirements", [])
                    job.responsibilities = ai_result.get("responsibilities", [])
                    job.benefits = ai_result.get("benefits", [])
                except Exception as e:
                    print(f"Gemini parser failed: {e}")

                    parsed = JobParser.parse(description)

                    job.salary = parsed["salary"]
                    job.requirements = parsed["requirements"]
                    job.responsibilities = parsed["responsibilities"]
                    job.benefits = parsed["benefits"]
                # -------------------------------------------

                # Консольный лог
                print(f"Company: {job.company}")
                print(f"Position: {job.title}")
                print(f"Salary: {job.salary}")
                print(f"Easy Apply: {job.easy_apply}")
                print(f"Requirements lines parsed: {len(job.requirements)}")
                print(f"Responsibilities lines parsed: {len(job.responsibilities)}")

                print("\nRequirements")
                print("-" * 40)
                print("\n".join(job.requirements[:10]))

                print("\nResponsibilities")
                print("-" * 40)
                print("\n".join(job.responsibilities[:10]))

                print("\nBenefits")
                print("-" * 40)
                print("\n".join(job.benefits[:10]))
                print("=" * 70)

            all_jobs.extend(location_jobs)

        browser.close()
        return all_jobs