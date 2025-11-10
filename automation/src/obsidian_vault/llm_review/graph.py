"""LangGraph workflow for note review and fixing."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from loguru import logger

from obsidian_vault.utils import TaxonomyLoader, build_note_index
from obsidian_vault.utils.frontmatter import load_frontmatter_text
from obsidian_vault.validators import ValidatorRegistry

from .agents import (
    run_bilingual_parity_check,
    run_concept_enrichment,
    run_issue_fixing,
    run_metadata_sanity_check,
    run_qa_failure_summary,
    run_qa_verification,
    run_technical_review,
)
from .analytics import ReviewAnalyticsRecorder
from .atomic_related_fixer import AtomicRelatedFixer
from .deterministic_fixer import DeterministicFixer
from .fix_memory import FixMemory
from .smart_code_parity import SmartCodeParityChecker
from .smart_validators import SmartValidatorSelector
from .state import NoteReviewState, NoteReviewStateDict, ReviewIssue
from .strict_qa_criteria import StrictQAVerifier
from .timestamp_policy import TimestampPolicy

if TYPE_CHECKING:
    from obsidian_vault.utils.taxonomy_loader import TaxonomyLoader as TaxonomyLoaderType


class CompletionMode(str, Enum):
    """Completion strictness modes for validation.

    Determines how strict the system is about remaining issues before completion.
    """
    STRICT = "strict"           # Block on any issue
    STANDARD = "standard"       # Allow minor warnings (recommended)
    PERMISSIVE = "permissive"   # Allow some errors (use with caution)


# Thresholds: {severity: max_allowed_count}
COMPLETION_THRESHOLDS = {
    CompletionMode.STRICT: {
        "CRITICAL": 0,
        "ERROR": 0,
        "WARNING": 0,
        "INFO": float('inf'),  # Informational never blocks
    },
    CompletionMode.STANDARD: {
        "CRITICAL": 0,
        "ERROR": 0,
        "WARNING": 3,  # Allow up to 3 warnings
        "INFO": float('inf'),
    },
    CompletionMode.PERMISSIVE: {
        "CRITICAL": 0,
        "ERROR": 2,   # Allow up to 2 errors (use cautiously)
        "WARNING": 10,  # Allow up to 10 warnings
        "INFO": float('inf'),
    },
}


class ProcessingProfile(str, Enum):
    """Operating modes that trade cost for stability or thoroughness."""

    BALANCED = "balanced"
    STABILITY = "stability"
    THOROUGH = "thorough"


class _ProfileSettings(TypedDict):
    """Internal configuration flags for a :class:`ProcessingProfile`."""

    parallel_validators: bool
    smart_selection: bool
    full_validator_pass: bool
    iteration_bonus: int
    enable_analytics: bool


PROFILE_SETTINGS: dict[ProcessingProfile, _ProfileSettings] = {
    ProcessingProfile.BALANCED: {
        "parallel_validators": True,
        "smart_selection": True,
        "full_validator_pass": False,
        "iteration_bonus": 0,
        "enable_analytics": True,
    },
    ProcessingProfile.STABILITY: {
        # Run validators sequentially to reduce contention while keeping
        # adaptive selection to avoid unnecessary work.
        "parallel_validators": False,
        "smart_selection": True,
        "full_validator_pass": False,
        "iteration_bonus": 0,
        "enable_analytics": True,
    },
    ProcessingProfile.THOROUGH: {
        # Aggressive quality mode: always execute the full validator suite and
        # allow extra iterations to chase down lingering issues.
        "parallel_validators": False,
        "smart_selection": False,
        "full_validator_pass": True,
        "iteration_bonus": 2,
        "enable_analytics": True,
    },
}


class ReviewGraph:
    """LangGraph workflow for reviewing and fixing notes.

    WORKFLOW ARCHITECTURE:
    ----------------------
    START → initial_llm_review → run_validators (includes metadata check each iteration)
      → check_bilingual_parity → [decision] → llm_fix_issues (loop) OR qa_verification (final)
      → [on failure] → summarize_qa_failures → END

    METADATA VALIDATION STRATEGY:
    -----------------------------
    Metadata sanity checks now run INSIDE the validator loop (not just once at the start).
    This ensures that any YAML changes made by the fix agent are re-validated on subsequent
    iterations, closing the gap where auto-created concept files or repaired frontmatter
    fields would bypass validation.

    QA FAILURE HANDLING:
    --------------------
    When the workflow reaches max iterations with unresolved issues or QA verification fails
    repeatedly, the summarize_qa_failures node is triggered to create an actionable summary
    for human follow-up. This prevents the workflow from silently failing without providing
    context about what went wrong and what needs manual attention.

    EXAMPLE DEBUG LOG TRACE (typical iteration):
    --------------------------------------------
    INFO: Running validators (iteration 1)
    INFO: Running metadata sanity check for note.md (iteration 1)
    DEBUG: Metadata sanity check found 2 issue(s)
    DEBUG: Running structural validators...
    DEBUG: Found 3 total issues (2 metadata + 1 structural)
    DEBUG: Pre-parity state: 3 existing validator issue(s)
    INFO: Running bilingual parity check for note.md (iteration 1)
    WARNING: Parity check found 2 new parity issue(s) - total issues: 3 validator + 2 parity = 5
    DEBUG: Parity issues: ['EN Answer has 3 examples, RU Answer has 1 example']
    DEBUG: [Decision] Evaluating next step: iteration=1/5, issues=5, error=False, completed=False, qa_passed=None
    INFO: [Parity Check Complete] Decision=continue, TotalIssues=5 (validator=3, parity=2), Iteration=1/5
    INFO: Fixing 5 issues
    INFO: Applied fixes: ['Fixed YAML field moc', 'Added missing RU examples', ...]

    [Loop back to validators...]

    INFO: Running validators (iteration 2)
    INFO: Running metadata sanity check for note.md (iteration 2)
    DEBUG: No metadata issues found
    DEBUG: Running structural validators...
    DEBUG: Found 0 total issues
    DEBUG: Pre-parity state: 0 existing validator issue(s)
    INFO: Running bilingual parity check for note.md (iteration 2)
    INFO: Bilingual parity check passed - 0 validator issue(s) remain
    DEBUG: [Decision] Evaluating next step: iteration=2/5, issues=0, error=False, completed=False, qa_passed=None
    INFO: No validator issues - routing to QA verification
    INFO: Running final QA verification for note.md
    SUCCESS: QA verification passed: All content accurate, bilingual parity maintained
    """

    def __init__(
        self,
        *,
        vault_root: Path,
        taxonomy: TaxonomyLoaderType,
        note_index: set[str],
        max_iterations: int = 5,
        dry_run: bool = False,
        completion_mode: CompletionMode = CompletionMode.STANDARD,
        processing_profile: ProcessingProfile = ProcessingProfile.BALANCED,
        enable_analytics: bool | None = None,
    ):
        """Initialize the review graph.

        Args:
            vault_root: Path to the vault root directory
            taxonomy: Loaded taxonomy
            note_index: Set of all note IDs in the vault
            max_iterations: Maximum fix iterations per note
            dry_run: If True, don't write any files to disk (validation only)
            completion_mode: Strictness level for issue completion (default: STANDARD)
            processing_profile: Workflow mode that balances stability vs throughput
            enable_analytics: Optional override to enable/disable analytics capture
        """
        self.vault_root = vault_root
        self.taxonomy = taxonomy
        self.note_index = note_index
        profile_settings = PROFILE_SETTINGS[processing_profile]
        self.processing_profile = processing_profile
        self.parallel_validators = profile_settings["parallel_validators"]
        self.use_smart_selection = profile_settings["smart_selection"]
        self.force_full_validator_pass = profile_settings["full_validator_pass"]

        bonus_iterations = profile_settings["iteration_bonus"]
        if bonus_iterations:
            logger.info(
                "Processing profile %s grants %d additional iteration(s)",
                processing_profile.value,
                bonus_iterations,
            )
        self.max_iterations = max_iterations + bonus_iterations
        self.dry_run = dry_run
        self.completion_mode = completion_mode
        self.fix_memory: dict[str, FixMemory] = {}
        self.timestamp_policy = TimestampPolicy(vault_root)
        self.smart_selector = SmartValidatorSelector()
        self.atomic_related = AtomicRelatedFixer()
        self.code_parity = SmartCodeParityChecker()
        self.strict_qa = StrictQAVerifier()
        self.deterministic_fixer = DeterministicFixer()
        analytics_enabled = (
            profile_settings["enable_analytics"]
            if enable_analytics is None
            else enable_analytics
        )
        self.analytics = ReviewAnalyticsRecorder(enabled=analytics_enabled)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(NoteReviewStateDict)

        workflow.add_node("initial_llm_review", self._initial_llm_review)
        workflow.add_node("run_validators", self._run_validators)
        workflow.add_node("check_bilingual_parity", self._check_bilingual_parity)
        workflow.add_node("llm_fix_issues", self._llm_fix_issues)
        workflow.add_node("qa_verification", self._qa_verification)
        workflow.add_node("summarize_qa_failures", self._summarize_qa_failures)

        workflow.add_edge(START, "initial_llm_review")
        workflow.add_edge("initial_llm_review", "run_validators")
        workflow.add_edge("run_validators", "check_bilingual_parity")

        workflow.add_conditional_edges(
            "check_bilingual_parity",
            self._should_continue_fixing,
            {
                "continue": "llm_fix_issues",
                "qa_verify": "qa_verification",
                "summarize_failures": "summarize_qa_failures",
                "done": END,
            },
        )

        workflow.add_edge("llm_fix_issues", "run_validators")

        workflow.add_conditional_edges(
            "qa_verification",
            self._should_continue_after_qa,
            {
                "continue": "llm_fix_issues",
                "summarize_failures": "summarize_qa_failures",
                "done": END,
            },
        )

        workflow.add_edge("summarize_qa_failures", END)

        return workflow.compile()

    async def _initial_llm_review(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: Initial technical/factual review by LLM.

        Args:
            state: Current state

        Returns:
            State updates
        """
        state_obj = NoteReviewState.from_dict(state)
        state_obj.decision = None
        history_updates: list[dict[str, Any]] = []

        logger.info(f"Running initial technical review for {state_obj.note_path}")
        history_updates.append(
            state_obj.add_history_entry("initial_llm_review", "Starting technical review")
        )

        try:
            result = await run_technical_review(
                note_text=state_obj.current_text,
                note_path=state_obj.note_path,
                taxonomy=self.taxonomy,
                vault_root=self.vault_root,
                note_index=self.note_index,
            )

            updates: dict[str, Any] = {}
            if result.changes_made:
                updates["current_text"] = result.revised_text
                updates["changed"] = True
                logger.info(f"Technical review made changes: {result.explanation}")
                history_updates.append(
                    state_obj.add_history_entry(
                        "initial_llm_review",
                        f"Made changes: {result.explanation}",
                        issues_found=result.issues_found,
                    )
                )
            else:
                logger.info("No technical issues found")
                history_updates.append(
                    state_obj.add_history_entry(
                        "initial_llm_review", "No technical issues found"
                    )
                )

            updates["history"] = history_updates
            return updates

        except Exception as e:
            logger.error("Error in technical review: {}", e)
            logger.error("Exception type: {}", type(e).__name__)
            logger.error("Exception details: {}", repr(e))

            # Log underlying cause if available
            if hasattr(e, '__cause__') and e.__cause__:
                logger.error("Underlying cause: {} - {}", type(e.__cause__).__name__, e.__cause__)

            # Log traceback for debugging
            import traceback
            logger.error("Traceback:\n{}", ''.join(traceback.format_exception(type(e), e, e.__traceback__)))

            history_updates.append(state_obj.add_history_entry(
                "initial_llm_review", f"Error during technical review: {e}"
            ))
            return {
                "error": f"Technical review failed: {e}",
                "completed": True,
                "history": history_updates,
            }

    def _detect_changed_sections(self, text_before: str, text_after: str) -> set[str]:
        """Detect which sections changed between two versions of a note.

        IMPROVEMENT 3: Section-level change tracking for incremental validation.

        Args:
            text_before: Note content before changes
            text_after: Note content after changes

        Returns:
            Set of changed section identifiers (e.g., 'yaml', 'question_en', 'answer_ru')
        """
        changed = set()

        # Parse YAML and body
        def parse_sections(text: str) -> tuple[str, dict[str, str]]:
            """Parse note into YAML and body sections."""
            if not text.startswith("---"):
                return "", {}

            parts = text.split("---", 2)
            if len(parts) < 3:
                return "", {}

            yaml_section = parts[1].strip()
            body = parts[2].strip()

            # Extract major sections from body
            sections = {}
            current_section = None
            current_content = []

            for line in body.split("\n"):
                # Detect section headers
                if line.strip().startswith("#"):
                    # Save previous section
                    if current_section:
                        sections[current_section] = "\n".join(current_content)

                    # Start new section
                    header = line.strip().lower()
                    if "question (en)" in header:
                        current_section = "question_en"
                    elif "вопрос (ru)" in header:
                        current_section = "question_ru"
                    elif "answer (en)" in header:
                        current_section = "answer_en"
                    elif "ответ (ru)" in header:
                        current_section = "answer_ru"
                    elif "follow-up" in header:
                        current_section = "followups"
                    elif "reference" in header:
                        current_section = "references"
                    elif "related" in header:
                        current_section = "related_questions"
                    else:
                        current_section = "other"

                    current_content = []
                else:
                    current_content.append(line)

            # Save last section
            if current_section:
                sections[current_section] = "\n".join(current_content)

            return yaml_section, sections

        yaml_before, sections_before = parse_sections(text_before)
        yaml_after, sections_after = parse_sections(text_after)

        # Check YAML changes
        if yaml_before != yaml_after:
            changed.add("yaml")

        # Check section changes
        all_sections = set(sections_before.keys()) | set(sections_after.keys())
        for section in all_sections:
            content_before = sections_before.get(section, "")
            content_after = sections_after.get(section, "")
            if content_before != content_after:
                changed.add(section)

        if changed:
            logger.debug(f"Detected changes in sections: {', '.join(sorted(changed))}")
        else:
            logger.debug("No section changes detected")

        return changed

    async def _run_validators(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: Run metadata checks and structural validation scripts.

        This node performs both metadata sanity checks and structural validation
        on every iteration, ensuring that YAML changes made by the fix agent are
        re-validated in subsequent iterations.

        Args:
            state: Current state

        Returns:
            State updates
        """
        state_obj = NoteReviewState.from_dict(state)
        state_obj.decision = None
        history_updates: list[dict[str, Any]] = []

        logger.info(f"Running validators (iteration {state_obj.iteration + 1})")
        history_updates.append(
            state_obj.add_history_entry(
                "run_validators",
                f"Running validation (iteration {state_obj.iteration + 1})",
            )
        )

        try:
            import asyncio

            # IMPROVEMENT 3: Detect changed sections for incremental validation
            if state_obj.iteration > 0:
                # Get text from previous iteration (before current fixes)
                prev_text = state.get("original_text", state_obj.original_text)
                if len(state_obj.history) > 0:
                    # Try to find previous current_text from history
                    for entry in reversed(state_obj.history):
                        if "iteration" in entry and entry["iteration"] == state_obj.iteration - 1:
                            # Found previous iteration, use that text
                            break
                    else:
                        prev_text = state_obj.original_text
                else:
                    prev_text = state_obj.original_text

                changed_sections = self._detect_changed_sections(prev_text, state_obj.current_text)
                state_obj.changed_sections = changed_sections
            else:
                # First iteration - all sections considered changed
                state_obj.changed_sections = {"yaml", "question_en", "question_ru", "answer_en", "answer_ru"}

            selected_validators: list[str] = []
            if state_obj.iteration == 0 or self.force_full_validator_pass:
                selected_validators = ["metadata", "structural", "parity"]
                logger.info(
                    "Iteration %d: Running full validator suite",
                    state_obj.iteration + 1,
                )
            else:
                if self.use_smart_selection:
                    # Enhanced smart selection with section tracking
                    if "yaml" in state_obj.changed_sections:
                        selected_validators.append("metadata")
                        logger.debug("YAML changed → metadata validator needed")

                    # If any content section changed, run structural + parity
                    content_sections = {"question_en", "question_ru", "answer_en", "answer_ru", "followups", "references"}
                    if content_sections & state_obj.changed_sections:
                        selected_validators.extend(["structural", "parity"])
                        logger.debug("Content sections changed → structural + parity validators needed")

                    # If nothing changed (shouldn't happen, but just in case)
                    if not state_obj.changed_sections:
                        # Run parity as sanity check
                        selected_validators.append("parity")
                        logger.debug("No changes detected → parity-only sanity check")

                    # Deduplicate
                    selected_validators = sorted(set(selected_validators))

                    # Estimate savings
                    total_validators = 3
                    calls_saved = total_validators - len(selected_validators)
                    pct_saved = (calls_saved / total_validators) * 100 if total_validators > 0 else 0
                    if calls_saved > 0:
                        logger.info(
                            "Incremental validation saved %d validator call(s) (%.0f%%) - changed sections: %s",
                            calls_saved,
                            pct_saved,
                            ', '.join(sorted(state_obj.changed_sections)),
                        )
                else:
                    selected_validators = ["metadata", "structural", "parity"]

            logger.info(
                "Running %d validator helper(s) for %s using %s execution",
                len(selected_validators),
                state_obj.note_path,
                "parallel" if self.parallel_validators else "sequential",
            )

            tasks: dict[str, Any] = {}
            if "metadata" in selected_validators:
                tasks["metadata"] = run_metadata_sanity_check(
                    note_text=state_obj.current_text,
                    note_path=state_obj.note_path,
                )
            if "parity" in selected_validators:
                tasks["parity"] = run_bilingual_parity_check(
                    note_text=state_obj.current_text,
                    note_path=state_obj.note_path,
                )

            if tasks:
                task_items = list(tasks.items())
                if self.parallel_validators and len(task_items) > 1:
                    results = await asyncio.gather(*[coro for _, coro in task_items])
                else:
                    results = []
                    for _, coro in task_items:
                        results.append(await coro)
                result_map = {
                    name: result for (name, _), result in zip(task_items, results)
                }
                metadata_result = result_map.get("metadata")
                parity_result = result_map.get("parity")
            else:
                metadata_result = None
                parity_result = None

            metadata_issues = []
            if metadata_result is not None:
                for issue in metadata_result.issues_found:
                    metadata_issues.append(
                        ReviewIssue(
                            severity="ERROR",
                            message=f"[Metadata] {issue}",
                            field="frontmatter",
                        )
                    )
                for warning in metadata_result.warnings:
                    metadata_issues.append(
                        ReviewIssue(
                            severity="WARNING",
                            message=f"[Metadata] {warning}",
                            field="frontmatter",
                        )
                    )

                if metadata_issues:
                    logger.info(
                        f"Metadata sanity check found {len(metadata_result.issues_found)} issue(s) "
                        f"and {len(metadata_result.warnings)} warning(s)"
                    )
                    history_updates.append(
                        state_obj.add_history_entry(
                            "metadata_sanity_check",
                            f"Found {len(metadata_result.issues_found)} issue(s) and {len(metadata_result.warnings)} warning(s)",
                            issues=metadata_result.issues_found,
                            warnings=metadata_result.warnings,
                        )
                    )
                else:
                    logger.debug("No metadata issues found")
            else:
                logger.debug("Metadata validator skipped (no changes)")

            parity_issues = []
            if parity_result is not None:
                for issue in parity_result.parity_issues:
                    parity_issues.append(
                        ReviewIssue(
                            severity="ERROR",
                            message=f"[Parity] {issue}",
                            field="content",
                        )
                    )
                for section in parity_result.missing_sections:
                    parity_issues.append(
                        ReviewIssue(
                            severity="ERROR",
                            message=f"[Parity] Missing section: {section}",
                            field="content",
                        )
                    )

                if parity_issues:
                    logger.info(
                        f"Parity check found {len(parity_issues)} issue(s)"
                    )
                    history_updates.append(
                        state_obj.add_history_entry(
                            "bilingual_parity_check",
                            f"Found {len(parity_issues)} parity issue(s)",
                            parity_issues=parity_result.parity_issues,
                            missing_sections=parity_result.missing_sections,
                        )
                    )
                else:
                    logger.debug("No parity issues found")
            else:
                logger.debug("Parity validator skipped (no changes)")

            logger.debug("Running structural validators...")
            frontmatter, body = load_frontmatter_text(state_obj.current_text)

            validators = ValidatorRegistry.create_validators(
                content=body,
                frontmatter=frontmatter or {},
                path=state_obj.note_path,
                taxonomy=self.taxonomy,
                vault_root=self.vault_root,
                note_index=self.note_index,
            )

            structural_issues = []
            for validator in validators:
                summary = validator.validate()
                structural_issues.extend(summary.issues)

            structural_review_issues = [
                ReviewIssue.from_validation_issue(issue) for issue in structural_issues
            ]

            all_review_issues = metadata_issues + structural_review_issues + parity_issues

            logger.info(
                f"Found {len(all_review_issues)} total issues "
                f"({len(metadata_issues)} metadata + {len(structural_review_issues)} structural + "
                f"{len(parity_issues)} parity)"
            )
            history_updates.append(
                state_obj.add_history_entry(
                    "run_validators",
                    f"Found {len(all_review_issues)} total issues "
                    f"({len(metadata_issues)} metadata + {len(structural_review_issues)} structural + "
                    f"{len(parity_issues)} parity)",
                    issues=[f"{i.severity}: {i.message}" for i in all_review_issues],
                )
            )

            next_state = replace(
                state_obj,
                issues=all_review_issues,
                iteration=state_obj.iteration + 1,
            )

            try:
                self.analytics.record_iteration(
                    state_obj.note_path,
                    iteration=next_state.iteration,
                    metadata_issues=len(metadata_issues),
                    structural_issues=len(structural_review_issues),
                    parity_issues=len(parity_issues),
                )
            except Exception as analytics_error:
                logger.warning(
                    "Failed to record analytics for %s iteration %d: %s",
                    state_obj.note_path,
                    next_state.iteration,
                    analytics_error,
                )

            previous_issue_count = len(state_obj.issues)
            current_issue_count = len(all_review_issues)

            if previous_issue_count > 0:
                improvement = previous_issue_count - current_issue_count
                improvement_rate = (improvement / previous_issue_count) * 100

                logger.info(
                    f"[Iteration {next_state.iteration}/{state_obj.max_iterations}] "
                    f"Issues: {current_issue_count} (was {previous_issue_count}, "
                    f"Δ{improvement:+d}, {improvement_rate:+.1f}%)"
                )

                # Warn if convergence is slowing or stalling
                if improvement <= 0:
                    logger.warning(
                        f"Convergence stalled: Issue count not decreasing "
                        f"(iteration {next_state.iteration})"
                    )
                elif improvement_rate < 20:
                    logger.warning(
                        f"Slow convergence: Only {improvement_rate:.1f}% improvement "
                        f"(iteration {next_state.iteration})"
                    )

                history_updates.append(
                    next_state.add_history_entry(
                        "convergence_metrics",
                        f"Convergence: {improvement:+d} issues ({improvement_rate:+.1f}%)",
                        previous_issues=previous_issue_count,
                        current_issues=current_issue_count,
                        improvement=improvement,
                        improvement_rate=improvement_rate,
                    )
                )

            next_state.record_current_issues()

            is_oscillating, oscillation_msg = next_state.detect_oscillation()
            if is_oscillating:
                logger.warning(f"Oscillation detected: {oscillation_msg}")
                next_state.requires_human_review = True
                next_state.error = f"Oscillation detected: {oscillation_msg}"
                history_updates.append(
                    next_state.add_history_entry(
                        "oscillation_detection",
                        oscillation_msg,
                        oscillation_detected=True,
                    )
                )

            decision, decision_message = self._compute_decision(next_state)
            next_state.decision = decision
            history_updates.append(
                next_state.add_history_entry("decision", decision_message)
            )

            return {
                "issues": all_review_issues,
                "iteration": next_state.iteration,
                "decision": decision,
                "history": history_updates,
                "issue_history": next_state.issue_history,
                "requires_human_review": next_state.requires_human_review,
                "error": next_state.error,
                "changed_sections": list(next_state.changed_sections),
            }

        except Exception as e:
            logger.error("Error running validators: {}", e)
            history_updates.append(
                state_obj.add_history_entry(
                    "run_validators", f"Error during validation: {e}"
                )
            )
            return {
                "error": f"Validation failed: {e}",
                "completed": True,
                "decision": "done",
                "history": history_updates,
            }

    async def _check_bilingual_parity(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: Compute decision after validation.

        This node is now a pass-through since parity checking has been moved
        to run in parallel with validators in _run_validators.

        Issue recording happens in run_validators only. This node does NOT
        record issues to prevent duplicate entries.

        Args:
            state: Current state

        Returns:
            State updates with decision
        """
        state_obj = NoteReviewState.from_dict(state)
        state_obj.decision = None
        history_updates: list[dict[str, Any]] = []

        logger.debug(
            f"Using existing issue recording from validators (iteration {state_obj.iteration})"
        )
        logger.debug(
            f"Issue history has {len(state_obj.issue_history)} snapshot(s)"
        )

        try:
            existing_issue_count = len(state_obj.issues) if state_obj.issues else 0
            logger.info(
                f"Total issues after parallel validation: {existing_issue_count}"
            )
            history_updates.append(
                state_obj.add_history_entry(
                    "check_bilingual_parity",
                    f"Using issue state with {existing_issue_count} issue(s) for decision"
                    )
                )

            decision, decision_message = self._compute_decision(state_obj)
            logger.debug(f"Decision after issue recording: {decision} - {decision_message}")
            history_updates.append(
                state_obj.add_history_entry("decision", decision_message)
            )

            logger.info(
                f"[Issue Recording Complete] "
                f"Decision={decision}, "
                f"TotalIssues={existing_issue_count}, "
                f"Iteration={state_obj.iteration}/{state_obj.max_iterations}"
            )

            return {
                "decision": decision,
                "issue_history": [list(s) for s in state_obj.issue_history],
                "history": history_updates,
            }

        except Exception as e:
            logger.error("Error in bilingual parity check: {}", e, exc_info=True)
            history_updates.append(
                state_obj.add_history_entry(
                    "check_bilingual_parity", f"Error during parity check: {e}"
                )
            )
            return {
                "error": f"Bilingual parity check failed: {e}",
                "completed": True,
                "history": history_updates,
            }

    async def _create_missing_concept_files(self, issues: list[ReviewIssue]) -> list[str]:
        """Create and enrich missing concept files referenced in validation issues.

        This method:
        1. Creates concept stub files with valid YAML frontmatter
        2. Enriches stubs with meaningful content using the knowledge-gap agent
        3. Writes enriched content back to the concept file

        IMPORTANT: Concept files must use the FULL Q&A frontmatter schema to pass validation.
        Validators expect all required fields (topic, subtopics, difficulty, moc, related, etc.)
        even for concept files. See InterviewQuestions/10-Concepts/c-dependency-injection.md
        for reference.

        Args:
            issues: List of validation issues

        Returns:
            List of created concept file names
        """
        created_files = []

        # Pattern to match concept file names (c-*.md)
        concept_pattern = re.compile(r'c-[\w-]+(?:\.md)?')

        # Extract all concept file references from issue messages
        concept_files = set()
        for issue in issues:
            matches = concept_pattern.findall(issue.message)
            for match in matches:
                # Ensure .md extension
                if not match.endswith('.md'):
                    match = f"{match}.md"
                concept_files.add(match)

        if not concept_files:
            return created_files

        logger.debug(f"Found {len(concept_files)} concept file references in issues")

        # Path to 10-Concepts directory
        concepts_dir = self.vault_root / "10-Concepts"
        if not concepts_dir.exists():
            logger.warning(f"Concepts directory not found: {concepts_dir}")
            return created_files

        # Create missing concept files
        for concept_file in concept_files:
            concept_path = concepts_dir / concept_file

            # Skip if file already exists
            if concept_path.exists():
                continue

            # Extract concept name from filename (remove c- prefix and .md extension)
            concept_name = concept_file.replace('c-', '').replace('.md', '')
            # Convert kebab-case to Title Case
            concept_title = ' '.join(word.capitalize() for word in concept_name.split('-'))

            # Generate concept file content
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            id_str = now.strftime('%Y%m%d-%H%M%S')

            # Determine topic from concept name (fallback to general if unknown)
            # Common mappings for concept topics
            topic_keywords = {
                'kotlin': 'kotlin',
                'android': 'android',
                'algorithm': 'algorithms',
                'data-structure': 'data-structures',
                'design': 'system-design',
                'pattern': 'architecture-patterns',
            }
            topic = 'programming-languages'  # Default fallback
            for keyword, topic_value in topic_keywords.items():
                if keyword in concept_name.lower():
                    topic = topic_value
                    break

            # Determine MOC based on topic
            topic_to_moc = {
                'kotlin': 'moc-kotlin',
                'android': 'moc-android',
                'algorithms': 'moc-algorithms',
                'data-structures': 'moc-algorithms',
                'system-design': 'moc-system-design',
                'architecture-patterns': 'moc-system-design',
                'programming-languages': 'moc-kotlin',
            }
            moc = topic_to_moc.get(topic, 'moc-cs')

            content = f"""---
id: "{id_str}"
title: "{concept_title} / {concept_title}"
aliases: ["{concept_title}"]
summary: "Foundational concept for interview preparation"
topic: "{topic}"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "{moc}"
related: []
created: "{date_str}"
updated: "{date_str}"
tags: ["{topic}", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

{concept_title} is a fundamental concept in software development.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

{concept_title} - фундаментальная концепция в разработке программного обеспечения.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- To be documented

## Ключевые Моменты (RU)

- To be documented

## References

- To be documented
"""

            try:
                # Write the concept file (unless in dry-run mode)
                if self.dry_run:
                    logger.info(
                        f"DRY RUN: Would create concept file: {concept_file} "
                        f"(in production, this would resolve broken link issues)"
                    )
                else:
                    concept_path.write_text(content, encoding='utf-8')
                    logger.info(f"Created missing concept file: {concept_file}")

                    # Verify the generated file has valid frontmatter
                    try:
                        from obsidian_vault.utils.frontmatter import load_frontmatter
                        fm, _ = load_frontmatter(concept_path)

                        # Check for critical required fields
                        required = ['id', 'title', 'topic', 'difficulty', 'moc', 'related', 'tags']
                        missing = [f for f in required if f not in fm]

                        if missing:
                            logger.error(
                                f"Auto-generated concept file {concept_file} is missing required fields: {missing}. "
                                f"This is a bug in the auto-generation template and should be reported."
                            )
                        else:
                            logger.debug(f"Verified {concept_file} has all required frontmatter fields")

                    except Exception as verify_err:
                        logger.warning(f"Could not verify frontmatter for {concept_file}: {verify_err}")

                created_files.append(concept_file)

                # QUICK WIN FIX: Only add to note index if file was actually created
                # In dry-run mode, don't add to index to prevent false positives
                # (validators would think file exists when it doesn't)
                if not self.dry_run:
                    # Remove .md extension for note index
                    concept_id = concept_file.replace('.md', '')
                    self.note_index.add(concept_id)
                    logger.debug(f"Added {concept_id} to note index")
                else:
                    logger.debug(
                        f"DRY RUN: Skipping note_index update for {concept_file} "
                        "(would cause false positives in validation)"
                    )

                # Enrich the concept stub with meaningful content using knowledge-gap agent
                # Skip enrichment in dry-run mode since we don't write the file anyway
                if not self.dry_run:
                    try:
                        logger.info(f"Enriching concept stub for {concept_name}...")
                        enrichment_result = await run_concept_enrichment(
                            concept_stub=content,
                            concept_name=concept_name,
                            topic=topic,
                            referencing_notes=None,  # TODO: Could extract from issues/context
                        )

                        # Write enriched content back to file
                        concept_path.write_text(enrichment_result.enriched_content, encoding='utf-8')
                        logger.success(
                            f"Enriched concept file {concept_file}: {enrichment_result.explanation}"
                        )

                        if enrichment_result.added_sections:
                            logger.debug(
                                f"Added/enriched sections: {', '.join(enrichment_result.added_sections)}"
                            )

                        if enrichment_result.key_concepts:
                            logger.debug(
                                f"Key concepts covered: {', '.join(enrichment_result.key_concepts)}"
                            )

                    except Exception as enrich_err:
                        logger.warning(
                            f"Failed to enrich concept file {concept_file}, keeping generic stub: {enrich_err}"
                        )
                        # Continue with generic stub if enrichment fails

            except Exception as e:
                logger.error("Failed to create concept file {}: {}", concept_file, e)

        return created_files

    def _get_concept_files(self) -> list[str]:
        """Return list of available concept file basenames (without .md).

        Returns:
            List like ['c-kotlin-coroutines-basics', 'c-coroutines', ...]
        """
        concepts_dir = self.vault_root / "10-Concepts"
        if not concepts_dir.exists():
            return []

        return sorted([
            f.stem for f in concepts_dir.glob("c-*.md")
        ])

    def _get_qa_files(self) -> list[str]:
        """Return list of available Q&A file basenames (without .md).

        Returns:
            List like ['q-coroutine-basics--kotlin--easy', ...]
        """
        qa_files = []
        for folder in self.vault_root.glob("*/"):
            if folder.name.startswith("00-") or folder.name.startswith("10-") or folder.name.startswith("90-"):
                continue  # Skip admin, concepts, MOCs
            qa_files.extend([f.stem for f in folder.glob("q-*.md")])
        return sorted(qa_files)

    def _get_moc_files(self) -> list[str]:
        """Return list of available MOC file basenames (without .md).

        Returns:
            List like ['moc-kotlin', 'moc-android', ...]
        """
        mocs_dir = self.vault_root / "90-MOCs"
        if not mocs_dir.exists():
            return []

        return sorted([
            f.stem for f in mocs_dir.glob("moc-*.md")
        ])

    def _should_issues_block_completion(self, issues: list[ReviewIssue]) -> tuple[bool, str]:
        """Check if issues should block completion based on severity thresholds.

        Args:
            issues: List of current issues

        Returns:
            (should_block, reason) tuple
        """
        if not issues:
            return False, "No issues remaining"

        # Count issues by severity
        severity_counts = Counter(issue.severity for issue in issues)

        # Get thresholds for current mode
        thresholds = COMPLETION_THRESHOLDS[self.completion_mode]

        # Check if any severity exceeds its threshold
        blocking_severities = []
        for severity, count in severity_counts.items():
            max_allowed = thresholds.get(severity, 0)
            if count > max_allowed:
                blocking_severities.append(f"{severity}:{count}>{max_allowed}")

        if blocking_severities:
            reason = (
                f"Issues exceed {self.completion_mode.value} mode thresholds: "
                f"{', '.join(blocking_severities)}"
            )
            return True, reason
        else:
            summary = ', '.join(f"{sev}:{cnt}" for sev, cnt in severity_counts.items())
            reason = (
                f"Issues within {self.completion_mode.value} mode thresholds: {summary}"
            )
            return False, reason

    def _get_fix_memory(self, note_path: str) -> FixMemory:
        """Get or create FixMemory for a note.

        Returns a FixMemory instance that tracks already-fixed fields to prevent oscillation.

        Args:
            note_path: Path to the note

        Returns:
            FixMemory instance for this note
        """
        if note_path not in self.fix_memory:
            self.fix_memory[note_path] = FixMemory()
            logger.debug(f"Created new FixMemory for {note_path}")
        return self.fix_memory[note_path]

    def _format_fix_history(self, fix_attempts: list, note_path: str, current_iteration: int) -> str:
        """Format fix attempt history for fixer agent context.

        Args:
            fix_attempts: List of FixAttempt objects
            note_path: Path to current note
            current_iteration: Current iteration number

        Returns:
            Formatted string describing previous fix attempts and fixed fields
        """
        lines = []

        memory = self._get_fix_memory(note_path)
        memory_context = memory.get_context_for_fixer(current_iteration)
        lines.append(memory_context)
        lines.append("")
        lines.append("=" * 70)
        lines.append("")

        if not fix_attempts:
            lines.append("No previous fix attempts in this session.")
            return "\n".join(lines)

        recent_attempts = fix_attempts[-5:]

        lines.append("PREVIOUS FIX ATTEMPTS (learn from these):")
        for attempt in recent_attempts:
            result_emoji = {
                "success": "✓",
                "partial": "~",
                "failed": "✗",
                "reverted": "↩"
            }.get(attempt.result, "?")

            lines.append(
                f"\nIteration {attempt.iteration} [{result_emoji} {attempt.result}]:"
            )
            lines.append(f"  Targeted: {len(attempt.issues_targeted)} issue(s)")

            if attempt.fixes_applied:
                lines.append(f"  Applied: {', '.join(attempt.fixes_applied[:3])}")
                if len(attempt.fixes_applied) > 3:
                    lines.append(f"    ...and {len(attempt.fixes_applied) - 3} more")

            if attempt.issues_remaining:
                lines.append(f"  Still had: {len(attempt.issues_remaining)} issue(s) after")

            if attempt.result in ("failed", "reverted"):
                lines.append("  ⚠ This approach didn't work - try a different strategy!")

        lines.append("\nIMPORTANT: Do NOT repeat failed approaches. Learn from the patterns above.")

        return "\n".join(lines)

    async def _llm_fix_issues(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: LLM fixes formatting/structure issues.

        Args:
            state: Current state

        Returns:
            State updates
        """
        state_obj = NoteReviewState.from_dict(state)
        history_updates: list[dict[str, Any]] = []

        logger.info(f"Fixing {len(state_obj.issues)} issues")
        history_updates.append(
            state_obj.add_history_entry(
                "llm_fix_issues", f"Attempting to fix {len(state_obj.issues)} issues"
            )
        )

        try:
            # IMPROVEMENT 1: Run coordinator agent to create optimal fix plan
            from .agents.runners import run_fix_coordination
            fix_plan = await run_fix_coordination(
                issues=[issue.message for issue in state_obj.issues],
                iteration=state_obj.iteration,
                max_iterations=state_obj.max_iterations,
                fix_history=[attempt.__dict__ if hasattr(attempt, '__dict__') else attempt for attempt in state_obj.fix_attempts],
                note_path=state_obj.note_path,
            )
            logger.info(f"Coordinator created fix plan: {len(fix_plan.issue_groups)} groups, order={' → '.join(fix_plan.fix_order)}")
            history_updates.append(
                state_obj.add_history_entry(
                    "fix_coordinator",
                    f"Created fix plan with {len(fix_plan.issue_groups)} groups",
                    fix_order=fix_plan.fix_order,
                    estimated_iterations=fix_plan.estimated_iterations,
                    high_risk_fixes=fix_plan.high_risk_fixes,
                )
            )

            # IMPROVEMENT 2: Run deterministic fixer + concept creation in parallel
            import asyncio
            logger.debug("Running deterministic fixer and concept creation in parallel...")
            deterministic_task = asyncio.create_task(
                asyncio.to_thread(
                    self.deterministic_fixer.fix,
                    note_text=state_obj.current_text,
                    issues=state_obj.issues,
                    note_path=state_obj.note_path,
                )
            )
            concept_task = asyncio.create_task(
                self._create_missing_concept_files(state_obj.issues)
            )

            # Wait for both to complete
            deterministic_result, created_concepts = await asyncio.gather(
                deterministic_task,
                concept_task,
            )
            logger.debug("Parallel execution complete")

            if created_concepts:
                logger.info(f"Auto-created {len(created_concepts)} missing concept files")
                history_updates.append(
                    state_obj.add_history_entry(
                        "concept_creation",
                        f"Auto-created missing concept files: {', '.join(created_concepts)}",
                        created_files=created_concepts,
                    )
                )

            if deterministic_result.changes_made:
                logger.info(
                    f"Deterministic fixer applied {len(deterministic_result.fixes_applied)} fix(es), "
                    f"resolved {len(deterministic_result.issues_fixed)} issue(s)"
                )
                history_updates.append(
                    state_obj.add_history_entry(
                        "deterministic_fixer",
                        f"Applied {len(deterministic_result.fixes_applied)} deterministic fix(es)",
                        fixes=deterministic_result.fixes_applied,
                        issues_fixed=deterministic_result.issues_fixed,
                    )
                )

                state_obj.current_text = deterministic_result.revised_text

                remaining_issues = [
                    issue for issue in state_obj.issues
                    if issue.message not in deterministic_result.issues_fixed
                ]

                if len(remaining_issues) == 0:
                    logger.success("All issues resolved by deterministic fixer - skipping LLM")
                    return {
                        "current_text": deterministic_result.revised_text,
                        "changed": True,
                        "fix_attempts": state_obj.fix_attempts + [
                            {
                                "iteration": state_obj.iteration,
                                "issues_targeted": [i.message for i in state_obj.issues],
                                "fixes_applied": deterministic_result.fixes_applied,
                                "result": "success",
                                "issues_remaining": [],
                            }
                        ],
                        "history": history_updates,
                        "decision": None,
                    }

                state_obj.issues = remaining_issues
                logger.info(
                    f"Deterministic fixer left {len(remaining_issues)} issue(s) for LLM"
                )
            else:
                logger.debug("No issues can be fixed deterministically - using LLM for all")

            issue_descriptions = [
                f"[{issue.severity}] {issue.message}"
                + (f" (field: {issue.field})" if issue.field else "")
                for issue in state_obj.issues
            ]

            available_concepts = self._get_concept_files()
            available_qa_files = self._get_qa_files()
            valid_moc_files = self._get_moc_files()

            logger.debug(
                f"Providing fixer with vault index: "
                f"{len(available_concepts)} concepts, "
                f"{len(available_qa_files)} Q&As, "
                f"{len(valid_moc_files)} MOCs"
            )

            fix_history = self._format_fix_history(
                state_obj.fix_attempts,
                state_obj.note_path,
                state_obj.iteration
            )
            logger.debug(f"Providing fix history: {len(state_obj.fix_attempts)} previous attempt(s)")

            memory = self._get_fix_memory(state_obj.note_path)
            logger.debug(f"Fix Memory status: {memory.get_summary()}")

            atomic_related_rules = self.atomic_related.format_rules_for_prompt()
            code_parity_rules = self.code_parity.format_rules_for_prompt()
            timestamp_rules = self.timestamp_policy.format_rule_for_prompt()

            result = await run_issue_fixing(
                note_text=state_obj.current_text,
                issues=issue_descriptions,
                note_path=state_obj.note_path,
                available_concepts=available_concepts,
                available_qa_files=available_qa_files,
                valid_moc_files=valid_moc_files,
                fix_history=fix_history,
                atomic_related_rules=atomic_related_rules,
                code_parity_rules=code_parity_rules,
                timestamp_rules=timestamp_rules,
                taxonomy=self.taxonomy,
                vault_root=self.vault_root,
            )

            from .state import FixAttempt
            attempt = FixAttempt(
                iteration=state_obj.iteration,
                issues_targeted=[issue.message for issue in state_obj.issues],
                fixes_applied=result.fixes_applied if result.changes_made else [],
                result="success" if result.changes_made else "failed",
                issues_remaining=[],
            )

            updates: dict[str, Any] = {}
            if result.changes_made:
                updates["current_text"] = result.revised_text
                updates["changed"] = True
                logger.info(f"Applied fixes: {', '.join(result.fixes_applied)}")
                history_updates.append(
                    state_obj.add_history_entry(
                        "llm_fix_issues",
                        "Applied fixes",
                        fixes=result.fixes_applied,
                    )
                )

                try:
                    yaml_before, _ = load_frontmatter_text(state_obj.current_text)
                    yaml_after, _ = load_frontmatter_text(result.revised_text)

                    if yaml_before and yaml_after:
                        memory.extract_fixes_from_description(
                            result.fixes_applied,
                            yaml_before,
                            yaml_after,
                            state_obj.iteration
                        )
                        logger.debug(f"Updated Fix Memory: {memory.get_summary()}")

                        regressions = memory.detect_regressions(yaml_after, state_obj.iteration)
                        if regressions:
                            logger.error(
                                f"REGRESSION DETECTED: {len(regressions)} field(s) were "
                                f"modified that were already fixed in previous iterations!"
                            )
                            for regression in regressions:
                                logger.error(f"  - {regression}")

                            # Add regressions to history for debugging
                            history_updates.append(
                                state_obj.add_history_entry(
                                    "fix_memory_regression",
                                    f"BLOCKED: Detected {len(regressions)} regression(s)",
                                    regressions=regressions,
                                )
                            )

                            logger.warning(
                                "BLOCKING fix due to regressions - reverting to previous state"
                            )

                            return {
                                "error": f"Fix caused {len(regressions)} regression(s): {regressions[0]}",
                                "requires_human_review": True,
                                "history": history_updates,
                                "decision": "summarize_failures",
                                "changed": False,
                            }
                except Exception as mem_err:
                    logger.warning(f"Failed to update Fix Memory: {mem_err}")

            else:
                logger.warning("No fixes could be applied - escalating to human review")
                history_updates.append(
                    state_obj.add_history_entry(
                        "llm_fix_issues",
                        "No fixes applied - requires human review",
                    )
                )
                updates["requires_human_review"] = True

            updated_attempts = state_obj.fix_attempts + [attempt]
            updates["fix_attempts"] = updated_attempts

            updates["history"] = history_updates
            updates.setdefault("decision", None)
            return updates

        except Exception as e:
            logger.error("Error fixing issues: {}", e)
            history_updates.append(
                state_obj.add_history_entry(
                    "llm_fix_issues", f"Error applying fixes: {e}"
                )
            )
            return {
                "error": f"Fix failed: {e}",
                "completed": True,
                "history": history_updates,
                "decision": None,
            }

    async def _qa_verification(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: Final QA/critic verification before marking as complete.

        This node runs ONLY when validator issues are resolved, to ensure:
        - No factual errors were introduced during fixes
        - Bilingual parity is maintained
        - Overall quality is acceptable

        Args:
            state: Current state

        Returns:
            State updates
        """
        state_obj = NoteReviewState.from_dict(state)
        history_updates: list[dict[str, Any]] = []

        logger.info(f"Running final QA verification for {state_obj.note_path}")
        history_updates.append(
            state_obj.add_history_entry(
                "qa_verification",
                f"Running final QA verification (after {state_obj.iteration} iterations)",
            )
        )

        try:
            strict_result = self.strict_qa.verify(
                current_issues=state_obj.issues,
                history=state_obj.history,
                issue_history=state_obj.issue_history,
                iteration=state_obj.iteration,
            )

            logger.debug(f"Strict QA pre-check: {strict_result.summary}")

            if not strict_result.should_pass:
                logger.warning(
                    f"Strict QA pre-check FAILED: {len(strict_result.blocking_reasons)} blocking reason(s)"
                )

                qa_issues = []
                for reason in strict_result.blocking_reasons:
                    qa_issues.append(
                        ReviewIssue(
                            severity=reason.severity,
                            message=f"[QA] {reason.message}",
                            field="qa_check",
                        )
                    )

                history_updates.append(
                    state_obj.add_history_entry(
                        "strict_qa_precheck",
                        f"✗ Strict QA pre-check failed: {strict_result.summary}",
                        blocking_reasons=[r.message for r in strict_result.blocking_reasons],
                        warnings=strict_result.warnings,
                    )
                )

                self.analytics.record_qa_attempt(
                    state_obj.note_path,
                    iteration=state_obj.iteration,
                    passed=False,
                    summary=strict_result.summary,
                )
                return {
                    "qa_verification_passed": False,
                    "qa_verification_summary": strict_result.summary,
                    "qa_failure_summary": f"Strict QA pre-check failed: {strict_result.summary}",
                    "issues": qa_issues,
                    "decision": "continue",
                    "history": history_updates,
                }

            logger.info("Strict QA pre-check PASSED - proceeding to LLM verification")
            history_updates.append(
                state_obj.add_history_entry(
                    "strict_qa_precheck",
                    f"✓ Strict QA pre-check passed: {strict_result.summary}",
                    warnings=strict_result.warnings,
                )
            )

            qa_criteria = self.strict_qa.format_rules_for_qa_agent()

            result = await run_qa_verification(
                note_text=state_obj.current_text,
                note_path=state_obj.note_path,
                iteration_count=state_obj.iteration,
                qa_criteria=qa_criteria,
            )

            updates: dict[str, Any] = {
                "qa_verification_passed": result.is_acceptable,
                "qa_verification_summary": result.summary,
                "history": history_updates,
            }

            self.analytics.record_qa_attempt(
                state_obj.note_path,
                iteration=state_obj.iteration,
                passed=result.is_acceptable,
                summary=result.summary,
            )

            if result.is_acceptable:
                logger.success(f"QA verification passed: {result.summary}")
                history_updates.append(
                    state_obj.add_history_entry(
                        "qa_verification",
                        f"✓ QA verification passed: {result.summary}",
                        quality_concerns=result.quality_concerns,
                    )
                )
                updates["completed"] = True
                updates["decision"] = "done"
            else:
                logger.warning("QA verification found issues that need fixing")

                qa_issues = []
                for error in result.factual_errors:
                    qa_issues.append(
                        ReviewIssue(
                            severity="ERROR",
                            message=f"[QA] Factual error: {error}",
                            field="content",
                        )
                    )
                for issue in result.bilingual_parity_issues:
                    qa_issues.append(
                        ReviewIssue(
                            severity="ERROR",
                            message=f"[QA] Bilingual parity: {issue}",
                            field="content",
                        )
                    )

                history_updates.append(
                    state_obj.add_history_entry(
                        "qa_verification",
                        f"✗ QA verification failed: {len(result.factual_errors)} factual errors, "
                        f"{len(result.bilingual_parity_issues)} parity issues",
                        factual_errors=result.factual_errors,
                        bilingual_parity_issues=result.bilingual_parity_issues,
                        quality_concerns=result.quality_concerns,
                    )
                )

                updates["issues"] = qa_issues
                updates["decision"] = "continue"

            return updates

        except Exception as e:
            logger.error("Error in QA verification: {}", e)
            history_updates.append(
                state_obj.add_history_entry(
                    "qa_verification", f"Error during QA verification: {e}"
                )
            )
            self.analytics.record_qa_attempt(
                state_obj.note_path,
                iteration=state_obj.iteration,
                passed=None,
                summary=str(e),
            )
            return {
                "error": f"QA verification failed: {e}",
                "completed": True,
                "decision": "done",
                "history": history_updates,
            }

    async def _summarize_qa_failures(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: Summarize QA failures when max iterations reached or persistent issues.

        This node runs when the workflow cannot resolve all issues automatically,
        creating an actionable summary for human follow-up.

        Args:
            state: Current state

        Returns:
            State updates with failure summary
        """
        state_obj = NoteReviewState.from_dict(state)
        history_updates: list[dict[str, Any]] = []

        logger.warning(
            f"Summarizing QA failures for {state_obj.note_path} "
            f"(iterations: {state_obj.iteration}/{state_obj.max_iterations})"
        )
        history_updates.append(
            state_obj.add_history_entry(
                "summarize_qa_failures",
                f"Creating failure summary for manual follow-up "
                f"(iterations: {state_obj.iteration}/{state_obj.max_iterations})",
            )
        )

        try:
            # Format unresolved issues
            issue_descriptions = [
                f"[{issue.severity}] {issue.message}"
                + (f" (field: {issue.field})" if issue.field else "")
                for issue in state_obj.issues
            ]

            result = await run_qa_failure_summary(
                note_text=state_obj.current_text,
                note_path=state_obj.note_path,
                history=state_obj.history,
                unresolved_issues=issue_descriptions,
                qa_verification_summary=state_obj.qa_verification_summary,
                iteration_count=state_obj.iteration,
                max_iterations=state_obj.max_iterations,
            )

            # Store the human-readable summary in state
            updates: dict[str, Any] = {
                "qa_failure_summary": result.human_readable_summary,
                "completed": True,
                "history": history_updates,
            }

            logger.warning(
                f"QA failure summary for {state_obj.note_path}:\n"
                f"Failure type: {result.failure_type}\n"
                f"Unresolved issues: {len(result.unresolved_issues)}\n"
                f"Recommended actions: {len(result.recommended_actions)}\n"
                f"Summary: {result.human_readable_summary}"
            )

            history_updates.append(
                state_obj.add_history_entry(
                    "summarize_qa_failures",
                    f"Created failure summary: {result.failure_type}",
                    failure_type=result.failure_type,
                    unresolved_issues=result.unresolved_issues,
                    iteration_summary=result.iteration_summary,
                    recommended_actions=result.recommended_actions,
                    qa_failure_reasons=result.qa_failure_reasons,
                    human_readable_summary=result.human_readable_summary,
                )
            )

            return updates

        except Exception as e:
            logger.error("Error summarizing QA failures: {}", e)
            history_updates.append(
                state_obj.add_history_entry(
                    "summarize_qa_failures", f"Error creating failure summary: {e}"
                )
            )
            return {
                "qa_failure_summary": f"Failed to create summary: {e}",
                "completed": True,
                "history": history_updates,
            }

    def _compute_decision(self, state: NoteReviewState) -> tuple[str, str]:
        """Compute the next step decision and corresponding history message.

        Decision logic:
        1. If requires_human_review flag set -> summarize_failures
        2. If oscillation detected -> summarize_failures
        3. If max iterations reached AND (issues remain OR QA failed) -> summarize_failures
        4. If max iterations reached AND no issues AND QA passed -> done
        5. If error occurred -> done
        6. If completed flag set -> done
        7. If no validator/parity issues AND QA not run yet -> qa_verify
        8. If no validator/parity issues AND QA passed -> done
        9. If validator/parity issues remain -> continue
        """

        logger.debug(
            f"[Decision] Evaluating next step: "
            f"iteration={state.iteration}/{state.max_iterations}, "
            f"issues={len(state.issues)}, "
            f"error={state.error is not None}, "
            f"completed={state.completed}, "
            f"requires_human_review={state.requires_human_review}, "
            f"qa_passed={state.qa_verification_passed}"
        )

        if state.requires_human_review:
            message = (
                f"Fix agent could not apply changes - escalating to human review "
                f"(iteration {state.iteration}/{state.max_iterations}, "
                f"{len(state.issues)} unresolved issue(s))"
            )
            logger.warning(message)
            return "summarize_failures", message

        is_oscillating, oscillation_explanation = state.detect_oscillation()
        if is_oscillating:
            message = (
                f"CIRCUIT BREAKER TRIGGERED: Oscillation detected - stopping iteration. "
                f"{oscillation_explanation}"
            )
            logger.error(message)
            return "summarize_failures", message

        if state.iteration >= state.max_iterations:
            has_unresolved_issues = state.has_any_issues()
            qa_failed = state.qa_verification_passed is False

            if has_unresolved_issues or qa_failed:
                message = (
                    f"Max iterations ({state.max_iterations}) reached with unresolved issues - "
                    f"triggering failure summarizer"
                )
                logger.warning(message)
                return "summarize_failures", message
            else:
                message = f"Stopping: max iterations ({state.max_iterations}) reached"
                logger.warning(message)
                return "done", message

        if state.error:
            message = f"Stopping: error occurred: {state.error}"
            logger.error(f"Stopping due to error: {state.error}")
            return "done", message

        if state.completed:
            message = "Stopping: completed flag set"
            logger.info("Completed flag set - stopping iteration")
            return "done", message

        should_block, block_reason = self._should_issues_block_completion(state.issues)

        if not should_block:
            if state.qa_verification_passed is None:
                message = f"Issues don't block completion ({block_reason}) - routing to QA verification"
                logger.info(message)
                return "qa_verify", message
            elif state.qa_verification_passed:
                message = f"Stopping: {block_reason} and QA verification passed"
                logger.success("Workflow complete - QA verification passed")
                return "done", message
            else:
                message = f"Continuing: QA verification found issues to fix (previous: {block_reason})"
                logger.info(message)
                return "continue", message
        else:
            message = f"Continuing to iteration {state.iteration + 1} ({block_reason})"
            logger.info(message)
            return "continue", message

    def _should_continue_fixing(self, state: NoteReviewStateDict) -> str:
        """Determine if we should continue the fix loop.

        Args:
            state: Current state

        Returns:
            "continue", "qa_verify", or "done"
        """
        state_obj = NoteReviewState.from_dict(state)

        if state_obj.decision:
            logger.debug(
                "Decision already computed",
                iteration=state_obj.iteration,
                decision=state_obj.decision,
            )
            self.analytics.set_iteration_decision(
                state_obj.note_path, state_obj.iteration, state_obj.decision
            )
            return state_obj.decision

        decision, _ = self._compute_decision(state_obj)
        self.analytics.set_iteration_decision(
            state_obj.note_path, state_obj.iteration, decision
        )
        return decision

    def _should_continue_after_qa(self, state: NoteReviewStateDict) -> str:
        """Determine if we should continue after QA verification.

        Args:
            state: Current state

        Returns:
            "continue" (if QA found issues to fix) or "done" (if QA passed)
        """
        state_obj = NoteReviewState.from_dict(state)

        if state_obj.decision:
            logger.debug(
                "Decision already set by QA verification node",
                decision=state_obj.decision,
            )
            self.analytics.set_iteration_decision(
                state_obj.note_path, state_obj.iteration, state_obj.decision
            )
            return state_obj.decision

        if state_obj.qa_verification_passed:
            self.analytics.set_iteration_decision(
                state_obj.note_path, state_obj.iteration, "done"
            )
            return "done"
        else:
            self.analytics.set_iteration_decision(
                state_obj.note_path, state_obj.iteration, "continue"
            )
            return "continue"

    def _resolve_note_path_key(self, note_path: Path) -> str:
        """Return a stable key for analytics and fix memory tracking."""

        try:
            return str(note_path.relative_to(self.vault_root.parent))
        except ValueError:
            logger.debug(
                "Note path %s is outside the repository root; using absolute path",
                note_path,
            )
            return str(note_path)

    def _create_error_state(
        self,
        note_path_key: str,
        *,
        original_text: str,
        error_message: str,
        iteration: int = 0,
        issues: list[ReviewIssue] | None = None,
        history_node: str = "process_note",
        history_message: str | None = None,
    ) -> NoteReviewState:
        """Build a :class:`NoteReviewState` representing a terminal error."""

        state = NoteReviewState(
            note_path=note_path_key,
            original_text=original_text,
            current_text=original_text,
            issues=list(issues) if issues else [],
            iteration=iteration,
            max_iterations=self.max_iterations,
        )
        state.error = error_message
        state.requires_human_review = True
        state.completed = True
        state.changed = False
        state.add_history_entry(history_node, history_message or error_message)
        return state

    async def process_note(self, note_path: Path) -> NoteReviewState:
        """Process a single note through the review workflow.

        Args:
            note_path: Path to the note file

        Returns:
            Final state after processing. If a fatal error occurs, the returned
            state will have ``error`` and ``requires_human_review`` populated so
            callers can surface the failure without crashing the batch run.
        """

        import time

        logger.info("=" * 70)
        logger.info(f"Processing note: {note_path.name}")
        logger.debug(f"Full path: {note_path}")

        note_path_key = self._resolve_note_path_key(note_path)
        self.analytics.start_note(
            note_path_key,
            profile=self.processing_profile.value,
        )

        start_time = time.time()

        # Read the note
        try:
            original_text = note_path.read_text(encoding="utf-8")
            logger.debug(f"Read {len(original_text)} characters from note")
        except Exception as e:
            logger.error("Failed to read note {}: {}", note_path, e)
            error_message = f"Failed to read note: {e}"
            error_state = self._create_error_state(
                note_path_key,
                original_text="",
                error_message=error_message,
                history_node="read_note",
            )
            elapsed = time.time() - start_time
            self.analytics.finalize(
                note_path_key,
                iterations=error_state.iteration,
                final_issue_count=len(error_state.issues),
                elapsed_seconds=elapsed,
                qa_passed=None,
                error=error_message,
                requires_human_review=True,
            )
            logger.info("=" * 70)
            return error_state

        initial_state = NoteReviewState(
            note_path=note_path_key,
            original_text=original_text,
            current_text=original_text,
            max_iterations=self.max_iterations,
        )
        logger.debug(f"Initialized state with max_iterations={self.max_iterations}")

        if note_path_key in self.fix_memory:
            self.fix_memory[note_path_key].clear()
            logger.debug("Cleared existing Fix Memory for this note")

        logger.info(f"Starting LangGraph workflow for {note_path.name}")
        try:
            config = {"recursion_limit": 50}
            final_state_dict = await self.graph.ainvoke(
                initial_state.to_dict(), config=config
            )
            final_state = NoteReviewState.from_dict(final_state_dict)
            elapsed_time = time.time() - start_time
            logger.debug(f"LangGraph workflow completed in {elapsed_time:.2f}s")
        except Exception as e:
            logger.error("LangGraph workflow failed for {}: {}", note_path, e)
            elapsed = time.time() - start_time
            error_message = str(e)
            error_state = self._create_error_state(
                note_path_key,
                original_text=initial_state.current_text,
                error_message=error_message,
                iteration=initial_state.iteration,
                issues=initial_state.issues,
                history_message=f"Workflow failed: {error_message}",
            )
            self.analytics.finalize(
                note_path_key,
                iterations=error_state.iteration,
                final_issue_count=len(error_state.issues),
                elapsed_seconds=elapsed,
                qa_passed=None,
                error=error_message,
                requires_human_review=True,
            )
            logger.info("=" * 70)
            return error_state

        elapsed_time = time.time() - start_time
        logger.success(
            f"Completed review for {note_path.name} - "
            f"changed: {final_state.changed}, "
            f"iterations: {final_state.iteration}, "
            f"final_issues: {len(final_state.issues)}, "
            f"time: {elapsed_time:.2f}s"
        )

        if final_state.error:
            logger.error(f"Workflow ended with error: {final_state.error}")

        if final_state.requires_human_review:
            logger.warning(f"Note requires human review: {note_path.name}")

        self.analytics.finalize(
            note_path_key,
            iterations=final_state.iteration,
            final_issue_count=len(final_state.issues),
            elapsed_seconds=elapsed_time,
            qa_passed=final_state.qa_verification_passed,
            error=final_state.error,
            requires_human_review=final_state.requires_human_review,
        )

        logger.debug(f"Workflow history: {len(final_state.history)} entries")
        logger.info("=" * 70)

        return final_state

    def get_note_analytics(self, note_path: str) -> dict[str, Any] | None:
        """Return analytics for a specific note path if recorded."""

        note_data = self.analytics.get_note(note_path)
        if not note_data:
            return None

        return {
            "note_path": note_data.note_path,
            "profile": note_data.profile,
            "iterations": note_data.iterations,
            "final_issue_count": note_data.final_issue_count,
            "initial_issue_count": note_data.initial_issue_count,
            "issues_resolved": note_data.issues_resolved,
            "elapsed_seconds": note_data.elapsed_seconds,
            "qa_passed": note_data.qa_passed,
            "requires_human_review": note_data.requires_human_review,
            "qa_attempts": [
                {
                    "iteration": qa.iteration,
                    "passed": qa.passed,
                    "summary": qa.summary,
                }
                for qa in note_data.qa_attempts
            ],
            "iterations_detail": [
                {
                    "iteration": stats.iteration,
                    "metadata_issues": stats.metadata_issues,
                    "structural_issues": stats.structural_issues,
                    "parity_issues": stats.parity_issues,
                    "total_issues": stats.total_issues,
                    "decision": stats.decision,
                }
                for stats in note_data.iteration_stats
            ],
        }

    def get_analytics_summary(self) -> dict[str, Any]:
        """Return aggregated analytics for the current review session."""

        return self.analytics.summary()


def create_review_graph(
    vault_root: Path,
    max_iterations: int = 10,
    dry_run: bool = False,
    completion_mode: CompletionMode = CompletionMode.STANDARD,
    processing_profile: ProcessingProfile = ProcessingProfile.BALANCED,
    enable_analytics: bool | None = None,
) -> ReviewGraph:
    """Create a ReviewGraph instance with loaded taxonomy and note index.

    Args:
        vault_root: Path to the vault root
        max_iterations: Maximum fix iterations per note (default: 10)
        dry_run: If True, don't write any files to disk (validation only)
        completion_mode: Strictness level for completion (default: STANDARD)
        processing_profile: Workflow mode controlling stability/throughput trade-offs
        enable_analytics: Optional override for analytics capture (defaults per profile)

    Returns:
        Configured ReviewGraph instance
    """
    logger.info("Initializing ReviewGraph")
    logger.debug(f"Vault root: {vault_root}")
    logger.debug(f"Max iterations: {max_iterations}")
    logger.debug(f"Dry run mode: {dry_run}")
    logger.debug(f"Completion mode: {completion_mode.value}")
    logger.debug(f"Processing profile: {processing_profile.value}")
    if enable_analytics is not None:
        logger.debug(f"Analytics enabled override: {enable_analytics}")

    repo_root = vault_root.parent if vault_root.name == "InterviewQuestions" else vault_root
    logger.debug(f"Repo root: {repo_root}")

    logger.info("Loading taxonomy from TAXONOMY.md")
    try:
        taxonomy = TaxonomyLoader(repo_root).load()
        logger.debug(f"Taxonomy loaded - topics: {len(taxonomy.topics) if hasattr(taxonomy, 'topics') else 'unknown'}")
    except Exception as e:
        logger.error("Failed to load taxonomy: {}", e)
        raise

    logger.info("Building note index")
    try:
        note_index = build_note_index(vault_root)
        logger.debug(f"Note index built - {len(note_index)} notes indexed")
    except Exception as e:
        logger.error("Failed to build note index: {}", e)
        raise

    logger.success("ReviewGraph initialized successfully")
    return ReviewGraph(
        vault_root=vault_root,
        taxonomy=taxonomy,
        note_index=note_index,
        max_iterations=max_iterations,
        dry_run=dry_run,
        completion_mode=completion_mode,
        processing_profile=processing_profile,
        enable_analytics=enable_analytics,
    )
