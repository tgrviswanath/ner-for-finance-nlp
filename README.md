# Project 09 - NER for Finance

Microservice NLP project that extracts named entities from financial news and reports using spaCy with custom finance-specific EntityRuler patterns.

## Architecture

```
Frontend :3000  →  Backend :8000  →  NLP Service :8001
  React/MUI        FastAPI/httpx      FastAPI/spaCy + EntityRuler
```

## Local Run

```bash
# Terminal 1 - NLP Service
cd nlp-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

## Docker

```bash
docker-compose up --build
```

## Stack

| Layer | Tools |
|-------|-------|
| NLP Service | spaCy (en_core_web_sm), EntityRuler (custom finance patterns) |
| Backend | FastAPI, httpx |
| Frontend | React, MUI, Recharts (horizontal bar chart) |

## Entity Types

| Label    | Description        | Example                    |
|----------|--------------------|----------------------------|
| ORG      | Organization       | Apple Inc., Federal Reserve |
| PERSON   | Person             | Tim Cook, Jerome Powell    |
| GPE      | Location           | United States, New York    |
| DATE     | Date               | January 2024, Q1 2024      |
| MONEY    | Monetary value     | $119.6 billion             |
| PERCENT  | Percentage         | 3.5%, 25 basis points      |
| TICKER   | Stock ticker       | AAPL, MSFT, GOOGL          |
| METRIC   | Finance metric     | revenue, EPS, EBITDA       |
| QUARTER  | Fiscal quarter     | Q1 2024, first quarter     |

## Features

- Inline text highlighting with color-coded entity spans
- Hover tooltip showing entity type
- Entity distribution bar chart
- Entities grouped by type
- Batch extraction mode
- 3 built-in sample financial texts
