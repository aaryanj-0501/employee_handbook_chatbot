from fastapi import APIRouter,UploadFile,File,BackgroundTasks,HTTPException,status
from services.handbook_services import process_handbook,get_result
from models.handbook_model import HandbookQuery  
import logging

logger = logging.getLogger(__name__)

router=APIRouter()
#HOME
@router.get("/")
def welcome():
    logger.info("Welcome test")
    return {"message":"Welcome to Employee Handbook Bot!"}

@router.post("/upload-handbook")
async def upload_handbook(file: UploadFile = File(...),background_tasks: BackgroundTasks=None):
    try:
        logger.info(f"Upload request recieved for file:{file.filename}")
        if not file.filename:
            logger.error("No filename provided")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Filename is required")
        
        if not file.filename.endswith(".pdf"):
            logger.error("Invalid file format")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please upload a PDF File")
        
        background_tasks.add_task(process_handbook,file)
        logger.info(f"Background task started for file:{file.filename}")
    
        return {"status":"Handbook uploaded and processing started."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading handbook pdf:{str(e)}",exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error processing upload:{str(e)}")

@router.post("/chat")
async def handbook_query(query:HandbookQuery, limit:int=5):
    try:
        if not query.question or not query.question.strip():
            logger.error("Query is empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Question is empty")
        
        if limit<=0 or limit>10:
            logger.warning(f"Invalid limit value {limit}, chaning it to 5")
            limit=5
        
        logger.info("Query recieved")
        search_result=await get_result(query.question,limit)
        logger.info("Query processed sucessfully")
    
        return search_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query:{str(e)}",exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error processing query:{str(e)}")


