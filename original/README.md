# Original CRMArena-Pro Compatibility Mode

This folder contains evaluation logic compatible with Salesforce's original CRMArena-Pro benchmark, enabling direct score comparison between AgentBeats leaderboard results and published benchmark scores.

## Overview

By **default**, both original and entropic scores are computed for each task. This enables:

- Direct comparison with published CRMArena-Pro results
- Separate tabs on AgentBeats leaderboard (original vs entropic)
- Analysis of how adversarial perturbations affect performance

## Configuration

Configuration is managed centrally via `shared/config.py` and environment variables.

### Environment Variables (`.env`)

```bash
# LLM Configuration (used by evaluators)
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o

# Assessment defaults
ASSESSMENT_SKIP_ORIGINAL=false  # Default: run both modes
```

### Request Config

```json
{
  "config": {
    "skip_original": false, // Default: run both modes
    "task_limit": 10
  }
}
```

Set `skip_original: true` to disable original scoring and only run entropic mode.

## Files

| File           | Purpose                                                  |
| -------------- | -------------------------------------------------------- |
| `evaluator.py` | LLM-based answer extraction with 5 task-specific prompts |
| `scorer.py`    | Binary scoring (0/1) and accuracy aggregation            |
| `metrics.py`   | EM, F1, BLEU, ROUGE for fuzzy_match tasks                |

## How Original Mode Differs

| Aspect                | Original Mode             | Entropic Mode              |
| --------------------- | ------------------------- | -------------------------- |
| **Perturbations**     | None (disabled)           | Schema Drift + Context Rot |
| **Scoring**           | Binary (0/1) → Accuracy % | 7 Dimensions               |
| **Answer Extraction** | Task-specific LLM prompts | Basic parsing              |
| **Output**            | Single accuracy metric    | Multi-dimensional scores   |

## Task-Specific Extraction Prompts

Original CRMArena-Pro uses different prompts based on task type:

| Task Type                    | Extraction Target  | Prompt Used                       |
| ---------------------------- | ------------------ | --------------------------------- |
| `best_region_identification` | States (NY, CA)    | `state_system_prompt`             |
| `monthly_trend_analysis`     | Months (May, June) | `month_system_prompt`             |
| `lead_qualification`         | BANT factors       | `bant_system_prompt`              |
| `wrong_stage_rectification`  | Opportunity stages | `opportunity_stage_system_prompt` |
| All other tasks              | IDs                | `id_system_prompt`                |

## Reward Metrics

The dataset uses 3 reward metrics:

| Metric              | Tasks       | Evaluation Method                 |
| ------------------- | ----------- | --------------------------------- |
| `exact_match`       | 1,700 (79%) | LLM extraction + exact comparison |
| `fuzzy_match`       | 200 (9%)    | EM, F1, BLEU, ROUGE scores        |
| `privacy_rejection` | 240 (11%)   | LLM checks if agent refused       |

## Output Format

Original mode produces output in this format:

```json
{
  "mode": "original",
  "scores": {
    "accuracy": 0.78,
    "accuracy_percent": 78.0
  },
  "summary": {
    "total_tasks": 100,
    "passed": 78,
    "failed": 22
  },
  "by_category": {
    "case_routing": { "total": 10, "passed": 8, "accuracy": 0.8 },
    "lead_qualification": { "total": 15, "passed": 12, "accuracy": 0.8 }
  }
}
```

## Reference

Ported from: `refrence/CRMArena-main/crm_sandbox/env/env.py` (lines 267-566)

Paper: [CRMArena-Pro: Holistic Assessment of LLM Agents](https://arxiv.org/abs/2505.18878)
