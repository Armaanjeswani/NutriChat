# NutriChat 🌿💬

NutriChat is a full-stack, retrieval-augmented generation (RAG) chatbot designed to answer nutrition-related questions. It uses a local large language model (LLM) through Ollama, a FastAPI backend, and a React frontend to provide a seamless, conversational experience.

## ✨ Features

- **Conversational AI**: Ask nutrition questions in natural language.
- **RAG Pipeline**: Retrieves relevant information from a knowledge base (a nutrition PDF) to provide accurate, context-aware answers.
- **Persistent Chat History**: Saves conversations to a MongoDB database.
- **Multi-Chat Interface**: Manage multiple conversations, similar to modern chatbot UIs.
- **Streaming Responses**: Bot responses are streamed word-by-word for a better user experience.
- **Clean, Modern UI**: Built with React and styled with Tailwind CSS.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Ollama, MongoDB
- **Frontend**: React (with Vite), JavaScript, Tailwind CSS, Axios
- **LLM**: Llama2 (or any other model supported by Ollama)

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- **Node.js**: [Download & Install Node.js](https://nodejs.org/en/download/)
- **Python**: [Download & Install Python](https://www.python.org/downloads/) (version 3.8+ recommended)
- **Ollama**: [Download & Install Ollama](https://ollama.com/) to run the LLM locally.
  - After installing Ollama, pull the model you wish to use (e.g., Llama2):
    ```sh
    ollama pull llama2
    ```

### 1. Backend Setup

First, set up and run the Python backend server.

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create and activate a Python virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    The `requirements.txt` file is necessary to install the correct Python packages. If it's missing, you can regenerate it from your local environment (while it's active) using this command:
    ```sh
    pip freeze > requirements.txt
    ```
    Then, install the packages:
    ```sh
    pip install -r requirements.txt
    ```

4.  **Create an environment file:**
    Create a file named `.env` in the `backend` directory and add your MongoDB connection string:
    ```
    MONGO_URI=mongodb+srv://<user>:<password>@<cluster-url>/...
    ```

5.  **Run the backend server:**
    ```sh
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

### 2. Frontend Setup

Next, set up and run the React frontend.

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```sh
    npm install
    ```

3.  **Run the frontend development server:**
    ```sh
    npm run dev
    ```
    The frontend will be running at `http://localhost:5173` and will connect to your backend server.

### 3. Start Chatting!

Open your browser to `http://localhost:5173` to start using NutriChat.

## 📁 Project Structure

```
rag-from-scratch/
├── backend/
│   ├── .gitignore
│   ├── main.py         # FastAPI application entrypoint
│   └── ...
├── frontend/
│   ├── .gitignore
│   ├── index.html
│   ├── src/            # React source code
│   └── ...
├── .gitignore          # Root gitignore
└── README.md
``` 