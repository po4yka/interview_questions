"""LangGraph workflow for note review and fixing."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from langgraph.graph import END, START, StateGraph
from loguru import logger

from obsidian_vault.utils import TaxonomyLoader, build_note_index, parse_note
from obsidian_vault.utils.frontmatter import load_frontmatter_text
from obsidian_vault.validators import ValidatorRegistry

from .agents import run_issue_fixing, run_technical_review
from .state import NoteReviewState, NoteReviewStateDict, ReviewIssue

if TYPE_CHECKING:
    from obsidian_vault.utils.taxonomy_loader import TaxonomyLoader as TaxonomyLoaderType


class ReviewGraph:
    """LangGraph workflow for reviewing and fixing notes."""

    def __init__(
        self,
        *,
        vault_root: Path,
        taxonomy: TaxonomyLoaderType,
        note_index: set[str],
        max_iterations: int = 5,
    ):
        """Initialize the review graph.

        Args:
            vault_root: Path to the vault root directory
            taxonomy: Loaded taxonomy
            note_index: Set of all note IDs in the vault
            max_iterations: Maximum fix iterations per note
        """
        self.vault_root = vault_root
        self.taxonomy = taxonomy
        self.note_index = note_index
        self.max_iterations = max_iterations
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create graph with state type
        workflow = StateGraph(NoteReviewStateDict)

        # Add nodes
        workflow.add_node("initial_llm_review", self._initial_llm_review)
        workflow.add_node("run_validators", self._run_validators)
        workflow.add_node("llm_fix_issues", self._llm_fix_issues)

        # Define edges
        workflow.add_edge(START, "initial_llm_review")
        workflow.add_edge("initial_llm_review", "run_validators")

        # Conditional edge from validators
        workflow.add_conditional_edges(
            "run_validators",
            self._should_continue_fixing,
            {
                "continue": "llm_fix_issues",
                "done": END,
            },
        )

        # After fixing, go back to validators
        workflow.add_edge("llm_fix_issues", "run_validators")

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
            logger.error(f"Error in technical review: {e}")
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
        """Node: Run existing validation scripts.

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
            # Parse the current note text to get frontmatter and body
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
            all_issues = []
            for validator in validators:
                summary = validator.validate()
                all_issues.extend(summary.issues)

            # Convert to ReviewIssue
            review_issues = [ReviewIssue.from_validation_issue(issue) for issue in all_issues]

            logger.info(f"Found {len(review_issues)} issues")
            history_updates.append(
                state_obj.add_history_entry(
                    "run_validators",
                    f"Found {len(review_issues)} issues",
                    issues=[f"{i.severity}: {i.message}" for i in review_issues],
                )
            )

            next_state = replace(
                state_obj,
                issues=review_issues,
                iteration=state_obj.iteration + 1,
            )
            decision, decision_message = self._compute_decision(next_state)
            next_state.decision = decision
            history_updates.append(
                next_state.add_history_entry("decision", decision_message)
            )

            return {
                "issues": review_issues,
                "iteration": next_state.iteration,
                "decision": decision,
                "history": history_updates,
            }

        except Exception as e:
            logger.error(f"Error running validators: {e}")
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
            # Convert issues to string descriptions
            issue_descriptions = [
                f"[{issue.severity}] {issue.message}"
                + (f" (field: {issue.field})" if issue.field else "")
                for issue in state_obj.issues
            ]

            result = await run_issue_fixing(
                note_text=state_obj.current_text,
                issues=issue_descriptions,
                note_path=state_obj.note_path,
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
                logger.warning("No fixes could be applied")
                history_updates.append(
                    state_obj.add_history_entry("llm_fix_issues", "No fixes applied")
                )
                # Stop iteration if no fixes can be applied
                updates["completed"] = True

            updates["history"] = history_updates
            updates.setdefault("decision", None)
            return updates

        except Exception as e:
            logger.error(f"Error fixing issues: {e}")
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

    def _compute_decision(self, state: NoteReviewState) -> tuple[str, str]:
        """Compute the next step decision and corresponding history message."""

        logger.debug(
            "Evaluating decision",
            iteration=state.iteration,
            max_iterations=state.max_iterations,
            issues=len(state.issues),
            error=state.error,
            completed=state.completed,
        )

        if state.iteration >= state.max_iterations:
            message = f"Stopping: max iterations ({state.max_iterations}) reached"
            logger.warning(message)
            return "done", message

        if not state.has_any_issues():
            message = "Stopping: no issues remaining"
            logger.success("No issues remaining - workflow complete")
            return "done", message

        if state.error:
            message = f"Stopping: error occurred: {state.error}"
            logger.error(f"Stopping due to error: {state.error}")
            return "done", message

        if state.completed:
            message = "Stopping: completed flag set"
            logger.info("Completed flag set - stopping iteration")
            return "done", message

        message = f"Continuing to iteration {state.iteration + 1}"
        logger.info(
            f"Continuing to iteration {state.iteration + 1} - "
            f"{len(state.issues)} issue(s) remaining"
        )
        return "continue", message

    def _should_continue_fixing(self, state: NoteReviewStateDict) -> str:
        """Determine if we should continue the fix loop.

        Args:
            state: Current state

        Returns:
            "continue" or "done"
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

    async def process_note(self, note_path: Path) -> NoteReviewState:
        """Process a single note through the review workflow.

        Args:
            note_path: Path to the note file

        Returns:
            Final state after processing
        """
        logger.info(f"=" * 70)
        logger.info(f"Processing note: {note_path.name}")
        logger.debug(f"Full path: {note_path}")

        # Read the note
        try:
            original_text = note_path.read_text(encoding="utf-8")
            logger.debug(f"Read {len(original_text)} characters from note")
        except Exception as e:
            logger.error(f"Failed to read note {note_path}: {e}")
            raise

        # Initialize state
        initial_state = NoteReviewState(
            note_path=str(note_path.relative_to(self.vault_root.parent)),
            original_text=original_text,
            current_text=original_text,
            max_iterations=self.max_iterations,
        )
        logger.debug(f"Initialized state with max_iterations={self.max_iterations}")

        # Run the graph
        logger.info(f"Starting LangGraph workflow for {note_path.name}")
        try:
            final_state_dict = await self.graph.ainvoke(initial_state.to_dict())
            final_state = NoteReviewState.from_dict(final_state_dict)
            logger.debug("LangGraph workflow completed")
        except Exception as e:
            logger.error(f"LangGraph workflow failed for {note_path}: {e}")
            raise

        # Log final results
        logger.success(
            f"Completed review for {note_path.name} - "
            f"changed: {final_state.changed}, "
            f"iterations: {final_state.iteration}, "
            f"final_issues: {len(final_state.issues)}"
        )

        if final_state.error:
            logger.error(f"Workflow ended with error: {final_state.error}")

        logger.debug(f"Workflow history: {len(final_state.history)} entries")
        logger.info(f"=" * 70)

        return final_state


def create_review_graph(
    vault_root: Path,
    max_iterations: int = 5,
) -> ReviewGraph:
    """Create a ReviewGraph instance with loaded taxonomy and note index.

    Args:
        vault_root: Path to the vault root
        max_iterations: Maximum fix iterations per note

    Returns:
        Configured ReviewGraph instance
    """
    logger.info("Initializing ReviewGraph")
    logger.debug(f"Vault root: {vault_root}")
    logger.debug(f"Max iterations: {max_iterations}")

    # Discover repo root
    repo_root = vault_root.parent if vault_root.name == "InterviewQuestions" else vault_root
    logger.debug(f"Repo root: {repo_root}")

    # Load taxonomy
    logger.info("Loading taxonomy from TAXONOMY.md")
    try:
        taxonomy = TaxonomyLoader(repo_root).load()
        logger.debug(f"Taxonomy loaded - topics: {len(taxonomy.topics) if hasattr(taxonomy, 'topics') else 'unknown'}")
    except Exception as e:
        logger.error(f"Failed to load taxonomy: {e}")
        raise

    # Build note index
    logger.info("Building note index")
    try:
        note_index = build_note_index(vault_root)
        logger.debug(f"Note index built - {len(note_index)} notes indexed")
    except Exception as e:
        logger.error(f"Failed to build note index: {e}")
        raise

    logger.success("ReviewGraph initialized successfully")
    return ReviewGraph(
        vault_root=vault_root,
        taxonomy=taxonomy,
        note_index=note_index,
        max_iterations=max_iterations,
    )
