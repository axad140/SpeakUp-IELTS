import os
import sys
import io
import json
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

# Ensure Unicode logs from imported modules don't crash on Windows cp1252 consoles.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ==============================================================
# CORE NLP IMPORTS - PROFESSIONAL UNIFIED ENGINE
# ==============================================================
from utils.professional_nlp_engine import (
    build_dynamic_report,
    build_question_metadata,
    get_professional_judgment,
)

# PRETRAINED REPLACEMENTS (No APIs used)
from utils.local_interviewer import local_examiner
from utils.pretrained_cv import cv_analyzer
from utils.body_language_analysis import body_language_analyzer

app = Flask(__name__, static_folder='../frontend/frontend/dist', static_url_path='')
app.secret_key = 'interview-insight-secret-key'

# In-memory database for sessions
active_sessions = {}

# ==============================================================
# FRONTEND STATIC SERVING (VITE SPA ROUTING)
# ==============================================================
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# ==============================================================
# API ROUTES (INTEGRATED FOR THE NEW VITE FRONTEND)
# ==============================================================

@app.route('/api/interview/session/start', methods=['POST'])
def start_session():
    data = request.json
    sid = data.get('session_id')
    active_sessions[sid] = {
        "info": data,
        "responses": [],
        "cv_frames": []
    }
    return jsonify({"success": True})

@app.route('/api/interview/questions', methods=['POST'])
def get_questions():
    data = request.json
    num = data.get('num', 6)
    questions = []
    
    # Generate completely local offline questions dynamically using Pre-Trained model
    for i in range(num):
        part = 1 if i < 2 else (2 if i < 4 else 3)
        field = data.get('field', 'general')
        category = data.get('category', 'general')
        context = f"IELTS speaking part {part}. Question: {i + 1}. Field: {field}. Category: {category}."
        generated_q = local_examiner.generate_question(context)
        metadata = build_question_metadata(generated_q, part=part, field=field, category=category)
        
        questions.append({
            "id": i + 1,
            "question": generated_q,
            "part": part,
            "field": field,
            "category": category,
            "keywords": metadata["keywords"],
            "tips": metadata["tips"],
            "duration": metadata["duration"]
        })
        
    return jsonify({"success": True, "questions": questions})

@app.route('/api/analyze/frame', methods=['POST'])
def analyze_frame():
    data = request.json
    sid = data.get('session_id')
    b64_frame = data.get('frame')
    
    cv_result = cv_analyzer.analyze_frame(b64_frame)
    if sid in active_sessions:
        active_sessions[sid]['cv_frames'].append(cv_result)
        
    return jsonify({"success": True, "result": cv_result})

