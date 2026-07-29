from database import Job, get_all_jobs, init_database, job_exists, save_job
from scrapers.linkedin import search_jobs
from llm import gemini


def main():
    print("=" * 50)
    print("AI Career Copilot v0.1.3")
    print("=" * 50)

    init_database()

    jobs = search_jobs()

    print(f"\nJobs found: {len(jobs)}")

    new_count = 0
    skipped_count = 0

    for job in jobs:
        url = job.get("url", "")

        if not url or job_exists(url):
            skipped_count += 1
            continue

        saved = save_job(
            Job(
                linkedin_url=url,
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
            )
        )

        if saved:
            new_count += 1
        else:
            skipped_count += 1

    print(f"New jobs: {new_count}")
    print(f"Skipped: {skipped_count}")

    # --- Добавленный блок тестирования Gemini ---
    print()
    print("=" * 60)
    print("Testing Gemini...")
    print("=" * 60)

    answer = gemini.ask("Say only: Gemini connected successfully.")
    print(answer)
    # --------------------------------------------

    if not jobs:
        print("No vacancies to display.")
        return

    for i, job in enumerate(jobs, start=1):
        print(f"\n[{i}] {job['title']}")
        print(f"    Company:  {job['company'] or '—'}")
        print(f"    Location: {job['location'] or '—'}")
        print(f"    URL:      {job['url']}")


if __name__ == "__main__":
    main()