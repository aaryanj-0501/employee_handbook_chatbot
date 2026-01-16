from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams,Distance,HnswConfigDiff,PayloadSchemaType
import os
from dotenv import load_dotenv
import logging

load_dotenv()
qdrant_url = os.getenv('QDRANT_URL')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

client = QdrantClient(
    url=qdrant_url, 
    api_key=qdrant_api_key,
)

COLLECTION_NAME=os.getenv('QDRANT_COLLECTION')

if COLLECTION_NAME not in [col.name for col in client.get_collections().collections]:
    client.create_collection(
        collection_name=COLLECTION_NAME,  
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

collection_info=client.get_collection(COLLECTION_NAME)
existing_indices=collection_info.payload_schema.keys()
fields_to_index=[
    "policy_type",
    "section",
    "location",
    "employee_type"
]

for field in fields_to_index:
    if field not in existing_indices:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD
        )
        print("Indices created")
print("Indices already created")
logging.info(f"Qdrant collection '{COLLECTION_NAME}' is set up.")
