#!/bin/bash

# ─────────────────────────────────────────────
#  EduGuard AI — Startup Script
# ─────────────────────────────────────────────

set -e  # Exit on any error

VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
FRONTEND_DIR="eduguard-frontend"
API_PORT=8000
FRONTEND_PORT=5173

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║        EduGuard AI  —  Startup       ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Python virtual environment ──────────
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[1/4] Creating Python virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}      ✔ Virtual environment created at ./$VENV_DIR${NC}"
else
    echo -e "${GREEN}[1/4] Virtual environment already exists — skipping creation.${NC}"
fi

# ── Step 2: Install Python dependencies ─────────
echo ""
echo -e "${YELLOW}[2/4] Installing Python dependencies...${NC}"
source "$VENV_DIR/bin/activate"

if [ ! -f "$REQUIREMENTS" ]; then
    echo -e "${RED}      ✘ $REQUIREMENTS not found. Aborting.${NC}"
    exit 1
fi

pip install --upgrade pip --quiet
pip install -r "$REQUIREMENTS" --quiet
echo -e "${GREEN}      ✔ Python dependencies installed.${NC}"

# ── Step 3: .env check ──────────────────────────
echo ""
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}      ⚠  .env created from .env.example — update your credentials before use.${NC}"
    else
        echo -e "${RED}      ✘ No .env or .env.example found. Some features may not work.${NC}"
    fi
fi

# ── Step 4: Frontend setup ───────────────────────
echo ""
echo -e "${YELLOW}[3/4] Setting up React frontend...${NC}"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}      ✘ Frontend directory '$FRONTEND_DIR' not found. Aborting.${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}      Installing npm packages (first run)...${NC}"
    npm install --silent
    echo -e "${GREEN}      ✔ npm packages installed.${NC}"
else
    echo -e "${GREEN}      ✔ node_modules present — skipping npm install.${NC}"
fi

cd ..

# ── Step 5: Free ports if already in use ────────
kill_port() {
    local port=$1
    local pid
    pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}      ⚠  Port $port in use (PID $pid) — killing...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}      ✔ Port $port is now free.${NC}"
    fi
}

echo ""
echo -e "${YELLOW}[4/4] Checking ports and starting services...${NC}"
kill_port "$API_PORT"
kill_port "$FRONTEND_PORT"
echo ""

# Start React dev server in background
cd "$FRONTEND_DIR"
npm run dev -- --port "$FRONTEND_PORT" --host > /tmp/eduguard_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}      ✔ React frontend starting (PID: $FRONTEND_PID)${NC}"

# Give the dev server a moment to bind
sleep 2

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  🚀 EduGuard AI is running!${NC}"
echo ""
echo -e "  ${BOLD}React Frontend:${NC}"
echo -e "  ${CYAN}➜  http://localhost:${FRONTEND_PORT}${NC}"
echo ""
echo -e "  ${BOLD}FastAPI Backend:${NC}"
echo -e "  ${GREEN}➜  http://127.0.0.1:${API_PORT}${NC}"
echo -e "  ${GREEN}➜  http://127.0.0.1:${API_PORT}/docs        (Swagger UI)${NC}"
echo -e "  ${GREEN}➜  http://127.0.0.1:${API_PORT}/redoc       (ReDoc)${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Press ${BOLD}Ctrl+C${NC} to stop all services."
echo ""

# Trap Ctrl+C to cleanly kill background processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down EduGuard AI services...${NC}"
    kill "$FRONTEND_PID" 2>/dev/null || true
    deactivate 2>/dev/null || true
    echo -e "${GREEN}Done. Goodbye!${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start FastAPI in foreground (keeps script alive)
uvicorn app.main:app --reload --host 0.0.0.0 --port "$API_PORT"
