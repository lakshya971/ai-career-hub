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
            from langchain_openai import ChatOpenAI
            # Fallback to st.secrets if api_key is empty
            active_key = api_key if api_key else st.secrets.get("GEMINI_API_KEY", "")
            if not active_key:
                return "⚠️ Gemini API key is missing. Please create a free key in Google AI Studio and provide it in the sidebar settings or secrets."
            llm = ChatOpenAI(
                model=model,
                openai_api_key=active_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            response = llm.invoke(prompt)
            return response.content
            
        else:
            # Default local Ollama
            llm = Ollama(model=model)
            response = llm.invoke(prompt)
            return response
            
    except Exception as e:
        return f"⚠️ Error generating answer from {provider} ({model}): {str(e)}"
