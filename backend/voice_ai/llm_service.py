import json
import logging
import re
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

SKILL_KEYWORDS = [
    'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'sql', 'mysql',
    'excel', 'ms excel', 'word', 'powerpoint', 'tally', 'photoshop', 'autocad',
    'salesforce', 'communication', 'leadership', 'management', 'customer service',
    'driving', 'bike riding', 'welding', 'carpentry', 'plumbing', 'packing',
    'loading', 'unloading', 'accounting', 'bookkeeping', 'typing', 'marketing',
    'sales', 'html', 'css', 'react', 'flutter', 'django', 'aws', 'linux', 'git',
    'node.js', 'testing', 'quality control', 'supervision', 'mechanic',
    'electrician', 'fabrication', 'cooking', 'housekeeping', 'security',
    'computer', 'digital marketing',
]

LANGUAGE_MAP = {
    'hindi': 'Hindi', 'हिन्दी': 'Hindi', 'हिंदी': 'Hindi',
    'english': 'English', 'अंग्रेजी': 'English', 'अंग्रेज़ी': 'English',
    'kannada': 'Kannada', 'ಕನ್ನಡ': 'Kannada', 'kanada': 'Kannada',
    'tamil': 'Tamil', 'தமிழ்': 'Tamil',
    'telugu': 'Telugu', 'తెలుగు': 'Telugu',
    'malayalam': 'Malayalam', 'മലയാളം': 'Malayalam',
    'marathi': 'Marathi', 'मराठी': 'Marathi',
    'gujarati': 'Gujarati', 'ગુજરાતી': 'Gujarati',
    'bengali': 'Bengali', 'বাংলা': 'Bengali',
    'punjabi': 'Punjabi', 'पंजाबी': 'Punjabi',
    'odia': 'Odia', 'oriya': 'Odia',
    'urdu': 'Urdu', 'nepali': 'Nepali',
}

HINDI_NUMBERS = {
    'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5, 'पाँच': 5,
    'छह': 6, 'छः': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10,
}

_EXP_YEARS_RE = re.compile(r'(\d{1,2})\s*(?:years?|yrs?|saal|saalo?|varsh(?:a|e|o)?)', re.IGNORECASE)
_EXP_UNIT_RE = re.compile(r'(?:years?|yrs?|saal|saalo?|varsh(?:a|e|o)?)', re.IGNORECASE)


class LLMProfileExtractionService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def extract_profile(self, transcript: str, language: str = "hi") -> dict:
        if not settings.OPENAI_API_KEY or not settings.OPENAI_API_KEY.startswith('sk-'):
            logger.warning("OPENAI_API_KEY not configured; using heuristic extraction")
            return self._heuristic_extract(transcript, language)

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
            logger.error(f"LLM extraction failed ({e}); using heuristic extraction", exc_info=True)
            return self._heuristic_extract(transcript, language)

    def _heuristic_extract(self, transcript: str, language: str = "hi") -> dict:
        text = transcript.lower()

        skills = []
        for keyword in SKILL_KEYWORDS:
            if keyword in text:
                display = 'MS Excel' if keyword == 'ms excel' else keyword.title()
                if display not in skills:
                    skills.append(display)

        years = 0
        match = _EXP_YEARS_RE.search(transcript)
        if match:
            years = int(match.group(1))
        else:
            unit = _EXP_UNIT_RE.search(transcript)
            if unit and unit.start() > 0:
                prev_word = transcript[:unit.start()].rstrip().split()[-1]
                if prev_word in HINDI_NUMBERS:
                    years = HINDI_NUMBERS[prev_word]

        languages = []
        lowered = transcript.lower()
        for key, display in LANGUAGE_MAP.items():
            if key in lowered and display not in languages:
                languages.append(display)

        return {
            "skills": skills,
            "experience_years": years,
            "education": [],
            "languages": languages,
            "certificates": [],
        }

    def _empty_result(self):
        return {
            "skills": [],
            "experience_years": 0,
            "education": [],
            "languages": [],
            "certificates": [],
        }
