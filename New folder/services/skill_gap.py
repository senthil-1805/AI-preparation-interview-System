class SkillGapAnalyzer:
    @staticmethod
    def analyze_gap(user_skill_names, required_skill_names):
        """
        Compare User Skills VS Required Job Skills.
        Returns dict containing matching_skills, missing_skills, coverage_pct.
        """
        user_skills_set = set(s.strip().lower() for s in user_skill_names)
        required_skills_set = set(s.strip().lower() for s in required_skill_names)
        
        # Original casing map
        casing_map = {s.strip().lower(): s for s in (list(user_skill_names) + list(required_skill_names))}

        matching_lower = user_skills_set.intersection(required_skills_set)
        missing_lower = required_skills_set.difference(user_skills_set)

        matching_skills = sorted([casing_map.get(s, s) for s in matching_lower])
        missing_skills = sorted([casing_map.get(s, s) for s in missing_lower])

        total_required = len(required_skill_names)
        if total_required > 0:
            coverage_pct = round((len(matching_skills) / total_required) * 100, 1)
        else:
            coverage_pct = 100.0

        return {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "total_user_skills": len(user_skill_names),
            "total_required_skills": total_required,
            "coverage_pct": min(coverage_pct, 100.0)
        }
