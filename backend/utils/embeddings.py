from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
import logging

logger=logging.getLogger(__name__)

load_dotenv()

MODEL_NAME=os.getenv("EMBED_MODEL_NAME")
embedding_model=HuggingFaceEmbeddings(model_name=MODEL_NAME)

def get_embedding(text:str):
    response=embedding_model.embed_query(text)

    logger.info("Generated embedding successfully.")
    return response



