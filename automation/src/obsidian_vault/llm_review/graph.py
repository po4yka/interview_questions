"""LangGraph workflow for note review and fixing."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
from .state import NoteReviewState, NoteReviewStateDict, ReviewIssue

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
    ):
        """Initialize the review graph.

        Args:
            vault_root: Path to the vault root directory
            taxonomy: Loaded taxonomy
            note_index: Set of all note IDs in the vault
            max_iterations: Maximum fix iterations per note
            dry_run: If True, don't write any files to disk (validation only)
            completion_mode: Strictness level for issue completion (default: STANDARD)
        """
        self.vault_root = vault_root
        self.taxonomy = taxonomy
        self.note_index = note_index
        self.max_iterations = max_iterations
        self.dry_run = dry_run
        self.completion_mode = completion_mode
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create graph with state type
        workflow = StateGraph(NoteReviewStateDict)

        # Add nodes
        workflow.add_node("initial_llm_review", self._initial_llm_review)
        workflow.add_node("run_validators", self._run_validators)
        workflow.add_node("check_bilingual_parity", self._check_bilingual_parity)
        workflow.add_node("llm_fix_issues", self._llm_fix_issues)
        workflow.add_node("qa_verification", self._qa_verification)
        workflow.add_node("summarize_qa_failures", self._summarize_qa_failures)

        # Define edges
        workflow.add_edge(START, "initial_llm_review")
        workflow.add_edge("initial_llm_review", "run_validators")

        # After validators, check bilingual parity
        workflow.add_edge("run_validators", "check_bilingual_parity")

        # Conditional edge from bilingual parity check
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

        # After fixing, go back to validators
        workflow.add_edge("llm_fix_issues", "run_validators")

        # Conditional edge from QA verification
        workflow.add_conditional_edges(
            "qa_verification",
            self._should_continue_after_qa,
            {
                "continue": "llm_fix_issues",
                "summarize_failures": "summarize_qa_failures",
                "done": END,
            },
        )

        # After summarizing failures, end the workflow
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

            history_updates.append(
                state_obj.add_history_entry(
                    "initial_llm_review", f"Error during technical review: {e}"
                )
            )
            return {
                "error": f"Technical review failed: {e}",
                "completed": True,
                "history": history_updates,
            }

    async def _run_validators(self, state: NoteReviewStateDict) -> dict[str, Any]:
        """Node: Run metadata checks and structural validation scripts.

        This node now performs BOTH metadata sanity checks AND structural validation
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
            # STEP 1: Run metadata sanity check (runs every iteration now)
            logger.info(
                f"Running metadata sanity check for {state_obj.note_path} "
                f"(iteration {state_obj.iteration + 1})"
            )
            metadata_result = await run_metadata_sanity_check(
                note_text=state_obj.current_text,
                note_path=state_obj.note_path,
            )

            # Convert metadata findings to ReviewIssues
            metadata_issues = []
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

            # STEP 2: Run structural validators
            logger.debug("Running structural validators...")
            frontmatter, body = load_frontmatter_text(state_obj.current_text)

            # Create validators
            validators = ValidatorRegistry.create_validators(
                content=body,
                frontmatter=frontmatter or {},
                path=state_obj.note_path,
                taxonomy=self.taxonomy,
                vault_root=self.vault_root,
                note_index=self.note_index,
            )

            # Run all validators
            structural_issues = []
            for validator in validators:
                summary = validator.validate()
                structural_issues.extend(summary.issues)

            # Convert to ReviewIssue
            structural_review_issues = [
                ReviewIssue.from_validation_issue(issue) for issue in structural_issues
            ]

            # STEP 3: Merge metadata and structural issues
            all_review_issues = metadata_issues + structural_review_issues

            logger.info(
                f"Found {len(all_review_issues)} total issues "
                f"({len(metadata_issues)} metadata + {len(structural_review_issues)} structural)"
            )
            history_updates.append(
                state_obj.add_history_entry(
                    "run_validators",
                    f"Found {len(all_review_issues)} total issues "
                    f"({len(metadata_issues)} metadata + {len(structural_review_issues)} structural)",
                    issues=[f"{i.severity}: {i.message}" for i in all_review_issues],
                )
            )

            next_state = replace(
                state_obj,
                issues=all_review_issues,
                iteration=state_obj.iteration + 1,
            )

            # STEP 4: Calculate convergence metrics
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

            # STEP 5: Record issues for oscillation detection
            next_state.record_current_issues()

            # STEP 6: Check for oscillation
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
        """Node: Check bilingual parity between EN and RU sections.

        This node runs EARLY in the loop (after validators) to catch translation
        drift before the QA stage, reducing recycle time when parity issues exist.

        ITERATION FLOW EXPLANATION:
        1. Validators run first and add issues to state (e.g., YAML errors, missing tags)
        2. This parity check runs and MERGES its issues with validator issues
        3. Decision logic evaluates TOTAL issue count (validators + parity)
        4. If ANY issues exist → route to llm_fix_issues
        5. llm_fix_issues attempts to fix ALL issues (both types)
        6. Loop back to validators (step 1) for next iteration
        7. When NO issues remain → route to qa_verification (final gate)

        This ensures validator issues and parity issues are fixed together in the
        same loop, reducing the number of iterations needed.

        Args:
            state: Current state

        Returns:
            State updates with merged issues and decision
        """
        state_obj = NoteReviewState.from_dict(state)
        state_obj.decision = None
        history_updates: list[dict[str, Any]] = []

        logger.info(
            f"Running bilingual parity check for {state_obj.note_path} "
            f"(iteration {state_obj.iteration})"
        )
        logger.debug(
            f"Pre-parity state: {len(state_obj.issues)} existing validator issue(s)"
        )
        history_updates.append(
            state_obj.add_history_entry(
                "check_bilingual_parity",
                f"Starting bilingual parity check (iteration {state_obj.iteration})",
            )
        )

        try:
            result = await run_bilingual_parity_check(
                note_text=state_obj.current_text,
                note_path=state_obj.note_path,
            )

            updates: dict[str, Any] = {"history": history_updates}

            # Convert parity findings to ReviewIssues and add to state
            parity_issues = []
            for issue in result.parity_issues:
                parity_issues.append(
                    ReviewIssue(
                        severity="ERROR",
                        message=f"[Parity] {issue}",
                        field="content",
                    )
                )
            for section in result.missing_sections:
                parity_issues.append(
                    ReviewIssue(
                        severity="ERROR",
                        message=f"[Parity] Missing section: {section}",
                        field="content",
                    )
                )

            existing_issue_count = len(state_obj.issues) if state_obj.issues else 0

            if parity_issues:
                # Merge parity issues with existing validator issues
                all_issues = (state_obj.issues or []) + parity_issues
                updates["issues"] = all_issues
                logger.warning(
                    f"Parity check found {len(parity_issues)} new parity issue(s) - "
                    f"total issues: {existing_issue_count} validator + "
                    f"{len(parity_issues)} parity = {len(all_issues)}"
                )
                logger.debug(f"Parity issues: {result.parity_issues}")
                if result.missing_sections:
                    logger.debug(f"Missing sections: {result.missing_sections}")
                history_updates.append(
                    state_obj.add_history_entry(
                        "check_bilingual_parity",
                        f"Found {len(parity_issues)} parity issue(s) - "
                        f"merged with {existing_issue_count} validator issue(s)",
                        parity_issues=result.parity_issues,
                        missing_sections=result.missing_sections,
                    )
                )
            else:
                logger.info(
                    f"Bilingual parity check passed - {existing_issue_count} "
                    f"validator issue(s) remain"
                )
                history_updates.append(
                    state_obj.add_history_entry(
                        "check_bilingual_parity", f"No parity issues found: {result.summary}"
                    )
                )

            # Compute and log decision for consistency with validators
            next_state = replace(state_obj, issues=updates.get("issues", state_obj.issues))
            decision, decision_message = self._compute_decision(next_state)
            updates["decision"] = decision
            logger.debug(f"Parity check decision: {decision} - {decision_message}")
            history_updates.append(
                next_state.add_history_entry("decision", decision_message)
            )

            # Summary log for debugging
            final_issue_count = len(next_state.issues) if next_state.issues else 0
            logger.info(
                f"[Parity Check Complete] "
                f"Decision={decision}, "
                f"TotalIssues={final_issue_count} "
                f"(validator={existing_issue_count}, parity={len(parity_issues)}), "
                f"Iteration={state_obj.iteration}/{state_obj.max_iterations}"
            )

            return updates

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
                    logger.info(f"DRY RUN: Would create concept file: {concept_file}")
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

                # Add to note index so it can be referenced (even in dry-run, for validation)
                # Remove .md extension for note index
                concept_id = concept_file.replace('.md', '')
                self.note_index.add(concept_id)

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

    def _format_fix_history(self, fix_attempts: list) -> str:
        """Format fix attempt history for fixer agent context.

        Args:
            fix_attempts: List of FixAttempt objects

        Returns:
            Formatted string describing previous fix attempts
        """
        if not fix_attempts:
            return "No previous fix attempts in this session."

        # Limit to last 5 attempts to avoid token bloat
        recent_attempts = fix_attempts[-5:]

        lines = ["PREVIOUS FIX ATTEMPTS (learn from these):"]
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

            # Add learning point for failed attempts
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

        # Auto-create and enrich missing concept files before attempting fixes
        created_concepts = await self._create_missing_concept_files(state_obj.issues)
        if created_concepts:
            logger.info(f"Auto-created {len(created_concepts)} missing concept files")
            history_updates.append(
                state_obj.add_history_entry(
                    "llm_fix_issues",
                    f"Auto-created missing concept files: {', '.join(created_concepts)}",
                    created_files=created_concepts,
                )
            )

        try:
            # Convert issues to string descriptions
            issue_descriptions = [
                f"[{issue.severity}] {issue.message}"
                + (f" (field: {issue.field})" if issue.field else "")
                for issue in state_obj.issues
            ]

            # Get available file indexes to help fixer make valid link suggestions
            available_concepts = self._get_concept_files()
            available_qa_files = self._get_qa_files()
            valid_moc_files = self._get_moc_files()

            logger.debug(
                f"Providing fixer with vault index: "
                f"{len(available_concepts)} concepts, "
                f"{len(available_qa_files)} Q&As, "
                f"{len(valid_moc_files)} MOCs"
            )

            # Format fix history to provide context about previous attempts
            fix_history = self._format_fix_history(state_obj.fix_attempts)
            logger.debug(f"Providing fix history: {len(state_obj.fix_attempts)} previous attempt(s)")

            result = await run_issue_fixing(
                note_text=state_obj.current_text,
                issues=issue_descriptions,
                note_path=state_obj.note_path,
                available_concepts=available_concepts,
                available_qa_files=available_qa_files,
                valid_moc_files=valid_moc_files,
                fix_history=fix_history,
            )

            # Record this fix attempt (will be updated with remaining issues after validation)
            from .state import FixAttempt
            attempt = FixAttempt(
                iteration=state_obj.iteration,
                issues_targeted=[issue.message for issue in state_obj.issues],
                fixes_applied=result.fixes_applied if result.changes_made else [],
                result="success" if result.changes_made else "failed",
                issues_remaining=[],  # Will be filled in next iteration by validators
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
            else:
                logger.warning("No fixes could be applied - escalating to human review")
                history_updates.append(
                    state_obj.add_history_entry(
                        "llm_fix_issues",
                        "No fixes applied - requires human review",
                    )
                )
                # Escalate to human review instead of silently marking as completed
                updates["requires_human_review"] = True

            # Add this fix attempt to the history
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
            result = await run_qa_verification(
                note_text=state_obj.current_text,
                note_path=state_obj.note_path,
                iteration_count=state_obj.iteration,
            )

            updates: dict[str, Any] = {
                "qa_verification_passed": result.is_acceptable,
                "qa_verification_summary": result.summary,
                "history": history_updates,
            }

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

                # Convert QA findings to ReviewIssues that can be fixed
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

                # Add QA issues to state for fixing
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
        1. If requires_human_review flag set -> summarize_failures (ESCALATION)
        2. If max iterations reached AND (issues remain OR QA failed) -> summarize_failures
        3. If max iterations reached AND no issues AND QA passed -> done
        4. If error occurred -> done
        5. If completed flag set -> done
        6. If no validator/parity issues AND QA not run yet -> qa_verify
        7. If no validator/parity issues AND QA passed -> done
        8. If validator/parity issues remain -> continue (fix loop)
        """

        # Detailed debug logging for decision evaluation
        logger.debug(
            f"[Decision] Evaluating next step: "
            f"iteration={state.iteration}/{state.max_iterations}, "
            f"issues={len(state.issues)}, "
            f"error={state.error is not None}, "
            f"completed={state.completed}, "
            f"requires_human_review={state.requires_human_review}, "
            f"qa_passed={state.qa_verification_passed}"
        )

        # NEW: Check for escalation flag first (failed fix attempts)
        if state.requires_human_review:
            message = (
                f"Fix agent could not apply changes - escalating to human review "
                f"(iteration {state.iteration}/{state.max_iterations}, "
                f"{len(state.issues)} unresolved issue(s))"
            )
            logger.warning(message)
            return "summarize_failures", message

        if state.iteration >= state.max_iterations:
            # Check if there are unresolved issues or QA failed
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

        # NEW: Check if remaining issues should block completion based on severity
        should_block, block_reason = self._should_issues_block_completion(state.issues)

        if not should_block:
            # If issues don't block AND QA hasn't been run yet, route to QA
            if state.qa_verification_passed is None:
                message = f"Issues don't block completion ({block_reason}) - routing to QA verification"
                logger.info(message)
                return "qa_verify", message
            # If QA passed, we're done
            elif state.qa_verification_passed:
                message = f"Stopping: {block_reason} and QA verification passed"
                logger.success("Workflow complete - QA verification passed")
                return "done", message
            # If QA failed, issues were added back to state, so continue fixing
            else:
                message = f"Continuing: QA verification found issues to fix (previous: {block_reason})"
                logger.info(message)
                return "continue", message
        else:
            # Issues block completion - continue fixing
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
            return state_obj.decision

        decision, _ = self._compute_decision(state_obj)
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
            return state_obj.decision

        # This should not normally happen as the QA verification node sets the decision
        # But as a fallback, check the QA verification result
        if state_obj.qa_verification_passed:
            return "done"
        else:
            return "continue"

    async def process_note(self, note_path: Path) -> NoteReviewState:
        """Process a single note through the review workflow.

        Args:
            note_path: Path to the note file

        Returns:
            Final state after processing
        """
        logger.info("=" * 70)
        logger.info(f"Processing note: {note_path.name}")
        logger.debug(f"Full path: {note_path}")

        # Read the note
        try:
            original_text = note_path.read_text(encoding="utf-8")
            logger.debug(f"Read {len(original_text)} characters from note")
        except Exception as e:
            logger.error("Failed to read note {}: {}", note_path, e)
            raise

        # Initialize state
        initial_state = NoteReviewState(
            note_path=str(note_path.relative_to(self.vault_root.parent)),
            original_text=original_text,
            current_text=original_text,
            max_iterations=self.max_iterations,
        )
        logger.debug(f"Initialized state with max_iterations={self.max_iterations}")

        # Run the graph with timing
        import time
        start_time = time.time()
        logger.info(f"Starting LangGraph workflow for {note_path.name}")
        try:
            final_state_dict = await self.graph.ainvoke(initial_state.to_dict())
            final_state = NoteReviewState.from_dict(final_state_dict)
            elapsed_time = time.time() - start_time
            logger.debug(f"LangGraph workflow completed in {elapsed_time:.2f}s")
        except Exception as e:
            logger.error("LangGraph workflow failed for {}: {}", note_path, e)
            raise

        # Log final results with detailed metrics
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

        logger.debug(f"Workflow history: {len(final_state.history)} entries")
        logger.info("=" * 70)

        return final_state


def create_review_graph(
    vault_root: Path,
    max_iterations: int = 10,
    dry_run: bool = False,
    completion_mode: CompletionMode = CompletionMode.STANDARD,
) -> ReviewGraph:
    """Create a ReviewGraph instance with loaded taxonomy and note index.

    Args:
        vault_root: Path to the vault root
        max_iterations: Maximum fix iterations per note (default: 10)
        dry_run: If True, don't write any files to disk (validation only)
        completion_mode: Strictness level for completion (default: STANDARD)

    Returns:
        Configured ReviewGraph instance
    """
    logger.info("Initializing ReviewGraph")
    logger.debug(f"Vault root: {vault_root}")
    logger.debug(f"Max iterations: {max_iterations}")
    logger.debug(f"Dry run mode: {dry_run}")
    logger.debug(f"Completion mode: {completion_mode.value}")

    # Discover repo root
    repo_root = vault_root.parent if vault_root.name == "InterviewQuestions" else vault_root
    logger.debug(f"Repo root: {repo_root}")

    # Load taxonomy
    logger.info("Loading taxonomy from TAXONOMY.md")
    try:
        taxonomy = TaxonomyLoader(repo_root).load()
        logger.debug(f"Taxonomy loaded - topics: {len(taxonomy.topics) if hasattr(taxonomy, 'topics') else 'unknown'}")
    except Exception as e:
        logger.error("Failed to load taxonomy: {}", e)
        raise

    # Build note index
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
    )
