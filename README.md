# 🤖 AI Assistant – RAG-based Document Chatbot

python -m src.pipeline
python -m src.ingest    
uvicorn server:app --reload


An **AI-powered document assistant** built during a hackathon.
The project allows users to **upload/search documents** and **ask questions** using a **Retrieval-Augmented Generation (RAG)** pipeline powered by **FAISS**, **Sentence Transformers**, and a **FastAPI backend**, with a modern frontend interface.

---

## ✨ Features

* 📄 Document ingestion (TXT, PDF, DOCX)
* 🧠 Semantic search using **FAISS vector database**
* 💬 AI-powered question answering over your documents
* 🌍 Multi-language support (Arabic, French, English)
* ⚡ FastAPI backend with clean REST endpoints
* 🖥️ Modern frontend (React + Vite)
* 🔒 CORS-enabled API for frontend-backend communication

---

## 🏗️ Project Architecture

```text
hackathon/
│
├── B/                     # Backend
│   ├── server.py          # FastAPI server
│   ├── src/
│   │   ├── ingest.py      # Document cleaning & chunking
│   │   ├── retriever.py   # FAISS retrieval logic
│   │   ├── search.py      # Semantic search
│   │   ├── chatbot.py    # RAG response generation
│   │   └── config.py     # Configuration
│   └── data/
│       ├── raw_docs/      # Original documents
│       └── index/         # FAISS index files
│
├── frontend/              # Frontend (React / Vite)
│   ├── src/
│   └── public/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd hackathon
```

---

### 2️⃣ Backend Setup (FastAPI)

```bash
cd B
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file if needed:

```env
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

Run the server:

```bash
uvicorn server:app --reload
```

Backend will be available at:

```
http://localhost:8000
```

---

### 3️⃣ Ingest Documents

Place your documents inside:

```text
B/data/raw_docs/
```

Then run:

```bash
python src/ingest.py
```

This will:

* Clean documents
* Split into chunks
* Build FAISS index

---

### 4️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## 🔗 API Endpoints

| Method | Endpoint  | Description                       |
| ------ | --------- | --------------------------------- |
| POST   | `/chat`   | Ask questions to the AI assistant |
| POST   | `/search` | Semantic document search          |
| GET    | `/health` | Server health check               |

---

## 🧠 Technologies Used

* **Backend**: FastAPI, Python
* **AI / NLP**: Sentence Transformers, FAISS
* **Frontend**: React, Vite, Tailwind CSS
* **Vector DB**: FAISS
* **Environment**: Python 3.10+

---

## ⚠️ Notes

* `__pycache__` and `.pyc` files are ignored
* Large document sets may take time to index
* Designed for hackathon & prototype use

---

## 📌 Future Improvements

* ✅ Authentication & user sessions
* 📊 Document analytics
* 🧾 Source highlighting in answers
* ☁️ Cloud deployment (Docker + AWS/GCP)
* 🧠 Streaming AI responses

---

## 👤 Author

**Ahmed Ghoul**
Computer Science Student – Web & Network Development

---

## 📄 License

This project is licensed under the **MIT License**.

---

⭐ If you like this project, give it a star!
