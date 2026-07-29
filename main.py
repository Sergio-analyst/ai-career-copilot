from database import Job, get_all_jobs, init_database, job_exists, save_job
from scrapers import linkedin
from llm import gemini


def main():
    print("=" * 50)
    print("AI Career Copilot v0.1.3")
    print("=" * 50)

    init_database()

    jobs = linkedin.search_jobs()

    print(f"\nJobs found: {len(jobs)}")

    new_count = 0
    skipped_count = 0
    job_objects = []

    for job_data in jobs:
        url = job_data.get("url", "") if isinstance(job_data, dict) else job_data.url

        if not url or job_exists(url):
            skipped_count += 1
            continue

        if isinstance(job_data, dict):
            job_obj = Job(
                linkedin_url=url,
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
            )
        else:
            job_obj = job_data

        saved = save_job(job_obj)

        if saved:
            new_count += 1
            job_objects.append(job_obj)
        else:
            skipped_count += 1

    print(f"New jobs: {new_count}")
    print(f"Skipped: {skipped_count}")

    # Descriptions are already collected inside linkedin.search_jobs() —
    # each job_data dict has a "description" key by the time we get here.
    # job_objects is a filtered subset of jobs (dupes removed), so we look
    # descriptions up by URL rather than assuming matching list positions.
    description_by_url = {
        job_data.get("url", ""): job_data.get("description", "")
        for job_data in jobs
        if isinstance(job_data, dict)
    }

    for job_obj in job_objects:
        description = description_by_url.get(job_obj.linkedin_url, "")
        job_obj.description = description

        print("=" * 70)
        print(job_obj.title)
        print(description[:1500])

    print()
    print("=" * 60)
    print("Testing Gemini...")
    print("=" * 60)

    answer = gemini.ask("Say only: Gemini connected successfully.")
    print(answer)

    if not job_objects:
        print("No vacancies to display.")
        return

    for i, job in enumerate(job_objects, start=1):
        print(f"\n[{i}] {job.title}")
        print(f"    Company:  {job.company or '—'}")
        print(f"    Location: {job.location or '—'}")
        print(f"    URL:      {getattr(job, 'linkedin_url', getattr(job, 'url', ''))}")


if __name__ == "__main__":
    main()