from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.resume import Resume
from models.skill import UserSkill, Skill
from models.job_role import JobRole, JobRoleSkill
from models.interview import Interview
from models.score import InterviewScore
from models.recommendation import Recommendation
from services.skill_gap import SkillGapAnalyzer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user = current_user
    latest_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    
    # Extract structured metrics if resume present
    structured = latest_resume.get_structured_data() if latest_resume else {}
    completeness_score = structured.get("completeness_score", 0.0) if latest_resume else 0.0
    experience_count = len(structured.get("experience", []))
    projects_count = len(structured.get("projects", []))
    education_count = len(structured.get("education", []))
    certifications_count = len(structured.get("certifications", []))

    # Target Job Role & Skills
    target_role = user.target_role
    user_skills = [us.skill.name for us in user.skills.all() if us.skill]
    
    required_skills = []
    if target_role:
        required_skills = [jrs.skill.name for jrs in target_role.role_skills if jrs.skill]

    # Skill Gap analysis
    gap_result = SkillGapAnalyzer.analyze_gap(user_skills, required_skills)
    
    # Interview Statistics
    user_interviews = Interview.query.filter_by(user_id=user.id, status='completed').order_by(Interview.created_at.desc()).all()
    total_interviews = len(user_interviews)
    
    scores = []
    for inv in user_interviews:
        if inv.scores:
            scores.append(inv.scores.overall_score)
            
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    best_score = round(max(scores), 1) if scores else 0.0

    recent_interviews = user_interviews[:5]
    recommendations = Recommendation.query.filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).limit(5).all()

    # Chart Data formatting
    score_trend_labels = [inv.created_at.strftime("%b %d") for inv in reversed(user_interviews[:7])]
    score_trend_data = [inv.scores.overall_score for inv in reversed(user_interviews[:7]) if inv.scores]

    skill_coverage_chart = {
        "matching": len(gap_result["matching_skills"]),
        "missing": len(gap_result["missing_skills"])
    }

    return render_template(
        'dashboard.html',
        latest_resume=latest_resume,
        structured=structured,
        completeness_score=completeness_score,
        experience_count=experience_count,
        projects_count=projects_count,
        education_count=education_count,
        certifications_count=certifications_count,
        target_role=target_role,
        user_skills=user_skills,
        gap_result=gap_result,
        total_interviews=total_interviews,
        avg_score=avg_score,
        best_score=best_score,
        recent_interviews=recent_interviews,
        recommendations=recommendations,
        score_trend_labels=score_trend_labels,
        score_trend_data=score_trend_data,
        skill_coverage_chart=skill_coverage_chart
    )
