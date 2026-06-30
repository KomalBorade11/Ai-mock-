from typing import Dict
from utils import analyze_resume, generate_questions, evaluate_answer, load_datasets

def analyze_node(state: Dict) -> Dict:
    """Analyze resume and extract skills."""
    try:
        if state.get("resume_text") and len(state["resume_text"].strip()) > 0:
            analysis = analyze_resume(state["resume_text"])
            state["analysis"] = analysis
        else:
            state["analysis"] = {"skills": ["Not provided"], "projects": [], "experience": ""}
    except Exception as e:
        print(f"Error in analyze_node: {e}")
        state["analysis"] = {"skills": ["General"], "projects": [], "experience": ""}
    return state

def question_node(state: Dict) -> Dict:
    """Generate questions based on role."""
    try:
        questions_df, _, kaggle_df = load_datasets()
        role = state.get("role", "")
        analysis = state.get("analysis", {})
        
        questions = generate_questions(role, analysis, questions_df, kaggle_df)
        state["questions"] = questions if questions else ["Tell us about yourself", "What are your strengths?", "Describe a challenge", "Why this role?", "Your experience?"]
        state["current_question_index"] = 0
    except Exception as e:
        print(f"Error in question_node: {e}")
        state["questions"] = ["Tell us about yourself", "What are your strengths?", "Describe a challenge", "Why this role?", "Your experience?"]
        state["current_question_index"] = 0
    return state

def evaluate_node(state: Dict) -> Dict:
    """Evaluate answer against reference."""
    try:
        if state["current_question_index"] >= len(state["questions"]):
            return state
        
        _, answers_df, kaggle_df = load_datasets()
        question = state["questions"][state["current_question_index"]]
        
        if not state["answers"] or len(state["answers"]) == 0:
            return state
        
        user_answer = state["answers"][-1]
        
        # Find reference answer from answers_df first
        ref_answer_rows = answers_df[answers_df['question'] == question]
        reference = ref_answer_rows['answer'].iloc[0] if not ref_answer_rows.empty else None
        
        # If not found in answers_df, try kaggle_df
        if not reference and not kaggle_df.empty:
            kaggle_rows = kaggle_df[kaggle_df['Question'] == question]
            reference = kaggle_rows['Answer'].iloc[0] if not kaggle_rows.empty else "No reference available"
        
        if not reference:
            reference = "No reference available"
        
        feedback = evaluate_answer(question, user_answer, reference)
        
        # Ensure feedbacks list is initialized
        if "feedbacks" not in state:
            state["feedbacks"] = []
        
        state["feedbacks"].append(feedback)
        state["total_score"] += int(feedback.get("score", 5))
        state["current_question_index"] += 1
    except Exception as e:
        print(f"Error in evaluate_node: {e}")
        # Add default feedback on error
        state["feedbacks"].append({"score": 6, "feedback": "Unable to evaluate", "strengths": "Participation", "weaknesses": "Technical evaluation"})
        state["total_score"] += 6
        state["current_question_index"] += 1
    
    return state