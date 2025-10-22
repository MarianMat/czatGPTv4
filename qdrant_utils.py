import os
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient, models
import streamlit as st

# --- Inicjalizacja klienta OpenAI (dla embeddingów) ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Nazwa kolekcji Qdrant ---
COLLECTION_NAME = "chat_memory"

def init_qdrant():
    """
    Inicjalizuje połączenie z Qdrant.
    Wymaga QDRANT_API_KEY i QDRANT_URL w sekcjach Streamlit secrets.
    """
    try:
        qdrant = QdrantClient(
            url=st.secrets["QDRANT_URL"],
            api_key=st.secrets["QDRANT_API_KEY"],
        )

        # Upewnij się, że kolekcja istnieje
        if COLLECTION_NAME not in [col.name for col in qdrant.get_collections().collections]:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

        return qdrant
    except Exception as e:
        st.error(f"❌ Błąd podczas inicjalizacji Qdrant: {e}")
        return None


def save_to_qdrant(prompt, answer, conversation_id, qdrant_client):
    """
    Zapisuje embedding tekstu i odpowiedzi do Qdrant.
    """
    try:
        if qdrant_client is None:
            st.warning("⚠️ Brak połączenia z Qdrant – pomijam zapis.")
            return

        # Połącz tekst użytkownika i odpowiedź asystenta
        combined_text = f"User: {prompt}\nAssistant: {answer}"

        # Utwórz embedding OpenAI (model text-embedding-3-small)
        emb_response = client.embeddings.create(
            input=combined_text,
            model="text-embedding-3-small"
        )
        vector = emb_response.data[0].embedding

        # Zbuduj punkt do zapisania
        point = models.PointStruct(
            id=str(uuid.uuid4()),  # unikalne ID
            vector=vector,
            payload={
                "conversation_id": str(conversation_id),
                "prompt": prompt,
                "answer": answer
            }
        )

        # Zapisz w Qdrant
        qdrant_client.upser_
