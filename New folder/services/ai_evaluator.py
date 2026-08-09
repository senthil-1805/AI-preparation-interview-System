from services.ai_service import AIService

class AIEvaluator:
    def __init__(self):
        self.ai_service = AIService()

    def evaluate(self, question_text, user_answer, sample_answer=None, target_skill=None):
        return self.ai_service.evaluate_answer(question_text, user_answer, sample_answer, target_skill)
