from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from operator import itemgetter
import os
from langchain_core.output_parsers import StrOutputParser

class PdfChatService:
    # Config and variables
    embedding_model = "mxbai-embed-large:latest"
    chat_model = "llama3.1:8b"

    # In-memory session store
    session_store = {}

    '''
        Takes in the session_id of user and the uploaded file contents in bytes
        Does the whole pre-processing part including
        1. Data ingestion
        2. Chunking of doc
        3. Generate the embeddings and store it in the vector db
        
        And returns and instance of the db
    '''
    def process_uploaded_pdf(self, session_id: str, contents: bytes, db_dir: str = "./chroma") -> Chroma:
        uploaded_path = self.write_to_temp_dir(session_id, contents)
        chunked_docs = self.load_and_split_pdf(uploaded_path)
        db = self.generate_embeddings_and_store(session_id=session_id, docs=chunked_docs, db_dir=db_dir)

        return db

    # Takes in bytes and stores it in a temporary local directory mapped to current user's session id
    def write_to_temp_dir(self, session_id: str, contents: bytes) -> str:
        dir = f"./temp/{session_id}"
        os.makedirs(dir, exist_ok=True)

        file_path = f"{dir}/temp.pdf"
        with open(file_path, "wb") as file:
            file.write(contents)

        return file_path
    
    # Takes in the file_path of a pdf and loads and splits it
    def load_and_split_pdf(self, file_path: str) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(chunk_size = 800, chunk_overlap=50)
        chunked_docs = PyPDFLoader(file_path=file_path).load_and_split(text_splitter=splitter)

        return chunked_docs
    
    # Takes in documents, Generates it embeddings and stores it in a Chroma based vector db
    def generate_embeddings_and_store(self, session_id: str, docs: list[Document], db_dir: str) -> Chroma:
        db = self.get_user_chroma_store(session_id=session_id, db_dir=db_dir)
        db.add_documents(documents=docs)

        return db
    
    # Returns a user mapped chroma store
    def get_user_chroma_store(self, session_id: str, db_dir="./chroma") -> Chroma:
        embeddings = OllamaEmbeddings(model=self.embedding_model)
        collection_name = f"user_{session_id}_collection"
        vector_db = Chroma(
            embedding_function=embeddings, 
            collection_name=collection_name, 
            persist_directory=db_dir
        )

        return vector_db
    
    # Methods related to chat

    '''
        Checks if chat history for a given session_id exists and returns, If not creates it and returns
    '''
    def get_session_messages(self, session_id) -> BaseChatMessageHistory:
        if session_id not in self.session_store:
            self.session_store[session_id] = ChatMessageHistory()
        
        return self.session_store[session_id]
    
    def get_retriever(self, session_id) -> VectorStoreRetriever:
        db = self.get_user_chroma_store(session_id)
        retriever = db.as_retriever(k=2)

        return retriever

    def answer_query(self, session_id: str, input: str) -> str:
        llm = OllamaLLM(model=self.chat_model)
        template = ChatPromptTemplate.from_messages([
        ("system",'''You are a helpful assistant.
          Answer only based on the provided context.
          If the answer is not in the context, respond with “I don’t know based on the provided information.”
          Do not guess or make up anything.
          Keep responses concise and direct — no extra commentary.
         
         <context> {context} </context>'''),
         MessagesPlaceholder(variable_name="messages"),
         ("user", input)
    ])
        retriever = self.get_retriever(session_id)
        

        core_chain = (
            RunnablePassthrough.assign(context=itemgetter("input") | retriever)
            | template 
            | llm 
            | StrOutputParser()
        )

        chat_with_history_runnable = RunnableWithMessageHistory(
            runnable=core_chain, 
            get_session_history=self.get_session_messages, 
            input_messages_key="input", 
            history_messages_key="messages",
            output_messages_key= "output",
        )
        
        config = {'configurable': {'session_id': session_id}}
        res = chat_with_history_runnable.invoke({"input": input}, config=config)

        return str(res)

        