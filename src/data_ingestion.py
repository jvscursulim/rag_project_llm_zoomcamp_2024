import json

from elasticsearch import Elasticsearch

try:
    es_client = Elasticsearch("http://localhost:9200")
except ValueError as e:
    print(e)

index_name = "gamedev-faq"
if es_client.indices.exists(index=index_name):
    pass
else:
    with open(file="../dataset/gamedev_faq_database.json", mode="r") as f:
        documents = json.load(f)
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "question": {"type": "text"},
                "answer": {"type": "text"} 
            }
        }
    }

    es_client.indices.create(index=index_name, body=index_settings)
    for doc in documents: 
        es_client.index(index=index_name, document=doc)