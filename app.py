import streamlit as st
import requests
from datetime import datetime

FASTAPI_URL = "http://localhost:8000/chat"

def create_new_chat():
    """Create a new chat session"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "conversation_messages" not in st.session_state:
        st.session_state.conversation_messages = []
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def get_model_response(messages, model, temperature, max_tokens, top_k, top_p, repeat_penalty):
    payload = {
        "messages": messages,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_k": top_k,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty
    }
    try:
        response = requests.post(FASTAPI_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"❌ Error contacting backend: {e}"

def main():
    st.set_page_config(
        page_title="Ollama Chat", 
        page_icon="🤖", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "conversation_messages" not in st.session_state:
        st.session_state.conversation_messages = []
    if "current_chat_id" not in st.session_state:
        create_new_chat()
    if "llm_model" not in st.session_state:
        st.session_state["llm_model"] = "tinyllama"

    # Sidebar for chat history and settings
    with st.sidebar:
        st.title("🤖 Ollama Chat")
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.conversation_messages = []
            st.session_state.current_chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.rerun()
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        st.session_state["llm_model"] = st.selectbox(
            "Select Model",
            ["tinyllama", "llama2", "mistral", "llama3.1", "llama3:8b", "deepseek-coder:1.3b-instruct", "nomic-embed-text:latest"],
            index=0
        )
        
        # Performance settings
        st.subheader("Performance")
        temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Lower = more factual, Higher = more creative"
        )
        max_tokens = st.slider(
            "Max Response Length",
            min_value=64,
            max_value=2048,
            value=512,
            step=64,
            help="Shorter responses are faster"
        )
        # Chat history in expandable section
        with st.expander("📚 Chat History", expanded=True):
            if st.session_state.chat_history:
                for i, (question, answer) in enumerate(reversed(st.session_state.chat_history)):
                    with st.container():
                        st.markdown(f"**Q{i+1}:** {question}")
                        st.markdown(f"**A{i+1}:** {answer[:150] + '...' if len(answer) > 150 else answer}")
                        st.divider()
            else:
                st.write("No history yet")

    # Main chat area
    st.title("Welcome to Ollama Chat! 🤖")
    st.caption("Optimized for fast responses with your local Ollama models")
    # Show conversation context info
    if st.session_state.conversation_messages:
        context_count = len(st.session_state.conversation_messages)
        st.info(f"💭 Conversation memory: {context_count} messages in context")
    # Chat input
    question = st.chat_input("Type your question here...", key="question_input")
    # Main interaction loop
    if question:
        with st.spinner(f"Generating response using {st.session_state['llm_model']}..."):
            st.session_state.chat_history.append((question, ""))
            with st.chat_message("user"):
                st.markdown(question)
            # Add user message to conversation context
            st.session_state.conversation_messages.append({"role": "user", "content": question})
            # Call FastAPI backend
            with st.chat_message("assistant"):
                response = st.empty()
                full_response = get_model_response(
                    messages=st.session_state.conversation_messages,
                    model=st.session_state["llm_model"],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_k=40,
                    top_p=0.9,
                    repeat_penalty=1.1
                )
                response.markdown(full_response)
            # Add assistant response to conversation context
            st.session_state.conversation_messages.append({"role": "assistant", "content": full_response})
            # Update history with full response
            st.session_state.chat_history[-1] = (question, full_response)

if __name__ == "__main__":
    main()
