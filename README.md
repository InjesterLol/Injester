# injester.lol

**Raw URL → Extract → AI scores readability/agent-performance → Auto-optimize → Re-score → Iterate → Output: AI-native version of any webpage**

Drop any URL into injester.lol. Get back an AI agent-actionable version of that page in seconds. Watch an AI agent go from failing to succeeding on the exact same task.

## Architecture

```
URL INPUT
   ↓
TAVILY EXTRACT          ← removes HTML noise, returns clean text
   ↓
NEBIUS MODEL            ← restructures into agent-optimized format
(Llama 3.1 70B / Qwen)    tags content, extracts entities, maps actions
   ↓
KARPATHY LOOP           ← agent optimizes its own restructuring prompt
                           3 iterations, score improves 3/5 → 5/5
   ↓
BENCHMARK               ← runs same task against raw vs. optimized
                           shows accuracy, token cost, completion rate
   ↓
THREE-PANEL UI          ← Human Web | AI View | Benchmark Score
```

## Tech Stack

| Layer | Tool |
|-------|------|
| Extraction | Tavily Extract API |
| Intelligence | Nebius Token Factory (Llama 3.1 70B / Qwen) |
| Backend | FastAPI (Python) |
| Frontend | React |

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env  # Set API URL
npm run dev
```

## Team

| Who | Role |
|-----|------|
| Ben (@Bshyong158) | Nebius + Tavily API setup, demo script, pitch, architecture |
| Vishal (@slowpoison) | FastAPI pipeline, Karpathy loop logic, benchmark runner |
| Alex (@shirazi) | Three-panel UI, score visualization, landing page |

## Demo Sites

- **United.com** — flight search (JS-heavy, anti-bot, 6+ step booking)
- **Airbnb.com** — listing page (infinite scroll, dynamic pricing, scattered content)

## Environment Variables

```
TAVILY_API_KEY=tvly-...
NEBIUS_API_KEY=...
NEBIUS_BASE_URL=https://api.studio.nebius.ai/v1/
NEBIUS_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
```
