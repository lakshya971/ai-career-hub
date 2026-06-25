from src.llm import generate_answer

def run_cover_letter_generation(resume_text, job_description, tone):
    prompt = f"""
    You are a professional career advisor. Write a customized, compelling cover letter for the candidate applying to the job described below.
    Use specific accomplishments, skills, and projects from the candidate's resume to show why they are the perfect fit.
    
    Target Job Description:
    {job_description}
    
    The cover letter must be written in a {tone} tone. 
    Keep it professional, engaging, and around 3-4 paragraphs (approx. 250-350 words).
    Use standard formatting, and place placeholders like [Your Name], [Company Name], [Date], and [Hiring Manager's Name] where appropriate.
    
    Output ONLY the letter itself. Do not write any conversational intro or outro text.
    """
    
    return generate_answer(resume_text, prompt)
