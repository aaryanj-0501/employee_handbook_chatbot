from langchain_community.llms.ollama import Ollama
import os
from dotenv import load_dotenv

load_dotenv()

QUERY_MODEL=os.getenv("CHAT_MODEL_NAME")
ANSWER_MODEL=os.getenv("ANSWER_MODEL")

def set_llm(type:str):
    llm=Ollama(
        model=(ANSWER_MODEL if type=="answer" else QUERY_MODEL),
        temperature=0
    )
    return llm