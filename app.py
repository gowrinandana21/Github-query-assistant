import streamlit as st
import re
from backend.repo_loader import clone_repo
from backend.index_repo import index_repository, collection_exists
from backend.vector_store import search
from backend.llm_explainer import explain_code

# -----------------------
# Page Config & Styling
# -----------------------
st.set_page_config(page_title="GitHub Query Assistant", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Outfit:wght@600&display=swap');
    
    /* Background */
    .stApp {
        background-color: #0D1117;
    }

    /* Logo/Heading */
    .logo-text {
        font-family: 'Outfit', sans-serif;
        color: #2F81F7;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-align: left;
    }

    /* Hide Default Avatars */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none;
    }

    /* Bubble Base Styling */
    .stChatMessage {
        background-color: #161B22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        color: #E6EDF3 !important;
        position: relative;
        max-width: 75%;
        padding: 8px 16px !important;
        margin-bottom: 25px !important;
        overflow: visible !important;
    }

    /* Assistant Tail (Top-Left) */
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        border-top-left-radius: 0px !important;
    }
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"])::before {
        content: "";
        position: absolute;
        top: -1px;
        left: -12px;
        width: 0;
        height: 0;
        border-right: 12px solid #30363d;
        border-bottom: 12px solid transparent;
    }

    /* User Tail (Top-Right) */
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        margin-left: auto !important;
        border-color: #2F81F7 !important;
        background-color: #0d419d26 !important;
        border-top-right-radius: 0px !important;
    }
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"])::after {
        content: "";
        position: absolute;
        top: -1px;
        right: -12px;
        width: 0;
        height: 0;
        border-left: 12px solid #2F81F7;
        border-bottom: 12px solid transparent;
    }

    /* Modern Text Input Fixes */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
    }

    [data-testid="stChatInput"] > div {
        border: 1px solid #30363d !important;
        border-radius: 25px !important;
        background-color: #161B22 !important;
    }

    /* Change Send Button Color from Red to GitHub Blue */
    [data-testid="stChatInputSubmitButton"] {
        color: #2F81F7 !important;
        background-color: transparent !important;
    }
    
    [data-testid="stChatInputSubmitButton"]:hover {
        color: #79c0ff !important;
    }

    /* Overall Text Styling */
    .stMarkdown p {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="logo-text">GitHub Query Assistant</div>', unsafe_allow_html=True)

# -----------------------
# Session State
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome. Please provide a **GitHub Repository URL** to begin."}
    ]
if "collection_name" not in st.session_state:
    st.session_state.collection_name = None

# -----------------------
# Chat Loop
# -----------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------
# Logic
# -----------------------
if prompt := st.chat_input("Ask a question or paste a URL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    is_url = re.match(r"https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+", prompt)

    if is_url:
        with st.chat_message("assistant"):
            with st.status("Analyzing Repository...", expanded=True) as status:
                repo_path, repo_name = clone_repo(prompt)
                st.session_state.collection_name = repo_name
                if not collection_exists(repo_name):
                    index_repository(repo_path, repo_name)
                status.update(label="Setup Complete", state="complete", expanded=False)
            
            response = f"Repository **{repo_name}** is indexed. How can I help you understand the code?"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    else:
        if not st.session_state.collection_name:
            with st.chat_message("assistant"):
                msg = "Please provide a GitHub URL first."
                st.info(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
        else:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    chunks = search(prompt, st.session_state.collection_name)
                    answer = explain_code(prompt, chunks)
                
                st.markdown(answer)
                with st.expander("Reference Files"):
                    for c in chunks:
                        st.text(f"File: {c['file_path']}")
                st.session_state.messages.append({"role": "assistant", "content": answer})