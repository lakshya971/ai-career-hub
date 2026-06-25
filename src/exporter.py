import json
from src.llm import generate_answer

def run_json_resume_export(resume_text):
    prompt = """
    Parse the candidate's resume content into a structured JSON object strictly matching the schema below. 
    Ensure you extract all information accurately. If a field cannot be found, set it to null or an empty array.
    
    JSON Schema:
    {
      "name": "Candidate's full name",
      "email": "Email address",
      "phone": "Phone number",
      "location": "City, Country or Address",
      "website": "LinkedIn, GitHub, or portfolio URL",
      "skills": ["Skill 1", "Skill 2", ...],
      "education": [
        {
          "institution": "University/School name",
          "degree": "Degree/Major name",
          "year": "Graduation year or date range"
        }
      ],
      "experience": [
        {
          "company": "Company/Organization name",
          "position": "Job title",
          "duration": "Date range (e.g. 2021 - Present)",
          "highlights": ["Responsibility/Achievement 1", "Responsibility/Achievement 2"]
        }
      ],
      "projects": [
        {
          "name": "Project name",
          "description": "Short project description",
          "technologies": ["Tech 1", "Tech 2"]
        }
      ]
    }
    
    Output ONLY valid, raw JSON. Do not add markdown code block syntax (such as ```json) or any conversational text.
    """
    
    response = generate_answer(resume_text, prompt)
    
    # Strip markdown block quotes if the LLM included them anyway
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Verify it is valid JSON
    try:
        parsed = json.loads(cleaned)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        # Fallback to return the cleaned string
        return cleaned
