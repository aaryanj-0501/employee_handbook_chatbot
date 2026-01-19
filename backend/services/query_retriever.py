from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config.qdrant import client,COLLECTION_NAME as collection_handbook
from utils.embeddings import get_embedding
from utils.llm_setup import set_llm
import json
import logging

logger=logging.getLogger(__name__)

prompt=PromptTemplate(
    input_variables=["query"],
    template="""
You are extracting filters for an employee handbook search.

Strictly allowed metadata fields and values:
-policy_type:Leave,Payroll,Work From Home, Conduct, Security, Benefits
-section:Introduction, Policies, Procedures, Health and Safety, Employee Benefits, Code of Conduct
-location:Headquarters, Branch Office, Remote, On-site
-employee_type:Full-Time, Part-Time, Contractor, Intern"
        
Given the user query, extract relevant metadata fields with one value per field.
Return ONLY the JSON format of the 4 metadata key:value pairs. 
If a field is not mentioned, omit it.
Do not add explanations OR introductory messages.       
    
Query:{query}"""
)
llm=set_llm("query")
query_chain=LLMChain(llm=llm,prompt=prompt)

def extract_metadata(query:str):
    response=query_chain.run(query)
    logger.info("Extracted Metadata:",response)
    return json.loads(response)

def build_filter(metadata):
    if not metadata:
        return None
    
    conditions=[]
    for k,val in metadata.items():
        conditions.append(
            FieldCondition(
                key=k,
                match=MatchValue(value=val)
            )
        )

    return Filter(should=conditions)

def get_query_retriever(query:str,limit:int=5):
    metadata=extract_metadata(query)
    filter=build_filter(metadata)

    embedding=get_embedding(query)
    
    search_result=client.query_points(
        collection_name=collection_handbook,
        query=embedding,
        query_filter=filter,
        limit=limit,
        with_payload=True,
    )

    return {
        "query":query,
        "results":[
            {
                "id":point.id,
                "score":point.score,
                "payload":point.payload
            }
            for point in search_result.points
        ]
    }
