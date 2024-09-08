import google.generativeai as genai
import streamlit as st

from typing import Any, Optional
from .model_settings import SAFETY_SETTINGS, GENERATION_CONFIG
from .evaluation_tools import calculate_hit_rate, calculate_mrr
from .rag import process_user_input, search, create_context_prompt


def configure_model(
    session_state: Any, model_name: str = "gemini-1.5-flash"
) -> Optional[Any]:
    if not session_state.api_key:
        with st.sidebar:
            st.warning(body="You must provide a Gemini API key!")

        return

    genai.configure(api_key=session_state.api_key)

    return genai.GenerativeModel(
        model_name=model_name,
        safety_settings=SAFETY_SETTINGS,
        generation_config=GENERATION_CONFIG,
    )


def set_api_key(session_state: Any):
    api_key = st.text_input(label="Insert your Gemini API key here", type="password")
    if api_key:
        session_state.api_key = api_key
