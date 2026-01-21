import os
import uuid
from dotenv import load_dotenv
from fastapi import HTTPException,status
from config.qdrant import client
from utils.embeddings import get_embedding
from utils.chunker import clean_text,chunk_text
from utils import pdf_loader
from services.query_retriever import get_query_retriever
from services.generate_metadata import infer_policy_type,infer_section,infer_location,infer_employee_type
from services.final_result import extract_context,clean_output,answer_chain
import logging

logger=logging.getLogger(__name__)

load_dotenv()
collection_handbook=os.getenv("QDRANT_COLLECTION")

def add_vectors(chunks:str):
    try:
        if not chunks or len(chunks)==0:
            logger.info("No chunks provided")
            raise ValueError("No chunks to process")
        
        points=[]
        logger.info("Adding vectors to Qdrant collection.")
        for chunk in chunks:
            clean_chunk=clean_text(chunk)
            embedding=get_embedding(clean_chunk)
            points.append({
                "id":str(uuid.uuid4()),
                "vector":embedding,
                "payload":{
                    "text":clean_chunk,
                    "source":"employee_handbook",
                    "policy_type":infer_policy_type(clean_chunk),
                    "section":infer_section(clean_chunk),
                    "location":infer_location(clean_chunk),
                    "employee_type":infer_employee_type(clean_chunk)
                }
            })

        logger.info(f"Chunk added: len(points)")
        client.upsert(
            collection_name=collection_handbook,
            points=points
        )
        logger.info("Vectors added successfully.")
    except Exception as e:
        logger.error(f"Error in add_vectors:{str(e)}",exc_info=True)
        raise
    
async def get_result(query:str,limit:int=5):
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Query is empty")
        logger.info(f"Processing query with limit {limit}")
        query_result=get_query_retriever(query,limit)

        logger.info(query_result)
        if not query_result or not query_result.get('results'):
            logger.warning(f"No result found")
            return{
                "answer":"According to the employee handbook this information is not specified.",
                "sources":[]
            }
        context=extract_context(query_result)

        if not context:
            logger.info(f"No context extracted")
            return{
                "answer":"According to the employee handbook this information is not specified.",
                "sources":[]
            }
        
        logger.info("Generating answer using LLM chain")
        response = answer_chain.invoke({
            "question": query,
            "context": context
        })
        return clean_output(response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_result:{str(e)}",exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to process query")

async def process_handbook(file):
    try:
        file_location=f"backend/temp_files/{file.filename}"
        with open(file_location,"wb") as buffer:
            buffer.write(await file.read())
            
        logger.info("File saved")
        logger.info(f"File saved successfully")
        text=pdf_loader.load_pdf(file_location)

        if not text:
            logger.error("No text extracted from pdf")
            raise ValueError("Failed to extract text from PDF")
        
        chunks=chunk_text(text)
        logger.info(f"Total chunks created:{len(chunks)}")
        add_vectors(chunks)

        logger.info("Handbook processed and vectors added successfully")
        

    except Exception as e:
        logger.error(f"error processing handbook{str(e)}",exc_info=True)
        raise