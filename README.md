# LLM Document QA System

A Django-based document question-answering system that allows users to upload documents, extract text, search document chunks, and ask questions using a RAG-based workflow with Ollama LLM support.

---

## Project Overview

This project is a document question-answering system built with Django and Django REST Framework.

The system can:

- Upload and process documents
- Extract text from supported files
- Split extracted text into searchable chunks
- Search relevant chunks based on a query
- Generate answers using retrieved document context
- Store question-answer history
- Provide both REST API and web interface
- Run locally or with Docker
- Connect to a local Ollama LLM provider

---

## Current Project Status

The project currently includes the implementation of the first twelve phases:

- Initial Django project setup
- Initial document upload, text extraction, and chunk creation
- REST API endpoints for documents, chunks, and question-answer history
- Text splitting and document chunk search API
- RAG-based Ask API with configurable LLM provider support
- Swagger/OpenAPI API documentation
- Docker and Docker Compose setup
- Django Template-based user interface
- Automated tests and quality assurance
- Multi-format document upload support
- LLM reliability, fallback handling, provider status, and answer metadata
- Final documentation and demo preparation

---

## Current Features

- Django project setup
- Django REST Framework API
- Django Template-based user interface
- Document upload and management
- Multi-format document upload support
- Supported file types: DOCX, PDF, TXT
- Text extraction from uploaded documents
- Text chunking and chunk storage
- Document CRUD API
- Read-only chunks API
- Question-answer history API
- Manual document reprocessing
- Search API for finding relevant chunks
- Ask API with RAG workflow
- Ollama LLM integration
- Mock fallback answer support
- LLM provider status display
- Answer metadata showing provider and model
- Swagger UI documentation
- ReDoc documentation
- Docker and Docker Compose support
- Persistent Docker volumes for media and SQLite database
- Automated tests for processing, API, UI, and documentation pages

---

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- python-docx
- pypdf
- httpx
- drf-spectacular
- Docker
- Docker Compose
- Ollama

---

## Supported File Types

The project supports these document formats:

```text
.docx
.pdf
.txt
```

### Notes

- DOCX files are processed with `python-docx`.
- PDF files are processed with `pypdf`.
- TXT files are read as plain text.
- PDF files must contain selectable text.
- Scanned image-based PDFs may not extract text correctly without OCR.
- Unsupported file types are rejected during upload.

---

## RAG Workflow

The Ask feature follows this flow:

```text
User Question
→ Search Relevant Chunks
→ Build Context
→ Send Context + Question to LLM
→ Generate Answer
→ Save Question/Answer History
```

The system is designed to answer based on uploaded document context.

---

## Environment Files

The project uses environment variables for local and Docker development.

Real environment files are ignored by Git:

```text
.env
.env.docker
```

Example files should be committed:

```text
.env.example
.env.docker.example
```

---

## Local Environment Example

Create a `.env` file in the project root based on `.env.example`:

```env
DEBUG=True
SECRET_KEY=replace-this-with-your-local-secret-key

LLM_PROVIDER=ollama

OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://localhost:11434

LLM_TIMEOUT_SECONDS=120
LLM_MAX_CONTEXT_CHARS=8000
LLM_FALLBACK_TO_MOCK=True

OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/auto
```

For local development, Ollama should be available at:

```text
http://localhost:11434
```

---

## Docker Environment Example

Create a `.env.docker` file in the project root based on `.env.docker.example`:

```env
DEBUG=True
SECRET_KEY=django-insecure-docker-development-key

LLM_PROVIDER=ollama

OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://host.docker.internal:11434

LLM_TIMEOUT_SECONDS=120
LLM_MAX_CONTEXT_CHARS=8000
LLM_FALLBACK_TO_MOCK=True

OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/auto
```

For Docker development, the Django container connects to Ollama through:

```text
http://host.docker.internal:11434
```

---

## Ollama Setup

This project uses Ollama as the local LLM provider.

Make sure the Ollama container is running:

```bash
docker start ollama
```

Check installed models:

```bash
docker exec -it ollama ollama list
```

The project currently uses:

```text
llama3.2:1b
```

If the model is not installed, install it inside the Ollama container:

```bash
docker exec -it ollama ollama pull llama3.2:1b
```

Test Ollama API:

