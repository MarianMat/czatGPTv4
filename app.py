import streamlit as st
from openai import OpenAI
from qdrant_utils import init_qdrant, save_to_qdrant
from db_utils import init_db, create_conversation, list_conversations, get_messages, save_message, get_conversation, update_conversation_name
from datetime import datetime
import re

# --- Inicjalizacja ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
qdrant_client = init_qdrant()
init_db()

model_pricings = {
    "gpt-4o": {"Opis": "Multimodalny – tekst, obraz, głos", "Input": 2.5, "Output": 10.0},
    "gpt-4o-mini": {"Opis": "Lekki i tani do chatbotów", "Input": 0.15, "Output": 0.6},
    "gpt-4-turbo": {"Opis": "Szybki tekstowy model", "Input": 1.5, "Output": 6.0},
    "gpt-3.5-turbo": {"Opis": "Budżetowa opcja", "Input": 0.5, "Output": 1.5}
}

translations = {
    "Polski": {
        "title": "🧠 MójGPT – Inteligentny czat z pamięcią",
        "chat_title": "💬 Rozmowa",
        "input_placeholder": "Zadaj pytanie",
        "language_switch": "🌍 Język interfejsu",
        "conversation_list": "📂 Wybierz rozmowę",
        "new_conversation": "🔄 Nowa rozmowa",
        "default_conversation_name": "Rozmowa {}",
        "model_select": "🤖 Wybierz model GPT",
        "personality": "🎭 Styl GPT",
        "memory_mode": "🧠 Tryb pamięci",
        "default_personality": "Jesteś ekspertem AI, który pomaga tworzyć projekty w Pythonie z wykorzystaniem API OpenAI."
    }
}

# --- Funkcja generująca automatyczny tytuł rozmowy ---
def generate_title_from_text(text: str) -> str:
    text = text.strip().split("\n")[0]
    text = re.sub(r"[^\w\sąęćłńóśźżĄĘĆŁŃÓŚŹŻ]", "", text)
    if len(text) > 50:
        text = text[:50] + "..."
    return text or "Nowa rozmowa"

# --- Funkcja generująca odpowiedź ---
def get_reply(prompt: str, memory: list, model: str, personality: str) -> dict:
    msgs = [{"role": "system", "content": personality}] + memory + [{"role": "user", "content": prompt}]
    resp = client.chat.completions.create(model=model, messages=msgs)
    usage = resp.usage
    return {
        "role": "assistant",
        "content": resp.choices[0].message.content,
        "usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
    }

# --- Konfiguracja strony ---
st.set_page_config(page_title="MójGPT", layout="centered")

# --- Stan aplikacji ---
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
    st.session_state.model = "gpt-4o"
    st.session_state.chatbot_personality = translations["Polski"]["default_personality"]
    st.session_state.memory_mode = "Pełna historia"
    st.session_state.conversation_title = None
    st.session_state.temp_prompt = ""  # Tymczasowy prompt dla nowej rozmowy
    st.session_state.first_message_sent = False

# --- Sidebar: język ---
lang = st.sidebar.selectbox(translations["Polski"]["language_switch"], ["Polski"], index=0)
t = translations[lang]

# --- Sidebar: Styl GPT (prompt) nad przyciskiem Nowa rozmowa ---
st.sidebar.markdown("---")
st.sidebar.subheader(t["personality"])
st.session_state.chatbot_personality = st.sidebar.text_area(
    "Treść promptu (rola asystenta):",
    value=st.session_state.get("chatbot_personality", translations["Polski"]["default_personality"]),
    height=150
)

# --- Sidebar: Nowa rozmowa ---
st.sidebar.markdown("---")
if st.sidebar.button(t["new_conversation"]):
    st.session_state.keep_prompt = st.sidebar.radio(
        "Czy chcesz zachować obecny prompt?", ["Tak", "Nie"], index=0
    )
    if st.session_state.keep_prompt == "Tak":
        st.session_state.temp_prompt = st.session_state.chatbot_personality
    else:
        st.session_state.temp_prompt = ""  # puste pole, użytkownik musi wpisać prompt
    st.session_state.conversation_id = None
    st.session_state.first_message_sent = False
    st.session_state.conversation_title = None

# --- Sidebar: Lista rozmów ---
st.sidebar.markdown(f"**{t['conversation_list']}**")
for cid, name in list_conversations():
    if st.sidebar.button(name, key=f"conv_{cid}"):
        st.session_state.conversation_id = cid
        st.session_state.first_message_sent = True
        conv = get_conversation(cid)
        st.session_state.chatbot_personality = conv[2]  # prompt z DB

# --- Sidebar: Model ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ " + t["model_select"])
st.session_state.model = st.sidebar.selectbox(
    t["model_select"],
    list(model_pricings.keys()),
    index=list(model_pricings.keys()).index(st.session_state.get("model", "gpt-4o"))
)

# --- Sidebar: Tryb pamięci ---
st.sidebar.markdown("---")
memory_mode_options = ["Ostatnie 10 wiadomości", "Rozszerzona (30)", "Pełna historia"]
st.session_state.memory_mode = st.sidebar.selectbox(
    t["memory_mode"],
    memory_mode_options,
    index=memory_mode_options.index(st.session_state.get("memory_mode", "Pełna historia"))
)

# --- Główne okno ---
st.title(t["title"])

# --- Historia czatu ---
messages = []
if st.session_state.conversation_id:
    messages = get_messages(st.session_state.conversation_id)
    conv = get_conversation(st.session_state.conversation_id)
    st.subheader(f"{t['chat_title']}: {conv[1]}")
    st.caption(f"🧩 Aktualny prompt: {st.session_state.chatbot_personality}")
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    st.subheader(f"{t['chat_title']}: Nowa rozmowa")
    st.caption(f"🧩 Aktualny prompt: {st.session_state.temp_prompt or 'Wpisz prompt aby rozpocząć rozmowę'}")

# --- Obsługa inputu ---
prompt = st.chat_input(t["input_placeholder"])
if prompt:
    # --- Pierwsza wiadomość nowej rozmowy ---
    if st.session_state.conversation_id is None:
        if not st.session_state.temp_prompt:
            st.warning("🛑 Wpisz najpierw prompt dla roli asystenta!")
        else:
            convo_id = create_conversation(
                generate_title_from_text(st.session_state.temp_prompt),
                st.session_state.temp_prompt,
                st.session_state.model,
                st.session_state.memory_mode,
                lang
            )
            st.session_state.conversation_id = convo_id
            st.session_state.first_message_sent = True
            messages = []

    # --- Standardowa logika dla wszystkich wiadomości ---
    if st.session_state.conversation_id:
        save_message(st.session_state.conversation_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- Przygotowanie pamięci ---
        if st.session_state.memory_mode == "Ostatnie 10 wiadomości":
            memory = messages[-10:]
        elif st.session_state.memory_mode == "Rozszerzona (30)":
            memory = messages[-30:]
        else:
            memory = messages

        # --- Generowanie odpowiedzi ---
        reply = get_reply(prompt, memory, st.session_state.model, st.session_state.chatbot_personality)
        save_message(st.session_state.conversation_id, "assistant", reply["content"])

        # --- Automatyczne nadanie tytułu, jeśli to pierwsza wiadomość ---
        if not st.session_state.conversation_title:
            new_title = generate_title_from_text(reply["content"])
            update_conversation_name(st.session_state.conversation_id, new_title)
            st.session_state.conversation_title = new_title

        with st.chat_message("assistant"):
            st.markdown(reply["content"])

        save_to_qdrant(prompt, reply["content"], f"Conv{st.session_state.conversation_id}", qdrant_client)


