import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FallbackEvaluator:
    @staticmethod
    def evaluate_answer(question_text, user_answer, sample_answer=None, target_skill=None):
        """
        Deterministic answer evaluator based on length, keyword coverage, 
        and TF-IDF cosine similarity against sample answer / question context.
        """
        if not user_answer or not user_answer.strip():
            return {
                "relevance_score": 0.0,
                "technical_score": 0.0,
                "completeness_score": 0.0,
                "clarity_score": 0.0,
                "overall_score": 0.0,
                "feedback": "No answer provided. Please articulate your thoughts to receive feedback.",
                "is_demo_mode": True
            }

        answer_clean = user_answer.strip()
        word_count = len(answer_clean.split())

        # 1. Clarity & Length Score (Base metric)
        if word_count < 10:
            clarity_score = 40.0
            length_feedback = "Answer is too brief. Provide more technical details and practical context."
        elif word_count < 30:
            clarity_score = 70.0
            length_feedback = "Good response length, but expanding with specific code examples or methodologies would strengthen your answer."
        else:
            clarity_score = 90.0
            length_feedback = "Strong articulation and thorough response structure."

        # 2. Relevance Score (TF-IDF Cosine Similarity)
        ref_text = (question_text + " " + (sample_answer or ""))
        relevance_score = 70.0
        try:
            vectorizer = TfidfVectorizer().fit_transform([ref_text, answer_clean])
            vectors = vectorizer.toarray()
            sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            relevance_score = min(round(float(sim * 100) + 40.0, 1), 98.0)
        except Exception:
            relevance_score = 75.0

        # 3. Technical Score (Skill / Keyword coverage)
        technical_score = 70.0
        keywords_found = []
        if target_skill and target_skill.lower() in answer_clean.lower():
            technical_score += 15.0
            keywords_found.append(target_skill)

        # Technical terms heuristic check
        tech_terms = ["architecture", "performance", "database", "api", "function", "class", "design", "scale", "security", "async", "cache", "query", "testing"]
        for term in tech_terms:
            if term in answer_clean.lower():
                technical_score += 3.0
                keywords_found.append(term)

        technical_score = min(round(technical_score, 1), 95.0)

        # 4. Completeness Score
        completeness_score = min(round((clarity_score * 0.4) + (relevance_score * 0.6), 1), 96.0)

        # 5. Overall Score
        overall_score = round(
            (technical_score * 0.35) + 
            (relevance_score * 0.30) + 
            (completeness_score * 0.20) + 
            (clarity_score * 0.15), 1
        )

        # Build constructive feedback string
        feedback_lines = [
            f"[DEMO/FALLBACK EVALUATOR]: Answer received ({word_count} words).",
            length_feedback,
        ]
        if keywords_found:
            feedback_lines.append(f"Key technical terms identified: {', '.join(keywords_found[:5])}.")
        else:
            feedback_lines.append("Try incorporating specific framework or domain terminology into your response.")

        return {
            "relevance_score": relevance_score,
            "technical_score": technical_score,
            "completeness_score": completeness_score,
            "clarity_score": clarity_score,
            "overall_score": overall_score,
            "feedback": " ".join(feedback_lines),
            "is_demo_mode": True
        }
