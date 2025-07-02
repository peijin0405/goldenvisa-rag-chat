<p align="center">
  <img src="https://github.com/user-attachments/assets/58d5272a-60be-4918-9d51-4600f23299c5" alt="LusAI Assistant" width="400"/>
</p>

## LusAI Assistant for Golden Visa (Powered by RAG & Ollama)

This project demonstrates a document ingestion pipeline for Retrieval-Augmented Generation (RAG) using the [LangChain](https://www.langchain.com/) framework with an [Ollama](https://ollama.com/) local LLM backend. The pipeline converts local unstructured files into vector embeddings and stores them in a Chroma vector database, enabling semantic search and question answering.

## 🔧 Key Technologies

- **LangChain**: Modular framework for building LLM-powered applications, used for document loading, transformation, and RAG chain creation.
- **Ollama + LLM (e.g., Ollama3/Mistral)**: Local language model used as the reasoning engine.
- **Chroma**: Embedded vector database for storing and retrieving document embeddings.
- **FastEmbed**: Lightweight, high-speed embedding model for converting text to vector representations.
- **Streamlit**: Can be added for a simple interactive front-end.

## 📁 Features

- Loads PDF and TXT documents from local `./data` directory.
- Splits documents into manageable chunks using recursive character splitting.
- Generates vector embeddings using `FastEmbedEmbeddings`.
- Stores processed documents and metadata in a persistent Chroma DB.
- Sets up a basic RAG pipeline to answer questions using retrieved chunks and Ollama-powered LLM responses.

## 🚀 How to Use

1. **Install dependencies**:
   ```bash
   pip install langchain langchain-community chromadb fastembed
   ```

2. **Start Ollama with a supported model**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   Make sure Ollama is running and the model (e.g., llama3) is downloaded.
   ```bash
   ollama run llama3
   ```

3. **Run the notebook**
   ```bash
   streamlit run streamlit_app.py
   ```
   

## 📂 Folder Structure

```graphql
.
├── streamlit_app.py             # Main retrieval pipeline logic
├── data/                        # Directory with PDF and TXT documents
└── chroma_db/                   # Auto-created directory for Chroma vector store

```

## 🧠 Example Use Case
After ingesting Golden Visa documents, you can query:

"What are the requirements for Portugal's Golden Visa?"

The system will retrieve semantically relevant document chunks and generate a response using the local LLM.


