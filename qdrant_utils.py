import os
import uuid
import streamlit as st
from openai import OpenAI
from qdrant_client import QdrantClient, models

# --- Inicjalizacja klienta OpenAI (dla embeddingów) ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Nazwa kolekcji ---
COLLECTION_NAME = "chat_memory"


def init_qdrant():
    """Inicjalizuje połączenie z Qdrant Cloud."""
    try:
        qdrant = QdrantClient(
            url=st.secrets["QDRANT_URL"],
            api_key=st.secrets["QDRANT_API_KEY"]
        )

        # Sprawdź, czy kolekcja istnieje — jeśli nie, utwórz
        collections = qdrant.get_collections().collections
        if COLLECTION_NAME not in [c.name for c in collections]:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE
                )
            )
        return qdrant

    except Exception as e:
        st.error(f"❌ Błąd inicjalizacji Qdrant: {e}")
        return None


def save_to_qdrant(prompt, answer, conversation_id, qdrant_client):
    """Zapisuje embedding (prompt + odpowiedź) w Qdrant."""
    try:
        if qdrant_client is None:
            st.warning("⚠️ Brak połączenia z Qdrant — zapis pominięty.")
            return

        combined_text = f"User: {prompt}\nAssistant: {answer}"

        # Tworzenie embeddingu
        emb = client.embeddings.create(
            input=combined_text,
            model="text-embedding-3-small"
        )
        vector = emb.data[0].embedding

        # Przygotowanie punktu do zapisu
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "conversation_id": str(conversation_id),
                "prompt": prompt,
                "answer": answer
            }
        )

        # Zapis do kolekcji
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )

    except Exception as e:
        st.warning(f"⚠️ Nie udało się zapisać danych do Qdrant: {e}")
