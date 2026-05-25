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
- OpenAPI schema generation
- Swagger UI documentation
- ReDoc documentation
- Interactive API testing through Swagger UI
- Docker support
- Docker Compose setup
- Automatic migrations on container startup
- Static files collection in Docker
- Docker environment configuration
- Persistent Docker volumes for media and SQLite database
- Django Template-based user interface
- Professional dashboard page
- Document filtering in the UI
- Document edit and delete support from the UI
- Manual document reprocessing from the UI
- Search interface with optional document filter
- Ask interface with optional document filter
- Question-answer history management from the UI
- Delete and clear history actions
- Automated test suite
- Document processing tests
- API endpoint tests
- Search and Ask API tests
- User interface page tests
- Swagger and ReDoc endpoint tests

---

## Tech Stack

- Python
- Django
- Django REST Framework
- python-docx
- LangChain
- langchain-text-splitters
- SQLite for local development

## How to Run the Project

The project can be run in two ways:

1. Local development using a Python virtual environment
2. Docker development using Docker Compose

---

## Option 1: Run Locally with Virtual Environment

### 1. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
open the project http://127.0.0.1:8000/admin/
```
## Option 2: Run with Docker

### 1. Make sure Docker Desktop is running

```bash
docker compose up --build
open http://127.0.0.1:8000/
Create a superuser inside Docker
open new terminal and write: docker compose exec web python manage.py createsuperuser
```

## API Documentation

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
```

---

## 4. Ask API

The Ask API is used to submit a user question and generate an answer based on the uploaded document chunks.

This endpoint implements the main RAG flow of the project:

```text
User Question → Search Relevant Chunks → Build Context → Generate Answer → Save History
```
---

## Swagger and OpenAPI Documentation

The project includes automatically generated API documentation using `drf-spectacular`.

Available documentation endpoints:

```text
GET /api/schema/ -----> http://127.0.0.1:8000/api/schema/
GET /api/docs/ -----> http://127.0.0.1:8000/api/docs/
GET /api/redoc/ -----> http://127.0.0.1:8000/api/redoc/
```
---

## Docker Setup

The project can be run with Docker and Docker Compose.

### Docker Files

The project includes:

```text
Dockerfile
docker-compose.yml
.dockerignore
entrypoint.sh
.env.docker
---
```
---

## User Interface

The project includes a Django Template-based user interface.

The UI allows users to use the main project features without manually typing API URLs or using Django Admin directly.

### UI Pages

```text
GET /
GET /documents/
GET /documents/upload/
GET /documents/{id}/
GET /documents/{id}/edit/
GET /documents/{id}/delete/
POST /documents/{id}/reprocess/
GET /search/
GET /ask/
GET /history/
GET /history/{id}/
GET /history/{id}/delete/
GET /history/clear/

---

## Automated Tests

The project includes automated tests to verify the main features and improve project reliability.

### Test Coverage

The tests cover:

- DOCX document processing
- Text extraction and chunk creation
- Search service
- Document API endpoints
- Chunks API endpoints
- Search API
- Ask API with mock LLM provider
- Question-answer history API
- Django Template user interface pages
- Swagger, ReDoc, and OpenAPI schema endpoints

### Run Tests Locally

```bash
python manage.py test
```

---
---

## Multi-format Document Upload

The project now supports multiple file formats for document upload, text extraction, search, and question answering.

### Supported File Types

```text
.docx
.pdf
.txt
```

---

## LLM Reliability and Answer Metadata

The project includes improved LLM reliability and answer transparency.

### Features

- Ollama provider availability check
- Safer document-grounded prompting
- Fallback answer when the LLM provider is unavailable
- LLM timeout and context-size configuration
- Dashboard LLM status display
- Answer metadata showing which provider/model generated the answer

### Answer Metadata

After asking a question, the UI shows the answer source, for example:

```text
Answered by: ollama / llama3.2:1b