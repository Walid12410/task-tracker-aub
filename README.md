# Task Tracker

A learning project that demonstrates REST API design with Python and FastAPI, featuring a JSON file backend and a vanilla JavaScript frontend.
The project covers FastAPI routing, Pydantic validation, layered architecture, and automated testing — without requiring a database server.

## Setup

### 1. Create a virtual environment

```bash
cd task-tracker/backend
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows PowerShell
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp ../.env.example .env
```

### 4. Start the backend server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs are at `http://localhost:8000/docs`.

### 5. Test the health endpoint

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok", "timestamp": "2026-07-26T10:00:00.000000+00:00"}
```

### 6. Run the test suite

```bash
pytest tests/ -v
```

### 7. Start the frontend (separate terminal)

```bash
cd task-tracker/frontend
python -m http.server 5500
```

Open `http://localhost:5500` in your browser.