```bash
curl http://localhost:11434/api/tags
```

---

## How to Run the Project Locally

### 1. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Create superuser

```bash
python manage.py createsuperuser
```

### 5. Start Ollama

```bash
docker start ollama
```

### 6. Run the Django server

```bash
python manage.py runserver 127.0.0.1:9000
```

### 7. Open the project

```text
http://127.0.0.1:9000/
```

Useful local URLs:

```text
Home:        http://127.0.0.1:9000/
Admin:       http://127.0.0.1:9000/admin/
API Root:    http://127.0.0.1:9000/api/
Swagger:     http://127.0.0.1:9000/api/docs/
ReDoc:       http://127.0.0.1:9000/api/redoc/
```

---

## How to Run the Project with Docker

### 1. Make sure Docker Desktop is running

Docker Desktop must be open and running.

### 2. Make sure Ollama is running

```bash
docker start ollama
```

### 3. Build and run the Django container

If dependencies or Docker files changed:

```bash
docker compose up --build
```

If only Python, HTML, CSS, or template files changed:

```bash
docker compose up
```

### 4. Open the project

If `docker-compose.yml` maps the project like this:

```yaml
ports:
  - "9000:8000"
```

Open:

```text
http://127.0.0.1:9000/
```

### 5. Create superuser inside Docker

Open a new terminal and run:

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Run tests inside Docker

```bash
docker compose exec web python manage.py test
```

---
## Run with OpenRouter Online LLM

Use this option if you want to run the project without a local Ollama model.

In this mode:

- Ollama is not required.
- The answer generation is handled by OpenRouter.
- You must provide a valid OpenRouter API key.
- Internet access is required.

### 1. Get an OpenRouter API key

Create an API key from your OpenRouter account.

Then place the key in your environment file.

### 2. Configure `.env` for local development

For local development, update `.env` like this:

```env
DEBUG=True
SECRET_KEY=replace-this-with-your-local-secret-key

LLM_PROVIDER=openrouter

OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://localhost:11434

LLM_TIMEOUT_SECONDS=120
LLM_MAX_CONTEXT_CHARS=8000
LLM_FALLBACK_TO_MOCK=True

OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=openrouter/auto
```

### 3. Configure `.env.docker` for Docker development

For Docker development, update `.env.docker` like this:

```env
DEBUG=True
SECRET_KEY=django-insecure-docker-development-key

LLM_PROVIDER=openrouter

OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://host.docker.internal:11434

LLM_TIMEOUT_SECONDS=120
LLM_MAX_CONTEXT_CHARS=8000
LLM_FALLBACK_TO_MOCK=True

OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=openrouter/auto
```

### 4. Run locally with OpenRouter

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:9000
```

Open:

```text
http://127.0.0.1:9000/
```

Then go to:

```text
http://127.0.0.1:9000/ask/
```

Ask a question after uploading a document.

If OpenRouter is configured correctly, the answer metadata should show something like:

```text
Answered by: openrouter / openrouter/auto
```

### 5. Run with Docker and OpenRouter

After updating `.env.docker`, run:

```bash
docker compose down
docker compose up --build
```

Open:

```text
http://127.0.0.1:9000/
```

Then test:

```text
http://127.0.0.1:9000/ask/
```

### 6. OpenRouter fallback behavior

If OpenRouter is selected but the API key is missing, invalid, expired, or the internet connection is unavailable, the project will use the fallback behavior when this setting is enabled:

```env
LLM_FALLBACK_TO_MOCK=True
```

In that case, the answer metadata may show:

```text
Answered by: mock / mock-fallback
```

This means the system retrieved document context, but the online LLM provider was not available.

---

## Choosing Between Ollama and OpenRouter

Use Ollama when:

- You want local LLM execution.
- You already have Ollama installed.
- You have the required model installed.
- You want the project to work without relying on an online API.

Use OpenRouter when:

- You do not have Ollama installed.
- Your laptop cannot run local LLM models efficiently.
- You want to use stronger online models.
- You have an OpenRouter API key and internet access.

To switch providers, only change this value:

```env
LLM_PROVIDER=ollama
```

or:

```env
LLM_PROVIDER=openrouter
```

Then restart the server or Docker container.

---

## LLM Provider Check

The dashboard shows the currently configured LLM provider and its availability.

Possible provider labels:

```text
ollama-langchain
openrouter
mock
```

The Ask page also shows which provider generated the answer:

```text
Answered by: ollama-langchain / llama3.2:1b
Answered by: openrouter / openrouter/auto
Answered by: mock / mock-fallback
```

---

## Important Docker Notes

The project has two separate containers:

```text
ollama
llm_document_qa_web
```

### Ollama container

The Ollama container runs the language model.

It exposes:

```text
11434:11434
```

### Django container

The Django container runs the project.

It handles:

- UI
- API
- Uploads
- Text extraction
- Chunking
- Search
- RAG flow
- History storage

The Django container connects to Ollama using:

```text
http://host.docker.internal:11434
```

If Ollama is turned off, upload and search still work, but Ask will use fallback behavior if fallback is enabled.

---

## User Interface

The project includes a Django Template-based user interface.

### Main UI Pages

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
```

