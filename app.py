import streamlit as st
import os
import re
import json

from src.doc_load import load_pdf
from src.chunking import create_chunk
from src.embedding import get_embedding_model
from src.vectordb import create_vector_store
from src.retrievel import retrieve_documents
from src.llm import generate_answer

# Import new advanced features
from src.ats import run_ats_match
from src.cover_letter import run_cover_letter_generation
from src.mock_interview import run_generate_questions, run_grade_answer
from src.roadmap import run_generate_roadmap
from src.exporter import run_json_resume_export

# Set page config
st.set_page_config(
    page_title="AI Career Hub & Recruiter Dashboard",
    page_icon="✦",
    layout="centered"
)

# Sidebar Configuration (Placed first to initialize llm_config before any LLM calls)
st.sidebar.markdown("<h2 style='color: var(--text-color); font-size: 1.4rem; margin-top: 10px; font-family: \"EB Garamond\", serif;'>🤖 LLM Engine</h2>", unsafe_allow_html=True)

# Dynamically check if local Ollama is available
import urllib.request
@st.cache_resource(ttl=60)
def is_ollama_available():
    try:
        with urllib.request.urlopen("http://localhost:11434/", timeout=1) as response:
            return response.status == 200
    except Exception:
        return False

# Prioritize provider based on Ollama availability
ollama_active = is_ollama_available()
if ollama_active:
    provider_options = ["Ollama (Local)", "Google Gemini API (Free)", "OpenAI GPT API", "Anthropic Claude API"]
else:
    provider_options = ["Google Gemini API (Free)", "OpenAI GPT API", "Anthropic Claude API", "Ollama (Local)"]

llm_provider = st.sidebar.selectbox("LLM Provider", provider_options, key="llm_provider_select")

llm_model = "llama3.2"
api_key = ""

if llm_provider == "Ollama (Local)":
    llm_model = st.sidebar.selectbox("Ollama Model", ["llama3.2", "llama3"], key="ollama_model_select")
elif llm_provider == "Google Gemini API (Free)":
    llm_model = st.sidebar.selectbox("Gemini Model", ["gemini-1.5-flash", "gemini-1.5-pro"], key="gemini_model_select")
    api_key = st.sidebar.text_input("Gemini API Key", type="password", placeholder="Pulls from secrets if blank", key="gemini_key_input")
elif llm_provider == "Anthropic Claude API":
    llm_model = st.sidebar.selectbox("Claude Model", ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"], key="claude_model_select")
    api_key = st.sidebar.text_input("Anthropic API Key", type="password", placeholder="Pulls from secrets if blank", key="anthropic_key_input")
elif llm_provider == "OpenAI GPT API":
    llm_model = st.sidebar.selectbox("GPT Model", ["gpt-4o-mini", "gpt-4o"], key="gpt_model_select")
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="Pulls from secrets if blank", key="openai_key_input")

# Save to session state for src/llm.py to read
st.session_state.llm_config = {
    "provider": llm_provider,
    "model": llm_model,
    "api_key": api_key
}

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: var(--text-color); font-size: 1.15rem; font-family: \"EB Garamond\", serif;'>⚙️ Search Settings</h3>", unsafe_allow_html=True)
k_value = st.sidebar.slider("Number of retrieved chunks (k)", min_value=1, max_value=8, value=5)

