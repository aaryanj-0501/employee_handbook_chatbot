import fitz
import logging

logger=logging.getLogger(__name__)

def load_pdf(file_path:str) -> str:
    try:
        if isinstance(file_path,(bytes,bytearray)):
            reader=fitz.open(stream=file_path,filetype="pdf")

        else:
            reader=fitz.open(file_path)
        text=""
        logger.info("Load pdf called")
        for page in reader:
            text+=page.get_text()+" "

        logger.info(text[:50])

        return text
    except Exception:
        return ""