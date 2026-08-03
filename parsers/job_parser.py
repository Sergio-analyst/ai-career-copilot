import re


class JobParser:

    @staticmethod
    def parse(text: str):

        result = {
            "salary": "Not specified",
            "requirements": [],
            "responsibilities": [],
            "benefits": [],
        }

        if not text:
            return result

        lines = [
            x.strip()
            for x in text.splitlines()
            if x.strip()
        ]

        current = None

        for line in lines:

            low = line.lower()

            # ---------- REQUIREMENTS ----------

            if any(k in low for k in [
                "requirements",
                "qualifications",
                "what we're looking for",
                "what you bring",
                "your profile",
                "skills & qualifications",
                "minimum qualifications",
                "preferred qualifications"
            ]):
                current = "requirements"
                continue

            # ---------- RESPONSIBILITIES ----------

            if any(k in low for k in [
                "responsibilities",
                "what you'll do",
                "what you will do",
                "your responsibilities",
                "key responsibilities",
                "duties",
                "role",
                "your role"
            ]):
                current = "responsibilities"
                continue

            # ---------- BENEFITS ----------

            if any(k in low for k in [
                "benefits",
                "what we offer",
                "why join",
                "perks",
                "our offer",
                "what you'll get"
            ]):
                current = "benefits"
                continue

            # ---------- STOP SECTION ----------

            if any(k in low for k in [
                "about us",
                "equal opportunity",
                "privacy",
                "apply now",
                "company description",
                "about the company"
            ]):
                current = None
                continue

            # ---------- SAVE ----------

            if current:

                if len(line) < 3:
                    continue

                if current == "requirements":
                    result["requirements"].append(line)

                elif current == "responsibilities":
                    result["responsibilities"].append(line)

                elif current == "benefits":
                    result["benefits"].append(line)

        # -------- Salary --------

        salary = re.search(
            r"([$€£AED]{1}\s?[\d,]+(?:\s*-\s*[$€£AED]?\s?[\d,]+)?)",
            text,
            re.IGNORECASE,
        )

        if salary:
            result["salary"] = salary.group(1)

        return result