# Custom premium Claude.com warm-editorial styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..700;1,400..700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Typography and Background */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Document elements scoped specifically to prevent layout glitches */
    p, li, label, [data-testid="stMarkdownContainer"] {
        font-family: 'Inter', sans-serif !important;
        line-height: 1.55 !important;
    }
    
    /* Serif Headlines */
    h1, h2, h3, h4, h5, h6, .display-title {
        font-family: 'EB Garamond', serif !important;
        font-weight: 400 !important;
        color: var(--text-color) !important;
        letter-spacing: -0.8px !important;
    }
    
    /* Title and Subtitle */
    .display-title {
        font-size: 2.8rem !important;
        line-height: 1.15 !important;
        text-align: center;
        margin-bottom: 8px;
    }
    .subtitle {
        color: var(--text-color) !important;
        opacity: 0.7 !important;
        text-align: center;
        font-size: 1.1rem !important;
        margin-bottom: 35px !important;
        font-weight: 400 !important;
    }
    
    /* Clean Feature Cards (Adapts to Light/Dark) */
    .editorial-card {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 28px !important;
        margin-bottom: 24px !important;
        box-shadow: none !important;
        transition: all 0.2s ease-in-out !important;
    }
    .editorial-card:hover {
        border-color: #cc785c !important; /* Accent Coral */
    }
    
    /* Monospace / Code surfaces (Always dark for high contrast code display) */
    .product-mockup-card-dark {
        background-color: #181715 !important;
        color: #faf9f5 !important; /* Light text on dark */
        border-radius: 12px !important;
        padding: 24px !important;
        border: 1px solid #252320 !important;
        margin-bottom: 20px !important;
    }
    .product-mockup-card-dark code, .product-mockup-card-dark pre {
        font-family: 'JetBrains Mono', monospace !important;
        color: #faf9f5 !important;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.8rem;
        font-weight: 500;
        border-radius: 9999px;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .badge-teal {
        background-color: rgba(93, 184, 166, 0.15) !important;
        color: #5db8a6 !important;
        border: 1px solid rgba(93, 184, 166, 0.25) !important;
    }
    .badge-amber {
        background-color: rgba(232, 165, 90, 0.15) !important;
        color: #e8a55a !important;
        border: 1px solid rgba(232, 165, 90, 0.25) !important;
    }
    .badge-coral {
        background-color: rgba(204, 120, 92, 0.12) !important;
        color: #cc785c !important;
        border: 1px solid rgba(204, 120, 92, 0.25) !important;
    }
    
    /* Sidebar border accent */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2) !important;
    }
    
    /* Primary Coral Action Button Wrapper */
    .primary-btn-wrapper .stButton button {
        background-color: #cc785c !important; /* Brand Coral */
        color: #ffffff !important;
        border: none !important;
    }
    .primary-btn-wrapper .stButton button:hover {
        background-color: #a9583e !important; /* Coral Active */
        box-shadow: 0 4px 12px rgba(204, 120, 92, 0.2) !important;
    }
    
    /* Category Filter style for Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: transparent !important;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2) !important;
        margin-bottom: 24px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-color) !important;
        opacity: 0.7 !important;
        font-weight: 500 !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        opacity: 1.0 !important;
        background-color: var(--secondary-background-color) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--secondary-background-color) !important; /* Cream card tab */
        border-color: rgba(128, 128, 128, 0.2) !important;
        color: var(--text-color) !important;
        opacity: 1.0 !important;
    }
    
    /* File uploader container styling */
    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(128, 128, 128, 0.25) !important;
        background-color: var(--secondary-background-color) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    
    /* Editorial Chat QA presentation */
    .user-query-container {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 8px !important;
        color: var(--text-color) !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
        font-size: 0.95rem !important;
    }
    .assistant-answer-container {
        background-color: transparent !important;
        border: none !important;
        border-left: 2px solid #cc785c !important; /* Coral indicator line */
        padding: 0 0 0 20px !important;
        margin-bottom: 28px !important;
        color: var(--text-color) !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    
    /* ATS Score Circle styling */
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        margin: 20px 0;
    }
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(#cc785c var(--value), rgba(128, 128, 128, 0.2) 0deg); /* Coral & Hairline border */
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .score-circle::before {
        content: "";
        position: absolute;
        width: 104px;
        height: 104px;
        border-radius: 50%;
        background: var(--background-color);
    }
    .score-text {
        position: absolute;
        font-size: 2.2rem;
        font-weight: 400;
        color: #cc785c;
        font-family: 'EB Garamond', serif !important;
    }
    
    /* Dynamic Info snippet card */
    .snippet-card {
        background-color: var(--secondary-background-color) !important;
        border-left: 4px solid #cc785c !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='display-title'>✦ AI Career Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A thoughtful RAG career hub and recruiter dashboard powered by local & cloud LLMs</p>", unsafe_allow_html=True)

# Cached PDF Processing & Indexing
@st.cache_resource
def process_resume(file_bytes, file_name):
    os.makedirs("documents", exist_ok=True)
    temp_path = os.path.join("documents", file_name)
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    doc = load_pdf(temp_path)
    chunks = create_chunk(doc)
    embeddings = get_embedding_model()
    vector_store = create_vector_store(chunks, embeddings)
    return vector_store, chunks

# Cached Resume Insights Generation
@st.cache_resource
def generate_resume_insights(_chunks_list, provider, model, api_key):
    config = {
        "provider": provider,
        "model": model,
        "api_key": api_key
    }
    context = "\n".join([c.page_content for c in _chunks_list[:4]])
    summary = generate_answer(context, "Give me a concise 3-sentence professional summary of this candidate's background and experience.", config=config)
    skills = generate_answer(context, "Extract the key technical and soft skills mentioned in this resume as a simple comma-separated list.", config=config)
    experience = generate_answer(context, "Summarize the candidate's work history, including notable job roles, companies, and durations in brief bullet points.", config=config)
    return summary, skills, experience

# Multi-file Uploader Card
uploaded_files = st.file_uploader("Upload resume PDF(s)", type=["pdf"], accept_multiple_files=True, key="resumes_uploader")

if uploaded_files:
    if len(uploaded_files) == 1:
        # SINGLE RESUME MODE (Career Hub Dashboard)
        uploaded_file = uploaded_files[0]
        file_bytes = uploaded_file.getvalue()
        
        with st.spinner("⚡ Parsing resume layout & building local FAISS index..."):
            vector_store, all_chunks = process_resume(file_bytes, uploaded_file.name)
            resume_text = "\n".join([chunk.page_content for chunk in all_chunks])
            
        st.toast("✅ Resume successfully indexed!", icon="✨")
        
        # Setup layout Tabs
        tabs = st.tabs([
            "💬 Chat Assistant", 
            "📊 Profile Highlights", 
            "🎯 ATS & Cover Letter", 
            "🗺️ Skill Gap & Roadmap",
            "🎙️ Mock Interview",
            "📥 Export JSON",
            "🔍 Raw Chunks"
        ])
        
        # 1. CHAT ASSISTANT
        with tabs[0]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>💬 Query the resume:</h3>", unsafe_allow_html=True)
            suggested_queries = [
                "What are the main technical skills of the candidate?",
                "Summarize the candidate's professional experience.",
                "Does this resume match a Senior Software Engineer role?"
            ]
            cols = st.columns(len(suggested_queries))
            selected_suggestion = None
            for i, q in enumerate(suggested_queries):
                if cols[i].button(q, key=f"suggest_{i}", use_container_width=True):
                    selected_suggestion = q
                    
            default_query = selected_suggestion if selected_suggestion else ""
            query = st.text_input("Enter your query:", value=default_query, placeholder="e.g. What is the candidate's experience with Python?", key="query_input")
            
            if query:
                st.markdown(f"<div class='user-query-container'><b>Question:</b> {query}</div>", unsafe_allow_html=True)
                with st.spinner("Consulting LLM..."):
                    retrieve_docs = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k_value}).invoke(query)
                    context = "\n".join([doc.page_content for doc in retrieve_docs])
                    answer = generate_answer(context, query)
                st.markdown("<div class='assistant-answer-container'><b>Answer:</b><br><br>" + answer.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                
                st.subheader("Retrieved Context Chunks")
                for idx, doc in enumerate(retrieve_docs):
                    page_info = f"Page {doc.metadata.get('page', 0) + 1}" if 'page' in doc.metadata else "N/A"
                    with st.expander(f"Chunk #{idx+1} — {page_info}", expanded=(idx==0)):
                        st.markdown(f"<div class='snippet-card' style='font-family: monospace;'>{doc.page_content}</div>", unsafe_allow_html=True)

        # 2. PROFILE HIGHLIGHTS
        with tabs[1]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>Highlights Candidate Profile</h3>", unsafe_allow_html=True)
            with st.spinner("Generating insights..."):
                summary, skills_extracted, experience_summary = generate_resume_insights(
                    all_chunks,
                    st.session_state.llm_config["provider"],
                    st.session_state.llm_config["model"],
                    st.session_state.llm_config["api_key"]
                )
                
            # Executive Summary card
            st.markdown(f"""
            <div class='editorial-card'>
                <h4>📋 Executive Summary</h4>
                <p style='margin-top: 10px;'>{summary}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Extracted Skills card
            skills_list = [s.strip() for s in skills_extracted.split(",") if s.strip()]
            if not skills_list:
                skills_html = f"<p>{skills_extracted}</p>"
            else:
                skills_html = "".join([f"<span class='badge badge-teal'>{s}</span>" for s in skills_list])
            st.markdown(f"""
            <div class='editorial-card'>
                <h4>🛠️ Extracted Skills</h4>
                <div style='margin-top: 12px;'>{skills_html}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Experience Overview card
            formatted_experience = experience_summary.replace("\n", "<br>")
            st.markdown(f"""
            <div class='editorial-card'>
                <h4>💼 Experience Overview</h4>
                <div style='margin-top: 10px;'>{formatted_experience}</div>
            </div>
            """, unsafe_allow_html=True)

        # 3. ATS & COVER LETTER
        with tabs[2]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>ATS Matcher & Cover Letter Generator</h3>", unsafe_allow_html=True)
            jd_text = st.text_area("Paste Target Job Description (JD):", height=200, placeholder="Paste the job requirements here...")
            
            col_letter_left, col_letter_right = st.columns(2)
            tone_selection = col_letter_left.selectbox("Select Cover Letter Tone:", ["Professional", "Enthusiastic", "Creative", "Bold"])
            
            if jd_text:
                st.markdown("<div class='primary-btn-wrapper'>", unsafe_allow_html=True)
                run_btn = st.button("Run ATS Match & Draft Cover Letter", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                if run_btn:
                    with st.spinner("Evaluating ATS compatibility..."):
                        ats_results = run_ats_match(resume_text, jd_text)
                    
                    st.markdown("---")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("##### Compatibility Score")
                        st.markdown(f"""
                        <div class='score-container'>
                            <div class='score-circle' style='--value: {ats_results["score"] * 3.6}deg;'>
                                <div class='score-text'>{ats_results["score"]}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("##### Matching Skills")
                        if ats_results["matching_skills"]:
                            for s in ats_results["matching_skills"]:
                                st.markdown(f"<span class='badge badge-teal'>{s}</span>", unsafe_allow_html=True)
                        else:
                            st.write("No direct skill matches found.")
                            
                        st.markdown("##### Missing Competencies")
                        if ats_results["missing_skills"]:
                            for s in ats_results["missing_skills"]:
                                st.markdown(f"<span class='badge badge-coral'>{s}</span>", unsafe_allow_html=True)
                        else:
                            st.write("Excellent keyword alignment!")
                    
                    recs_html = "".join([f"<li style='margin-bottom: 6px;'>{rec}</li>" for rec in ats_results["recommendations"]])
                    st.markdown(f"""
                    <div class='editorial-card'>
                        <h4>Optimization Suggestions</h4>
                        <ul style='margin-top: 10px; padding-left: 20px; color: var(--text-color);'>{recs_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Cover Letter Generation
                    st.markdown("---")
                    st.markdown("### Tailored Cover Letter")
                    with st.spinner("Drafting cover letter..."):
                        cover_letter = run_cover_letter_generation(resume_text, jd_text, tone_selection)
                    
                    st.text_area("Drafted Letter (you can copy or edit it):", cover_letter, height=350, key="cover_letter_editor")
                    
                    st.download_button(
                        label="📥 Download Cover Letter (.txt)",
                        data=cover_letter,
                        file_name=f"{uploaded_file.name.replace('.pdf', '')}_cover_letter.txt",
                        mime="text/plain"
                    )

        # 4. SKILL GAP & ROADMAP
        with tabs[3]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>Skill Gap & Learning Roadmap</h3>", unsafe_allow_html=True)
            target_role = st.text_input("Enter your target career role:", placeholder="e.g. Data Scientist, Cloud Architect, Fullstack Engineer")
            
            if target_role:
                st.markdown("<div class='primary-btn-wrapper'>", unsafe_allow_html=True)
                roadmap_btn = st.button("Generate Learning Roadmap", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                if roadmap_btn:
                    with st.spinner("Designing custom roadmap plan..."):
                        roadmap_md = run_generate_roadmap(resume_text, target_role)
                    st.markdown(roadmap_md)

        # 5. MOCK INTERVIEW
        with tabs[4]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>Interactive Mock Interviewer</h3>", unsafe_allow_html=True)
            st.markdown("Take a customized technical and situational interview tailored directly to the experience and projects on your resume.")
            
            # Setup interactive interview in session state
            if "interview_questions" not in st.session_state or st.session_state.get("current_file_idx_key") != uploaded_file.name:
                st.session_state.interview_questions = []
                st.session_state.current_file_idx_key = uploaded_file.name
                st.session_state.evaluations = {}
                st.session_state.user_answers = {}
                
            st.markdown("<div class='primary-btn-wrapper'>", unsafe_allow_html=True)
            gen_btn = st.button("Generate 3 Interview Questions", key="gen_questions_btn", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if gen_btn:
                with st.spinner("Preparing questions..."):
                    st.session_state.interview_questions = run_generate_questions(resume_text)
                    st.session_state.evaluations = {}
                    st.session_state.user_answers = {}
            
            if st.session_state.interview_questions:
                st.markdown("---")
                q_tabs = st.tabs([f"Question {i+1}" for i in range(len(st.session_state.interview_questions))])
                
                for idx, q in enumerate(st.session_state.interview_questions):
                    with q_tabs[idx]:
                        st.markdown(f"<div style='font-size: 1.15rem; font-weight: 500; margin-bottom: 12px; color: #141413;'>{q}</div>", unsafe_allow_html=True)
                        
                        ans_key = f"ans_{idx}"
                        user_ans = st.text_area("Your Answer:", height=120, key=ans_key)
                        
                        st.markdown("<div class='primary-btn-wrapper'>", unsafe_allow_html=True)
                        submit_btn = st.button("Submit Answer", key=f"submit_ans_{idx}")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        if submit_btn:
                            if not user_ans.strip():
                                st.warning("Please type an answer first!")
                            else:
                                with st.spinner("Evaluating response..."):
                                    eval_result = run_grade_answer(resume_text, q, user_ans)
                                    st.session_state.evaluations[idx] = eval_result
                                    st.session_state.user_answers[idx] = user_ans
                                    
                        if idx in st.session_state.evaluations:
                            res = st.session_state.evaluations[idx]
                            st.markdown("---")
                            col_score, col_feedback = st.columns([1, 3])
                            with col_score:
                                st.markdown("##### Score")
                                st.markdown(f"""
                                <div class='score-container' style='margin-top: 10px;'>
                                    <div class='score-circle' style='--value: {res["score"] * 36}deg;'>
                                        <div class='score-text'>{res["score"]}/10</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_feedback:
                                st.markdown("##### Interview Feedback")
                                st.write(res["feedback"])
                                
                            with st.expander("Recommended Response"):
                                st.write(res["model_answer"])

        # 6. EXPORT JSON
        with tabs[5]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>Structured JSON Exporter</h3>", unsafe_allow_html=True)
            st.markdown("Extract unstructured resume data and export it into a standardized JSON Schema representation.")
            
            st.markdown("<div class='primary-btn-wrapper'>", unsafe_allow_html=True)
            export_btn = st.button("Extract & Convert to JSON", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if export_btn:
                with st.spinner("Parsing entities..."):
                    extracted_json = run_json_resume_export(resume_text)
                
                # Show parsed JSON inside a dark code block card
                st.markdown("<div class='product-mockup-card-dark'>", unsafe_allow_html=True)
                st.code(extracted_json, language="json")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 Download JSON Resume",
                    data=extracted_json,
                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_schema.json",
                    mime="application/json"
                )

        # 7. RAW CHUNKS
        with tabs[6]:
            st.markdown("<h3 style='font-size: 1.35rem; margin-top: 15px;'>Parsed Resume Chunks</h3>", unsafe_allow_html=True)
            st.markdown(f"The PDF was parsed into **{len(all_chunks)}** distinct text chunks for semantic indexing.")
            
            col1, col2 = st.columns(2)
            col1.metric("Total Chunks", len(all_chunks))
            total_chars = sum([len(c.page_content) for c in all_chunks])
            col2.metric("Total Characters", f"{total_chars:,}")
            
            st.markdown("---")
            for idx, chunk in enumerate(all_chunks):
                page_num = f"Page {chunk.metadata.get('page', 0) + 1}" if 'page' in chunk.metadata else "Unknown"
                with st.expander(f"Chunk #{idx+1} ({page_num})", expanded=False):
                    st.code(chunk.page_content, language="text")

    else:
        # MULTI-RESUME MODE (Recruiter Comparison Dashboard)
        st.markdown("<h3 style='font-size: 1.45rem; color: #141413; margin-top: 15px;'>👥 Recruiter Leaderboard & Candidate Comparison</h3>", unsafe_allow_html=True)
        st.markdown(f"Uploaded **{len(uploaded_files)}** candidate resumes. Paste a job description below to rank and compare them.")
        
        recruiter_jd = st.text_area("Paste Target Job Description (JD):", height=200, placeholder="Paste requirements here...", key="recruiter_jd_input")
        
        if recruiter_jd:
            st.markdown("<div class='primary-btn-wrapper'>", unsafe_allow_html=True)
            rank_btn = st.button("Rank Candidates", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if rank_btn:
                leaderboard = []
                progress_bar = st.progress(0)
                for idx, file in enumerate(uploaded_files):
                    file_bytes = file.getvalue()
                    # Process and index
                    with st.spinner(f"Processing candidate ({idx+1}/{len(uploaded_files)}): {file.name}..."):
                        _, chunks = process_resume(file_bytes, file.name)
                        full_text = "\n".join([c.page_content for c in chunks])
                        
                        # Get summary & ATS score
                        ats_results = run_ats_match(full_text, recruiter_jd)
                        candidate_summary, _, _ = generate_resume_insights(
                            chunks,
                            st.session_state.llm_config["provider"],
                            st.session_state.llm_config["model"],
                            st.session_state.llm_config["api_key"]
                        )
                        
                        name_match = re.search(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+", full_text)
                        candidate_name = name_match.group(0) if name_match else file.name.replace(".pdf", "")
                        
                        leaderboard.append({
                            "name": candidate_name,
                            "filename": file.name,
                            "score": ats_results["score"],
                            "matching_skills": ats_results["matching_skills"][:5],
                            "summary": candidate_summary
                        })
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                # Sort leaderboard by score descending
                leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
                
                st.markdown("### Rank Leaderboard")
                for rank, cand in enumerate(leaderboard):
                    rank_icon = "🥇" if rank == 0 else "🥈" if rank == 1 else "🥉" if rank == 2 else "✦"
                    st.markdown(f"""
                    <div class='editorial-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <h4 style='margin: 0; color: #141413; font-size: 1.35rem;'>{rank_icon} Rank #{rank+1}: {cand["name"]}</h4>
                            <span class='badge badge-sky' style='font-size: 1.05rem; padding: 6px 14px;'>ATS Match: {cand["score"]}%</span>
                        </div>
                        <p style='color: #6c6a64; font-size: 0.85rem; margin-top: 0;'>File: <code>{cand["filename"]}</code></p>
                        <p style='margin: 12px 0;'><b>Candidate Profile:</b> {cand["summary"]}</p>
                        <div>
                            <b>Overlapping Skills:</b>
                    """, unsafe_allow_html=True)
                    
                    if cand["matching_skills"]:
                        for s in cand["matching_skills"]:
                            st.markdown(f"<span class='badge badge-teal'>{s}</span>", unsafe_allow_html=True)
                    else:
                        st.write("No matching skills extracted.")
                    st.markdown("</div></div>", unsafe_allow_html=True)

else:
    # Landing page state
    st.markdown("""
    <div class='editorial-card' style='text-align: center; padding: 40px;'>
        <p style='font-size: 3rem;'>📤</p>
        <h3 style='margin-top: 10px;'>No resume uploaded yet</h3>
        <p style='color: #6c6a64;'>Please upload one or more PDF resumes above to start analysis or rank candidates.</p>
    </div>
    """, unsafe_allow_html=True)