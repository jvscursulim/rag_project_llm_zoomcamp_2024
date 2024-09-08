import time

import google.generativeai as genai
import streamlit as st

from elasticsearch import Elasticsearch


def search(
    query: str, es_client: Elasticsearch, index_name: str, n_results: int, boosting: int
) -> list:
    """Search for results that are similar to the query given by the user.

    Args:
        query (str): The user query.
        es_client (Elasticsearch): An initialized elasticsearch client.
        index_name (str): The index name of the knowledge base.
        n_results (int): The number of results to be considered as context.
        boosting (int): Boosting value.

    Returns:
        list: A list with the most relevant results.
    """

    search_query = {
        "size": n_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": [f"question^{boosting}", "answer"],
                        "type": "best_fields",
                    }
                },
            }
        },
    }

    response = es_client.search(index=index_name, body=search_query)
    search_results = [hit for hit in response['hits']['hits']]

    return search_results


def build_prompt(query: str, search_results: list) -> str:
    """Build the prompt that will be send to the LLM model.

    Args:
        query (str): The user query.
        search_results (list): A list with the most relevant
        results from the search process.

    Returns:
        str: A string that represents the prompt that will be
        send to the LLM model.
    """

    prompt_template = """
    You're a game devolper assistant and knows how to work with unity engine.
    Answer the QUESTION based on the CONTEXT from the FAQ database.
    Use only facts from the CONTEXT when answering.
    If the CONTEXT does not contain the answerm, output NONE.

    QUESTION: {question}

    CONTEXT: {context}
    """.strip()

    context = ""

    for doc in search_results:
        context = context + f"question: {doc['_source']['question']}\nanswer: {doc['_source']['answer']}\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()

    return prompt


def response_generator(chat_session: genai.ChatSession, message: dict):
    """Creates a stream effect in the responde of
    the LLM.

    Args:
        text_model (str): The name of the LLM model.
        messages (dict): A dictionary with the message sent
        to the LLM.

    Yields:
        str: Generate the characteres of the LLM response.
    """

    response = chat_session.send_message(message)

    for word in response.text.split(" "):
        yield word + " "
        time.sleep(0.05)


def process_user_input(
    chat_session, es_client: Elasticsearch, index_name: str, query: str, n_results: int, boosting: int
) -> None:
    """Processes user input

    Args:
        chat_session: A Gemini chat session.
        es_client (Elasticsearch): An initialized elasticsearch client.
        index_name (str): The index name of the knowledge base.
        prompt (str): A sequence of tokens with user query and the context.
        n_results (int): The number of search results to be considered.
        boosting (int): Boosting value.
    """

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "parts": [query]})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(query)

    search_results = search(
        query=query, es_client=es_client, index_name=index_name, n_results=n_results, boosting=boosting
    )
    prompt = build_prompt(query=query, search_results=search_results)

    # Display assistant response in chat message container
    with st.chat_message("model", avatar="ai"):
        response = st.write_stream(
            response_generator(
                chat_session=chat_session,
                message=prompt,
            )
        )
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "model", "parts": [response]})
