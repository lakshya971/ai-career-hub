import re
from src.llm import generate_answer

def run_generate_questions(resume_text):
    prompt = """
    You are a technical recruiter. Based on the candidate's resume, generate exactly 3 challenging technical or situational interview questions that directly test the candidate on the skills, technologies, projects, and experiences they have listed.
    
    Output the questions strictly in the following format:
    QUESTION 1: <question content>
    QUESTION 2: <question content>
    QUESTION 3: <question content>
    
    Do not add any other intro/outro text.
    """
    
    response = generate_answer(resume_text, prompt)
    
    questions = []
    try:
        matches = re.findall(r"QUESTION \d+:\s*(.*?)(?=QUESTION \d+:|$)", response, re.IGNORECASE | re.DOTALL)
        questions = [q.strip() for q in matches if q.strip()]
    except Exception as e:
        pass
        
    # fallback if parsing fails
    if not questions:
        questions = [
            "Can you describe one of the main technical projects listed on your resume and your specific role in it?",
            "What technical challenges did you face during your recent work experience and how did you resolve them?",
            "How do you ensure code quality and best practices in the technologies you list as your primary skills?"
        ]
        
    return questions[:3]

def run_grade_answer(resume_text, question, user_answer):
    prompt = f"""
    You are a technical interviewer evaluating a candidate's response.
    
    Question Asked:
    {question}
    
    Candidate's Answer:
    {user_answer}
    
    Evaluate the candidate's answer based on standard industry expectations and the experience context shown in their resume.
    
    Output your evaluation strictly in the following format:
    
    SCORE: <Specify a score from 1 to 10. Format: just the number, e.g., 8>
    FEEDBACK: <Write a paragraph of constructive feedback, highlighting what was good and what could be improved>
    MODEL ANSWER: <Write an example of an ideal/comprehensive response to the question using the candidate's resume context>
    """
    
    response = generate_answer(resume_text, prompt)
    
    score = 5
    feedback = ""
    model_answer = ""
    
    try:
        score_match = re.search(r"SCORE:\s*(\d+)", response, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            
        feedback_match = re.search(r"FEEDBACK:\s*(.*?)(?=\n[A-Z]|$)", response, re.IGNORECASE | re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
            
        model_match = re.search(r"MODEL ANSWER:\s*(.*)", response, re.IGNORECASE | re.DOTALL)
        if model_match:
            model_answer = model_match.group(1).strip()
    except Exception as e:
        pass
        
    return {
        "score": score,
        "feedback": feedback if feedback else "No feedback available.",
        "model_answer": model_answer if model_answer else "No model answer available.",
        "raw_response": response
    }
