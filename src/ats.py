import re
from src.llm import generate_answer

def run_ats_match(resume_text, job_description):
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) reviewer and hiring manager. 
    Analyze the candidate's resume content against the provided Job Description.
    
    Job Description:
    {job_description}
    
    Output your analysis STRICTLY in the following format. Do not write any other introductory or concluding text:
    
    SCORE: <Specify a matching percentage score between 0 and 100 based on qualifications, experience, and skills match. Format: just the number, e.g., 75>
    MATCHING SKILLS: <Comma-separated list of technical/soft skills present in both the resume and the job description>
    MISSING SKILLS: <Comma-separated list of important keywords, tools, or skills present in the job description but missing/weak in the resume>
    RECOMMENDATIONS:
    - <Actionable suggestion 1 on how to improve the resume for this role>
    - <Actionable suggestion 2>
    - <Actionable suggestion 3>
    """
    
    # We call generate_answer, passing the resume text as context and our custom instructions as query.
    response = generate_answer(resume_text, prompt)
    
    # Parse the response
    score = 50  # default fallback
    matching_skills = []
    missing_skills = []
    recommendations = []
    
    try:
        score_match = re.search(r"SCORE:\s*(\d+)", response, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            
        matching_match = re.search(r"MATCHING SKILLS:\s*(.*?)(?=\n[A-Z]|$)", response, re.IGNORECASE | re.DOTALL)
        if matching_match:
            # Clean matching skills (splitting by commas or newlines if any)
            raw_match = matching_match.group(1).replace("\n", ",")
            matching_skills = [s.strip().lstrip("-* ").strip() for s in raw_match.split(",") if s.strip()]
            
        missing_match = re.search(r"MISSING SKILLS:\s*(.*?)(?=\n[A-Z]|$)", response, re.IGNORECASE | re.DOTALL)
        if missing_match:
            raw_missing = missing_match.group(1).replace("\n", ",")
            missing_skills = [s.strip().lstrip("-* ").strip() for s in raw_missing.split(",") if s.strip()]
            
        rec_match = re.search(r"RECOMMENDATIONS:\s*(.*)", response, re.IGNORECASE | re.DOTALL)
        if rec_match:
            recs_text = rec_match.group(1).strip()
            recommendations = [line.strip().lstrip("-* ").strip() for line in recs_text.split("\n") if line.strip()]
    except Exception as e:
        pass
        
    return {
        "score": score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "raw_response": response
    }
