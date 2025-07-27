# PDF Chat Application

A Streamlit-based web application that allows users to upload PDF documents and chat with them using AI. The application uses LangChain, Ollama, and ChromaDB to provide intelligent question-answering capabilities based on the content of uploaded PDFs.

## Features

- **PDF Upload**: Upload PDF documents directly through the web interface
- **Document Processing**: Automatic text extraction and chunking from PDF files
- **Vector Search**: Efficient document retrieval using ChromaDB vector database
- **Conversational AI**: Chat with your PDF documents using Ollama's LLaMA 3.1 model
- **Session Management**: Each user session maintains its own document store and chat history
- **Real-time Chat**: Interactive chat interface with message history

## Service Architecture

The core functionality is handled by the `PdfChatService` class located in `services/pdf_chat_service.py`. This service provides:

### Key Components:

1. **Document Processing Pipeline**:
   - PDF loading and text extraction using PyPDFLoader
   - Text chunking with RecursiveCharacterTextSplitter (800 characters with 50 character overlap)
   - Vector embeddings generation using Ollama's `mxbai-embed-large` model

2. **Vector Database**:
   - ChromaDB for storing and retrieving document embeddings
   - Session-based collections for multi-user support
   - Persistent storage in the `./chroma` directory

3. **Chat System**:
   - LLaMA 3.1 8B model for natural language understanding
   - Context-aware responses based on retrieved document chunks
   - In-memory chat history management per session
   - RAG (Retrieval-Augmented Generation) architecture

4. **Session Management**:
   - Unique session IDs for each user
   - Temporary file storage for uploaded PDFs
   - Isolated vector stores per session

### Workflow:
1. User uploads a PDF file
2. File is temporarily stored and processed
3. Document is chunked and converted to embeddings
4. Embeddings are stored in ChromaDB with session-specific collection
5. User can ask questions about the document
6. System retrieves relevant chunks and generates contextual responses

## Prerequisites

Before running the application, ensure you have:

- Python 3.8 or higher
- Ollama installed and running locally
- The following Ollama models pulled:
  - `mxbai-embed-large:latest` (for embeddings)
  - `llama3.1:8b` (for chat responses)

To install Ollama and pull the required models:
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull required models
ollama pull mxbai-embed-large:latest
ollama pull llama3.1:8b
```

## Installation & Setup

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd pdf_chat_tw_assignment
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Ollama is running**:
   Make sure the Ollama service is running and the required models are available.

## Running the Application

From the project root directory, run:

```bash
streamlit run app.py
```

The application will start and be available at `http://localhost:8501` (or the URL displayed in your terminal).

## Usage

1. **Upload PDF**: Click "Upload a pdf to get started!" and select your PDF file
2. **Wait for Processing**: The application will process your document and display "File processed ✅"
3. **Start Chatting**: Use the text input at the bottom to ask questions about your PDF
4. **View Responses**: Chat history will be displayed with user questions and AI responses

## Project Structure

```
pdf_chat_tw_assignment/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── services/
│   └── pdf_chat_service.py        # Core PDF processing and chat service
├── chroma/                         # ChromaDB storage directory
└── temp/                          # Temporary PDF storage
```

## Technical Details

- **Framework**: Streamlit for web interface
- **LLM**: Ollama with LLaMA 3.1 8B model
- **Embeddings**: Ollama mxbai-embed-large model
- **Vector Database**: ChromaDB
- **Document Processing**: LangChain with PyPDFLoader
- **Chat Interface**: streamlit-chat for message display

## Notes

- Each user session maintains its own document collection in ChromaDB
- Temporary PDF files are stored in session-specific directories
- The application uses in-memory storage for chat history (resets on restart)
- Vector embeddings are persisted in the ChromaDB directory
