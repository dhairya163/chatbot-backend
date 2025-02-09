# Chatbot Backend

A FastAPI-based backend service for the chatbot application with MongoDB integration.

## Tech Stack

- Python 3.11
- FastAPI
- MongoDB
- Poetry (dependency management)

## Project Structure

```
app/
├── api/          # API routes
├── core/         # Core configuration
├── database/     # Database connections
├── models/       # MongoDB models
├── schemas/      # Pydantic schemas
└── services/     # Business logic
```

## Setup Instructions

1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Copy the environment file and update the values:
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`