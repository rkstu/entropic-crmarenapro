# Entropic CRMArena

> **🏆 AgentX Competition Phase 1 | Deadline: January 15, 2026**

[![Docker](https://img.shields.io/badge/Docker-ghcr.io%2Frkstu%2Fentropic--crmarena--green-blue)](https://ghcr.io/rkstu/entropic-crmarena-green)
[![AgentBeats](https://img.shields.io/badge/AgentBeats-Registered-green)](https://agentbeats.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**A2A-compliant benchmark** for evaluating CRM agents with adversarial robustness testing.

| Resource | Link |
|----------|------|
| 🏠 **AgentBeats Platform** | [agentbeats.dev](https://agentbeats.dev) |
| 📚 **Official Tutorial** | [docs.agentbeats.dev/tutorial](https://docs.agentbeats.dev/tutorial/) |
| 🎥 **Video Tutorial** | [YouTube](https://www.youtube.com/watch?v=ZmBnC4xTyRU) |
| 🏅 **Competition Details** | [Berkeley RDI AgentX](https://rdi.berkeley.edu/agentx-agentbeats) |

---

## 📋 Table of Contents

| Section | Description |
|---------|-------------|
| [Overview](#overview) | What this benchmark does, features, dataset |
| [Part 1: Local Testing](#-part-1-local-testing) | Test your agent locally (7 steps) |
| [Part 2: Leaderboard Submission](#-part-2-agentbeats-leaderboard-submission) | Submit to AgentBeats (7 steps) |
| [Configuration](#️-configuration) | All config options |
| [Technical Reference](#-technical-reference) | Task format, scoring, schemas |
| [Changelog](#-changelog) | Version history |

---

## Overview

### What This Benchmark Evaluates

| Capability | Description |
|------------|-------------|
| **Functional Correctness** | Can the agent complete CRM tasks accurately? |
| **Adversarial Robustness** | Can it handle Schema Drift and Context Rot? |
| **Efficiency** | Token usage, query count, trajectory length |
| **Safety** | Hallucination rate, privacy awareness |

### Key Features

- ✅ **Schema Drift**: Tests agent adaptation to renamed database columns
- ✅ **Context Rot**: Tests agent filtering of distractor records
- ✅ **7-Dimension Scoring**: Comprehensive evaluation beyond accuracy
- ✅ **Local Task Caching**: 0.01s load time (no network dependency)
- ✅ **Detailed Timing**: Full Green vs Purple agent breakdown
- ✅ **A2A Compliant**: Works with any A2A-compatible agent

### Dataset

| Metric | Value |
|--------|-------|
| Source | [Salesforce/CRMArenaPro](https://huggingface.co/datasets/Salesforce/CRMArenaPro) |
| Tasks | 2,140 |
| Categories | 22 task types |
| Load Time | **0.01s** (local cache) |

### Registered Agents

| Agent | Type | AgentBeats ID |
|-------|------|---------------|
| **Entropic CRMArena** | 🟢 Green | `019ba211-13b7-7e83-9086-c8015a5e4957` |
| **Baseline CRM Agent** | 🟣 Purple | `019ba27e-3b82-7d43-8822-51357ccd4861` |

---

## 🚀 Part 1: Local Testing

Use this to **test your Purple Agent locally** before submitting to the leaderboard.

### Prerequisites

| Requirement | Description |
|-------------|-------------|
| Python 3.12+ | Required for both agents |
| uv | Package manager ([install](https://github.com/astral-sh/uv)) |
| Nebius API Key | For LLM calls ([get key](https://nebius.ai)) |
| 3 Terminal Windows | One for each agent + one for testing |

### Step 1: Clone Green Agent

```bash
# Terminal 1
git clone https://github.com/rkstu/entropic-crmarenapro.git
cd entropic-crmarenapro
uv sync
```

### Step 2: Set Environment Variables

```bash
# In both Terminal 1 and Terminal 2
export NEBIUS_API_KEY=your_nebius_api_key_here
```

### Step 3: Start Green Agent (Terminal 1)

```bash
# Terminal 1 - Green Agent on port 9009
uv run src/server.py --host 127.0.0.1 --port 9009
```

You should see:
```
============================================================
Entropic CRMArena Green Agent
============================================================
Server: http://127.0.0.1:9009/
...
INFO:     Uvicorn running on http://127.0.0.1:9009
```

### Step 4: Start Your Purple Agent (Terminal 2)

**Option A: Use our baseline agent**
```bash
# Terminal 2 - Clone baseline if needed
git clone https://github.com/rkstu/baseline-crm-agent.git
cd baseline-crm-agent
uv sync
export NEBIUS_API_KEY=your_key
uv run src/server.py --host 127.0.0.1 --port 9010
```

**Option B: Use your own agent**
```bash
# Terminal 2 - Your agent must:
# 1. Expose /.well-known/agent-card.json
# 2. Accept POST requests with A2A message format
# 3. Return answers in A2A response format
cd /path/to/your/agent
uv run src/server.py --host 127.0.0.1 --port 9010
```

### Step 5: Verify Both Agents Are Running (Terminal 3)

```bash
# Check Green Agent
curl http://127.0.0.1:9009/.well-known/agent-card.json
# Should return: {"name": "Entropic CRMArena", ...}

# Check Purple Agent  
curl http://127.0.0.1:9010/.well-known/agent-card.json
# Should return: {"name": "Your Agent Name", ...}
```

### Step 6: Run Assessment (Terminal 3)

**Quick test (1 task):**
```bash
curl -X POST http://127.0.0.1:9009/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": "1",
    "params": {
      "message": {
        "messageId": "test-001",
        "role": "user",
        "parts": [{
          "kind": "text",
          "text": "{\"participants\": {\"agent\": \"http://127.0.0.1:9010/\"}, \"config\": {\"task_limit\": 1, \"drift_level\": \"none\", \"rot_level\": \"none\", \"org_type\": \"b2b\"}}"
        }]
      }
    }
  }'
```

**Standard test (5 tasks):**
```bash
curl -X POST http://127.0.0.1:9009/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": "1",
    "params": {
      "message": {
        "messageId": "test-005",
        "role": "user",
        "parts": [{
          "kind": "text",
          "text": "{\"participants\": {\"agent\": \"http://127.0.0.1:9010/\"}, \"config\": {\"task_limit\": 5, \"drift_level\": \"none\", \"rot_level\": \"none\", \"org_type\": \"b2b\"}}"
        }]
      }
    }
  }'
```

**Adversarial test (with Schema Drift):**
```bash
curl -X POST http://127.0.0.1:9009/ \
  -H "Content-Type: application/json" \
  -d '{
        "jsonrpc": "2.0",
        "method": "message/send",
        "id": "1",
        "params": {
            "message": {
        "messageId": "test-adv",
                "role": "user",
        "parts": [{
          "kind": "text",
          "text": "{\"participants\": {\"agent\": \"http://127.0.0.1:9010/\"}, \"config\": {\"task_limit\": 5, \"drift_level\": \"low\", \"rot_level\": \"low\", \"org_type\": \"b2b\"}}"
        }]
      }
    }
  }'
```

### Step 7: Interpret Results

The response includes:
```json
{
  "summary": {
    "total_tasks": 5,
    "total_passed": 1,
    "pass_rate": 0.2,
    "avg_score": 54.1
  },
  "timing": {
    "total_seconds": 435.7,
    "purple_agent_seconds": 435.7,
    "purple_agent_percent": 100.0
  },
  "dimension_averages": {
    "FUNCTIONAL": 30.7,
    "TOKEN_EFFICIENCY": 98.9,
    "TRAJECTORY_EFFICIENCY": 100.0,
    ...
  }
}
```

| Field | Meaning |
|-------|---------|
| `pass_rate` | % of tasks with crm_reward > 0 |
| `avg_score` | Average 7D score (0-100) |
| `purple_agent_percent` | % of time spent in your agent (should be ~100%) |

---

## 🏆 Part 2: AgentBeats Leaderboard Submission

Once your agent performs well locally, submit it to the official leaderboard!

### Step 1: Containerize Your Purple Agent

Create a `Dockerfile` in your agent's repo:

```dockerfile
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (must match what you register)
EXPOSE 9010

# Start command
CMD ["python", "src/server.py", "--host", "0.0.0.0", "--port", "9010"]
```

Build and push to GitHub Container Registry:

```bash
# Build for linux/amd64 (required by AgentBeats)
docker build --platform linux/amd64 -t ghcr.io/YOUR_USERNAME/your-agent:latest .

# Login to GHCR
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Push
docker push ghcr.io/YOUR_USERNAME/your-agent:latest

# IMPORTANT: Make the package public
# Go to: GitHub → Your Profile → Packages → your-agent → Package Settings → Make Public
```

### Step 2: Register Your Purple Agent on AgentBeats

1. Go to [agentbeats.dev](https://agentbeats.dev)
2. **Login with GitHub**
3. Click **"Register Agent"** (top right)
4. Fill in:
   | Field | Value |
   |-------|-------|
   | Agent Type | **Purple** |
   | Display Name | Your agent's name |
   | Docker Image | `ghcr.io/YOUR_USERNAME/your-agent:latest` |
   | Repository URL | Your GitHub repo URL |
5. Click **"Register"**
6. **⚠️ Copy your Agent ID** (you'll need this!)

### Step 3: Fork the Leaderboard Repository

1. Go to the leaderboard repo (linked from Green Agent page)
2. Click **"Fork"** → Create fork
3. In your fork: **Actions tab → Enable workflows**

### Step 4: Configure Your Assessment

Edit `scenario.toml` in your forked repo:

```toml
# Green Agent (this benchmark)
[green_agent]
agentbeats_id = "019ba211-13b7-7e83-9086-c8015a5e4957"  # Entropic CRMArena
env = { NEBIUS_API_KEY = "${NEBIUS_API_KEY}" }

# Your Purple Agent
[[participants]]
agentbeats_id = "YOUR_AGENT_ID_FROM_STEP_2"  # ← Paste your ID here!
name = "agent"
env = { NEBIUS_API_KEY = "${NEBIUS_API_KEY}" }

# Assessment configuration
[config]
task_limit = 20           # Number of tasks
drift_level = "none"      # Start with "none", then try "low"
rot_level = "none"        # Start with "none", then try "low"
org_type = "b2b"          # b2b or b2c
max_steps = 15            # Max turns per task
timeout = 300             # Seconds per task
```

### Step 5: Add API Key as GitHub Secret

1. Go to your forked repo → **Settings**
2. **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add:
   | Name | Value |
   |------|-------|
   | `NEBIUS_API_KEY` | Your Nebius API key |
5. Click **"Add secret"**

### Step 6: Run the Assessment

1. **Commit and push** your `scenario.toml`
2. Go to **Actions** tab in your fork
3. Watch the workflow run (takes ~10-30 minutes depending on task_limit)
4. When complete, click **"Submit your results"** link

### Step 7: Submit to Leaderboard

1. The workflow creates a **Pull Request** with your results
2. **Merge the PR** (or wait for approval if submitting to someone else's leaderboard)
3. 🎉 **Your scores appear on [agentbeats.dev](https://agentbeats.dev) within minutes!**

### Troubleshooting Leaderboard Submission

| Issue | Solution |
|-------|----------|
| Workflow fails immediately | Check `NEBIUS_API_KEY` secret is set |
| Docker image not found | Make sure package is **public** on GHCR |
| Agent times out | Reduce `task_limit` or increase `timeout` |
| Low scores | Test locally first with `drift_level: none` |

---

## ⚙️ Configuration

### Basic Config

```json
{
  "participants": {"agent": "http://your-agent:port/"},
  "config": {
    "task_limit": 20,
    "drift_level": "none",
    "rot_level": "none",
    "org_type": "b2b"
  }
}
```

### All Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_limit` | int | null | Max tasks to run |
| `task_percentage` | float | 5.0 | % of tasks to sample |
| `task_ids` | list | null | Specific task IDs |
| `task_categories` | list | null | Filter by category |
| `drift_level` | string | "none" | none/low/medium/high |
| `rot_level` | string | "none" | none/low/medium/high |
| `max_steps` | int | 15 | Max agent turns |
| `timeout` | int | 300 | Seconds per task |
| `org_type` | string | "b2b" | b2b or b2c |

### Adversarial Levels

| Level | Schema Drift | Context Rot |
|-------|--------------|-------------|
| `none` | 0% renamed | 0 distractors |
| `low` | ~10% renamed | 1-2 distractors |
| `medium` | ~30% renamed | 3-4 distractors |
| `high` | ~50% renamed | 5+ distractors |

---

## 📊 Technical Reference

<details>
<summary><b>Task Format Sent to Purple Agent</b></summary>

```json
{
  "type": "crm_task",
  "task_id": "456",
  "task_category": "sales_insight_mining",
  "prompt": "Which competitors are we at a disadvantage against?",
  "persona": "You are detail-oriented and methodical.",
  "required_context": "Domain information and transcripts...",
  "config": {"org_type": "b2b", "max_steps": 15},
  "entropy": {"drift_level": "low", "rot_level": "low"}
}
```

</details>

<details>
<summary><b>Expected Response Format</b></summary>

```json
{
  "task_id": "456",
  "answer": "Quantum Circuits Inc.",
  "category": "sales_insight_mining",
  "metrics": {
    "tokens": 5000,
    "tool_calls": 3,
    "queries": 2
  }
}
```

</details>

<details>
<summary><b>7-Dimension Scoring System</b></summary>

| Dimension | Weight | Description |
|-----------|--------|-------------|
| FUNCTIONAL | 30% | Task completion accuracy |
| DRIFT_ADAPTATION | 20% | Success under schema drift |
| TOKEN_EFFICIENCY | 12% | Fewer tokens = higher score |
| QUERY_EFFICIENCY | 12% | Fewer queries = higher score |
| ERROR_RECOVERY | 8% | Graceful failure handling |
| TRAJECTORY_EFFICIENCY | 10% | Optimal path to answer |
| HALLUCINATION_RATE | 8% | Valid tool calls only |

**Total Score = Σ (Dimension × Weight)**

</details>

<details>
<summary><b>Results Format</b></summary>

```json
{
  "summary": {
    "total_tasks": 5,
    "total_passed": 1,
    "pass_rate": 0.2,
    "avg_score": 54.1
  },
  "dimension_averages": {
    "FUNCTIONAL": 30.7,
    "DRIFT_ADAPTATION": 0.0,
    "TOKEN_EFFICIENCY": 98.9,
    "QUERY_EFFICIENCY": 98.8,
    "ERROR_RECOVERY": 44.0,
    "TRAJECTORY_EFFICIENCY": 100.0,
    "HALLUCINATION_RATE": 96.0
  },
  "timing": {
    "total_seconds": 435.7,
    "purple_agent_seconds": 435.7,
    "green_agent_seconds": 0.0,
    "purple_agent_percent": 100.0
  }
}
```

</details>

<details>
<summary><b>Project Structure</b></summary>

```
entropic-crmarenapro/
├── src/
│   ├── server.py       # A2A server (port 9009)
│   ├── agent.py        # Assessment + timing
│   ├── executor.py     # A2A executor
│   └── messenger.py    # Purple agent client
├── crm/
│   ├── tasks.py        # Task loader (local cache)
│   ├── entropy.py      # Schema Drift + Context Rot
│   ├── evaluator.py    # Answer evaluation
│   └── scorer.py       # 7-Dimension scoring
├── data/
│   └── crmarena_b2b_tasks.json  # Cached tasks (3.8MB)
├── tests/
├── Dockerfile
└── pyproject.toml
```

</details>

<details>
<summary><b>Task Categories (22 Total)</b></summary>

| Category | Reward Metric |
|----------|---------------|
| lead_qualification | exact_match |
| lead_routing | exact_match |
| case_routing | exact_match |
| handle_time | exact_match |
| transfer_count | exact_match |
| sales_insight_mining | exact_match |
| monthly_trend_analysis | exact_match |
| best_region_identification | exact_match |
| conversion_rate_comprehension | exact_match |
| knowledge_qa | fuzzy_match |
| named_entity_disambiguation | exact_match |
| private_customer_information | privacy_rejection |
| confidential_company_knowledge | privacy_rejection |
| ... and more |

</details>

<details>
<summary><b>Database Schema</b></summary>

| Table | Key Columns |
|-------|-------------|
| Account | Id, Name, BillingState |
| Contact | Id, Name, AccountId |
| Lead | Id, Name, Status, OwnerId |
| Case | Id, Subject, AccountId, OrderItemId__c |
| Opportunity | Id, Name, StageName, Amount |
| OrderItem | Id, OrderId, Product2Id |
| Product2 | Id, Name, ProductCode |
| VoiceCallTranscript__c | Id, Body__c, LeadId__c |

**Key Relationships:**
```
Case.OrderItemId__c → OrderItem.Id → Product2.Id
Case.AccountId → Account.Id
Lead.Id → VoiceCallTranscript__c.LeadId__c
```

</details>

<details>
<summary><b>Performance & Timing</b></summary>

| Component | Time | Notes |
|-----------|------|-------|
| Task Loading | 0.01s | Local cache |
| Context Build | 0.001s | Per task |
| Evaluation | 0.15s | Per task |
| Scoring | 0.002s | Per task |
| **Green Agent Total** | **<1%** | Near-instant |

**Test Results (5 tasks):**
```
Total:        435.7s
├─ Purple:    435.7s (100%)  ← LLM inference
└─ Green:     0.0s   (0%)    ← Benchmark overhead
```

</details>

<details>
<summary><b>Docker Commands</b></summary>

```bash
# Build
docker build --platform linux/amd64 -t ghcr.io/rkstu/entropic-crmarena-green:latest .

# Run
docker run -p 9009:9009 -e NEBIUS_API_KEY=$NEBIUS_API_KEY ghcr.io/rkstu/entropic-crmarena-green:latest

# Push
docker push ghcr.io/rkstu/entropic-crmarena-green:latest
```

</details>

---

## 📝 Changelog

### v1.1.0 (January 15, 2026)

- ✅ **Local Task Caching**: 0.01s load (was 10-30s from HuggingFace)
- ✅ **Detailed Timing**: Green vs Purple agent breakdown
- ✅ **Fixed Continuation Bug**: 1 turn per task (was 10)
- ✅ **Green Agent Efficiency**: <1% overhead

### v1.0.0 (January 9, 2026)

- Initial release with A2A SDK
- Schema Drift & Context Rot
- 7-Dimension Scoring

---

## 📄 License

MIT

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTROPIC CRMARENA                        │
├─────────────────────────────────────────────────────────────┤
│  GREEN AGENT ID:  019ba211-13b7-7e83-9086-c8015a5e4957     │
│  DOCKER IMAGE:    ghcr.io/rkstu/entropic-crmarena-green    │
│  REPO:            github.com/rkstu/entropic-crmarenapro    │
│  PORT:            9009                                      │
└─────────────────────────────────────────────────────────────┘
```
