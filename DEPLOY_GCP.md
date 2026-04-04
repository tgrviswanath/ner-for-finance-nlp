# GCP Deployment Guide — Project 09 NER for Finance

---

## GCP Services for Financial NER

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Natural Language API**       | Extract PERSON, ORG, DATE, MONEY, LOCATION entities from financial text      | Replace your spaCy + EntityRuler pipeline          |
| **Vertex AI AutoML NER**             | Train custom entities: TICKER, METRIC, QUARTER on your financial data        | When you need finance-specific entity types        |
| **Vertex AI Gemini**                 | Gemini Pro for structured financial entity extraction via prompt             | When you need flexible schema-free extraction      |

> **Cloud Natural Language API** provides built-in NER for standard entity types. For finance-specific entities (TICKER, METRIC, QUARTER), use **Vertex AI AutoML Entity Extraction**.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + nlp-service containers — serverless, scales to zero   | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------|
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track NER latency, entity distribution, request volume                    |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Cloud Natural Language API         │
│ NLP Service :8001 │    │ + Vertex AI AutoML NER             │
│ spaCy+EntityRuler │    │ No model maintenance needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create financer-project --name="Finance NER"
gcloud config set project financer-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com language.googleapis.com \
  aiplatform.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create financer-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/financer-project/financer-repo
docker build -f docker/Dockerfile.nlp-service -t $AR/nlp-service:latest ./nlp-service
docker push $AR/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy nlp-service \
  --image $AR/nlp-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

NLP_URL=$(gcloud run services describe nlp-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars NLP_SERVICE_URL=$NLP_URL
```

---

## Option B — Use Cloud Natural Language API

```python
from google.cloud import language_v1

client = language_v1.LanguageServiceClient()

def extract_entities(text: str) -> dict:
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    result = client.analyze_entities(request={"document": document})
    entities = {}
    for entity in result.entities:
        entity_type = language_v1.Entity.Type(entity.type_).name
        entities.setdefault(entity_type, []).append({
            "text": entity.name,
            "salience": round(entity.salience, 3)
        })
    return {"entities": entities, "entity_count": sum(len(v) for v in entities.values())}
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (nlp-service)    | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Cloud Natural Language API | 5k units free         | $0–pay per call    |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$11–17/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete nlp-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete financer-repo --location=$GCP_REGION --quiet
gcloud projects delete financer-project
```
