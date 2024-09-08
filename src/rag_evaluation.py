import json

import google.generativeai as genai
import pandas as pd

from elasticsearch import Elasticsearch
from tqdm import tqdm
from utils import create_context_prompt, search

api_key = "INSERT YOUR GEMINI KEY HERE"

GENERATION_CONFIG1 = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

GENERATION_CONFIG2 = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

prompt_template = """
You're an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation

QUESTION: {question}

GENERATED ANSWER: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{"Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
"Explanation": "[Provide a brief explanation for your evaluation]"}}
""".strip()

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=SAFETY_SETTINGS,
    generation_config=GENERATION_CONFIG1,
)
chat_session1 = model.start_chat(history=[])

model_judge = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=SAFETY_SETTINGS,
    generation_config=GENERATION_CONFIG2,
)
chat_session_judge = model_judge.start_chat(history=[])

try:
    es_client = Elasticsearch("http://localhost:9200")
except ValueError as e:
    print(e)
index_name = "gamedev-faq"
n_results = 5
boosting = (4, 1)

df_ground_truth = pd.read_csv(
    filepath_or_buffer="../dataset/ground_truth_retrieval.csv"
)
sample_ground_truth = df_ground_truth.sample(n=16, random_state=42)
sample_ground_truth = sample_ground_truth.to_dict(orient="records")

evaluations = []

for record in tqdm(sample_ground_truth):
    search_results = search(query=record['question'],
                            es_client=es_client,
                            index_name=index_name,
                            n_results=n_results,
                            boosting=boosting)
    
    context_prompt = create_context_prompt(query=record['question'], search_results=search_results)
    message = {"role": "user", "parts": [context_prompt]}
    response = chat_session1.send_message(message)
    rag_evaluation_prompt = prompt_template.format(
            question=record['question'], answer=response.text
        )
    message = {"role": "user", "parts": [rag_evaluation_prompt]}
    response_judge = chat_session_judge.send_message(message)
    eval_judge = json.loads(response_judge.text)
    
    evaluations.append([record, response.text, eval_judge])

df = pd.DataFrame(data=evaluations, columns=["record", "answer", "evaluation"])
df['id'] = df.record.apply(lambda x: x['id'])
df['question'] = df.record.apply(lambda x: x['question'])
df['relevance'] = df.evaluation.apply(lambda x: x['Relevance'])
df['explanation'] = df.evaluation.apply(lambda x: x['Explanation'])

print(df.relevance.value_counts(normalize=True))
