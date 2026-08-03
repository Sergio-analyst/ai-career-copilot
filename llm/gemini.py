import os

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()


class Gemini:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        self.client = genai.Client(api_key=api_key)

        # можно позже заменить на другой
        self.model = "gemini-3.5-flash"

    def ask(self, prompt: str) -> str:

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            return response.text.strip()

        except ServerError:
            return "Gemini is temporarily unavailable."

        except Exception as e:
            return f"Gemini error: {e}"


gemini = Gemini()