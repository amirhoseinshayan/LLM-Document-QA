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
