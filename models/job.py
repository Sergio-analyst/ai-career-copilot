from dataclasses import dataclass, field


@dataclass
class Job:

    company: str = ""
    title: str = ""
    location: str = ""

    url: str = ""
    status: str = "new"

    easy_apply: bool = False

    salary: str = ""

    date_posted: str = ""

    experience: str = ""

    employment_type: str = ""

    workplace: str = ""

    description: str = ""

    requirements: list[str] = field(default_factory=list)

    responsibilities: list[str] = field(default_factory=list)

    benefits: list[str] = field(default_factory=list)

    skills: list[str] = field(default_factory=list)