# ✦ TalentSearch AI: RAG Career Hub & Recruiter Dashboard

A premium, theme-responsive career assistant and candidate evaluation dashboard powered by **Retrieval-Augmented Generation (RAG)**. The application is built on LangChain, FAISS, and Streamlit, supporting local LLMs (via Ollama) and cloud API engines (Anthropic Claude & OpenAI GPT).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://talentsearchai.streamlit.app/)

🔗 **Live Deployment:** [talentsearchai.streamlit.app](https://talentsearchai.streamlit.app/)

---

## 🎨 Premium Editorial UI Design

Inspired by the warm, minimalist, and editorial design aesthetic of **Claude.com**:
*   **Color Palette**: Tinted cream canvas background (`#faf9f5`), charcoal-ink text (`#141413`), and warm coral accent highlights (`#cc785c`).
*   **Typography**: Display serif titles (**EB Garamond**) with negative tracking, paired with high-readability sans-serif body fonts (**Inter**).
*   **Dynamic Theme Toggling**: Built using responsive CSS variables, supporting seamless, legibility-optimized switches between **Light** and **Dark** modes.

---

## ✨ Key Features

The app automatically switches between two operational modes based on user uploads:

### 👤 Candidate Mode (Single Resume Uploaded)
An all-in-one career acceleration suite:
1.  **💬 Q&A Chat Assistant**: Query the uploaded resume using semantic search (RAG) backed by a local FAISS database, displaying the specific source text chunks.
2.  **📊 Profile Highlights**: Generates key summaries, extracts technical/soft skills into color-coded badges, and organizes work history automatically.
3.  **🎯 ATS Matcher & Cover Letter Generator**: Paste a job description (JD) to calculate compatibility scores, find missing keyword competencies, and instantly write tailored cover letters (configurable tone).
4.  **🗺️ Skill Gap & Learning Roadmap**: Enter a target dream role to receive a customized, weekly study guide mapped directly to your current skill gaps.
5.  **🎙️ Mock Interviewer**: Take a simulated interview with questions derived from your actual experience. Input your answers to receive graded feedback (out of 10) and model responses.
6.  **📥 Structured JSON Exporter**: Parse the unstructured resume layout into a standardized JSON resume schema and download the file.

### 👥 Recruiter Mode (Multiple Resumes Uploaded)
A candidate-evaluation leaderboard:
*   **Rank Candidates**: Upload multiple candidate resumes and paste a target job description.
*   **Candidate Ranking**: Ranks candidates side-by-side using semantic scoring against the JD, highlighting overlap skills and candidate summaries.

---

## 🛠️ Technology Stack

*   **Frontend**: Streamlit (Python-based interactive UI)
*   **RAG Orchestration**: LangChain & LangChain Community
*   **Document Loader**: PyPDF
*   **Text Splitter**: `RecursiveCharacterTextSplitter` (token/character chunking)
*   **Embeddings**: HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
*   **Vector Database**: FAISS (Facebook AI Similarity Search)
*   **LLM Providers**:
    *   **Local**: Ollama (`llama3.2`, `llama3`)
    *   **Cloud (API)**: Anthropic Claude (`claude-3-5-sonnet`, `claude-3-haiku`), OpenAI GPT (`gpt-4o`, `gpt-4o-mini`)

---

## 📁 Directory Structure

```text
rag-project/
├── .streamlit/
│   └── config.toml          # Default theme colors (cream, coral, sans-serif font)
├── documents/               # Staging directory for parsed resume PDFs
├── src/
│   ├── ats.py               # ATS match and compatibility analysis
│   ├── chunking.py          # Document splitter utilities
│   ├── cover_letter.py      # Cover letter drafter engine
│   ├── doc_load.py          # PyPDF loader configuration
│   ├── embedding.py         # HuggingFace Embeddings initialization
│   ├── exporter.py          # Standard JSON Resume schema exporter
│   ├── llm.py               # Core API & Ollama router controller
│   ├── mock_interview.py    # Simulated interview question & evaluation logic
│   ├── retrievel.py         # Semantic chunk retrieval query executor
│   ├── roadmap.py           # Skill gap week-by-week planner
│   └── vectordb.py          # FAISS vector store manager
├── app.py                   # Main Streamlit web application
├── requirements.txt         # Package dependencies
└── README.md                # Project documentation
```

---

## 🚀 Local Setup & Installation

Follow these steps to run the application locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/lakshya971/ai-career-hub.git
cd ai-career-hub
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Install & Run Ollama (For Local Offline Mode)
1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Pull the default model:
   ```bash
   ollama pull llama3.2
   ```

### 4. Run the Streamlit Application
```bash
python -m streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## ☁️ Cloud Deployment Configuration

When deploying this application on **Streamlit Community Cloud**:

1. Log in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
2. Select your repository `lakshya971/ai-career-hub`, select branch `main`, and specify the file path as `app.py`.
3. To enable the cloud API backends (Anthropic/OpenAI), navigate to **App Settings** > **Secrets** in the Streamlit Cloud Dashboard and configure your keys:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   ANTHROPIC_API_KEY = "your-anthropic-api-key"
   ```
4. Click **Deploy**. Streamlit Cloud will automatically read the dependencies from `requirements.txt` and establish your web endpoint!
