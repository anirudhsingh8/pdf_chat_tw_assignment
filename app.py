import streamlit as st
import uuid
from services.pdf_chat_service import PdfChatService
from streamlit_chat import message
import time

def on_input_change():
    prompt = st.session_state.user_input
    if prompt:
        st.session_state.chats.append(prompt)
        session_id = st.session_state.session_id
        llm_response = st.session_state.service.answer_query(session_id=session_id, input=prompt)
        st.session_state.chats.append(llm_response)
        st.session_state.user_input = None

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chats = []
    st.session_state.service = PdfChatService()
    print(f"# Initialized session with session_id: {st.session_state.session_id}")

st.title("AskPDF")
if "uploaded_doc" not in st.session_state:
    uploaded_doc = st.file_uploader("Upload a pdf to get started!", type="pdf", accept_multiple_files=False)
    if uploaded_doc:
        file_bytes = uploaded_doc.getvalue()
        session_id = st.session_state.session_id
        st.session_state.uploaded_doc = uploaded_doc
        st.session_state.service.process_uploaded_pdf(session_id=session_id, contents=file_bytes)
        st.write("File processed ✅")
        time.sleep(1)
        st.rerun()

if "uploaded_doc" in st.session_state:
    st.text(f"Session id: {st.session_state.session_id}")
    
    st.subheader("Chats")
    chat_container = st.empty()

    with chat_container.container():    
        for i in range(len(st.session_state.chats)):
            chat = st.session_state.chats[i]
            message(chat, is_user=i%2==0, key=f"{i}_user")

    with st.container():
        st.text_input(label="Ask anything here", key="user_input", on_change=on_input_change)