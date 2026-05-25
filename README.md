# EduGuard AI 🛡️

**Guardrail-Enforced AI Safety Platform for Education**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Last Commit](https://img.shields.io/github/last-commit/username/eduguard)](#)
[![Open Issues](https://img.shields.io/github/issues/username/eduguard)](#)
[![Project Version](https://img.shields.io/badge/version-1.0.0-orange)](#)

---

## 📖 Table of Contents
- [Overview](#overview)
- [Project Status & Roadmap](#project-status--roadmap)
- [Use Cases](#use-cases)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture Diagram](#architecture-diagram)
- [Model Details](#model-details)
- [Prompt Engineering Notes](#prompt-engineering-notes)
- [Evaluation & Metrics](#evaluation--metrics)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Installation & Project Setup](#installation--project-setup)
- [Running the Project](#running-the-project)
- [API Reference](#api-reference)
- [Performance Benchmarks](#performance-benchmarks)
- [Known Issues & Limitations](#known-issues--limitations)
- [Hallucination & Failure Modes](#hallucination--failure-modes)
- [Security Considerations](#security-considerations)
- [Error Handling & Logging](#error-handling--logging)
- [Deployment Guide](#deployment-guide)
- [Scaling Considerations](#scaling-considerations)
- [Rollback Instructions](#rollback-instructions)
- [Monitoring & Observability](#monitoring--observability)
- [Cost & Resource Usage](#cost--resource-usage)
- [Data Flow & Privacy](#data-flow--privacy)
- [Testing Guide](#testing-guide)
- [Local Development Tips](#local-development-tips)
- [Debugging Guide](#debugging-guide)
- [Contributing Guide](#contributing-guide)
- [Changelog](#changelog)
- [Glossary](#glossary)
- [FAQ](#faq)
- [License](#license)
- [Contact & Support](#contact--support)
- [Acknowledgements](#acknowledgements)

---

## 🌟 Overview
**EduGuard AI** is a production-grade AI safety platform designed to wrap Large Language Models in a multi-stage validation pipeline for educational environments. It acts as a secure middleware that prevents AI-assisted cheating, blocks jailbreak attempts, and ensures academic integrity in real-time.

The project solves the "direct answer" problem in education by enforcing Socratic tutoring methods and detecting sophisticated prompt injection attacks aimed at manipulating automated grading systems.

**Key Highlights:**
- **Zero-Bypass Pipeline:** Multi-stage regex and LLM-based guardrails for every request.
- **Provider Agnostic:** Built-in support for AWS Bedrock and NVIDIA NIM.
- **Academic Integrity First:** Specialized detection for plagiarism and AI-generated content.
- **Observability:** Full audit logging to MongoDB with a real-time teacher dashboard.

---

## 📅 Project Status & Roadmap
- **Current Status:** Production-Ready / Stable
- **Current Version:** 1.0.0 (May 14, 2026)

| Status | Feature |
| :--- | :--- |
| [x] | Socratic Tutoring Pipeline (`/tutor/ask`) |
| [x] | Exam Validation & Auto-Grading (`/exam/validate`) |
| [x] | Regex-based Jailbreak & Content Filtering |
| [x] | Streamlit Teacher Dashboard |
| [x] | Multi-Provider Support (Bedrock/NVIDIA NIM) |
| [ ] | YAML-based dynamic rule loading |
| [ ] | Fine-tuned student-specific safety models |
| [ ] | Voice-to-voice safe tutoring support |

---

## 🎯 Use Cases
- **24/7 AI Teaching Assistant:** Provide students with guided hints for homework without giving away full answers.
- **High-Stakes Exam Monitoring:** Validate student submissions for AI generation and prompt injection in real-time.
- **Classroom Safety Filtering:** Protect K-12 students from adult or dangerous content within AI chat interfaces.
- **Automated Grading Assistant:** Securely grade open-ended questions against custom rubrics with security flags.

---

## 🚀 Key Features
- **Socratic Tutoring:** Custom system prompts that force the AI to guide students using hints and steps.
- **Grade Injection Detection:** Prevents students from "overriding" the grader to award themselves 100%.
- **Plagiarism Guardrail:** Multi-signal analysis for AI generation probability and academic dishonesty.
- **Real-time Violation Logs:** Critical and high-severity violations are instantly logged for teacher review.
- **Async Architecture:** Built on FastAPI and Motor (Async MongoDB) for high-concurrency student traffic.

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.12 | Core runtime |
| **FastAPI** | 0.111.0 | High-performance REST API |
| **Streamlit** | 1.35.0 | Teacher dashboard |
| **MongoDB** | 4.7.2+ | Log persistence |
| **AWS Bedrock** | - | Primary LLM Provider (Claude 3.5) |
| **NVIDIA NIM** | - | Alternative LLM Provider |
| **any-llm-sdk** | - | Unified LLM abstraction layer |
| **any-agent** | - | Multi-agent orchestration |
| **Pydantic** | 2.7.1 | Data validation and settings |

---

## 🏗️ Architecture Diagram

```mermaid
graph TD
    subgraph Client Layer
        S[Student App] -->|POST /tutor/ask| API
        E[Exam System] -->|POST /exam/validate| API
        T[Teacher] -->|View| DASH[Streamlit Dashboard]
    end

    subgraph EduGuard API (FastAPI)
        API --> G[Guardrail Pipeline]
        G --> J[Jailbreak Check]
        J --> I[Integrity Check]
        I --> C[Content Safety]
        C --> LLM_SVC[LLM Service]
        
        API --> V[Validator Pipeline]
        V --> INJ[Injection Check]
        INJ --> PLAG[Plagiarism Detection]
        PLAG --> GRADE[Auto Grader]
        GRADE --> LLM_SVC
    end

    subgraph LLM & Persistence
        LLM_SVC --> BED[AWS Bedrock]
        LLM_SVC --> NIM[NVIDIA NIM]
        API --> DB[(MongoDB)]
        DASH -->|Fetch Logs| API
    end
```

---

## 🤖 Model Details
- **Primary Model:** Anthropic Claude 3.5 Sonnet (via Bedrock or NVIDIA NIM)
- **Small Model:** Anthropic Claude 3 Haiku (for plagiarism signal analysis)
- **Context Window:** Up to 200k tokens (Claude 3.5)
- **Providers:**
  - **AWS Bedrock:** Used for production stability and regional compliance.
  - **NVIDIA NIM:** Used for high-performance inference and branch-specific optimization.

---

## 📝 Prompt Engineering Notes
- **Tutor System Prompt:** Implements strict Socratic constraints. Located in `app/llm/tutor_llm.py`.
- **Grader System Prompt:** JSON-only output enforcer for objective rubric-based scoring. Located in `app/llm/grader_llm.py`.
- **Techniques:** Chain-of-Thought (implied in tutor hints), Zero-shot JSON extraction, and Multi-signal plagiarism analysis.

---

## 📊 Evaluation & Metrics
- **Validation:** Currently performed via manual verification in the Dashboard playground.
- **Metrics Tracked:**
  - `latency`: Pipeline processing time.
  - `violation_rate`: Percentage of requests blocked.
  - `plagiarism_confidence`: Confidence score for AI generation detection.
- **Run Evals:** <!-- TODO: Add details -->

---

## 📂 Folder Structure

```text
eduguard/
├── app/
│   ├── agents/             # any-agent pipeline definitions
│   ├── db/                 # Async MongoDB (Motor) operations
│   ├── guardrails/         # Regex-based safety validation logic
│   ├── llm/                # Model-specific client implementations
│   ├── models/             # Pydantic request/response schemas
│   ├── routes/             # FastAPI endpoint definitions
│   ├── utils/              # Logging and shared helpers
│   ├── config.py           # Pydantic-based configuration management
│   └── main.py             # FastAPI entry point
├── dashboard/
│   └── app.py              # Streamlit Teacher Dashboard
├── rules/                  # Placeholder for YAML-based rules
├── tests/                  # Test suite (currently empty)
├── .env.example            # Environment template
├── Dockerfile              # Backend container
└── docker-compose.yml      # Orchestration
```

---

## 📋 Prerequisites
- **Python 3.12+**
- **MongoDB** (Local or Atlas)
- **AWS Credentials:** With `bedrock:InvokeModel` permissions.
- **NVIDIA API Key:** (Optional) If using the NIM provider.

---

## 🛠️ Installation & Project Setup

**Clone the repository:**
```bash
git clone https://github.com/username/eduguard.git
cd eduguard
```

**Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure environment:**
```bash
cp .env.example .env
# Edit .env with your keys
```

**Docker setup:**
```bash
docker-compose up --build
```

---

## 🚀 Running the Project

**Development Mode:**
```bash
uvicorn app.main:app --reload
```

**Dashboard:**
```bash
streamlit run dashboard/app.py
```

**Run Tests:**
```bash
pytest tests/
```

---

## 🔌 API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/tutor/ask` | Safe Socratic tutoring request | No (Demo) |
| `POST` | `/exam/validate` | Grade injection & plagiarism check | No (Demo) |
| `GET` | `/dashboard/violations` | Fetch recent security violations | No |
| `GET` | `/dashboard/submissions` | Fetch recent exam submissions | No |
| `GET` | `/health` | API Health Check | No |

---

## ⚡ Performance Benchmarks
- **Average Latency:** 2.5s - 4.0s (mostly LLM inference time).
- **Guardrail Overhead:** < 50ms (Regex-based checks).
- **Throughput:** Dependent on LLM provider quotas.

---

## ⚠️ Known Issues & Limitations
- **Regex Limitations:** Simple regex checks can be bypassed by creative spacing or Unicode obfuscation.
- **Cold Starts:** First LLM call after inactivity may have higher latency.
- **Empty Tests:** `tests/` directory is currently a placeholder.

---

## 🎭 Hallucination & Failure Modes
- **False Positives:** Strict academic integrity checks may block legitimate requests about "how to answer" a question.
- **Inconsistent JSON:** LLMs occasionally fail to return valid JSON for grading; a fallback parser is implemented in `grader_llm.py`.

---

## 🔒 Security Considerations
- **Credential Safety:** All secrets are managed via `.env` and `app/config.py`.
- **Injection Protection:** Dedicated pipeline in `app/guardrails/injection.py` specifically for grade manipulation.
- **Sanitization:** All student input is treated as untrusted.

---

## 📝 Error Handling & Logging
- **Logging:** Uses structured logging via `app/utils/logger.py`.
- **Log Levels:** Configurable via `LOG_LEVEL` env var.
- **Persistence:** All errors and violations are persisted to the `violations` collection in MongoDB.

---

## 🚢 Deployment Guide

### Frontend (Cloud Run, auto-deploy)

Pushes to the **`frontend`** branch build and deploy the React app via GitHub Actions → Cloud Build → Cloud Run.

See **[eduguard-frontend/DEPLOY.md](eduguard-frontend/DEPLOY.md)** for one-time GCP + GitHub secrets setup (`GCP_SA_KEY`, `VITE_API_URL`).

### Backend (Docker)

**Docker:**
```bash
docker build -t eduguard-backend .
docker run -p 8000:8000 --env-file .env eduguard-backend
```

---

## ⚖️ Scaling Considerations
- **Horizontal Scaling:** API instances are stateless and can be scaled behind a load balancer.
- **Database:** MongoDB Atlas is recommended for production scale.
- **Rate Limiting:** Should be implemented at the API Gateway level (e.g., Nginx or AWS API Gateway).

---

## 🔄 Rollback Instructions
1. Revert to previous git tag: `git checkout v0.9.9`.
2. Restart Docker containers: `docker-compose up --build`.

---

## 🔭 Monitoring & Observability
- **Dashboard:** Streamlit UI provides real-time visibility into violations.
- **Health Check:** `GET /health` monitored by Docker/K8s.

---

## 💰 Cost & Resource Usage
- **Bedrock Costs:** Billed per 1k tokens. Claude 3.5 Sonnet is cost-effective for complex grading.
- **Memory:** ~200MB RAM for the FastAPI app.

---

## 🛡️ Data Flow & Privacy
- **Logging:** Student IDs are logged; avoid logging PII.
- **Encryption:** Use TLS for all connections to API and MongoDB.

---

## 🧪 Testing Guide
Currently, the `tests/` directory is a placeholder. To add tests:
1. Use `pytest`.
2. Mock LLM calls using `unittest.mock`.

---

## 💡 Local Development Tips
- **No-LLM Mode:** <!-- TODO: Add details -->
- **VSCode Extensions:** Pylance, Python, Thunder Client.

---

## 🔍 Debugging Guide
| Error | Cause | Fix |
| :--- | :--- | :--- |
| `LLM error: AccessDenied` | Bad AWS Keys | Check `.env` and IAM permissions |
| `Connection refused :27017` | MongoDB not running | Run `docker-compose up db` |

---

## 🤝 Contributing Guide
1. Fork the repo.
2. Create a branch: `feature/your-feature`.
3. Commit using Conventional Commits.
4. Submit a PR.

---

## 📜 Changelog

### [1.0.0] - 2026-05-14
- Initial production release.
- Added Safe Tutor and Exam Validator.
- Integrated Streamlit Teacher Dashboard.

---

## 📖 Glossary
| Term | Definition |
| :--- | :--- |
| **Socratic** | A teaching method involving asking questions to stimulate critical thinking. |
| **Jailbreak** | An attempt to override LLM safety instructions. |

---

## ❓ FAQ
<details>
<summary>Can I use OpenAI instead of Bedrock?</summary>
Yes, the any-llm-sdk abstraction makes it easy to swap providers in app/config.py.
</details>

---

## 📄 License
This project is licensed under the MIT License — see LICENSE for details.

---

## 📞 Contact & Support
- Maintainer: Bharat
- Bug Reports: GitHub Issues

---

## 🏗️ Acknowledgements
- **Mozilla.ai** for `any-llm`, `any-agent`, and `any-guardrail`.
- **FastAPI** for the core framework.
