import requests
import json

json_path = "mappings.json"
es_index = "contractorderform-ada" #for hf change mappings.json dims to 768 - It uses sentence transformer embeddings

with open(json_path) as json_file:
    payload = json.load(json_file)
    payload_data = json.dumps(payload)
    print(payload_data)
    headers = {'content-type': 'application/json'}
    es_url = "http://localhost:9200/{}".format(es_index)
    response = requests.request("PUT", es_url, data=payload_data, headers=headers)
    print(response)