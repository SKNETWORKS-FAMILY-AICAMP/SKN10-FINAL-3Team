from .RAG import *
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def decode_unicode(text):
    try:
        return text.encode().decode('unicode_escape')
    except:
        return text


def main(query: str):
    DATA_PATH = "test/data/"
    data_list = os.listdir(DATA_PATH)
    docs = []

    for data in data_list:
      docs.extend(load_json(os.path.join(DATA_PATH, data)))

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)
    db = create_faiss_db(docs, embeddings)
    save_faiss_db(db, os.path.join(DATA_PATH, "faiss_index"))

    results = db.similarity_search(query, k=3)

    return {"documents_list": results}