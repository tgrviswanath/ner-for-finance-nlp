# Azure Deployment Guide — Project 09 NER for Finance

---

## Azure Services for Financial NER

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Language — NER**          | Extract PERSON, ORG, DATE, MONEY, LOCATION entities from financial text      | Replace your spaCy + EntityRuler pipeline          |
| **Azure AI Language — Custom NER**   | Train custom entities: TICKER, METRIC, QUARTER on your financial data        | When you need finance-specific entity types        |
| **Azure OpenAI Service**             | GPT-4 for structured financial entity extraction via prompt                  | When you need flexible schema-free extraction      |

> **Azure AI Language Custom NER** is the direct replacement for your spaCy EntityRuler. Train on your financial corpus via Language Studio — no code needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, nlp-service)       | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Train and Manage Your Model

| Service                        | What it does                                                              | When to use                                           |
|--------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Machine Learning**     | Fine-tune spaCy/BERT NER on financial corpus                              | When you need domain-specific financial NER           |
| **Azure AI Language Studio**   | Train custom NER without code via UI                                      | Quick custom entity training on financial data        |

### 4. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 5. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track NER latency, entity distribution, request volume               |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure AI Language Custom NER       │
│ NLP Service :8001 │    │ Finance-specific entities          │
│ spaCy+EntityRuler │    │ No model maintenance needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-finance-ner --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-finance-ner --name financeacr --sku Basic --admin-enabled true
az acr login --name financeacr
ACR=financeacr.azurecr.io
docker build -f docker/Dockerfile.nlp-service -t $ACR/nlp-service:latest ./nlp-service
docker push $ACR/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name finance-env --resource-group rg-finance-ner --location uksouth

az containerapp create \
  --name nlp-service --resource-group rg-finance-ner \
  --environment finance-env --image $ACR/nlp-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-finance-ner \
  --environment finance-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars NLP_SERVICE_URL=http://nlp-service:8001
```

---

## Option B — Use Azure AI Language Custom NER

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

client = TextAnalyticsClient(
    endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_LANGUAGE_KEY"))
)

def extract_entities(text: str) -> dict:
    result = client.recognize_custom_entities(
        [text], project_name="finance-ner", deployment_name="production"
    )[0]
    entities = {}
    for entity in result.entities:
        entities.setdefault(entity.category, []).append({
            "text": entity.text, "confidence": round(entity.confidence_score * 100, 2)
        })
    return {"entities": entities, "entity_count": sum(len(v) for v in entities.values())}
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (nlp-svc) | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure AI Language        | S tier    | Pay per call      |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–20/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-finance-ner --yes --no-wait
```
