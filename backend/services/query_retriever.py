from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config.qdrant import client,COLLECTION_NAME as collection_handbook
from utils.embeddings import get_embedding
from utils.llm_setup import set_llm
import logging

logger=logging.getLogger(__name__)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are extracting filters for an employee handbook search.

Strictly allowed metadata fields and values:
-policy_type: Leave, Payroll, Work From Home, Conduct, Security, Benefits, General
-section: Introduction, Policies, Procedures, Health and Safety, Employee Benefits, Code of Conduct, General
-location: Headquarters, Branch Office, Remote, On-site, General
-employee_type: Full-Time, Part-Time, Contractor, Intern, General

Rules:
- Do NOT add any text except the JSON Output
- Each of the 4 metadata fields MUST be present
- If a field is not explicitly mentioned, set it to "General"
- Return ONLY valid JSON with exactly 4 key:value pairs

"""
    ),
    (
        "human",
        """
Examples:

Query: "What is the leave policy of the company?"
Answer:
{{"policy_type":"Leave","section":"Policies","location":"General","employee_type":"General"}}

Query: "Is there a work from home policy for full-time employees?"
Answer:
{{"policy_type":"Work From Home","section":"General","location":"General","employee_type":"Full-Time"}}

Query: "Explain payroll procedures at the headquarters office"
Answer:
{{"policy_type":"Payroll","section":"Procedures","location":"Headquarters","employee_type":"General"}}

Query: "What benefits are available for interns?"
Answer:
{{"policy_type":"Benefits","section":"Employee Benefits","location":"General","employee_type":"Intern"}}

Query: "Code of conduct for contractors working remotely"
Answer:
{{"policy_type":"Conduct","section":"Code of Conduct","location":"Remote","employee_type":"Contractor"}}

Query: "Health and safety guidelines for branch office staff"
Answer:
{{"policy_type":"General","section":"Health and Safety","location":"Branch Office","employee_type":"General"}}

Now extract metadata for the following query.

Query: "{query}"
Answer:
"""
    )
])

llm=set_llm("query")
query_chain=prompt | llm | JsonOutputParser()

def extract_metadata(query:str):
    response=query_chain.invoke({"query":query})
    logger.info("Extracted Metadata: %s",response)
    return response

def build_filter(metadata:dict):
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
