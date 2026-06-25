import streamlit as st
from langchain_community.llms import Ollama

def generate_answer(context, query, config=None):
    # Resolve config. Default to session state, then fallback to local Ollama
    if config is None:
        config = st.session_state.get("llm_config", {"provider": "Ollama (Local)", "model": "llama3.2"})
        
    provider = config.get("provider", "Ollama (Local)")
    model = config.get("model", "llama3.2")
    api_key = config.get("api_key", "")
    
    prompt = f"""
    Context information is below.
    ---------------------
    {context}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {query}
    Answer:
    """
    
    try:
        if "anthropic" in provider.lower():
            # pyrefly: ignore [missing-import]
            from langchain_anthropic import ChatAnthropic
            # Fallback to st.secrets if api_key is empty
            active_key = api_key if api_key else st.secrets.get("ANTHROPIC_API_KEY", "")
            if not active_key:
                return "⚠️ Anthropic API key is missing. Please provide it in the sidebar settings."
            llm = ChatAnthropic(model=model, anthropic_api_key=active_key)
            response = llm.invoke(prompt)
            return response.content
            
        elif "openai" in provider.lower():
            # pyrefly: ignore [missing-import]
            from langchain_openai import ChatOpenAI
            # Fallback to st.secrets if api_key is empty
            active_key = api_key if api_key else st.secrets.get("OPENAI_API_KEY", "")
            if not active_key:
                return "⚠️ OpenAI API key is missing. Please provide it in the sidebar settings."
            llm = ChatOpenAI(model=model, openai_api_key=active_key)
            response = llm.invoke(prompt)
            return response.content
            
        elif "gemini" in provider.lower():
            # pyrefly: ignore [missing-import]
            from langchain_google_genai import ChatGoogleGenerativeAI
            # Fallback to st.secrets if api_key is empty
            active_key = api_key if api_key else st.secrets.get("GEMINI_API_KEY", "")
            if not active_key:
                return "⚠️ Gemini API key is missing. Please create a free key in Google AI Studio and provide it in the sidebar settings or secrets."
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=active_key
            )
            response = llm.invoke(prompt)
            return response.content
            
        else:
            # Default local Ollama
            llm = Ollama(model=model)
            response = llm.invoke(prompt)
            return response
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg or "429" in error_msg:
            return f"⚠️ API quota exceeded for {provider}. Please verify your billing balance at platform.openai.com/settings/billing or switch to the Google Gemini API (Free) or local Ollama."
        elif "connection refused" in error_msg.lower() or "failed to establish a new connection" in error_msg.lower() or "connectionerror" in error_msg.lower():
            return f"⚠️ Local Ollama service is not running. Please make sure the Ollama desktop app is running on your machine, or switch to a Cloud API provider (Gemini/OpenAI) in the sidebar."
        elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower() or "401" in error_msg:
            return f"⚠️ Invalid API key for {provider}. Please check the key configuration in the sidebar settings or secrets."
        elif "not_found" in error_msg.lower() or "404" in error_msg:
            return f"⚠️ Model not found or unavailable for {provider} ({model}). Please verify model availability or check if your API key has access."
        else:
            return f"⚠️ Error generating answer from {provider} ({model}): {error_msg}"
