import json

from elasticsearch import Elasticsearch
from tqdm import tqdm

try:
    es_client = Elasticsearch("http://localhost:9200")
except ValueError as e:
    print(e)

with open(file="../dataset/gamedev_faq_database.json", mode="r") as f:
    documents = json.load(f)

index_settings = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text"},
            "question": {"type": "text"},
            "answer": {"type": "text"},
        }
    },
}

index_name = "gamedev-faq"
es_client.indices.delete(index=index_name, ignore_unavailable=True)
es_client.indices.create(index=index_name, body=index_settings)

for doc in tqdm(documents):
    es_client.index(index=index_name, document=doc)
