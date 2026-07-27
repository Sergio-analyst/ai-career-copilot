from scrapers.linkedin import search_jobs


def main():
    print("=" * 50)
    print("AI Career Copilot v0.1")
    print("=" * 50)

    jobs = search_jobs("Data Analyst Dubai")

    print(f"\nJobs found: {len(jobs)}")


if __name__ == "__main__":
    main()