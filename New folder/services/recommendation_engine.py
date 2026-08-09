class RecommendationEngine:
    @staticmethod
    def generate_recommendations(interview_score, missing_skills):
        """
        Generate list of recommended study topics and action items based on scores and missing skills.
        """
        recs = []

        # 1. Skill Gap Recommendations
        if missing_skills:
            top_missing = missing_skills[:3]
            for skill in top_missing:
                recs.append({
                    "topic": f"Master {skill}",
                    "action_item": f"Build a practical mini-project utilizing {skill} to bridge your target role gap."
                })

        # 2. Score-based Recommendations
        if interview_score.technical_score < 75:
            recs.append({
                "topic": "Technical Fundamentals & Code Patterns",
                "action_item": "Review core algorithm structures, data types, and framework paradigms to boost technical accuracy."
            })
        if interview_score.communication_score < 75:
            recs.append({
                "topic": "Structured Answer Delivery (STAR Method)",
                "action_item": "Practice structuring scenario responses with Situation, Task, Action, and Result framework."
            })
        if interview_score.relevance_score < 75:
            recs.append({
                "topic": "Domain Terminology & Concise Messaging",
                "action_item": "Focus directly on addressing prompt constraints with concise industry-standard nomenclature."
            })

        # Default fallback recommendation if high score
        if not recs:
            recs.append({
                "topic": "Advanced System Design & Microservices",
                "action_item": "Explore distributed caching, load balancing, and high-throughput architectural patterns."
            })

        return recs
