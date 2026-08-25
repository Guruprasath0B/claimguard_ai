# ClaimGuard AI

**Autonomous Cashless Mediclaim Pre-Auth & TPA Fraud Detection Agent**

ClaimGuard AI is an AI-powered healthcare insurance claims system designed to automate **cashless pre-authorization, claim validation, fraud detection, and adjudication support** for Indian health insurance and TPA operations.

## Key Features

* Medical document and claim data ingestion
* Indian PII/PHI detection and redaction
* Claim information extraction
* IRDAI/rule-based policy validation
* Hospital tariff and billing validation
* Patient claim-history analysis
* Fraud and anomaly detection
* Qdrant-based knowledge retrieval
* LangGraph-based agent workflow
* Structured claim adjudication decisions
* LangSmith tracing and observability

## Tech Stack

**Python · LangGraph · LangChain · OpenAI · Qdrant · FastAPI · Presidio · Mem0 · LangSmith**

## Workflow

```text
Claim Input
    ↓
PII/PHI Redaction
    ↓
Claim Extraction
    ↓
Policy & Rule Validation
    ↓
Tariff/Billing Validation
    ↓
Patient History Check
    ↓
Fraud Detection
    ↓
AI Adjudication
    ↓
Final Decision
```
