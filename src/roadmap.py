from src.llm import generate_answer

def run_generate_roadmap(resume_text, target_role):
    prompt = f"""
    The candidate wants to transition from their current profile (as described in their resume) to the target role: "{target_role}".
    
    Your tasks:
    1. Identify key technical or conceptual skill GAPS that the candidate needs to acquire to be competitive for the "{target_role}" role.
    2. Design a structured week-by-week (e.g., 4-to-6-week plan) learning roadmap to bridge these gaps. Include practical projects/exercises.
    
    Output format:
    
    ### 🎯 Target Role: {target_role}
    
    #### ⚠️ Detected Skill Gaps:
    - **[Skill 1]**: Explanation of the gap based on their resume vs target role requirements
    - **[Skill 2]**: ...
    
    #### 🗺️ Custom Learning Roadmap:
    - **Week 1: [Topic Title]**
      - *Focus Areas:* [Specific libraries, tools, or concepts to cover]
      - *Hands-on Project:* [A mini-project to build]
    - **Week 2: [Topic Title]**
      - ...
      
    Make the roadmap highly actionable, practical, and tailored to what they already know. Do not include conversational intro/outro text.
    """
    
    return generate_answer(resume_text, prompt)
