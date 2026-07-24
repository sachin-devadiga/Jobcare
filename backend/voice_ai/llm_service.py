import json
import logging
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger('jobcare')

EXTRACT_SYSTEM_PROMPT = """You are a resume parser for a voice-enabled job platform. Extract structured profile information from the user's spoken transcript. The user may speak in Hindi, English, Hinglish, or other Indian languages.

Return ONLY valid JSON with no markdown, no code fences, no extra text.

Fields to extract:
- "skills": array of strings — technical/professional skills mentioned (Python, Excel, communication, etc.)
- "experience_years": number — total years of professional work experience (0 if fresher/none)
- "education": array of objects with { "degree": string, "field": string (optional), "institution": string (optional), "year": number (optional) }
- "languages": array of strings — languages the person speaks
- "certificates": array of objects with { "name": string, "issuer": string (optional), "year": number (optional) }

If a field has no data, use an empty array or 0 as appropriate. Do not hallucinate."""


class LLMProfileExtractionService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def extract_profile(self, transcript: str, language: str = "hi") -> dict:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not configured; returning empty extraction")
            return self._empty_result()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Language: {language}\n\nTranscript:\n{transcript}"},
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content.strip()
            parsed = json.loads(content)
            return {
                "skills": parsed.get("skills", []),
                "experience_years": parsed.get("experience_years", 0),
                "education": parsed.get("education", []),
                "languages": parsed.get("languages", []),
                "certificates": parsed.get("certificates", []),
            }

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}", exc_info=True)
            return self._empty_result()

    def _empty_result(self):
        return {
            "skills": [],
            "experience_years": 0,
            "education": [],
            "languages": [],
            "certificates": [],
        }
