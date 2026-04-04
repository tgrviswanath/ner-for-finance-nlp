# AWS Deployment Guide — Project 09 NER for Finance

---

## AWS Services for Financial NER

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Comprehend**      | Extract PERSON, ORG, DATE, MONEY, LOCATION entities from financial text      | Replace your spaCy + EntityRuler pipeline          |
| **Amazon Comprehend Custom** | Train custom entities: TICKER, METRIC, QUARTER on your financial data      | When you need finance-specific entity types        |
| **Amazon Bedrock**         | Claude/Titan for structured financial entity extraction via prompt           | When you need flexible schema-free extraction      |

> **Amazon Comprehend Custom Entity Recognition** trained on your financial corpus is the direct replacement for your spaCy EntityRuler with custom finance patterns.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + nlp-service containers in a private VPC               | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 4. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track NER latency, entity distribution, request volume                    |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Comprehend Custom NER       │
│ NLP Service :8001 │    │ Finance-specific entities          │
│ spaCy+EntityRuler │    │ No model maintenance needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name financer/nlp-service --region $AWS_REGION
aws ecr create-repository --repository-name financer/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.nlp-service -t $ECR/financer/nlp-service:latest ./nlp-service
docker push $ECR/financer/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/financer/backend:latest ./backend
docker push $ECR/financer/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name financer-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/financer/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "NLP_SERVICE_URL": "http://nlp-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Comprehend Custom NER

```python
import boto3

comprehend = boto3.client("comprehend", region_name="eu-west-2")

def extract_entities(text: str) -> dict:
    result = comprehend.detect_entities(Text=text[:5000], LanguageCode="en")
    entities = {}
    for entity in result["Entities"]:
        entities.setdefault(entity["Type"], []).append({
            "text": entity["Text"],
            "confidence": round(entity["Score"] * 100, 2)
        })
    return {"entities": entities, "entity_count": sum(len(v) for v in entities.values())}
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (nlp-service)   | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Comprehend          | Pay per unit      | ~$1–5/month        |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$24–37/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name financer/backend --force
aws ecr delete-repository --repository-name financer/nlp-service --force
```
