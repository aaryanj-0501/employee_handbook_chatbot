from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 120) -> list[str]:
    """
    Splits the input text into chunks using RecursiveCharacterTextSplitter.

    Args:
        text (str): The text to be chunked.
        chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of overlapping characters between chunks.

    Returns:
        list[str]: A list of text chunks.
    """

    if not text or not isinstance(text, str):
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n",
                    "\n",
                    " ",
                    ""]
    )
    chunks = text_splitter.split_text(text)

    
    return chunks

def clean_text(text:str) -> str:
    if not text or not isinstance(text,str):
        return None
    #Replace new lines and tabs with spaces
    text=re.sub(r"[\n\t\r]+"," ",text)
    #Remove multiple spaces
    text=re.sub(r"\s{2,}"," ",text)

    return text.strip()