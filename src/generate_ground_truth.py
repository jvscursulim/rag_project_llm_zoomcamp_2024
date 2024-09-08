import json

import google.generativeai as genai
import numpy as np
import pandas as pd

from tqdm import tqdm

api_key = "INSERT YOUR GEMINI API KEY HERE"

GENERATION_CONFIG = {
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

with open(file="../dataset/gamedev_faq_database.json", mode="r") as f:
    questions = json.load(f)

prompt_template = """

You emulate a game developer that is using Unity game engine.
Formulate 5 questions that this game developer could ask based on a FAQ record.
Make the question specific to the title.
The record should contain the answer to the questions, and the questions should be complete and not too short.
If possible, use as fewer words as possible from the record.

The record:

title: {title}
question: {question}
answer: {answer}

The 5 questions must be on a JSON parsable format.

{{"questions": ["question1", "question2", ..., "question5"]}}

""".strip()

np.random.seed(seed=42)
questions_index = np.random.choice(a=[*range(len(questions))], size=16, replace=False)

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=SAFETY_SETTINGS,
    generation_config=GENERATION_CONFIG,
)
chat_session = model.start_chat(history=[])

data = []

for idx in tqdm(questions_index):
    q = questions[idx]
    message = {
        "role": "user",
        "parts": [
            prompt_template.format(
                title=q["title"], question=q["question"], answer=q["answer"]
            )
        ],
    }
    response = chat_session.send_message(message)
    try:
        for generated_question in json.loads(response.text)["questions"]:
            data.append([q["id"], generated_question])
    except:
        pass

df = pd.DataFrame(data=data, columns=["id", "question"])
df.to_csv("../dataset/ground_truth_retrieval.csv", index=False)