### UI Features

- Dashboard with project statistics
- LLM provider status display
- Document upload page
- Document list and filtering
- Document detail page
- Extracted text display
- Generated chunks display
- Document edit and delete
- Manual document reprocessing
- Search interface
- Ask interface
- Thinking/loading state while LLM is generating an answer
- Answer metadata showing provider/model
- Question-answer history
- Delete history item
- Clear all history
- Links to API Docs and Admin

---

## Answer Metadata

After asking a question, the UI shows which provider and model generated the answer.

Example with Ollama:

```text
Answered by: ollama / llama3.2:1b
```

Example with fallback:

```text
Answered by: mock / mock-fallback
```

This helps users understand whether the answer came from the real LLM or from the fallback system.

---

## API Documentation

The project includes automatically generated API documentation using `drf-spectacular`.

Available documentation endpoints:

```text
GET /api/schema/
GET /api/docs/
GET /api/redoc/
```

Local URLs:

```text
http://127.0.0.1:9000/api/schema/
http://127.0.0.1:9000/api/docs/
http://127.0.0.1:9000/api/redoc/
```

---

## REST API Endpoints

Base API URL:

```text
http://127.0.0.1:9000/api/
```

### API Root

```text
GET /api/
```

### Documents API

```text
GET    /api/documents/
POST   /api/documents/
GET    /api/documents/{id}/
PUT    /api/documents/{id}/
PATCH  /api/documents/{id}/
DELETE /api/documents/{id}/
POST   /api/documents/{id}/reprocess/
```

### Chunks API

```text
GET /api/chunks/
GET /api/chunks/{id}/
GET /api/chunks/?document={document_id}
```

### Search API

```text
POST /api/search/
```

Example request:

```json
{
  "query": "document question answering",
  "top_k": 5
}
```

### Ask API

```text
POST /api/ask/
```

Example request:

```json
{
  "question": "What is this document about?",
  "top_k": 5
}
```

The Ask API performs the main RAG flow:

```text
Search Relevant Chunks
→ Build Context
→ Generate Answer
→ Save History
```

### History API

```text
GET /api/history/
GET /api/history/{id}/
```

---

## Automated Tests

The project includes automated tests to verify the main features.

### Test Coverage

Tests cover:

- Document processing
- Text extraction
- Chunk creation
- Document API endpoints
- Chunks API endpoints
- Search API
- Ask API
- Question-answer history API
- User interface pages
- Swagger and ReDoc pages

### Run tests locally

```bash
python manage.py test
```

### Run tests in Docker

```bash
docker compose exec web python manage.py test
```

---

## Git Ignore Notes

The following files should not be committed:

```text
.env
.env.docker
db.sqlite3
media/
venv/
__pycache__/
staticfiles/
*.gguf
ollama_models/
```

The following example files should be committed:

```text
.env.example
.env.docker.example
```

---

## Development Notes

- Use `.env` for local development.
- Use `.env.docker` for Docker development.
- Use `http://localhost:11434` for local Ollama access.
- Use `http://host.docker.internal:11434` for Docker-to-host Ollama access.
- If only code or templates changed, `docker compose up` is usually enough.
- If `requirements.txt`, `Dockerfile`, `entrypoint.sh`, or `docker-compose.yml` changed, rebuild with `docker compose up --build`.
- PDF extraction works best with text-based PDFs.
- Scanned PDFs require OCR, which is not included yet.

---

