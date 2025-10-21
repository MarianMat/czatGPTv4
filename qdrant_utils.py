from qdrant_client import QdrantClient, models
from openai import OpenAI
import streamlit as st

def init_qdrant():
    client = QdrantClient(
        url=st.secrets["QDRANT_URL"],
        api_key=st.secrets["QDRANT_API_KEY"],
    )
    try:
        client.get_collection("conversations")
    except:
        client.recreate_collection(
            collection_name="conversations",
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )
    return client

def save_to_qdrant(user_msg, assistant_msg, conversation_id, client):
    openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    emb_user = openai_client.embeddings.create(model="text-embedding-3-small", input=user_msg).data[0].embedding
    emb_assistant = openai_client.embeddings.create(model="text-embedding-3-small", input=assistant_msg).data[0].embedding

    client.upsert(
        collection_name="conversations",
        points=[
            models.PointStruct(
                id=None,
                vector=emb_user,
                payload={"conversation_id": conversation_id, "role": "user", "content": user_msg}
            ),
            models.PointStruct(
                id=None,
                vector=emb_assistant,
                payload={"conversation_id": conversation_id, "role": "assistant", "content": assistant_msg}
            )
        ]
    )
