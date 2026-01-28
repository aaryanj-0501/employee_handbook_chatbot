from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams,Distance,HnswConfigDiff,PayloadSchemaType
import os
from dotenv import load_dotenv
import logging

logger=logging.getLogger(__name__)
load_dotenv()

# Lazy-load client to prevent startup failure if Qdrant is unavailable
_client = None
_client_initialized = False

def get_qdrant_client():
    """
    Get or initialize the Qdrant client with lazy loading.
    This prevents server startup failure if Qdrant is temporarily unavailable.
    """
    global _client, _client_initialized
    
    if _client is not None:
        return _client
    
    try:
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        if not qdrant_url:
            logger.warning("QDRANT_URL environment variable not set")
            return None
        
        _client = QdrantClient(
            url=qdrant_url, 
            api_key=qdrant_api_key,
        )
        logger.info("Connected to Qdrant successfully")
        
        # Initialize collection if needed
        COLLECTION_NAME = os.getenv('QDRANT_COLLECTION')
        if COLLECTION_NAME and not _client_initialized:
            _initialize_collection(COLLECTION_NAME)
            _client_initialized = True
        
        return _client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return None

def _initialize_collection(collection_name: str):
    """Initialize Qdrant collection and indices if they don't exist."""
    try:
        if collection_name not in [col.name for col in _client.get_collections().collections]:
            _client.create_collection(
                collection_name=collection_name,  
                vectors_config=VectorParams(
                    size=1024,                    #Vector dimension
                    distance=Distance.COSINE      #distance metric
                ),
                hnsw_config=HnswConfigDiff(
                    m=16,                         #Number of edges per node
                    ef_construct=200,             #number of neighbors during idex construction-affects accuracy and speed
                    full_scan_threshold=1000      #threshold to full sacn below this size
                )
            )
            logger.info(f"Created Qdrant collection: {collection_name}")

        collection_info=_client.get_collection(collection_name)
        existing_indices=collection_info.payload_schema.keys() if collection_info.payload_schema else {}
        fields_to_index=[
            "policy_type",
            "section",
            "location",
            "employee_type"
        ]

        for field in fields_to_index:
            if field not in existing_indices:
                _client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD
                )
                logger.info(f"Created index for field: {field}")
        logger.info("Qdrant collection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {e}")

# Create a lazy-loading wrapper for backward compatibility
class LazyQdrantClient:
    def __getattr__(self, name):
        client = get_qdrant_client()
        if client is None:
            raise RuntimeError("Qdrant client is not available. Check your configuration and connection.")
        return getattr(client, name)

client = LazyQdrantClient()
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION', 'employee_handbook')
logger.info(f"Qdrant collection '{COLLECTION_NAME}' is set up.")
