import streamlit as st

from elasticsearch import Elasticsearch
from streamlit_mic_recorder import speech_to_text
from utils import configure_model, set_api_key, process_user_input

if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(
    page_title="Gamedev Chatbot", page_icon=":video_game:", layout="wide"
)

st.title(":male-technologist: Gamedev Chatbot :video_game:")
st.divider()

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    set_api_key(st.session_state)
    gemini_model = st.text_input(label="Model name:", value="gemini-1.5-flash")
    index_name = st.text_input(label="Index name:", value="gamedev-faq")

model = configure_model(st.session_state, model_name=gemini_model)
try:
    es_client = Elasticsearch("http://localhost:9200")
except ValueError as e:
    st.warning(body=e)

if model:
    chat_session = model.start_chat(history=st.session_state.messages)

    with st.sidebar:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.write("Voice input: ")
            text_from_voice = speech_to_text(
                language="en",
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=True,
                use_container_width=False,
                callback=None,
                args=(),
                kwargs={},
                key=None,
            )
            judge_llm = st.toggle(label="RAG evaluation", value=False)
        with col2:
            n_results = st.number_input(label="Search results:", min_value=1, step=1)
            boosting_question = st.number_input(label="Question boosting:", value=1)
            boosting_answer = st.number_input(label="Answer boosting:", value=1)
        boosting = (boosting_question, boosting_answer)
        st.divider()
        query = st.chat_input(placeholder="What is your question gamedev?")

    with st.container(border=True):

        for idx, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                role = "user"
            else:
                role = "ai"
            with st.chat_message(role):
                st.markdown(message["parts"][0])

        if query or text_from_voice:
            if query:
                process_user_input(
                    chat_session=chat_session,
                    es_client=es_client,
                    index_name=index_name,
                    query=query,
                    n_results=n_results,
                    boosting=boosting,
                    judge_llm=judge_llm,
                )
            elif text_from_voice:
                process_user_input(
                    chat_session=chat_session,
                    es_client=es_client,
                    index_name=index_name,
                    query=text_from_voice,
                    n_results=n_results,
                    boosting=boosting,
                    judge_llm=judge_llm,
                )
