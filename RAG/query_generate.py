import utils
from langchain import ElasticVectorSearch
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

def search_with_hf(query):
    embedding = HuggingFaceEmbeddings()
    elastic_vector_search = ElasticVectorSearch(
        elasticsearch_url="http://localhost:9200",
        index_name="amazoncom-inc-prospectus-hf",
        embedding=embedding
    )
    docs = elastic_vector_search.similarity_search(query)
    print([doc.page_content for doc in docs])

def search_with_openai(query):
    model_name = 'text-embedding-ada-002'

    embedding = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=utils.KEY
    )
    elastic_vector_search = ElasticVectorSearch(
        elasticsearch_url="http://localhost:9200",
        index_name="amazoncom-inc-prospectus-ada",
        embedding=embedding
    )
    
    docs = elastic_vector_search.similarity_search(query)
    for doc in docs:
        print(doc["page_content"])
        print("******")

def generate_by_query(query, repo, embed):
    index = repo + "-" + embed.lower()
    if embed == "HF":
        embedding = HuggingFaceEmbeddings()
    elif embed == "ADA":
        model_name = 'text-embedding-ada-002'

        embedding = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=utils.KEY
        )
    elastic_vector_search = ElasticVectorSearch(
        elasticsearch_url="http://localhost:9200",
        index_name=index,
        embedding=embedding
    )
    # completion llm
    llm = ChatOpenAI(
        openai_api_key=utils.KEY,
        model_name='gpt-3.5-turbo',
        temperature=0.0
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=elastic_vector_search.as_retriever()
    )
    return qa.run(query)
if __name__ == "__main__":
    query = "What is par call date?"
    #search_with_openai()
    #search_with_hf(query)
    print(generate_by_query(query))