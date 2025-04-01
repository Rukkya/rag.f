# RAG Chatbot with Multi-Model Support

## Overview
This project implements a **Retrieval-Augmented Generation (RAG) Chatbot** that uses multiple state-of-the-art models such as **Gimini, GPT, Anthropic, Bloom, MPT,** and **Llama**. The chatbot allows real-time multi-chat support, including the ability to upload documents (PDF, DOCX, TXT) for content processing. Additionally, it integrates a robust **ChromaDB** for storing embeddings, a **Flask** backend for API integration, and a **Streamlit** frontend for user interaction. The system also supports processing **RSS feeds** for live content retrieval.

## Features
- **Multi-Model Support**: Supports Gimini, GPT, Anthropic, Bloom, MPT, and Llama models for diverse chatbot interactions.
- **Document Upload**: Allows users to upload documents (PDF, DOCX, TXT) for automatic text extraction and chatbot interaction.
- **Embeddings Storage**: Utilizes **ChromaDB** for storing and retrieving embeddings, enhancing search and response generation.
- **Multi-Chat Support**: Handles simultaneous conversations, making it easier for users to switch between chats.
- **RSS Feed Integration**: Can process RSS feeds to gather real-time information for chatbot interactions.
- **Flask Backend**: API integration using Flask for smooth communication with the models.
- **Streamlit Frontend**: Interactive UI built with Streamlit for ease of use and file uploads.
- **PostgreSQL**: Data storage for chat history, user interactions, and system data.

## Requirements
- Python 3.7+
- Flask
- Streamlit
- ChromaDB
- PostgreSQL
- OpenAI GPT API (or any other model API you choose to use)
- Additional dependencies can be installed via `requirements.txt`.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/Rukkya/rag-chatbot.git
    cd rag-chatbot
    ```

2. Set up a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up PostgreSQL and ChromaDB following the appropriate setup guides:
    - **PostgreSQL**: Ensure PostgreSQL is installed and a database is set up for storing chat history.
    - **ChromaDB**: Follow [ChromaDB installation guide](https://www.chroma.ai/docs).

## Usage
1. **Start Flask Backend**:
    ```bash
    python app.py
    ```

2. **Start Streamlit Frontend**:
    ```bash
    streamlit run frontend.py
    ```

3. **Interact with the Chatbot**: 
   - Visit the Streamlit UI and start interacting with the chatbot.
   - You can upload PDFs, DOCX, or TXT files, and the chatbot will extract and process the text for chat interactions.
   - You can also initiate multiple chats and switch between them.
   - The chatbot will use different models depending on the user's selection.

4. **Processing RSS Feeds**: 
   - RSS feeds can be submitted for real-time content retrieval and incorporated into the chat responses.

## Project Structure
rag-chatbot/ 
│── app.py # Main Flask backend API 
│── frontend.py # Streamlit frontend UI 
│── requirements.txt # Dependencies
│── models/ # Directory for storing model code or API interactions 
│── database/ # Database setup for PostgreSQL and ChromaDB 
│── README.md # Project documentation


## Acknowledgments
- **ChromaDB** for efficient embeddings storage.
- **Flask** for the backend API.
- **Streamlit** for the interactive UI.
- **OpenAI GPT, Anthropic, Bloom, MPT, and Llama** for model integration.
