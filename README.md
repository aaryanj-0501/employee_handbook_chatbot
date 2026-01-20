# 🧠 Employee Handbook Chatbot

### RAG-Based Intelligent HR Assistant

## 📌 Project Overview

The **Employee Handbook Chatbot** is an AI-powered assistant designed to help employees quickly understand company policies, leave rules, benefits, and HR guidelines by chatting with an employee handbook document.

The chatbot uses **Retrieval-Augmented Generation (RAG)** to fetch accurate answers directly from handbook PDFs, ensuring responses are **context-aware, reliable, and up-to-date**.

---
# 🎥 Demo Video
📌 A complete walkthrough of the project is available in the demo video below:
https://drive.google.com/file/d/1_JQP6J1mwjuDZ8bfG6OgfFpBCCpTFcsp/view?usp=drive_link

## 🔍 System Architecture

**Backend:** FastAPI
**Vector Store:** Qdrant
**LLM / Embeddings:** HuggingFace
**Framework:** LangChain
**Frontend:** Streamlit
**Testing:** Pytest
**Chunking & Retrieval:** Context + Metadata-based

---

## 🔄 System Flow

```
User Asks Question
        ↓
Streamlit Frontend
        ↓
FastAPI Backend
        ↓
Query Embedding
        ↓
Qdrant Vector Search
        ↓
Relevant Handbook Chunks
        ↓
RAG Chain (LangChain)
        ↓
LLM-Generated Answer
        ↓
Response to User
```

---

## 📂 Features

✅ Upload employee handbook PDFs
✅ Intelligent Q&A on HR policies
✅ Accurate answers grounded in documents
✅ Fast semantic search using vector DB
✅ Clean UI for non-technical users

---

## 🧩 RAG Strategy

### ✔ Used

* **Document Chunking**
  * Chunk size optimized for HR policies

* **Vector Embeddings**
  * Free, efficient embedding models
    
* **Efficient Retrieval**
  * Metadata based retieval using LLM
    
* **LLM Grounding**

  * Answers strictly based on handbook content

---

## ▶️ How to Run the Project

### 1️⃣ Create & Activate Virtual Environment

```bash
python -m venv .venv
```

**Windows**

```powershell
.venv\Scripts\Activate.ps
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Run Qdrant on Cloud


---

### 4️⃣ Run Backend (FastAPI)

From project root:

```bash
uvicorn backend.main:app --reload
```

📌 Backend API:

```
http://127.0.0.1:8000
```

📌 API Docs:

```
http://127.0.0.1:8000/docs
```

---

### 5️⃣ Run Frontend (Streamlit)

Open a new terminal:

```bash
cd frontend
streamlit run app.py
```

📌 Frontend UI:

```
http://localhost:8501
```

---

## 🧪 Testing & Coverage

### Run Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=backend --cov-report=term-missing
```

### Generate HTML Coverage Report

```bash
pytest --cov=backend --cov-report=html
```

📂 Coverage output:

```
backend/htmlcov/index.html
```

---

## 🛠️ Tech Stack

| Layer       | Technology |
| ----------- | ---------- |
| Backend     | FastAPI    |
| Frontend    | Streamlit  |
| LLM Runtime | Ollama     |
| Framework   | LangChain  |
| Vector DB   | Qdrant     |
| Testing     | Pytest     |
| Coverage    | pytest-cov |

---

## 🎯 Design Decisions

✔ RAG architecture chosen to avoid hallucinations
✔ Local LLMs used for privacy & cost efficiency
✔ Qdrant selected for fast and scalable vector search
✔ Clean separation between frontend and backend

---

## 🚀 Future Enhancements

* 🔹 Multi-handbook support
* 🔹 PDF / DOC export of answers
* 🔹 AI-powered policy summaries

---

## 👨‍💻 Author

**Aaryan Jadhav**
Employee Handbook Automation | RAG Systems | LangChain | FastAPI | Qdrant | GenAI
