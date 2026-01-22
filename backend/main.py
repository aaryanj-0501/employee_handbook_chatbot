from fastapi import FastAPI
from routes.handbook_routes import router
from routes.auth_routes import router as auth_router
from starlette.middleware.cors import CORSMiddleware
from middleware.rate_limit_middleware import RateLimitMiddleware
import logging
from config.logging_config import setup_logging
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Startup logic
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Employee Handbook Chatbot")

    yield

    #Shutdown logic 
    logger.info("Shutting down Employee Handbook Chatbot")

app = FastAPI(title="Employee Handbook Bot",lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)

