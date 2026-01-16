from pydantic import BaseModel

class HandbookQuery(BaseModel):
    question: str

    