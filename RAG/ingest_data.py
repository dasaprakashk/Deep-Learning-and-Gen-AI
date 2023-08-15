import fitz
import utils
import tiktoken
from tqdm.auto import tqdm
from uuid import uuid4
from elasticsearch import Elasticsearch, helpers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


tokenizer = tiktoken.get_encoding('p50k_base')

class IngestPDFData():
    def __init__(self, path, embedding, index):
        self.path = path
        self.embedding = embedding
        self.index = index
        self.es = Elasticsearch('http://localhost:9200')

    def get_pdf_text_by_page(self, doc):
        page_text = []
        for page_num, page in enumerate(doc):
            page_dict = {}
            page_dict["page_num"] = page_num
            data = page.get_text()
            #cleaned_data = data.replace("\n", " ")
            cleaned_data = data.replace("\xa0", " ")
            page_dict["page_text"] = cleaned_data
            page_text.append(page_dict)
        return page_text

    def split_text(self, page_text):

        def tiktoken_len(text):
            tokens = tokenizer.encode(
                text,
                disallowed_special=()
            )
            return len(tokens)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=20,
            length_function=tiktoken_len,
            separators=["\n\n", "\n", " ", ""]
        )

        block_text = []
        token_length = 0

        for page in page_text:
            chunks = text_splitter.split_text(page["page_text"])
            for block_num, chunk in enumerate(chunks):
                block_dict = {}
                block_dict["page_num"] = page["page_num"]
                block_dict["block_num"] = block_num
                block_dict["text"] = chunk.replace("\n", " ")
                token_length += tiktoken_len(chunk)
                block_text.append(block_dict)
        print("Total token length:", token_length)
        return block_text
    
    def read_pdf(self):
        doc = fitz.open(self.path)
        page_text = self.get_pdf_text_by_page(doc)
        block_text = self.split_text(page_text)
        return block_text

    def create_embeddings(self, block_text):
        batch_limit = 100
        if self.embedding == "HF":
            embeddings = HuggingFaceEmbeddings()
        elif self.embedding == "ADA":
            model_name = 'text-embedding-ada-002'
            embeddings = OpenAIEmbeddings(
                model=model_name,
                openai_api_key=utils.KEY
            )
        index_name = self.index + "-" + self.embedding.lower()
        print(index_name)
        #metas = [{"page":f['page'], "type":f["type"]} for f in header_para]
        #texts = [f['text'] for f in header_para]
        texts = []
        metadatas = []
        ids = []
        for i, record in enumerate(tqdm(block_text)):
            metadata = {
                "page": record["page_num"],
                "block": record["block_num"],
                "text": record["text"]
            }
            texts.append(record["text"])
            metadatas.append(metadata)
            #print(str(uuid4()))
            ids.append(str(uuid4()))
            if len(metadatas) >= batch_limit:
                body = []
                embeds = embeddings.embed_documents(texts)
                for id, embedding, metadata, text in zip(ids, embeds, metadatas, texts):
                    entry = {"vector": embedding, "metadata": metadata, "text":text, "_id": id, "_index":index_name, "_op_type":"index"}
                    body.append(entry)
                helpers.bulk(self.es, body)
                texts = []
                metadatas = []
                ids = []
        body = []
        embeds = embeddings.embed_documents(texts)
        for id, embedding, metadata, text in zip(ids, embeds, metadatas, texts):
            entry = {"vector": embedding, "metadata": metadata, "text":text, "_id": id, "_index":index_name, "_op_type":"index"}
            body.append(entry)
        helpers.bulk(self.es, body)
        texts = []
        metadatas = []
        ids = []

    def ingest_data(self):
        block_text = self.read_pdf()
        self.create_embeddings(block_text)    

if __name__ == "__main__":
    ingestData = IngestPDFData(path='Data/Contract-Order Form.pdf', embedding="ADA", index="contractorderform")
    ingestData.ingest_data()