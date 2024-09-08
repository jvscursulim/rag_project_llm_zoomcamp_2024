import pandas as pd

from elasticsearch import Elasticsearch
from tqdm import tqdm
from utils import calculate_hit_rate, calculate_mrr, search

try:
    es_client = Elasticsearch("http://localhost:9200")
except ValueError as e:
    print(e)

df_ground_truth = pd.read_csv(filepath_or_buffer="../dataset/ground_truth_retrieval.csv")
ground_truth = df_ground_truth.to_dict(orient="records")

relevance_total = []

# Search Settings
index_name = "gamedev-faq"
n_results = 5
boosting = (4, 1)

for q in tqdm(ground_truth):
    question_id = q['id']
    results = search(query=q['question'],
                     es_client=es_client,
                     index_name=index_name,
                     n_results=n_results,
                     boosting=boosting)
    relevance = [r["_source"]['id'] == question_id for r in results]
    relevance_total.append(relevance)

print(f"Hit-rate: {calculate_hit_rate(relevance_total=relevance_total)} | MRR: {calculate_mrr(relevance_total=relevance_total)}")





