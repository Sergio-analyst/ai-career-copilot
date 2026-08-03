import json
import google.generativeai as genai

from config.settings import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def parse_job(description: str):

    prompt = f"""
You are an expert HR recruiter.

Extract information from this LinkedIn job description.

Return ONLY valid JSON.

Schema:

{{
"title":"",
"summary":"",
"salary":"",
"experience":"",
"employment_type":"",
"workplace":"",
"requirements":[],
"responsibilities":[],
"benefits":[],
"skills":[]
}}

Job description:

{description}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")
        text = text.replace("```", "")

    elif text.startswith("```"):
        text = text.replace("```", "")

    return json.loads(text)