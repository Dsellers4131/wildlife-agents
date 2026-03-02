# [M] Wildlife Condition Monitor

> Real-time hunting condition intelligence powered by local AI — built as a demonstration 
> of agentic automation engineering for Moultrie / EBSCO Industries.
>
> https://wildlife-agents-dbwg2ykh5gj4dkmuzfnzmn.streamlit.app/

![Python](https://img.shields.io/badge/Python-3.13-blue)
![LangChain](https://img.shields.io/badge/LangChain-1.x-green)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1:8b-orange)
![AWS SQS](https://img.shields.io/badge/AWS-SQS-yellow)
![Prefect](https://img.shields.io/badge/Prefect-3.x-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)

---

## What This Is

A fully autonomous hunting condition monitoring pipeline that:

1. Ingests real-time environmental data — live weather via OpenWeatherMap API and 
   mathematically calculated moon phase
2. Runs a hybrid scoring engine — deterministic formula scores conditions 1-10, 
   local LLM (llama3.1:8b via Ollama) writes natural language reasoning for hunters
3. Publishes condition alerts to AWS SQS when score reaches threshold — 
   simulating the hunter notification system
4. Orchestrates everything with Prefect — scheduled runs, retry logic, 
   full observability and run history

This project mirrors the core architecture described in Moultrie's Agentic 
Automation Engineer role — environmental signal ingestion, LLM-powered 
decision loops, event-driven alerting, and pipeline observability.

---

## Architecture
```
┌─────────────────────────────────────────┐
│           Prefect Scheduler             │
│         (runs every 6 hours)            │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────▼──────────┐
         │   Data Collector   │  ← OpenWeatherMap API + Moon Calculator
         │      Agent         │
         └─────────┬──────────┘
                   │ structured JSON
         ┌─────────▼──────────┐
         │  Scoring Engine    │  ← Deterministic formula (pressure +
         │  (Hybrid)          │    temp + wind + moon = score/10)
         └─────────┬──────────┘
                   │ score + breakdown
         ┌─────────▼──────────┐
         │  Condition Analyst │  ← llama3.1:8b via Ollama
         │      Agent         │    writes hunter-facing reasoning
         └─────────┬──────────┘
                   │ if score >= 7
         ┌─────────▼──────────┐
         │     AWS SQS        │  ← hunting-alerts queue
         │   hunting-alerts   │    (Lambda → SNS → SMS in production)
         └────────────────────┘
```

---

## Tech Stack

| Technology | Role |
|---|---|
| **LangChain + LCEL** | Agent orchestration and LLM chaining |
| **Ollama (llama3.1:8b)** | Local LLM — no cloud API, runs on device |
| **OpenWeatherMap API** | Live weather data — temp, pressure, wind, humidity |
| **Moon Phase Calculator** | Mathematical calculation, no external dependency |
| **AWS SQS** | Message queue for decoupled alert delivery |
| **Prefect** | Pipeline scheduling, retry logic, observability |
| **Streamlit** | Interactive UI with Moultrie brand styling |

---

## Scoring System

The condition score is **deterministic** — same inputs always produce the same score. 
The LLM is only used to write the natural language explanation.

| Factor | Max Points | Ideal Conditions |
|---|---|---|
| Barometric Pressure | 3 | 1010-1020 hPa stable |
| Temperature | 3 | 35-55°F |
| Wind Speed | 2 | Under 10 mph |
| Moon Phase | 2 | New Moon |
| **Total** | **10** | |

Alerts fire to AWS SQS when score ≥ 7.

---

## Why Deterministic Scoring + LLM Reasoning

A pure LLM scoring approach is unreliable for a production hunting app — 
the model may weight factors differently run to run. Hunters need to trust 
that a 7/10 today means the same thing as a 7/10 tomorrow.

The hybrid approach separates concerns:
- **Formula** handles the number — consistent, auditable, explainable
- **LLM** handles the language — intelligent, natural, hunter-facing

In production v2, the formula would be replaced by a supervised ML model 
trained on trail camera trigger data correlated with weather conditions — 
an approach Moultrie is uniquely positioned to execute given their billions 
of trail camera images.

---

## Project Structure
```
wildlife-agents/
├── agents/
│   ├── weather_collector.py   # Data collection agent
│   └── condition_analyst.py   # Hybrid scoring + LLM reasoning agent
├── tools/
│   ├── weather_tool.py        # OpenWeatherMap API wrapper
│   ├── moon_tool.py           # Mathematical moon phase calculator
│   ├── scoring.py             # Deterministic scoring engine
│   ├── queue_tool.py          # AWS SQS publisher
│   └── locations.py           # US hunting city coordinates
├── assets/
│   └── moultrie_logo.png
├── .streamlit/
│   └── config.toml            # Moultrie brand theme
├── app.py                     # Streamlit UI
├── flow.py                    # Prefect orchestration flow
└── README.md
```

---

## Running Locally

**Prerequisites:**
- Python 3.13+
- Ollama installed with llama3.1:8b pulled
- OpenWeatherMap API key (free tier)
- AWS account with SQS queue configured

**Setup:**
```bash
git clone https://github.com/dallassellers/wildlife-agents
cd wildlife-agents
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure environment:**
```bash
cp .env.example .env
# Fill in your API keys
```

**Run the UI:**
```bash
streamlit run app.py
```

**Run the scheduled pipeline:**
```bash
python flow.py

# To deploy with schedule (runs every 6 hours):
# flow.serve(name="wildlife-monitor", cron="0 */6 * * *")
```

---

## What I Would Build Next

- **Dead letter queue** — failed SQS messages routed to a DLQ for inspection
- **Lambda consumer** — reads SQS and triggers SNS for real SMS delivery to hunters
- **ML scoring model** — supervised model trained on trail camera + weather correlation data
- **Property-specific baselines** — hunters calibrate thresholds for their specific land
- **LangSmith tracing** — full agent decision traces for observability dashboard

---

## Built By

**Dallas Sellers** — Senior Automation Engineer  
MS Computer Science (in progress) — University of Colorado Boulder  
Specialization: Machine Learning, Computer Vision, Deep Learning

[LinkedIn]linkedin.com/in/dallas-sellers229 · 
[GitHub]https://github.com/Dsellers4131
