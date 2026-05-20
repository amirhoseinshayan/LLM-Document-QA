# LLM Document QA System

A Django-based document question-answering system.

---

## Current Features

- Django project setup
- `documents` app setup
- Document management through Django Admin
- DOCX file upload support
- Full text extraction from DOCX files
- Full text storage in the database
- LangChain-based text chunking
- Chunk storage in the database
- Document CRUD API
- Read-only chunks API
- Read-only question-answer history API
- Manual document reprocessing API
- Search API for finding relevant document chunks
- Question/Answer history models prepared for the next phases
- SQLite for local development

---

## Tech Stack

- Python
- Django
- Django REST Framework
- python-docx
- LangChain
- langchain-text-splitters
- SQLite for local development

## How to Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
open http://127.0.0.1:8000/admin/

---

# API Documentation

This section describes the current REST API endpoints implemented in the project.

Base API URL:

```text
http://127.0.0.1:8000/api/

API Root -------> GET /api/
Documents API ------> GET /api/documents/
    Create Documents -------> POST /api/documents/
    Retrieve Document -------> GET /api/documents/{id}/
    Update Document -------> PUT /api/documents/{id}/
    Partial Update Document ------> PATCH /api/documents/{id}/
    Delete Document ------> DELETE /api/documents/{id}/
    Reprocess Document ------> POST /api/documents/{id}/reprocess/
Chunks API -----> GET /api/chunks/
    Retrieve Chunk ------> GET /api/chunks/{id}/
    Filter Chunks by Document ------> GET /api/chunks/?document={document_id}
List Question/Answer History -----> GET /api/history/
    Retrieve Question/Answer History ------> GET /api/history/{id}/

API Testing Guide:
    -run python manage.py runserver
    -then open http://127.0.0.1:8000/api/


---

## 4. Ask API

The Ask API is used to submit a user question and generate an answer based on the uploaded document chunks.

This endpoint implements the main RAG flow of the project:

```text
User Question → Search Relevant Chunks → Build Context → Generate Answer → Save History

---
## Project Structure

```text
llm_document_qa/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── documents/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── document_processor.py
│   │   ├── docx_extractor.py
│   │   └── search_service.py
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tests.py
│   └── views.py
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
