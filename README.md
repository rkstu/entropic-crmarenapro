# Entropic CRMArena

[![Docker](https://img.shields.io/badge/Docker-ghcr.io%2Frkstu%2Fentropic--crmarena--green-blue)](https://ghcr.io/rkstu/entropic-crmarena-green)
[![AgentBeats](https://img.shields.io/badge/AgentBeats-Registered-green)](https://agentbeats.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## Updates
- This project won **1st Place** at [Berkeley RDI AgentX–AgentBeats](https://rdi.berkeley.edu/agentx-agentbeats) Competition, Business Process Agent Track, and earned the [Agentic AI MOOC Legendary Tier certification](https://drive.google.com/file/d/18XVFI23ps3To4FhiVg5S9goW3kh9JoMm/view?usp=sharing)
- Published a detailed Medium walkthrough of the project — [Medium](https://medium.com/@rahulkumar_dev/building-crm-agents-that-survive-production-793498b80a3c)

## What is Entropic CRMArena?

We extend the [Salesforce CRMArenaPro](https://huggingface.co/datasets/Salesforce/CRMArenaPro) benchmark with **adversarial robustness testing** and **multi-dimensional evaluation** for CRM agents. While the original benchmark measures functional task completion across 22 CRM categories, real-world deployments face schema changes and noisy data that standard benchmarks fail to capture.

### Our Contributions

| Extension | Description |
| --------- | ----------- |
| **Schema Drift** | We programmatically rename database columns (e.g., `owner_id` → `assigned_agent`) at configurable intensity levels, testing whether agents can adapt to evolving schemas without explicit retraining. |
| **Context Rot** | We inject semantically plausible but irrelevant distractor records into task contexts, measuring an agent's ability to filter noise and maintain focus on relevant information. |
| **7-Dimension Scoring** | Beyond binary pass/fail, we evaluate agents on functional accuracy, drift adaptation, token efficiency, query efficiency, error recovery, trajectory efficiency, and hallucination rate—providing a holistic view of agent capabilities. |

### Implementation

- **A2A-Compliant Green Agent** — Implements the [Agent-to-Agent protocol](https://google.github.io/A2A/) for standardized evaluation
- **Near-Zero Evaluation Overhead** — <0.5% of total runtime, ensuring measured performance reflects the tested agent rather than benchmark artifacts
- **Containerized & Reproducible** — Docker images for consistent evaluation across environments

---

> **AgentX Competition Phase 1** — This benchmark is registered on the [AgentBeats leaderboard](https://agentbeats.dev) for the Berkeley RDI AgentX competition.

### Essential Resources

| Resource              | Link                                                                          | Description                                      |
| --------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------ |
| **Video Tutorial**    | [YouTube: AgentBeats End-to-End](https://www.youtube.com/watch?v=ZmBnC4xTyRU) | Complete walkthrough of agent setup & submission |
| **Official Tutorial** | [docs.agentbeats.dev/tutorial](https://docs.agentbeats.dev/tutorial/)         | Step-by-step guide with repo templates           |
| **AgentBeats**        | [agentbeats.dev](https://agentbeats.dev)                                      | Register agents & view leaderboards              |
| **Competition**       | [Berkeley RDI AgentX](https://rdi.berkeley.edu/agentx-agentbeats)             | Rules, deadlines, prizes                         |

### Template Repositories

| Template                 | Link                                                                                          | Use For                           |
| ------------------------ | --------------------------------------------------------------------------------------------- | --------------------------------- |
| **Agent Template**       | [RDI-Foundation/agent-template](https://github.com/RDI-Foundation/agent-template)             | Build A2A-compliant Purple agents |
| **Green Agent Template** | [RDI-Foundation/green-agent-template](https://github.com/RDI-Foundation/green-agent-template) | Build benchmark evaluators        |
| **AgentBeats Tutorial**  | [RDI-Foundation/agentbeats-tutorial](https://github.com/RDI-Foundation/agentbeats-tutorial)   | Learning examples & concepts      |

> ⚠️ **Important**: Your Purple Agent should follow the [agent-template](https://github.com/RDI-Foundation/agent-template) architecture to ensure A2A compatibility!

---

## Table of Contents

| Section                                                                     | Description                                     |
| --------------------------------------------------------------------------- | ----------------------------------------------- |
| [What is Entropic CRMArena?](#what-is-entropic-crmarena)                    | Project overview, contributions, implementation |
| [Overview](#overview)                                                       | Capabilities, features, dataset                 |
| [Building Your Purple Agent](#building-your-purple-agent)                   | A2A compatibility & template                    |
| [Part 1: Local Testing](#part-1-local-testing)                              | Test your agent locally (7 steps)               |
| [Part 2: Leaderboard Submission](#part-2-agentbeats-leaderboard-submission) | Submit to AgentBeats (7 steps)                  |
| [Configuration](#configuration)                                             | All config options                              |
| [Technical Reference](#technical-reference)                                 | Task format, scoring, schemas                   |
| [Changelog](#changelog)                                                     | Version history                                 |

---

## Overview

### What This Benchmark Evaluates

| Capability                 | Description                                  |
| -------------------------- | -------------------------------------------- |
| **Functional Correctness** | Can the agent complete CRM tasks accurately? |
| **Adversarial Robustness** | Can it handle Schema Drift and Context Rot?  |
| **Efficiency**             | Token usage, query count, trajectory length  |
| **Safety**                 | Hallucination rate, privacy awareness        |

### Key Features

- ✅ **Schema Drift**: Tests agent adaptation to renamed database columns
- ✅ **Context Rot**: Tests agent filtering of distractor records
- ✅ **7-Dimension Scoring**: Comprehensive evaluation beyond accuracy
- ✅ **Local Task Caching**: 0.01s load time (no network dependency)
- ✅ **Detailed Timing**: Full Green vs Purple agent breakdown
- ✅ **A2A Compliant**: Works with any A2A-compatible agent

### Dataset

| Metric     | Value                                                                            |
| ---------- | -------------------------------------------------------------------------------- |
| Source     | [Salesforce/CRMArenaPro](https://huggingface.co/datasets/Salesforce/CRMArenaPro) |
| Tasks      | 2,140                                                                            |
| Categories | 22 task types                                                                    |
| Load Time  | **0.01s** (local cache)                                                          |

### Registered Agents

| Agent                  | Type      | AgentBeats ID                          |
| ---------------------- | --------- | -------------------------------------- |
| **Entropic CRMArena**  | 🟢 Green  | `019ba211-13b7-7e83-9086-c8015a5e4957` |
| **Baseline CRM Agent** | 🟣 Purple | `019ba27e-3b82-7d43-8822-51357ccd4861` |

---

## Building Your Purple Agent

Before testing, make sure your agent is **A2A compatible**.

### Recommended: Use the Official Template

```bash
# Create your agent from the official template
# Go to: https://github.com/RDI-Foundation/agent-template
# Click "Use this template" → Create a new repository

# Then clone your new repo
git clone https://github.com/YOUR_USERNAME/your-agent.git
cd your-agent
```

### Required Agent Structure

Your agent must follow this structure (from [agent-template](https://github.com/RDI-Foundation/agent-template)):

```
your-agent/
├── src/
│   ├── server.py      # A2A server setup
│   ├── executor.py    # Request handling
│   ├── agent.py       # Your logic here!
│   └── messenger.py   # A2A messaging
├── Dockerfile
├── pyproject.toml
└── .github/workflows/
    └── test-and-publish.yml
```

### A2A Compliance Checklist

| Requirement        | Description                                  |
| ------------------ | -------------------------------------------- |
| ✅ Agent Card      | Expose `/.well-known/agent-card.json`        |
| ✅ JSON-RPC        | Accept POST requests with A2A message format |
| ✅ Response Format | Return answers in A2A artifact format        |
| ✅ Docker          | Build for `linux/amd64` platform             |

> See the [AgentBeats Tutorial](https://docs.agentbeats.dev/tutorial/) for detailed implementation guidance.

---

## Part 1: Local Testing

Use this to **test your Purple Agent locally** before submitting to the leaderboard.

### Prerequisites

| Requirement        | Description                                                                                                             |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| Python 3.12+       | Required for both agents                                                                                                |
| uv                 | Package manager ([install](https://github.com/astral-sh/uv))                                                            |
| LLM API Key        | **Either** `NEBIUS_API_KEY` ([nebius.ai](https://nebius.ai)) **or** `OPENAI_API_KEY` ([openai.com](https://openai.com)) |
| 3 Terminal Windows | One for each agent + one for testing                                                                                    |

> 💡 **API Key Options**: This benchmark works with any OpenAI-compatible API. We use `NEBIUS_API_KEY` for cost-effective access to large models (Llama 70B/405B), but `OPENAI_API_KEY` works too!

### Step 1: Clone Green Agent

```bash
# Terminal 1
git clone https://github.com/rkstu/entropic-crmarenapro.git
cd entropic-crmarenapro
uv sync
```

### Step 2: Set Environment Variables

```bash
# Option A: Using Nebius (recommended for large models)
export NEBIUS_API_KEY=your_nebius_api_key_here

# Option B: Using OpenAI
export OPENAI_API_KEY=your_openai_api_key_here
```

> 💡 Set the same key in **both terminals** (Green and Purple agent).

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

> **Note**: Schema Drift (`medium`) and Context Rot (`medium`) are now hardcoded. Only `task_limit` needs to be specified.

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
          "text": "{\"participants\": {\"agent\": \"http://127.0.0.1:9010/\"}, \"config\": {\"task_limit\": 1}}"
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
          "text": "{\"participants\": {\"agent\": \"http://127.0.0.1:9010/\"}, \"config\": {\"task_limit\": 5}}"
        }]
      }
    }
  }'
```

**Full benchmark (all 2,140 tasks):**

```bash
curl -X POST http://127.0.0.1:9009/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": "1",
    "params": {
      "message": {
        "messageId": "test-full",
        "role": "user",
        "parts": [{
          "kind": "text",
          "text": "{\"participants\": {\"agent\": \"http://127.0.0.1:9010/\"}, \"config\": {}}"
        }]
      }
    }
  }'
```

### Step 7: Interpret Results

The response includes both **Original** (CRMArena-Pro compatible) and **Entropic** (7-Dimension) scores:

```json
{
  "summary": {
    "total_tasks": 5,
    "total_passed": 2,
    "pass_rate": 0.4,
    "avg_score": 70.9
  },
  "dimension_averages": {
    "FUNCTIONAL": 58.0,
    "DRIFT_ADAPTATION": 40.0,
    "TOKEN_EFFICIENCY": 99.5,
    "QUERY_EFFICIENCY": 99.4,
    "ERROR_RECOVERY": 58.0,
    "TRAJECTORY_EFFICIENCY": 100.0,
    "HALLUCINATION_RATE": 88.0
  },
  "original": {
    "scores": {
      "accuracy": 0.4,
      "accuracy_percent": 40.0
    }
  },
  "extension_metrics": {
    "drift_level": "medium",
    "rot_level": "medium",
    "org_type": "b2b"
  },
  "timing": {
    "total_seconds": 42.5,
    "purple_agent_seconds": 40.0,
    "purple_agent_percent": 94.2
  }
}
```

| Field                  | Meaning                                         |
| ---------------------- | ----------------------------------------------- |
| `pass_rate`            | % of tasks with crm_reward > 0                  |
| `avg_score`            | Average 7D score (0-100)                        |
| `original.accuracy`    | CRMArena-Pro compatible accuracy                |
| `extension_metrics`    | Hardcoded adversarial settings used             |
| `purple_agent_percent` | % of time spent in your agent (should be ~90%+) |

**Per-Task Results** include:
- `task_query`: Original question from the dataset
- `dataset_reference`: Source, split, idx, reward_metric
- `entropic`: 7-Dimension scores
- `original`: CRMArena-Pro compatible reward

---

## Part 2: AgentBeats Leaderboard Submission

Once your agent performs well locally, submit it to the official leaderboard!

### Recommended: Watch the Tutorial First

Before starting, watch the **[AgentBeats YouTube Tutorial](https://www.youtube.com/watch?v=ZmBnC4xTyRU)** for a complete walkthrough of the submission process.

### Pre-Submission Checklist

| Requirement            | Details                                                                                     |
| ---------------------- | ------------------------------------------------------------------------------------------- |
| ✅ Agent works locally | Tested with Part 1 above                                                                    |
| ✅ A2A compatible      | Built using [agent-template](https://github.com/RDI-Foundation/agent-template) architecture |
| ✅ Docker image ready  | Built for `linux/amd64`                                                                     |
| ✅ Image is PUBLIC     | GitHub Packages → Settings → Make Public                                                    |

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
6. **Copy your Agent ID** (you'll need this!)

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
env = { OPENAI_API_KEY = "${OPENAI_API_KEY}" }  # Or use NEBIUS_API_KEY

# Your Purple Agent
[[participants]]
agentbeats_id = "YOUR_AGENT_ID_FROM_STEP_2"  # ← Paste your ID here!
name = "agent"
env = { OPENAI_API_KEY = "${OPENAI_API_KEY}" }  # Or use NEBIUS_API_KEY

# Assessment configuration (only task_limit is configurable)
[config]
task_limit = 20           # Number of tasks (omit for full 2,140 tasks)

# NOTE: The following are HARDCODED in the green agent and cannot be changed:
# drift_level = "medium"  (hardcoded)
# rot_level = "medium"    (hardcoded)
# org_type = "b2b"        (hardcoded)
# max_steps = 10          (hardcoded)
# timeout = 300           (hardcoded)
```

> 💡 **API Key**: Use whichever API key matches your secret name in Step 5. Both `OPENAI_API_KEY` and `NEBIUS_API_KEY` work!

### Step 5: Add API Key as GitHub Secret

1. Go to your forked repo → **Settings**
2. **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add ONE of these:

   | Name             | Value           | Provider                                     |
   | ---------------- | --------------- | -------------------------------------------- |
   | `NEBIUS_API_KEY` | Your Nebius key | [nebius.ai](https://nebius.ai) (recommended) |
   | `OPENAI_API_KEY` | Your OpenAI key | [openai.com](https://openai.com)             |

5. Click **"Add secret"**

> ⚠️ Make sure the secret name matches what you used in `scenario.toml`!

### Step 6: Run the Assessment

1. **Commit and push** your `scenario.toml`
2. Go to **Actions** tab in your fork
3. Watch the workflow run (takes ~10-30 minutes depending on task_limit)
4. When complete, click **"Submit your results"** link

### Step 7: Submit to Leaderboard

1. The workflow creates a **Pull Request** with your results
2. **Merge the PR** (or wait for approval if submitting to someone else's leaderboard)
3. Your scores appear on [agentbeats.dev](https://agentbeats.dev) within minutes!

### Troubleshooting Leaderboard Submission

| Issue                      | Solution                                    |
| -------------------------- | ------------------------------------------- |
| Workflow fails immediately | Check `NEBIUS_API_KEY` secret is set        |
| Docker image not found     | Make sure package is **public** on GHCR     |
| Agent times out            | Reduce `task_limit` or increase `timeout`   |
| Low scores                 | Test locally first with `drift_level: none` |

---

## Configuration

### Hardcoded Evaluation Settings (v2.0.0)

For consistent leaderboard evaluation, the following parameters are **hardcoded** in the green agent and cannot be overridden:

| Parameter     | Value      | Description                           |
| ------------- | ---------- | ------------------------------------- |
| `drift_level` | `"medium"` | Schema drift intensity (~30% renamed) |
| `rot_level`   | `"medium"` | Context rot intensity (3-4 distractors) |
| `org_type`    | `"b2b"`    | Business-to-Business dataset split    |
| `max_steps`   | `10`       | Maximum agent turns per task          |
| `timeout`     | `300`      | Seconds per task                      |

> **Why hardcoded?** This ensures all leaderboard submissions are evaluated under identical adversarial conditions, making scores directly comparable.

### Configurable Options

Only `task_limit` can be configured for evaluation runs:

```json
{
  "participants": { "agent": "http://your-agent:port/" },
  "config": {
    "task_limit": 5
  }
}
```

| Parameter         | Type   | Default | Description                    |
| ----------------- | ------ | ------- | ------------------------------ |
| `task_limit`      | int    | null    | Max tasks to run (null = all 2,140) |
| `task_percentage` | float  | 5.0     | % of tasks to sample (if no limit) |
| `task_ids`        | list   | null    | Specific task IDs              |
| `task_categories` | list   | null    | Filter by category             |

### Adversarial Levels (Reference)

| Level      | Schema Drift | Context Rot     |
| ---------- | ------------ | --------------- |
| `none`     | 0% renamed   | 0 distractors   |
| `low`      | ~10% renamed | 1-2 distractors |
| **`medium`** | **~30% renamed** | **3-4 distractors** |
| `high`     | ~50% renamed | 5+ distractors  |

> The benchmark uses **medium** level for both Schema Drift and Context Rot.

---

## Technical Reference

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
  "config": { "org_type": "b2b", "max_steps": 15 },
  "entropy": { "drift_level": "low", "rot_level": "low" }
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

| Dimension             | Weight | Description                  |
| --------------------- | ------ | ---------------------------- |
| FUNCTIONAL            | 30%    | Task completion accuracy     |
| DRIFT_ADAPTATION      | 20%    | Success under schema drift   |
| TOKEN_EFFICIENCY      | 12%    | Fewer tokens = higher score  |
| QUERY_EFFICIENCY      | 12%    | Fewer queries = higher score |
| ERROR_RECOVERY        | 8%     | Graceful failure handling    |
| TRAJECTORY_EFFICIENCY | 10%    | Optimal path to answer       |
| HALLUCINATION_RATE    | 8%     | Valid tool calls only        |

**Total Score = Σ (Dimension × Weight)**

</details>

<details>
<summary><b>Results Format</b></summary>

```json
{
  "summary": {
    "total_tasks": 5,
    "total_passed": 2,
    "pass_rate": 0.4,
    "avg_score": 70.9
  },
  "dimension_averages": {
    "FUNCTIONAL": 58.0,
    "DRIFT_ADAPTATION": 40.0,
    "TOKEN_EFFICIENCY": 99.5,
    "QUERY_EFFICIENCY": 99.4,
    "ERROR_RECOVERY": 58.0,
    "TRAJECTORY_EFFICIENCY": 100.0,
    "HALLUCINATION_RATE": 88.0
  },
  "extension_metrics": {
    "drift_level": "medium",
    "rot_level": "medium",
    "org_type": "b2b",
    "skip_original": false
  },
  "original": {
    "scores": {
      "accuracy": 0.4,
      "accuracy_percent": 40.0
    },
    "summary": {
      "total_tasks": 5,
      "passed": 2,
      "failed": 3
    }
  },
  "timing": {
    "total_seconds": 42.5,
    "purple_agent_seconds": 40.0,
    "green_agent_seconds": 2.5,
    "purple_agent_percent": 94.2
  }
}
```

**Per-Task Result Structure:**

```json
{
  "task_idx": "456",
  "task_category": "sales_insight_mining",
  "task_query": "Which competitors are we at a disadvantage against?",
  "dataset_reference": {
    "source": "Salesforce/CRMArenaPro",
    "split": "b2b",
    "idx": "456",
    "reward_metric": "fuzzy_match"
  },
  "entropic": {
    "crm_reward": 1.0,
    "total_score": 98.3,
    "dimension_scores": {...},
    "success": true
  },
  "original": {
    "reward": 1,
    "parsed_answer": ["Adaptive Design Solutions"]
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

| Category                       | Reward Metric     |
| ------------------------------ | ----------------- |
| lead_qualification             | exact_match       |
| lead_routing                   | exact_match       |
| case_routing                   | exact_match       |
| handle_time                    | exact_match       |
| transfer_count                 | exact_match       |
| sales_insight_mining           | exact_match       |
| monthly_trend_analysis         | exact_match       |
| best_region_identification     | exact_match       |
| conversion_rate_comprehension  | exact_match       |
| knowledge_qa                   | fuzzy_match       |
| named_entity_disambiguation    | exact_match       |
| private_customer_information   | privacy_rejection |
| confidential_company_knowledge | privacy_rejection |
| ... and more                   |

</details>

<details>
<summary><b>Database Schema</b></summary>

| Table                    | Key Columns                              |
| ------------------------ | ---------------------------------------- |
| Account                  | Id, Name, BillingState                   |
| Contact                  | Id, Name, AccountId                      |
| Lead                     | Id, Name, Status, OwnerId                |
| Case                     | Id, Subject, AccountId, OrderItemId\_\_c |
| Opportunity              | Id, Name, StageName, Amount              |
| OrderItem                | Id, OrderId, Product2Id                  |
| Product2                 | Id, Name, ProductCode                    |
| VoiceCallTranscript\_\_c | Id, Body**c, LeadId**c                   |

**Key Relationships:**

```
Case.OrderItemId__c → OrderItem.Id → Product2.Id
Case.AccountId → Account.Id
Lead.Id → VoiceCallTranscript__c.LeadId__c
```

</details>

<details>
<summary><b>Performance & Timing</b></summary>

| Component             | Time    | Notes        |
| --------------------- | ------- | ------------ |
| Task Loading          | 0.01s   | Local cache  |
| Context Build         | 0.001s  | Per task     |
| Evaluation            | 0.15s   | Per task     |
| Scoring               | 0.002s  | Per task     |
| **Green Agent Total** | **<6%** | Near-instant |

**Test Results (5 tasks with drift=medium, rot=medium):**

```
Total:        42.5s
├─ Purple:    40.0s (94.2%)  ← LLM inference + SQL
└─ Green:     2.5s  (5.8%)   ← Evaluation overhead
```

**Per-Task Breakdown:**

| Task | Category | Time | Purple % |
|------|----------|------|----------|
| 456 | sales_insight_mining | 3.6s | 100% |
| 102 | monthly_trend_analysis | 3.8s | 100% |
| 1126 | best_region_identification | 17.3s | 95.5% |
| 1003 | conversion_rate_comprehension | 9.7s | 91.3% |
| 914 | handle_time | 8.1s | 89.6% |

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

## Changelog

### v2.0.0 (February 28, 2026)

- ✅ **Hardcoded Adversarial Settings**: `drift_level=medium`, `rot_level=medium`, `org_type=b2b` for consistent leaderboard evaluation
- ✅ **Dual Scoring Modes**: Both Original (CRMArena-Pro) and Entropic (7-Dimension) scores
- ✅ **Enhanced Result Format**: Includes `task_query` and `dataset_reference` for traceability
- ✅ **Full Dataset Support**: `task_limit=None` runs all 2,140 tasks
- ✅ **OpenAI API Support**: Works with `OPENAI_API_KEY` in addition to `NEBIUS_API_KEY`

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
