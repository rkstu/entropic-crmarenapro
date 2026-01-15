"""
Entropic CRMArena Green Agent

Implements CRM agent evaluation with Schema Drift, Context Rot,
and 7-Dimension Scoring.
"""

import json
import logging
import random
import time
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ValidationError, Field
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart, DataPart
from a2a.utils import get_message_text, new_agent_text_message

from messenger import Messenger

# Import CRM modules (these will be in the crm/ directory)
from crm.tasks import TaskLoader, CRMTask, TASK_CATEGORIES
from crm.entropy import EntropyEngine, DriftLevel, RotLevel
from crm.evaluator import CRMArenaEvaluator
from crm.scorer import SevenDimensionScorer, AgentMetrics

logger = logging.getLogger(__name__)


class EvalRequest(BaseModel):
    """Request format sent by the AgentBeats platform to green agents."""
    participants: dict[str, HttpUrl]  # role -> agent URL
    config: dict[str, Any]


class AssessmentConfig(BaseModel):
    """Configuration for CRMArena assessment."""
    # Task selection
    task_ids: Optional[list[str]] = Field(None, description="Specific task IDs to run")
    task_categories: Optional[list[str]] = Field(None, description="Filter by task categories")
    task_percentage: float = Field(5.0, description="Percentage of tasks to sample (1-100)")
    task_limit: Optional[int] = Field(None, description="Maximum number of tasks")
    
    # Entropy settings (our innovation)
    drift_level: str = Field("none", description="Schema drift: none, low, medium, high")
    rot_level: str = Field("none", description="Context rot: none, low, medium, high")
    
    # Evaluation settings
    max_steps: int = Field(15, description="Maximum agent turns per task")
    timeout: int = Field(300, description="Timeout per task in seconds")
    org_type: str = Field("b2b", description="Organization type: b2b or b2c")


