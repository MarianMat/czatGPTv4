from qdrant_client import QdrantClient, models
from openai import OpenAI
import uuid

def save_to_qdrant(prompt, reply, conv_id, client):
    try:
        # Stworzenie embeddingu z treści promptu
        openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        emb = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=prompt
        ).data[0].embedding

        # Upewnij się, że reply to tekst
        if isinstance(reply, dict):
            reply_text = reply.get("content", str(reply))
        else:
            reply_text = str(reply)

        # Tworzenie punktu do zapisania
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=emb,
            payload={
                "conversation_id": str(conv_id),
                "prompt": str(prompt),
                "reply": reply_text,
            },
        )

        client.upsert(collection_name="chat_memory", points=[point])

    except Exception as e:
        print(f"❌ Błąd zapisu do Qdrant: {e}")
