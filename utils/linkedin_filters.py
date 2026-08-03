from urllib.parse import quote


def build_search_url(keywords: str, location: str) -> str:
    """
    LinkedIn search URL with filters.

    Easy Apply
    Past Week
    Entry + Associate + Mid
    """

    return (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote(keywords)}"
        f"&location={quote(location)}"
        "&f_AL=true"
        "&f_TPR=r604800"
        "&f_E=2,3,4"
        "&sortBy=DD"
    )