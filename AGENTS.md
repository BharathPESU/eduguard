markdown# EduGuard AI — AGENTS.md

## Project Overview
EduGuard AI is a two-endpoint AI safety platform for education built with FastAPI.
It blocks cheating, jailbreaks, grade manipulation, and detects plagiarism before
any student input reaches the LLM.

---

## Tech Stack
- **Framework:** FastAPI + Uvicorn
- **LLM Provider:** AWS Bedrock (Claude models via any-llm-sdk)
- **Guardrails:** Mozilla.ai any-guardrail + custom regex patterns
- **Agent Orchestration:** Mozilla.ai any-agent (tinyagent)
- **Database:** MongoDB (async via Motor)
- **Dashboard:** Streamlit
- **Python Version:** 3.12
- **Environment:** Ubuntu, virtualenv at ./venv

---

## Project Structure
eduguard/
├── app/
│   ├── main.py                  # FastAPI app entry point, registers routers
│   ├── config.py                # Loads .env settings via pydantic Settings class
│   ├── guardrails/
│   │   ├── jailbreak.py         # Regex-based jailbreak + academic integrity check
│   │   ├── content.py           # Regex-based adult/violence/drug content filter
│   │   ├── injection.py         # Regex-based grade manipulation injection detector
│   │   ├── integrity.py         # (reserved for future integrity checks)
│   │   └── plagiarism.py        # (reserved for future plagiarism guardrail)
│   ├── llm/
│   │   ├── bedrock_client.py    # Core invoke_llm() using any-llm-sdk bedrock provider
│   │   ├── tutor_llm.py         # Socratic tutor prompt + calls invoke_llm()
│   │   ├── grader_llm.py        # Exam grader prompt + returns JSON via invoke_llm()
│   │   └── plagiarism_llm.py    # Plagiarism signal detector + returns JSON via invoke_llm()
│   ├── agents/
│   │   ├── tutor_agent.py       # any-agent pipeline for tutor flow
│   │   └── validator_agent.py   # any-agent pipeline for exam validation flow
│   ├── routes/
│   │   ├── tutor.py             # POST /tutor/ask endpoint
│   │   └── exam.py              # POST /exam/validate endpoint
│   ├── models/
│   │   └── request_models.py    # Pydantic models: TutorRequest, ExamRequest
│   ├── db/
│   │   └── mongo.py             # Async MongoDB operations via Motor
│   └── utils/
│       └── logger.py            # Python logging setup, logger = logging.getLogger("eduguard")
├── dashboard/
│   └── app.py                   # Streamlit teacher dashboard
├── rules/
│   ├── jailbreak_rules.yaml     # (reserved for future YAML-based rules)
│   ├── integrity_rules.yaml
│   └── injection_rules.yaml
├── tests/                       # pytest test files
├── .env                         # Environment variables (never commit)
├── requirements.txt             # All dependencies
├── Dockerfile
└── docker-compose.yml

---

## API Endpoints

### POST /tutor/ask
Accepts a student question and runs it through 3 guardrail stages before LLM.

**Request:**
```json
{
  "student_id": "STU_001",
  "question": "Can you explain photosynthesis?",
  "subject": "Biology",
  "grade_level": "10"
}
```

**Pipeline stages:**
1. Jailbreak check (regex)
2. Academic integrity check (regex)
3. Content safety check (regex)
4. If all pass → invoke tutor LLM via AWS Bedrock

**Response (success):**
```json
{
  "status": "success",
  "stages_passed": ["jailbreak_check", "integrity_check", "content_safety"],
  "response": "guided tutoring response"
}
```

**Response (blocked):**
```json
{
  "status": "blocked",
  "stage": "integrity_check",
  "reason": "academic_integrity_violation",
  "message": "I can guide you with hints but not give the answer directly.",
  "response": null
}
```

---

### POST /exam/validate
Accepts a student exam answer and runs injection check, plagiarism detection, and grading.

**Request:**
```json
{
  "student_id": "STU_001",
  "exam_id": "EXAM_PHY_001",
  "question": "Explain Newton's second law.",
  "rubric": "Definition(25) Formula(25) Example(25) Clarity(25)",
  "student_answer": "F=ma means force equals mass times acceleration.",
  "grade_level": "10"
}
```

**Pipeline stages:**
1. Grade injection check (regex)
2. Plagiarism detection (LLM via Bedrock)
3. Answer grading (LLM via Bedrock)

**Response (success):**
```json
{
  "status": "success",
  "stages_passed": ["injection_check", "plagiarism_detection", "grading"],
  "security": {
    "injection_attempt": false,
    "plagiarism_suspected": false,
    "ai_generated_probability": 20,
    "plagiarism_confidence": 15,
    "signals": []
  },
  "grading": {
    "score": 72,
    "grade": "B",
    "concept_scores": {},
    "correct_parts": [],
    "incorrect_parts": [],
    "feedback": "Good grasp of formula but lacks example.",
    "improvement_suggestion": "Add a numerical worked example."
  }
}
```

---

## Environment Variables (.env)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
TUTOR_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
GRADER_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
PLAGIARISM_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
MONGO_URI=mongodb://localhost:27017
DB_NAME=eduguard
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key

---

## Key Design Decisions

- **any-guardrail is NOT used for jailbreak/integrity/injection** — those use
  pure regex to avoid torch/HuggingFace dependency issues at startup.
- **any-guardrail** is available if needed for future ML-based guardrail expansion.
- **invoke_llm()** in bedrock_client.py is the single function all LLM files use.
  Never use boto3 directly — always go through invoke_llm().
- **All __init__.py files are empty** — do not add imports to them,
  it causes circular import errors on startup.
- **MongoDB operations are all async** using Motor. Never use pymongo sync calls
  inside async route functions.
- **Grader and plagiarism LLMs return JSON** — always parse with try/except
  and fallback to find("{") / rfind("}") extraction.

---

## Dependencies (requirements.txt)
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.1
python-dotenv==1.0.1
boto3==1.34.84
pymongo==4.7.2
motor==3.4.0
streamlit==1.35.0
requests==2.31.0
pyyaml==6.0.1
httpx==0.27.0
pytest==8.2.0
any-llm-sdk[bedrock]
any-guardrail
any-agent[tinyagent]

---

## How to Run
```bash
# Activate venv
source venv/bin/activate

# Start API server
uvicorn app.main:app --reload --port 8000

# Start Streamlit dashboard (separate terminal)
streamlit run dashboard/app.py --server.port 8501
```

---

## Dashboard Routes (added to main.py)
GET /dashboard/violations    → returns last 50 violation logs from MongoDB
GET /dashboard/submissions   → returns last 50 exam submissions from MongoDB

---

## Common Errors & Fixes
- **ImportError: cannot import name 'bedrock'** → bedrock_client.py must export
  invoke_llm() not a bedrock object. All LLM files import invoke_llm.
- **ModuleNotFoundError: torch** → any-guardrail tries to load HuggingFace model.
  Do not initialize AnyGuardrail at module level. Use regex guardrails instead.
- **Circular import on startup** → __init__.py files must be empty.
- **any-llm==0.1.0 not found** → correct package name is any-llm-sdk[bedrock].