@app.route('/api/analyze/answer', methods=['POST'])
def analyze_answer():
    data = request.json
    answer = data.get('answer', '')
    question = data.get('question', '')
    sid = data.get('session_id')
    context = {
        "field": data.get("field", ""),
        "category": data.get("category", ""),
        "part": data.get("part", ""),
        "keywords": data.get("keywords", []),
    }
    
    # 1. CORE NLP PIPELINE - USING PROFESSIONAL UNIFIED ENGINE
    report = get_professional_judgment(question, answer, context=context)
    
    if report.get("status") != "success":
        return jsonify({"success": False, "error": report.get("error")})

    # Extract data from unified report
    grammar_data = report['grammar']
    lexical_data = report['lexical']
    coherence_data = report['coherence']
    fluency_data = report['fluency']
    judgment_data = report['judgment']
    band_result = report['overall_band']

    # 2. LOCAL OFFLINE RESPONSE GENERATION
    interviewer_report = report['interviewer_report']
    
    # 3. SCORE AGGREGATION
    overall_band = band_result['band']

    # 4. CV SNAPSHOT LINKED TO THIS SESSION
    session = active_sessions.get(sid, {})
    session_frames = session.get('cv_frames', [])
    latest_cv = session_frames[-1] if session_frames else {}
    avg_cv_confidence = round(
        sum(frame.get('confidence_score', 70) for frame in session_frames) / len(session_frames)
    ) if session_frames else 70
    pronunciation_band = round(max(4.0, min(9.0, avg_cv_confidence / 11.5)), 1)

    # 5. NLP-DRIVEN FEEDBACK STRINGS
    feedback = report.get("feedback", {})
    vocab_feedback = feedback.get("lr", "")
    fluency_feedback = feedback.get("fc", "")
    grammar_feedback = feedback.get("gra", "")

    pronunciation_feedback = latest_cv.get('guidance') or (
        f"Presentation confidence is estimated at {avg_cv_confidence}%. "
        "Camera evidence was limited for this answer." if not session_frames
        else f"Presentation confidence is estimated at {avg_cv_confidence}% from live camera frames."
    )
    model_answer = local_examiner.generate_model_answer(question=question, candidate_answer=answer)
    strengths = report.get("strengths", [])
    improvements = report.get("improvements", [])
    grammar_errors = grammar_data.get("errors", [])
    
    # Bundle exactly to Vite Frontend API contract
    analysis_packet = {
        "success": True,
        "answer": answer,
        "overall_band": overall_band,
        "band_label": band_result['label'],
        "analysis_confidence": report.get("analysis_confidence", band_result.get("confidence")),
        "model_status": report.get("model_status", {}),
        "bands": {
            "overall": overall_band,
            "fc": band_result['breakdown']['fluency_coherence'],
            "lr": band_result['breakdown']['lexical_resource'],
            "gra": band_result['breakdown']['grammatical_range'],
            "p": pronunciation_band
        },
        "nlp": {
            "grammar_score": grammar_data['accuracy_percentage'],
            "vocab_score": lexical_data['score'] * 10,
            "fluency_score": fluency_data['score'] * 10,
            "word_count": lexical_data['word_count'],
            "vocabulary_level": lexical_data.get("level") or _score_level(lexical_data['score']),
            "fluency_level": _score_level(fluency_data['score']),
            "complexity_level": _score_level(coherence_data['score']),
            "advanced_words": lexical_data.get("advanced_words", lexical_data.get("idioms_found", [])),
            "filler_count": fluency_data['filler_count'],
            "total_markers": coherence_data.get('discourse_markers_found', 0),
            "grammar_errors": grammar_data['estimated_errors'],
            "semantic_relevance": judgment_data.get("semantic_relevance"),
            "relevance_score": judgment_data.get("relevance_score"),
            "confidence": judgment_data.get("confidence")
        },
        "cv_snapshot": {
            "avg_confidence": avg_cv_confidence,
            "frames_analyzed": len(session_frames)
        },
        "body_language": latest_cv.get("body_language") if session_frames else None,
        "ai": {
            "ai_powered": True,
            "fc_feedback": fluency_feedback,
            "lr_feedback": vocab_feedback,
            "gra_feedback": grammar_feedback,
            "p_feedback": pronunciation_feedback,
            "strengths": strengths,
            "improvements": improvements,
            "corrected_answer": grammar_data['corrected_text'],
            "model_answer": model_answer,
            "interviewer_report": interviewer_report,
            "grammar_errors": grammar_errors
        }
    }
    return jsonify(analysis_packet)

@app.route('/api/transcribe/audio', methods=['POST'])
def transcribe_audio():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"success": False, "error": "No audio file uploaded"}), 400

    from utils.speech_transcription import transcribe_audio_from_file

    result = transcribe_audio_from_file(audio_file)
    if result.get("error"):
        return jsonify({
            "success": False,
            "text": result.get("text", ""),
            "error": result.get("error"),
        }), 500

    return jsonify({
        "success": True,
        "text": result.get("text", ""),
        "confidence": result.get("confidence", 0),
        "language": result.get("language", "en"),
        "processing_time": result.get("processing_time"),
    })

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    data = request.json or {}
    responses = data.get("responses", [])
    report = build_dynamic_report(
        responses=responses,
        cv=data.get("cv", {}),
        name=data.get("name", "Candidate"),
        field=data.get("field", "General"),
        category=data.get("category", "general"),
    )
    return jsonify({"success": True, "report": report})

