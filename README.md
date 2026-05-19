# LLM Document QA System

A Django-based document question-answering system.

## Current Features

- Django project setup
- Document management through Django Admin
- DOCX file upload support
- Full text extraction from DOCX files
- Text chunking and storage
- Question/Answer history models

## Tech Stack

- Python
- Django
- Django REST Framework
- python-docx
- SQLite for local development

## How to Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

########then open http://127.0.0.1:8000/admin/