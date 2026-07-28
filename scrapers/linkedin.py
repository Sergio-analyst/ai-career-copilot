from urllib.parse import quote

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from config.settings import (
    HEADLESS,
    LINKEDIN_URL,
    PROFILE_DIR,
    SEARCH_KEYWORDS,
    SEARCH_LOCATION,
)

# How many vacancies to collect.
MAX_JOBS = 10

# LinkedIn renders slightly different markup for the jobs list depending on
# whether the session is authenticated. We try known variants, in order.
JOB_CARD_SELECTORS = [
    "ul.jobs-search__results-list li",                          # logged-out / classic search results
    "div.jobs-search-results-list li[data-occludable-job-id]",  # logged-in results (current layout)
    "li.jobs-search-results__list-item",                        # alternate logged-in layout
]

# Selectors for the fields inside a single job card, in priority order.
TITLE_LINK_SELECTORS = "a.base-card__full-link, a.job-card-container__link, a.job-card-list__title"
COMPANY_SELECTORS = [
    "h4.base-search-card__subtitle",
    ".job-card-container__primary-description",
    ".job-card-container__company-name",
]
LOCATION_SELECTORS = [
    "span.job-search-card__location",
    ".job-card-container__metadata-item",
]


def _first_text(card, selectors: list[str]) -> str:
    """Return the inner text of the first selector (from `selectors`) that
    matches inside `card`, or "" if none match. Never raises."""
    for selector in selectors:
        try:
            locator = card.locator(selector)
            if locator.count() > 0:
                return locator.first.inner_text(timeout=5000).strip()
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue
    return ""


def _extract_job(card) -> dict | None:
    """Extract {title, company, location, url} from a single job card.

    Returns None (instead of raising) if the card doesn't look like a
    real job listing, so one bad card can't crash the whole scrape.
    """
    try:
        link = card.locator(TITLE_LINK_SELECTORS).first
        if link.count() == 0:
            return None

        title = link.inner_text(timeout=5000).strip()
        url = link.get_attribute("href", timeout=5000) or ""

        if not title or not url:
            return None

        company = _first_text(card, COMPANY_SELECTORS)
        location = _first_text(card, LOCATION_SELECTORS)

        return {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
        }
    except PlaywrightTimeoutError:
        return None
    except Exception:
        return None


def search_jobs() -> list[dict]:
    """Open LinkedIn Jobs search and return up to MAX_JOBS vacancies.

    Each item is {"title": str, "company": str, "location": str, "url": str}.
    Never raises on scraping/navigation failures: on any problem (LinkedIn
    layout change, no results, network hiccup) this prints a message and
    returns whatever was collected so far (possibly an empty list).
    """
    search_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote(SEARCH_KEYWORDS)}"
        f"&location={quote(SEARCH_LOCATION)}"
    )

    jobs: list[dict] = []

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=HEADLESS,
            )

            try:
                page = context.new_page()

                print("Opening LinkedIn...")
                page.goto(LINKEDIN_URL, wait_until="domcontentloaded", timeout=60000)

                # Wait for the page to settle instead of a fixed sleep. This
                # is best-effort: LinkedIn keeps background requests alive,
                # so a timeout here is not fatal.
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PlaywrightTimeoutError:
                    pass

                print("Opening Jobs Search...")
                page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

                # Wait for the results list (any known layout variant) to
                # attach to the DOM, instead of sleeping a fixed amount of
                # time. If nothing shows up, treat it as "no vacancies"
                # rather than crashing.
                combined_selector = ", ".join(JOB_CARD_SELECTORS)
                try:
                    page.wait_for_selector(combined_selector, timeout=20000)
                except PlaywrightTimeoutError:
                    print("\nNo job listings found (empty search results or unrecognized page layout).")
                    return jobs

                cards = page.locator(combined_selector)
                count = min(cards.count(), MAX_JOBS)

                for i in range(count):
                    job = _extract_job(cards.nth(i))
                    if job:
                        jobs.append(job)

                print(f"\nOpened:\n{search_url}")

            finally:
                context.close()

    except PlaywrightTimeoutError as exc:
        print(f"\nTimed out while loading LinkedIn: {exc}")
    except Exception as exc:
        print(f"\nUnexpected error while scraping LinkedIn: {exc}")

    return jobs