class Agent:
    """
    Entropic CRMArena Green Agent.
    
    Evaluates CRM agents with adversarial robustness testing:
    - Schema Drift: Randomly renames database columns
    - Context Rot: Injects distractor records into results
    - 7D Scoring: Multi-dimensional evaluation
    """
    
    # Required participant role
    required_roles: list[str] = ["agent"]
    required_config_keys: list[str] = []  # All config has defaults

    def __init__(self):
        self.messenger = Messenger()
        self.task_loader: Optional[TaskLoader] = None
        self.entropy_engine: Optional[EntropyEngine] = None
        self.evaluator: Optional[CRMArenaEvaluator] = None
        self.scorer = SevenDimensionScorer()
        self.results: list[dict[str, Any]] = []

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        """Validate the assessment request."""
        missing_roles = set(self.required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing required participant roles: {missing_roles}"

        # Validate config values
        config = request.config
        
        drift = config.get("drift_level", "none")
        if drift not in ["none", "low", "medium", "high"]:
            return False, f"Invalid drift_level: {drift}. Must be none/low/medium/high"
        
        rot = config.get("rot_level", "none")
        if rot not in ["none", "low", "medium", "high"]:
            return False, f"Invalid rot_level: {rot}. Must be none/low/medium/high"
        
        org = config.get("org_type", "b2b")
        if org not in ["b2b", "b2c"]:
            return False, f"Invalid org_type: {org}. Must be b2b/b2c"
        
        # Validate task categories if specified
        categories = config.get("task_categories")
        if categories:
            invalid = [c for c in categories if c not in TASK_CATEGORIES]
            if invalid:
                return False, f"Invalid task categories: {invalid}"

        return True, "ok"

    def _parse_config(self, config: dict[str, Any]) -> AssessmentConfig:
        """Parse and validate assessment configuration."""
        return AssessmentConfig(
            task_ids=config.get("task_ids"),
            task_categories=config.get("task_categories"),
            task_percentage=config.get("task_percentage", 5.0),
            task_limit=config.get("task_limit"),
            drift_level=config.get("drift_level", "none"),
            rot_level=config.get("rot_level", "none"),
            max_steps=config.get("max_steps", 15),
            timeout=config.get("timeout", 300),
            org_type=config.get("org_type", "b2b"),
        )

    def _initialize_components(self, config: AssessmentConfig):
        """Initialize evaluation components."""
        # Task loader
        self.task_loader = TaskLoader(org_type=config.org_type)
        
        # Entropy engine for drift/rot
        drift = DriftLevel(config.drift_level) if config.drift_level != "none" else DriftLevel.NONE
        rot = RotLevel(config.rot_level) if config.rot_level != "none" else RotLevel.NONE
        self.entropy_engine = EntropyEngine(drift_level=drift, rot_level=rot)
        
        # Answer evaluator
        self.evaluator = CRMArenaEvaluator()

    def _get_tasks(self, config: AssessmentConfig) -> list[CRMTask]:
        """Get tasks based on configuration."""
        if config.task_ids:
            # Specific task IDs
            tasks = []
            for task_id in config.task_ids:
                task = self.task_loader.get_task_by_idx(task_id)
                if task:
                    tasks.append(task)
            return tasks
        
        elif config.task_categories:
            # Filter by categories
            return self.task_loader.load_tasks(
                categories=config.task_categories,
                limit=config.task_limit
            )
        
        else:
            # Sample random tasks
            all_tasks = self.task_loader.load_tasks()
            sample_size = int(len(all_tasks) * config.task_percentage / 100)
            if config.task_limit:
                sample_size = min(sample_size, config.task_limit)
            sample_size = max(1, sample_size)  # At least 1 task
            
            random.seed(42)  # Reproducibility
            return random.sample(all_tasks, min(sample_size, len(all_tasks)))

    async def _evaluate_single_task(
        self,
        task: CRMTask,
        purple_agent_url: str,
        config: AssessmentConfig,
        updater: TaskUpdater,
    ) -> dict[str, Any]:
        """
        Evaluate a single task with the purple agent.
        
        Sends the task prompt to the purple agent and evaluates the response.
        Tracks metrics for all 7 dimensions of scoring.
        """
        task_start_time = time.time()
        
        # Build task context with entropy applied
        context_start = time.time()
        task_context = self._build_task_context(task, config)
        context_time = time.time() - context_start
        
        # Initialize metric tracking
        conversation_turns = 0
        total_tokens_estimate = 0
        tool_calls_detected = 0
        invalid_tool_calls = 0
        queries_detected = 0
        errors_encountered = 0
        errors_recovered = 0
        purple_agent_time = 0.0  # Track time spent waiting for Purple Agent
        
        # Optimal turns heuristic based on task complexity
        optimal_turns = self._estimate_optimal_turns(task)
        
        # Send task to purple agent
        try:
            # First turn - send task
            conversation_turns += 1
            turn_start = time.time()
            response = await self.messenger.talk_to_agent(
                message=json.dumps(task_context),
                url=purple_agent_url,
                new_conversation=True,
                timeout=config.timeout,
            )
            turn_time = time.time() - turn_start
            purple_agent_time += turn_time
            logger.info(f"[TIMING] Task {task.idx} Turn 1: {turn_time:.2f}s (Purple Agent)")
            
            # Track metrics from response
            response_metrics = self._parse_response_metrics(response)
            total_tokens_estimate += response_metrics.get("tokens", 0)
            tool_calls_detected += response_metrics.get("tool_calls", 0)
            invalid_tool_calls += response_metrics.get("invalid_tool_calls", 0)
            queries_detected += response_metrics.get("queries", 0)
            
            # Multi-turn: Allow agent to request more info or make tool calls
            max_turns = min(config.max_steps, 10)
            while conversation_turns < max_turns:
                # Check if agent needs more turns
                needs_continuation = self._check_needs_continuation(response)
                if not needs_continuation:
                    break
                
                conversation_turns += 1
                try:
                    turn_start = time.time()
                    response = await self.messenger.talk_to_agent(
                        message="Continue processing. Provide your final answer.",
                        url=purple_agent_url,
                        new_conversation=False,  # Continue conversation
                        timeout=config.timeout,
                    )
                    turn_time = time.time() - turn_start
                    purple_agent_time += turn_time
                    logger.info(f"[TIMING] Task {task.idx} Turn {conversation_turns}: {turn_time:.2f}s (Purple Agent)")
                    
                    # Track additional metrics
                    turn_metrics = self._parse_response_metrics(response)
                    total_tokens_estimate += turn_metrics.get("tokens", 0)
                    tool_calls_detected += turn_metrics.get("tool_calls", 0)
                    queries_detected += turn_metrics.get("queries", 0)
                    
                except Exception as e:
                    errors_encountered += 1
                    logger.warning(f"Turn {conversation_turns} error: {e}")
                    break
            
            # Parse agent response
            agent_answer = self._extract_answer(response)
            
            # Evaluate answer
            eval_start = time.time()
            eval_result = self.evaluator.evaluate(
                proposed_answer=agent_answer,
                gt_answer=task.answer,
                reward_metric=task.reward_metric,
                task_name=task.task,
            )
            eval_time = time.time() - eval_start
            
            crm_reward = eval_result.get("reward", 0)
            task_completed = True
            final_state = "success" if crm_reward > 0 else "failed"
            
            # Create metrics for 7D scoring with REAL tracked values
            metrics = AgentMetrics(
                task_completed=task_completed,
                crm_reward=crm_reward,
                drift_level=self._drift_level_to_int(config.drift_level),
                drift_percentage=self.entropy_engine.get_drift_percentage() if self.entropy_engine else 0,
                rot_level=self._rot_level_to_int(config.rot_level),
                # Token tracking
                total_tokens=total_tokens_estimate,
                # Query tracking
                queries_executed=queries_detected,
                queries_failed=0,
                # Error tracking
                errors_encountered=errors_encountered,
                errors_recovered=errors_recovered,
                final_state=final_state,
                # Trajectory tracking (TES)
                actual_turns=conversation_turns,
                optimal_turns=optimal_turns,
                # Hallucination tracking
                total_tool_calls=tool_calls_detected,
                invalid_tool_calls=invalid_tool_calls,
                malformed_tool_calls=0,
            )
            
            # Calculate 7D score
            score_start = time.time()
            score_result = self.scorer.score(task.idx, task.task, metrics)
            score_time = time.time() - score_start
            
            # Calculate total task time
            task_total_time = time.time() - task_start_time
            green_agent_time = task_total_time - purple_agent_time
            
            # Log timing breakdown
            logger.info(f"[TIMING] Task {task.idx} COMPLETE:")
            logger.info(f"  ├─ Purple Agent: {purple_agent_time:.2f}s ({purple_agent_time/task_total_time*100:.1f}%)")
            logger.info(f"  ├─ Green Agent:  {green_agent_time:.2f}s ({green_agent_time/task_total_time*100:.1f}%)")
            logger.info(f"  │   ├─ Context build: {context_time:.3f}s")
            logger.info(f"  │   ├─ Evaluation:    {eval_time:.3f}s")
            logger.info(f"  │   └─ Scoring:       {score_time:.3f}s")
            logger.info(f"  └─ TOTAL: {task_total_time:.2f}s")
            
            return {
                "task_idx": task.idx,
                "task_category": task.task,
                "crm_reward": crm_reward,
                "total_score": score_result.total_score,
                "dimension_scores": score_result.dimension_breakdown,
                "agent_answer": agent_answer[:500] if agent_answer else None,
                "expected_answer": str(task.answer)[:200],
                "success": crm_reward > 0,
                # Include tracking metrics in output for transparency
                "metrics": {
                    "turns": conversation_turns,
                    "tokens_estimate": total_tokens_estimate,
                    "tool_calls": tool_calls_detected,
                    "queries": queries_detected,
                },
                # Timing breakdown
                "timing": {
                    "total_seconds": round(task_total_time, 2),
                    "purple_agent_seconds": round(purple_agent_time, 2),
                    "green_agent_seconds": round(green_agent_time, 2),
                    "purple_agent_percent": round(purple_agent_time/task_total_time*100, 1) if task_total_time > 0 else 0,
                }
            }
            
        except Exception as e:
            logger.error(f"Task {task.idx} evaluation failed: {e}")
            return {
                "task_idx": task.idx,
                "task_category": task.task,
                "crm_reward": 0,
                "total_score": 0,
                "dimension_scores": {},
                "error": str(e),
                "success": False,
            }
    
    def _estimate_optimal_turns(self, task: CRMTask) -> int:
        """Estimate optimal number of turns based on task complexity."""
        # Simple tasks: 1 turn
        # Complex multi-hop: 2-3 turns
        simple_tasks = ["knowledge_qa", "named_entity_disambiguation", "lead_qualification"]
        complex_tasks = ["monthly_trend_analysis", "conversion_rate_comprehension", "handle_time"]
        
        if task.task in simple_tasks:
            return 1
        elif task.task in complex_tasks:
            return 3
        else:
            return 2
    
    def _parse_response_metrics(self, response: str) -> dict[str, int]:
        """
        Parse metrics from agent response.
        
        Agents can optionally include metrics in their response:
        {"metrics": {"tokens": 500, "tool_calls": 3, "queries": 2}}
        
        Otherwise, estimate from response characteristics.
        """
        metrics = {
            "tokens": 0,
            "tool_calls": 0,
            "invalid_tool_calls": 0,
            "queries": 0,
        }
        
        if not response:
            return metrics
        
        # Try to parse explicit metrics from response
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "metrics" in data:
                agent_metrics = data["metrics"]
                metrics["tokens"] = agent_metrics.get("tokens", 0)
                metrics["tool_calls"] = agent_metrics.get("tool_calls", 0)
                metrics["queries"] = agent_metrics.get("queries", 0)
                return metrics
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Estimate tokens from response length (~4 chars per token)
        metrics["tokens"] = len(response) // 4
        
        # Detect tool calls by common patterns
        tool_patterns = ["SELECT", "FROM", "WHERE", "query(", "search(", "get_", "find_"]
        for pattern in tool_patterns:
            metrics["tool_calls"] += response.upper().count(pattern)
        
        # Detect SQL queries
        sql_patterns = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        for pattern in sql_patterns:
            metrics["queries"] += response.upper().count(pattern)
        
        return metrics
    
    def _check_needs_continuation(self, response: str) -> bool:
        """Check if agent response indicates it needs more turns."""
        if not response:
            return False
        
        # If agent gave a final answer, don't continue
        if "<respond>" in response.lower() or '"answer"' in response.lower():
            return False
        
        # Check for explicit continuation signals (be conservative!)
        continuation_signals = [
            "TOOL_CALL",
            "ACTION:",
            "<execute>",
            "<describe>",
        ]
        
        response_lower = response.lower()
        for signal in continuation_signals:
            if signal.lower() in response_lower:
                return True
        
        return False

    def _build_task_context(self, task: CRMTask, config: AssessmentConfig) -> dict[str, Any]:
        """Build task context with optional entropy transformations."""
        prompt = task.query
        required_context = task.get_required_context()
        
        # Apply Schema Drift - modify column names in prompt and context
        if config.drift_level != "none" and self.entropy_engine:
            prompt, drift_applied = self._apply_schema_drift(prompt, config.drift_level)
            required_context = self._apply_drift_to_context(required_context, config.drift_level)
            logger.info(f"Schema drift applied: {drift_applied} modifications")
        
        # Apply Context Rot - inject distractor information
        if config.rot_level != "none" and self.entropy_engine:
            required_context = self._apply_context_rot(required_context, config.rot_level)
            logger.info(f"Context rot applied at level: {config.rot_level}")
        
        context = {
            "type": "crm_task",
            "task_id": task.idx,
            "task_category": task.task,
            "prompt": prompt,
            "persona": task.persona,
            "required_context": required_context,
            "config": {
                "org_type": config.org_type,
                "max_steps": config.max_steps,
            }
        }
        
        # Add entropy metadata if active
        if config.drift_level != "none" or config.rot_level != "none":
            context["entropy"] = {
                "drift_level": config.drift_level,
                "rot_level": config.rot_level,
                "drift_mappings": self.entropy_engine.state.drift_mappings if self.entropy_engine else [],
                "note": "Schema/context has been modified for robustness testing"
            }
        
        return context
    
    def _apply_schema_drift(self, text: str, drift_level: str) -> tuple[str, int]:
        """Apply schema drift by replacing column names with synonyms."""
        if not text or drift_level == "none":
            return text, 0
        
        # Column name mappings based on drift level
        drift_mappings = {
            "low": {
                "Status": "CaseStatus",
                "OwnerId": "AssignedTo",
                "AccountId": "CustomerRef",
            },
            "medium": {
                "Status": "StatusCode",
                "OwnerId": "AssignedAgent",
                "AccountId": "ClientId",
                "ContactId": "PersonRef",
                "Subject": "Title",
                "Description": "Details",
            },
            "high": {
                "Status": "st_code",
                "OwnerId": "own_ref",
                "AccountId": "acct_id",
                "ContactId": "cont_ref",
                "Subject": "subj",
                "Description": "desc",
                "Priority": "pri_level",
                "CreatedDate": "create_dt",
                "CaseNumber": "ticket_num",
            },
        }
        
        mappings = drift_mappings.get(drift_level, {})
        modifications = 0
        
        for original, drifted in mappings.items():
            if original in text:
                text = text.replace(original, drifted)
                modifications += 1
        
        return text, modifications
    
    def _apply_drift_to_context(self, context: str, drift_level: str) -> str:
        """Apply schema drift to the required context."""
        if not context:
            return context
        drifted, _ = self._apply_schema_drift(context, drift_level)
        return drifted
    
    def _apply_context_rot(self, context: str, rot_level: str) -> str:
        """Inject distractor information into the context."""
        if not context or rot_level == "none":
            return context
        
        # Distractor templates based on rot level
        distractors = {
            "low": [
                "\n\n[Note: Some records may have been updated recently. Verify timestamps.]",
            ],
            "medium": [
                "\n\n[System Notice: Database migration in progress. Some field names may vary.]",
                "\n\n[Info: Legacy records from previous CRM system included for reference.]",
            ],
            "high": [
                "\n\n[Warning: Multiple customer records with similar names exist. Verify IDs carefully.]",
                "\n\n[Notice: Archived cases from 2019-2020 included. Filter by date if needed.]",
                "\n\n[Alert: Some account records are marked as duplicates pending merge.]",
            ],
        }
        
        import random
        rot_items = distractors.get(rot_level, [])
        if rot_items:
            random.seed(hash(context) % 2**32)  # Reproducible
            num_distractors = {"low": 1, "medium": 2, "high": 3}.get(rot_level, 1)
            selected = random.sample(rot_items, min(num_distractors, len(rot_items)))
            context = context + "".join(selected)
        
        return context

    def _extract_answer(self, response: str) -> str:
        """Extract the answer from agent response."""
        if not response:
            return ""
        
        # Try to parse as JSON
        try:
            data = json.loads(response)
            if isinstance(data, dict):
                return data.get("answer", data.get("response", str(data)))
            return str(data)
        except json.JSONDecodeError:
            return response

    def _drift_level_to_int(self, level: str) -> int:
        """Convert drift level string to int."""
        return {"none": 0, "low": 1, "medium": 2, "high": 3}.get(level, 0)

    def _rot_level_to_int(self, level: str) -> int:
        """Convert rot level string to int."""
        return {"none": 0, "low": 1, "medium": 2, "high": 3}.get(level, 0)

    def _create_aggregated_results(
        self,
        config: AssessmentConfig,
        purple_agent_id: str,
    ) -> dict[str, Any]:
        """Create aggregated results artifact (AgentBeats-compatible format)."""
        total_tasks = len(self.results)
        total_passed = sum(1 for r in self.results if r.get("crm_reward", 0) > 0)
        
        # Calculate averages
        avg_score = sum(r.get("total_score", 0) for r in self.results) / total_tasks if total_tasks > 0 else 0
        pass_rate = total_passed / total_tasks if total_tasks > 0 else 0
        
        # Dimension averages
        dimension_avgs = {}
        for result in self.results:
            for dim, score in result.get("dimension_scores", {}).items():
                if dim not in dimension_avgs:
                    dimension_avgs[dim] = []
                dimension_avgs[dim].append(score)
        
        dimension_averages = {
            dim: sum(scores) / len(scores) if scores else 0
            for dim, scores in dimension_avgs.items()
        }
        
        # Category breakdown
        by_category = {}
        for result in self.results:
            cat = result.get("task_category", "unknown")
            if cat not in by_category:
                by_category[cat] = {"count": 0, "passed": 0, "total_score": 0}
            by_category[cat]["count"] += 1
            by_category[cat]["passed"] += 1 if result.get("crm_reward", 0) > 0 else 0
            by_category[cat]["total_score"] += result.get("total_score", 0)
        
        for cat in by_category:
            count = by_category[cat]["count"]
            by_category[cat]["pass_rate"] = by_category[cat]["passed"] / count if count > 0 else 0
            by_category[cat]["avg_score"] = by_category[cat]["total_score"] / count if count > 0 else 0
        
        return {
            "participants": {
                "agent": purple_agent_id,
            },
            "results": self.results,
            "summary": {
                "pass_rate": round(pass_rate, 3),
                "total_tasks": total_tasks,
                "total_passed": total_passed,
                "avg_score": round(avg_score, 1),
            },
            "dimension_averages": {k: round(v, 1) for k, v in dimension_averages.items()},
            "by_category": by_category,
            "extension_metrics": {
                "drift_level": config.drift_level,
                "rot_level": config.rot_level,
                "org_type": config.org_type,
            },
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """
        Run the CRMArena assessment.
        
        Main entry point called by the A2A executor.
        """
        assessment_start_time = time.time()
        logger.info("=" * 60)
        logger.info("[TIMING] ASSESSMENT STARTED")
        logger.info("=" * 60)
        
        input_text = get_message_text(message)

        # Parse and validate request
        try:
            request: EvalRequest = EvalRequest.model_validate_json(input_text)
            ok, msg = self.validate_request(request)
            if not ok:
                await updater.reject(new_agent_text_message(msg))
                return
        except ValidationError as e:
            await updater.reject(new_agent_text_message(f"Invalid request: {e}"))
            return

        # Parse config
        config = self._parse_config(request.config)
        
        # Get purple agent URL
        purple_agent_url = str(request.participants["agent"])
        
        # Initialize components
        await updater.update_status(
            TaskState.working,
            new_agent_text_message("Initializing CRMArena evaluation components...")
        )
        
        init_start = time.time()
        try:
            self._initialize_components(config)
        except Exception as e:
            await updater.reject(new_agent_text_message(f"Failed to initialize: {e}"))
            return
        init_time = time.time() - init_start
        logger.info(f"[TIMING] Component initialization: {init_time:.3f}s")
        
        # Get tasks
        task_load_start = time.time()
        tasks = self._get_tasks(config)
        total_tasks = len(tasks)
        task_load_time = time.time() - task_load_start
        logger.info(f"[TIMING] Task loading ({total_tasks} tasks): {task_load_time:.3f}s")
        
        if total_tasks == 0:
            await updater.reject(new_agent_text_message("No tasks found matching configuration"))
            return
        
        await updater.update_status(
            TaskState.working,
            new_agent_text_message(
                f"Starting assessment with {total_tasks} tasks. "
                f"Drift: {config.drift_level}, Rot: {config.rot_level}"
            )
        )
        
        # Run evaluation for each task
        self.results = []
        total_purple_time = 0.0
        total_green_time = 0.0
        
        for i, task in enumerate(tasks):
            # Progress update
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    f"[{i+1}/{total_tasks}] Evaluating task {task.idx} ({task.task})"
                )
            )
            
            # Evaluate task
            result = await self._evaluate_single_task(task, purple_agent_url, config, updater)
            self.results.append(result)
            
            # Track timing
            if "timing" in result:
                total_purple_time += result["timing"].get("purple_agent_seconds", 0)
                total_green_time += result["timing"].get("green_agent_seconds", 0)
            
            # Task completion update
            status = "✓" if result.get("crm_reward", 0) > 0 else "✗"
            timing_info = ""
            if "timing" in result:
                timing_info = f" ({result['timing']['total_seconds']:.1f}s)"
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    f"[{i+1}/{total_tasks}] {status} Task {task.idx}: score={result.get('total_score', 0):.1f}{timing_info}"
                )
            )
        
        # Create final results artifact
        aggregated = self._create_aggregated_results(config, purple_agent_url)
        
        # Calculate total time
        assessment_total_time = time.time() - assessment_start_time
        overhead_time = assessment_total_time - total_purple_time - total_green_time
        
        # Log final timing summary
        logger.info("=" * 60)
        logger.info("[TIMING] ASSESSMENT COMPLETE - SUMMARY")
        logger.info("=" * 60)
        logger.info(f"  Total tasks:        {total_tasks}")
        logger.info(f"  Total time:         {assessment_total_time:.2f}s")
        logger.info(f"  ├─ Purple Agent:    {total_purple_time:.2f}s ({total_purple_time/assessment_total_time*100:.1f}%)")
        logger.info(f"  ├─ Green Agent:     {total_green_time:.2f}s ({total_green_time/assessment_total_time*100:.1f}%)")
        logger.info(f"  └─ Overhead:        {overhead_time:.2f}s ({overhead_time/assessment_total_time*100:.1f}%)")
        logger.info(f"  Avg time per task:  {assessment_total_time/total_tasks:.2f}s")
        logger.info("=" * 60)
        
        # Add timing to aggregated results
        aggregated["timing"] = {
            "total_seconds": round(assessment_total_time, 2),
            "purple_agent_seconds": round(total_purple_time, 2),
            "green_agent_seconds": round(total_green_time, 2),
            "avg_seconds_per_task": round(assessment_total_time / total_tasks, 2),
            "purple_agent_percent": round(total_purple_time/assessment_total_time*100, 1) if assessment_total_time > 0 else 0,
        }
        
        # Calculate summary text with timing
        summary_text = (
            f"Assessment Complete\n"
            f"==================\n"
            f"Tasks: {aggregated['summary']['total_tasks']}\n"
            f"Passed: {aggregated['summary']['total_passed']}\n"
            f"Pass Rate: {aggregated['summary']['pass_rate']:.1%}\n"
            f"Avg Score: {aggregated['summary']['avg_score']:.1f}\n"
            f"\nTiming:\n"
            f"  Total: {assessment_total_time:.1f}s\n"
            f"  Purple Agent: {total_purple_time:.1f}s ({total_purple_time/assessment_total_time*100:.0f}%)\n"
            f"  Green Agent: {total_green_time:.1f}s ({total_green_time/assessment_total_time*100:.0f}%)\n"
            f"\nDimension Averages:\n"
        )
        for dim, score in aggregated.get("dimension_averages", {}).items():
            summary_text += f"  {dim}: {score:.1f}\n"
        
        await updater.add_artifact(
            parts=[
                Part(root=TextPart(text=summary_text)),
                Part(root=DataPart(data=aggregated))
            ],
            name="CRMArena Assessment Results",
        )
