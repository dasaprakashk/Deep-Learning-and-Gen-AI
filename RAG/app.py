from flask import Flask, request
import query_generate
from ingest_data import IngestPDFData
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "App is running!!"

@app.route("/upload")
def upload():
    if request.method == "POST":
        data = json.loads(request.data)
        path = data["path"]
        embedding = data["embedding"]
        index = data["index"]
        ingest_pdf = IngestPDFData(path, embedding, index)
        ingest_pdf.create_embeddings()

@app.post("/generate")
def generate():
    if request.method == 'POST':
        print(request, request.get_data())
        data = json.loads(request.data)
        query = data["query"]
        repo = data["repo"]
        embedding = data["embedding"]
        print(query, repo, embedding)
        return query_generate.generate_by_query(query, repo, embedding)