from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
import ollama
import os
from dotenv import load_dotenv
import logging

load_dotenv()
#os.environ["OPENAI_API_KEY"]=os.getenv("OPEN_AI_API_KEY")
MODEL_NAME=os.getenv("EMBED_MODEL_NAME")
embedding_model=HuggingFaceEmbeddings(model=MODEL_NAME)

def get_embedding(text:str):
    response=embedding_model.embed_query(text)

    logging.info("Generated embedding successfully.")
    return response