@app.route('/api/report/pdf', methods=['POST'])
def report_pdf():
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"PDF generation requires reportlab: {exc}"
        }), 500

    payload = request.json or {}
    report = payload.get("report") or {}
    meta = report.get("meta", {})
    overall = report.get("overall", {})
    ai_report = report.get("ai_report", {})
    questions = report.get("questions", [])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="IELTS Speaking Report",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#16213e"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1f3b73"),
        spaceBefore=12,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="SmallMuted",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#555555"),
        fontSize=9,
        leading=12,
    ))

    def text(value, fallback=""):
        if value is None:
            return fallback
        return str(value).replace("\n", "<br/>")

    story = [
        Paragraph("IELTS Speaking Report", styles["ReportTitle"]),
        Paragraph(
            f"{text(meta.get('name'), 'Candidate')} | {text(meta.get('field'), 'General')} | "
            f"{text(meta.get('date'))} {text(meta.get('time'))}",
            styles["SmallMuted"],
        ),
        Spacer(1, 12),
    ]

    score_data = [
        ["Overall Band", text(overall.get("band"), "N/A")],
        ["Level", text(overall.get("label"), "N/A")],
        ["Fluency & Coherence", text(overall.get("fc"), "N/A")],
        ["Lexical Resource", text(overall.get("lr"), "N/A")],
        ["Grammar & Accuracy", text(overall.get("gra"), "N/A")],
        ["Pronunciation", text(overall.get("p"), "N/A")],
    ]
    score_table = Table(score_data, colWidths=[2.2 * inch, 4.0 * inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0a500")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([score_table, Spacer(1, 12)])

    if ai_report.get("summary"):
        story.extend([
            Paragraph("AI Assessment", styles["SectionTitle"]),
            Paragraph(text(ai_report.get("summary")), styles["BodyText"]),
        ])

    for title, key in [
        ("Key Strengths", "top_strengths"),
        ("Priority Improvements", "critical_improvements"),
    ]:
        items = ai_report.get(key) or []
        if items:
            story.append(Paragraph(title, styles["SectionTitle"]))
            for item in items[:6]:
                story.append(Paragraph(f"- {text(item)}", styles["BodyText"]))

    if ai_report.get("study_plan"):
        story.append(Paragraph("Study Plan", styles["SectionTitle"]))
        for week in ai_report["study_plan"][:4]:
            tasks = ", ".join(text(task) for task in week.get("daily_tasks", [])[:3])
            story.append(Paragraph(
                f"Week {text(week.get('week'))}: <b>{text(week.get('theme'))}</b> - {tasks}",
                styles["BodyText"],
            ))

    if questions:
        story.append(Paragraph("Question Breakdown", styles["SectionTitle"]))
        for question in questions:
            story.extend([
                Paragraph(
                    f"Q{text(question.get('num'))} | Band {text(question.get('band'), 'N/A')}: "
                    f"{text(question.get('question'))}",
                    styles["Heading3"],
                ),
                Paragraph(f"<b>Your answer:</b> {text(question.get('answer'))}", styles["BodyText"]),
            ])
            improvements = question.get("improvements") or []
            if improvements:
                story.append(Paragraph(
                    f"<b>Improve:</b> {text('; '.join(improvements[:3]))}",
                    styles["SmallMuted"],
                ))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    filename = f"IELTS_Report_{meta.get('name', 'Candidate')}.pdf".replace(" ", "_")
    return app.response_class(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.route('/api/analyze/cv-summary/<sid>', methods=['GET'])
def get_cv_summary(sid):
    if sid not in active_sessions or not active_sessions[sid]['cv_frames']:
        return jsonify({"success": True, "cv": {"avg_confidence": 55, "frames_analyzed": 0, "dominant_emotion": "neutral"}})
    
    frames = active_sessions[sid]['cv_frames']
    count = len(frames)
    good_eye = sum(1 for f in frames if f.get('eye_contact'))
    confidence_values = [f.get('confidence_score', 55) for f in frames]
    emotion_counts = {}
    for frame in frames:
        emotion = frame.get("emotion", "neutral")
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    def avg_from(path, default=55):
        values = []
        for frame in frames:
            value = frame
            for key in path:
                value = value.get(key, {}) if isinstance(value, dict) else {}
            if isinstance(value, (int, float)):
                values.append(value)
        return round(sum(values) / len(values)) if values else default

    dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
    emotion_percentages = {
        emotion: round(total / count * 100, 1)
        for emotion, total in sorted(emotion_counts.items(), key=lambda item: item[1], reverse=True)
    }
    
    return jsonify({
        "success": True, 
        "cv": {
            "avg_confidence": round(sum(confidence_values) / count),
            "eye_contact_rate": round(good_eye / count * 100),
            "dominant_emotion": dominant_emotion,
            "emotion_percentages": emotion_percentages,
            "presentation_score": avg_from(["presentation", "presentation_score"]),
            "framing_score": avg_from(["frame_quality", "framing_score"]),
            "lighting_score": avg_from(["frame_quality", "lighting_score"]),
            "movement_stability": avg_from(["movement", "stability_score"]),
            "posture_score": avg_from(["posture", "posture_score"]),
            "head_position_score": avg_from(["head_position", "head_score"]),
            "engagement_score": avg_from(["engagement", "engagement_score"]),
            "feedback": body_language_analyzer.get_session_summary().get("feedback", []),
            "frames_analyzed": count
        }
    })

@app.route('/api/interview/session/<sid>/response', methods=['POST'])
def save_response(sid):
    if sid in active_sessions:
        active_sessions[sid]['responses'].append(request.json)
    return jsonify({"success": True})

@app.route('/api/interview/session/<sid>/end', methods=['POST'])
def end_session(sid):
    return jsonify({"success": True})

@app.route('/api/analyze/body-language-summary/<sid>', methods=['GET'])
def get_body_language_summary(sid):
    summary = body_language_analyzer.get_session_summary()
    recommendations = []
    if summary['average_posture'] < 65:
        recommendations.append("Work on maintaining better posture - sit upright with shoulders back.")
    if summary['average_engagement'] < 60:
        recommendations.append("Improve engagement - show more facial expression and open your eyes wider.")
    if summary['average_confidence'] < 60:
        recommendations.append("Build confidence - maintain eye contact and speak with authority.")
    if summary['average_head_position'] < 65:
        recommendations.append("Keep your head level - avoid tilting or turning to the side.")
    if summary.get('average_movement_stability', 70) < 60:
        recommendations.append("Reduce fidgeting and keep your movement controlled while answering.")
    if summary.get('average_framing', 70) < 60:
        recommendations.append("Improve camera framing - keep face and shoulders centered.")
    if summary.get('average_lighting', 70) < 60:
        recommendations.append("Improve lighting so facial expressions are clearly visible.")
    if summary.get('average_presentation', 70) < 60:
        recommendations.append("Keep clothing, background, and visible presentation simple and professional.")
    
    if not recommendations:
        recommendations = ["Excellent body language throughout the interview! Keep up this performance."]
    
    return jsonify({
        "success": True,
        "body_language_summary": {
            **summary,
            "recommendations": recommendations,
            "interpretation": {
                "overall_body_language_band": summary.get('body_language_band', 5.0),
                "band_description": _get_band_description(summary.get('body_language_band', 5.0)),
                "strengths": _get_body_language_strengths(summary),
                "areas_for_improvement": _get_body_language_improvements(summary)
            }
        }
    })

@app.route('/api/analyze/gesture-frequency/<sid>', methods=['GET'])
def get_gesture_analysis(sid):
    if sid not in active_sessions or not active_sessions[sid]['cv_frames']:
        return jsonify({
            "success": True,
            "gesture_analysis": {
                "overall_movement": "moderate",
                "gesture_variety": "good",
                "fidgeting_level": "low",
                "confidence_indicators": "positive"
            }
        })
    
    frames = active_sessions[sid]['cv_frames']
    overall_confidence_scores = [f.get('overall_score', 70) for f in frames]
    avg_confidence = sum(overall_confidence_scores) / len(overall_confidence_scores) if overall_confidence_scores else 70
    
    return jsonify({
        "success": True,
        "gesture_analysis": {
            "frames_analyzed": len(frames),
            "average_confidence_score": round(avg_confidence),
            "confidence_trend": _get_trend(overall_confidence_scores),
            "overall_movement": "natural" if avg_confidence > 70 else "needs_work",
            "gesture_variety": "good" if len(frames) > 3 else "limited",
            "fidgeting_level": "low" if avg_confidence > 65 else "moderate",
            "confidence_indicators": "positive" if avg_confidence > 70 else "neutral"
        }
    })

def _get_trend(scores):
    if len(scores) < 2:
        return "stable"
    first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2) if len(scores) > 1 else scores[0]
    second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2) if len(scores) > 1 else scores[-1]
    if second_half_avg > first_half_avg + 5:
        return "improving"
    elif first_half_avg > second_half_avg + 5:
        return "declining"
    else:
        return "stable"

def _score_level(score):
    if score >= 8:
        return "Excellent"
    if score >= 7:
        return "Strong"
    if score >= 6:
        return "Developing"
    if score >= 5:
        return "Limited"
    return "Needs work"

def _get_band_description(band):
    if band >= 8:
        return "Excellent - Professional, confident, and engaging presentation"
    elif band >= 7:
        return "Good - Solid body language with minor areas for improvement"
    elif band >= 6:
        return "Acceptable - Generally good but needs some refinement"
    elif band >= 5:
        return "Moderate - Fair body language with several areas to work on"
    else:
        return "Needs Improvement - Focus on posture, eye contact, and engagement"

def _get_body_language_strengths(summary):
    strengths = []
    if summary['average_posture'] >= 75:
        strengths.append("Excellent posture and spinal alignment")
    if summary['average_engagement'] >= 75:
        strengths.append("High engagement and eye contact")
    if summary['average_confidence'] >= 75:
        strengths.append("Confident and professional demeanor")
    if summary['average_head_position'] >= 75:
        strengths.append("Well-maintained head position")
    if summary.get('average_movement_stability', 0) >= 75:
        strengths.append("Controlled movement with low fidgeting")
    if summary.get('average_framing', 0) >= 75:
        strengths.append("Professional camera framing")
    if summary.get('average_presentation', 0) >= 75:
        strengths.append("Professional visible presentation")
    return strengths if strengths else ["Consistent body language throughout"]

def _get_body_language_improvements(summary):
    improvements = []
    if summary['average_posture'] < 65:
        improvements.append("Improve posture - sit upright")
    if summary['average_engagement'] < 65:
        improvements.append("Increase engagement - show more facial expression")
    if summary['average_confidence'] < 65:
        improvements.append("Build confidence - strengthen eye contact")
    if summary['average_head_position'] < 65:
        improvements.append("Stabilize head position - reduce tilting")
    if summary.get('average_movement_stability', 70) < 65:
        improvements.append("Reduce fidgeting and keep gestures controlled")
    if summary.get('average_framing', 70) < 65:
        improvements.append("Center your face and shoulders in the frame")
    if summary.get('average_lighting', 70) < 65:
        improvements.append("Improve lighting for clearer facial visibility")
    if summary.get('average_presentation', 70) < 65:
        improvements.append("Use simpler, more interview-appropriate visual presentation")
    return improvements if improvements else ["Continue with current body language"]

if __name__ == '__main__':
    from config import PORT, HOST, DEBUG_MODE
    print(f"Starting Integrated Interview Dashboard on port {PORT}")
    app.run(debug=DEBUG_MODE, host=HOST, port=PORT)
