from fastapi import HTTPException
from utils.llm_setup import set_llm
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain

llm=set_llm("answer")
rag_prompt=PromptTemplate(
    input_variables=["question","context"],
    template="""
You are an AI assistant answering questions strictly from an employee handbook.

RULES:
-Answer ONLY using the provided context.
-Do NOT use external knowledge. 
-If the answer is not present in the context , say:
"According to the employee handbook, this information is not specified."

ANSWER FORMAT:
- Provide a clear, concise, and professional response.
- Use complete sentences.
- If multiple points are mentioned, use bullet points.
- Do NOT mention the word "context" or quote it verbatim unless required.

Context:
{context}

Question:
{question}

Answer:
"""
)

answer_chain=LLMChain(
    llm=llm,
    prompt=rag_prompt
)

def extract_context(query_result):
    if not isinstance(query_result, dict) or "results" not in query_result:
        raise HTTPException(
            status_code=500,
            detail="Invalid query result structure"
        )
    context=[]
    for query in query_result['results']:
        context.append(query['payload']['text'])

    return context

def clean_output(text:str)->str:
    lines=text.splitlines()
    cleaned=[]
    for line in lines:
        if line.strip() and not line.lower().startswith(("of course","sure","here is")):
            cleaned.append(line.strip())
    
    return cleaned
