from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.job_role import JobRole
from models.interview import Interview
from models.question import Question
from models.answer import Answer
from models.score import InterviewScore
from models.recommendation import Recommendation, Progress
from services.question_generator import QuestionGenerator
from services.ai_evaluator import AIEvaluator
from services.recommendation_engine import RecommendationEngine
from services.skill_gap import SkillGapAnalyzer

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/start-interview', methods=['GET', 'POST'])
@login_required
def start_interview():
    target_role = current_user.target_role
    if not target_role:
        # Assign first job role if not set
        target_role = JobRole.query.first()

    if request.method == 'POST':
        role_id = request.form.get('role_id', type=int)
        if role_id:
            role = JobRole.query.get(role_id)
            if role:
                target_role = role

        # Create new Interview session
        interview = Interview(
            user_id=current_user.id,
            job_role_id=target_role.id,
            total_questions=5,
            status='in_progress'
        )
        db.session.add(interview)
        db.session.flush()

        # Generate Questions
        questions = QuestionGenerator.generate_questions_for_interview(current_user, target_role, count=5)
        for q in questions:
            # Ensure question exists in DB
            if not q.id:
                db.session.add(q)
                db.session.flush()

            answer_entry = Answer(
                interview_id=interview.id,
                question_id=q.id,
                user_answer=""
            )
            db.session.add(answer_entry)

        db.session.commit()
        return redirect(url_for('interview.conduct_interview', interview_id=interview.id))

    job_roles = JobRole.query.all()
    return render_template('start_interview.html', target_role=target_role, job_roles=job_roles)

@interview_bp.route('/interview/<int:interview_id>', methods=['GET', 'POST'])
@login_required
def conduct_interview(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id:
        flash('Unauthorized access to interview.', 'danger')
        return redirect(url_for('dashboard.index'))

    answers = Answer.query.filter_by(interview_id=interview.id).order_by(Answer.id.asc()).all()

    if request.method == 'POST':
        # Save answers from form submission
        for ans in answers:
            field_name = f"answer_{ans.id}"
            user_text = request.form.get(field_name, '')
            ans.user_answer = user_text

        db.session.commit()

        # Process & Evaluate Answers
        evaluator = AIEvaluator()
        tech_scores = []
        rel_scores = []
        comp_scores = []
        clar_scores = []
        overall_scores = []

        for ans in answers:
            eval_res = evaluator.evaluate(
                question_text=ans.question.text,
                user_answer=ans.user_answer,
                sample_answer=ans.question.sample_answer,
                target_skill=ans.question.target_skill.name if ans.question.target_skill else None
            )
            ans.relevance_score = eval_res["relevance_score"]
            ans.technical_score = eval_res["technical_score"]
            ans.completeness_score = eval_res["completeness_score"]
            ans.clarity_score = eval_res["clarity_score"]
            ans.overall_score = eval_res["overall_score"]
            ans.feedback = eval_res["feedback"]
            ans.is_evaluated = True

            tech_scores.append(eval_res["technical_score"])
            rel_scores.append(eval_res["relevance_score"])
            comp_scores.append(eval_res["completeness_score"])
            clar_scores.append(eval_res["clarity_score"])
            overall_scores.append(eval_res["overall_score"])

        # Compute aggregate scores
        avg_tech = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0.0
        avg_rel = round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else 0.0
        avg_comm = round((sum(comp_scores) + sum(clar_scores)) / (len(comp_scores) * 2), 1) if comp_scores else 0.0
        avg_overall = round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else 0.0

        status_str = "Interview Ready" if avg_overall >= 80 else ("Needs Practice" if avg_overall >= 60 else "Needs Work")

        # Save InterviewScore
        score_entry = InterviewScore(
            interview_id=interview.id,
            overall_score=avg_overall,
            technical_score=avg_tech,
            communication_score=avg_comm,
            relevance_score=avg_rel,
            status=status_str,
            strengths="Strong technical articulation on core questions." if avg_tech >= 75 else "Good effort across basic concepts.",
            weak_areas="Expand depth on complex scenario-based architectural questions." if avg_tech < 75 else "Minor formatting improvements."
        )
        db.session.add(score_entry)

        # Generate & Save Recommendations
        user_skills = [us.skill.name for us in current_user.skills.all() if us.skill]
        required_skills = [jrs.skill.name for jrs in interview.job_role.role_skills if jrs.skill] if interview.job_role else []
        gap = SkillGapAnalyzer.analyze_gap(user_skills, required_skills)

        recs = RecommendationEngine.generate_recommendations(score_entry, gap["missing_skills"])
        for r in recs:
            rec_obj = Recommendation(
                interview_id=interview.id,
                user_id=current_user.id,
                topic=r["topic"],
                action_item=r["action_item"]
            )
            db.session.add(rec_obj)

        # Save Progress Record
        prog = Progress(
            user_id=current_user.id,
            overall_score=avg_overall,
            skill_coverage_pct=gap["coverage_pct"]
        )
        db.session.add(prog)

        interview.status = 'completed'
        db.session.commit()

        flash('Mock Interview completed and evaluated successfully!', 'success')
        return redirect(url_for('interview.view_report', interview_id=interview.id))

    return render_template('interview.html', interview=interview, answers=answers)

@interview_bp.route('/report/<int:interview_id>')
@login_required
def view_report(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id:
        flash('Unauthorized access to report.', 'danger')
        return redirect(url_for('dashboard.index'))

    score = interview.scores
    answers = interview.answers
    recommendations = Recommendation.query.filter_by(interview_id=interview.id).all()

    return render_template('report.html', interview=interview, score=score, answers=answers, recommendations=recommendations)
