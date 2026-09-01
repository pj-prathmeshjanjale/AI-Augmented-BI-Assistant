"""
LLM Provider Abstraction Module.
Supports Groq API by default with optional OpenAI API configuration via environment variables.
"""

import os
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()


def get_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    provider: Optional[str] = None
) -> Any:
    """
    Factory function returning a LangChain BaseChatModel instance.
    Defaults to Groq (LLM_PROVIDER=groq).
    Supports OpenAI if LLM_PROVIDER=openai and OPENAI_API_KEY is configured.
    """
    selected_provider = (provider or os.getenv("LLM_PROVIDER", "groq")).strip().lower()

    # 1. OPENAI PROVIDER
    if selected_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ Warning: OPENAI_API_KEY not found in environment, falling back to Groq.")
        else:
            try:
                from langchain_openai import ChatOpenAI
                target_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                return ChatOpenAI(
                    model=target_model,
                    api_key=api_key,
                    temperature=temperature
                )
            except Exception as e:
                print(f"⚠️ Failed to initialize ChatOpenAI ({e}), falling back to Groq.")

    # 2. GROQ PROVIDER (DEFAULT)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables or .env file.")

    target_model = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    try:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=target_model,
            groq_api_key=groq_api_key,
            temperature=temperature,
            request_timeout=25.0
        )
    except Exception as e:
        print(f"⚠️ Primary ChatGroq model '{target_model}' error: {e}. Trying fallback...")
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model="qwen/qwen3.6-27b",
                groq_api_key=groq_api_key,
                temperature=temperature,
                request_timeout=25.0
            )
        except Exception as e2:
            print(f"⚠️ Secondary ChatGroq fallback error: {e2}. Trying OpenAI compatible endpoint...")
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="openai/gpt-oss-120b",
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_api_key,
                temperature=temperature,
                timeout=25.0
            )
