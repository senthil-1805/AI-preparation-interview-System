import os
import json
import requests
from services.fallback_evaluator import FallbackEvaluator

class AIService:
    def __init__(self, mode=None):
        self.mode = mode or os.environ.get('AI_MODE', 'demo')
        self.openai_key = os.environ.get('OPENAI_API_KEY', '')
        self.gemini_key = os.environ.get('GEMINI_API_KEY', '')

    def is_api_configured(self):
        return self.mode == 'api' and (bool(self.openai_key) or bool(self.gemini_key))

    def evaluate_answer(self, question_text, user_answer, sample_answer=None, target_skill=None):
        """
        Evaluate candidate response. Uses LLM API if key is available and mode is 'api'.
        Otherwise uses safe, deterministic FallbackEvaluator in DEMO mode.
        """
        if not self.is_api_configured():
            return FallbackEvaluator.evaluate_answer(question_text, user_answer, sample_answer, target_skill)

        # Attempt OpenAI / API evaluation if key present
        try:
            if self.openai_key:
                return self._call_openai(question_text, user_answer, sample_answer, target_skill)
            elif self.gemini_key:
                return self._call_gemini(question_text, user_answer, sample_answer, target_skill)
        except Exception as e:
            # Fall back gracefully if external API call fails
            res = FallbackEvaluator.evaluate_answer(question_text, user_answer, sample_answer, target_skill)
            res["feedback"] += f" (API attempt fallback: {str(e)})"
            return res

        return FallbackEvaluator.evaluate_answer(question_text, user_answer, sample_answer, target_skill)

    def _call_openai(self, question, answer, sample, skill):
        prompt = f"""You are an expert technical interviewer evaluating an answer.
Question: {question}
Candidate Answer: {answer}
Skill Context: {skill or 'General'}

Respond strictly with valid JSON format containing:
{{
    "relevance_score": float (0-100),
    "technical_score": float (0-100),
    "completeness_score": float (0-100),
    "clarity_score": float (0-100),
    "overall_score": float (0-100),
    "feedback": "constructive text feedback"
}}"""
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            parsed = json.loads(content)
            parsed["is_demo_mode"] = False
            return parsed
        raise Exception(f"OpenAI API status {resp.status_code}")

    def _call_gemini(self, question, answer, sample, skill):
        # Gemini REST call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = f"Evaluate this interview answer for Question: '{question}' and Answer: '{answer}'. Return JSON with keys relevance_score, technical_score, completeness_score, clarity_score, overall_score, feedback."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            txt = resp.json()['candidates'][0]['content']['parts'][0]['text']
            clean_json = txt.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            parsed["is_demo_mode"] = False
            return parsed
        raise Exception(f"Gemini API status {resp.status_code}")
