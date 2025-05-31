import os
import re
from langchain_community.document_loaders import JSONLoader
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def load_json(file_path:str):
  loader = JSONLoader(
    file_path = file_path,
    jq_schema='{"사건번호": .["사건번호"], "선고일": .["선고일"], "주문": .["주문"], "이유": .["이유"]}',
    text_content = False
  )
  return loader.load()

def create_faiss_db(docs:Document, embeddings):
  db = FAISS.from_documents(docs, embeddings)
  return db

def save_faiss_db(db: FAISS, file_path: str):
  file_name = os.path.basename(file_path)
  trans_name = re.sub("[가-힣]", "_", file_name).replace(".json", "")
  save_dir = os.path.join("test", "faiss_index", trans_name)
    
  if not os.path.exists(save_dir):
    os.makedirs(save_dir, exist_ok=True)
  
  db.save_local(save_dir)

def load_faiss_db(embeddings, file_path:str="./faiss_db"):
  db = FAISS.load_local(file_path, embeddings)
  return db

def create_rag_model(db:FAISS):
  llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
  retriever = db.as_retriever()

  rag_model = RetrievalQA.from_chain_type(
      llm=llm,
      chain_type="stuff",
      retriever=retriever,
      return_source_documents=True
    )
  
  return rag_model