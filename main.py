from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from pathlib import Path
import shutil
from graph import analyze_node, question_node, evaluate_node
from utils import extract_resume_text, transcribe_audio, generate_first_question, interviewer_agent, generate_final_feedback

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}})

# In-memory session storage (for demo, use database in production)
sessions = {}

def error_response(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    """Upload PDF resume and extract text."""
    try:
        file = request.files.get("file")
        if not file:
            return error_response("No resume file provided", 400)

        filename = file.filename or "resume.pdf"
        if not filename.lower().endswith('.pdf'):
            return error_response("Only PDF files allowed", 400)

        temp_path = BASE_DIR / f"temp_{time.time_ns()}.pdf"
        file.save(temp_path)

        resume_text = extract_resume_text(str(temp_path))
        os.remove(temp_path)

        if not resume_text or not resume_text.strip():
            return error_response("Could not extract text from PDF", 400)

        session_id = str(time.time())
        sessions[session_id] = {
            "resume_text": resume_text,
            "role": "",
            "level": "",
            "chat_history": [],
            "history": [],
            "last_question": "",
            "answers": [],
            "questions": [],
            "current_question_index": 0,
            "feedbacks": [],
            "total_score": 0,
            "start_time": 0,
            "end_time": 0,
            "interview_completed": False,
            "current_topic": "",
            "question_count": 0,
            "max_questions": 10,
            "analysis": {}
        }

        return jsonify({"session_id": session_id, "resume_text": resume_text[:300] + "..."})
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@app.route("/start_interview", methods=["POST"])
def start_interview():
    """Start interview with role."""
    try:
        session_id = request.form.get("session_id")
        role = request.form.get("role")

        if not session_id or session_id not in sessions:
            return error_response("Session not found", 404)
        if not role or not role.strip():
            return error_response("Role is required", 400)

        state = sessions[session_id]
        state["role"] = role
        state["start_time"] = time.time()

        state = analyze_node(state)
        state = question_node(state)

        if state.get("questions"):
            first_question = state["questions"][0]
        else:
            first_question = generate_first_question(role, state["analysis"])
            state["questions"] = [first_question]

        state["chat_history"].append({
            "type": "question",
            "content": first_question,
            "timestamp": time.time(),
            "question_number": 1
        })
        state["last_question"] = first_question
        state["level"] = state["analysis"].get("experience", "")
        state["current_topic"] = state["analysis"].get("domain", "introduction")
        state["question_count"] = 1
        state["current_question_index"] = 0
        sessions[session_id] = state

        return jsonify({
            "success": True,
            "chat_history": state["chat_history"],
            "current_question": first_question
        })
    except Exception as e:
        return error_response(f"Error starting interview: {str(e)}", 500)


@app.route("/process_transcript", methods=["POST"])
def process_transcript():
    """Process real-time transcript from speech recognition."""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get("session_id")
        answer = str(data.get("answer", data.get("transcript", ""))).strip()

        if not session_id or session_id not in sessions:
            return error_response("Invalid session", 400)
        if not answer:
            return error_response("No answer provided", 400)

        state = sessions[session_id]

        elapsed = time.time() - state["start_time"]
        if elapsed > 1800:
            state["interview_completed"] = True
            sessions[session_id] = state
            return jsonify({
                "completed": True,
                "message": "Interview time completed (30 minutes)",
                "final_feedback": generate_final_feedback(state["chat_history"], state["role"])
            })

        if state["question_count"] >= state.get("max_questions", 10):
            state["interview_completed"] = True
            state["end_time"] = time.time()
            sessions[session_id] = state
            return jsonify({
                "completed": True,
                "message": "Interview completed successfully",
                "final_feedback": generate_final_feedback(state["chat_history"], state["role"])
            })

        state["answers"].append(answer)
        state["chat_history"].append({
            "type": "answer",
            "content": answer,
            "timestamp": time.time()
        })

        last_question = state.get("last_question", "")
        state["history"].append({
            "question": last_question,
            "answer": answer
        })

        next_question = interviewer_agent(
            state["role"],
            state["history"],
            answer,
            state.get("analysis", {})
        )

        if not next_question:
            next_question = "Can you walk me through that in more detail?"

        state["chat_history"].append({
            "type": "question",
            "content": next_question,
            "timestamp": time.time(),
            "question_number": state["question_count"] + 1
        })
        state["last_question"] = next_question
        state["question_count"] += 1

        sessions[session_id] = state
        return jsonify({"next_question": next_question})
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")
        return error_response(f"Processing error: {str(e)}", 500)


@app.route("/end_interview_early", methods=["POST"])
def end_interview_early():
    """End interview early and provide feedback."""
    try:
        session_id = request.form.get("session_id")
        if not session_id or session_id not in sessions:
            return error_response("Session not found", 404)

        state = sessions[session_id]
        state["interview_completed"] = True
        state["end_time"] = time.time()

        feedback = generate_final_feedback(state["chat_history"], state["role"])
        state["chat_history"].append({
            "type": "feedback",
            "content": feedback,
            "timestamp": time.time()
        })
        sessions[session_id] = state

        return jsonify({
            "completed": True,
            "message": "Interview ended early",
            "chat_history": state["chat_history"],
            "feedback": feedback
        })
    except Exception as e:
        return error_response(f"Error ending interview: {str(e)}", 500)


@app.route("/get_chat_history", methods=["GET"])
def get_chat_history():
    """Get current chat history."""
    try:
        session_id = request.args.get("session_id")
        if not session_id or session_id not in sessions:
            return error_response("Session not found", 404)

        state = sessions[session_id]
        return jsonify({"chat_history": state["chat_history"]})
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@app.route("/end_interview", methods=["POST"])
def end_interview():
    """End interview and get final feedback."""
    try:
        session_id = request.form.get("session_id")
        if not session_id or session_id not in sessions:
            return error_response("Session not found", 404)

        state = sessions[session_id]
        state["end_time"] = time.time()

        if not any(item["type"] == "feedback" for item in state["chat_history"]):
            feedback = generate_final_feedback(state["chat_history"], state["role"])
            state["chat_history"].append({
                "type": "feedback",
                "content": feedback,
                "timestamp": time.time()
            })

        final_feedback = state["chat_history"][-1]["content"] if state["chat_history"] and state["chat_history"][-1]["type"] == "feedback" else "Interview completed"
        del sessions[session_id]

        return jsonify({
            "completed": True,
            "chat_history": state["chat_history"],
            "final_feedback": final_feedback
        })
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    if (FRONTEND_DIR / path).exists():
        return app.send_static_file(path)
    return app.send_static_file('index.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True)