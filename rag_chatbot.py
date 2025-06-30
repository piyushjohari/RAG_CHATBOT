import streamlit as st
from dotenv import load_dotenv
from src.llm_calls import get_llm_answer
from src.chroma_manager import ChromaManager
from src.embeddings import Embedder

load_dotenv()
top_n_results = 10
embedder = Embedder()
chroma_manager = ChromaManager()

# ---- Streamlit UI starts here ----

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 RAG Chatbot Demo")
st.caption("Ask domain-specific questions based on your documentation!")

# Persistent chat history: messages = [{"role": "user"/"assistant", "content": "..."}]
if "messages" not in st.session_state:
    st.session_state.messages = []

def clear_history():
    st.session_state.messages = []

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    k = st.slider("Top-K retrieved context chunks", min_value=1, max_value=15, value=10)
    st.button("Restart Conversation", on_click=clear_history)
    show_context_chunks = st.toggle("Show retrieved context (sources)", value=True)
    st.markdown("---")
    st.info("Built with Streamlit. Backend is your RAG pipeline.")

# Chat message display
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Input area
query_text = st.chat_input("Type your question, or say hi...")

if query_text:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query_text})

    # RAG retrieval step: get top K chunks
    embeddings = embedder.embed_user_query(query_text)
    search_results = chroma_manager.query(embeddings, k)
    
    # LLM Query Result
    answer = get_llm_answer(query_text, search_results)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Show context optionally
    if show_context_chunks:
        with st.expander("🔍 Retrieved Context Chunks", expanded=False):
            st.markdown(f"{search_results}")

    st.rerun()  # Refresh chat
