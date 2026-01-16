from fastapi import FastAPI
from routes.handbook_routes import router
from starlette.middleware.cors import CORSMiddleware
import logging
from config.logging_config import setup_logging

app=FastAPI(title="Employee Handbook Bot")

@app.on_event("startup")
def startup():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Employee Handbook Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

