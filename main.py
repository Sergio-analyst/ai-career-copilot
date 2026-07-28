from scrapers.linkedin import search_jobs


def main():

    print("=" * 50)
    print("AI Career Copilot v0.1.3")
    print("=" * 50)

    jobs = search_jobs()

    print(f"\nJobs found: {len(jobs)}")

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
