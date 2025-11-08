"""LangGraph workflow for note review and fixing."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from langgraph.graph import END, START, StateGraph
from loguru import logger

from obsidian_vault.utils import TaxonomyLoader, build_note_index, parse_note
from obsidian_vault.utils.frontmatter import load_frontmatter_text
from obsidian_vault.validators import ValidatorRegistry

from .agents import run_issue_fixing, run_technical_review
from .state import NoteReviewState, ReviewIssue

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
        workflow = StateGraph(NoteReviewState)

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

    async def _initial_llm_review(self, state: NoteReviewState) -> dict:
        """Node: Initial technical/factual review by LLM.

        Args:
            state: Current state

        Returns:
            State updates
        """
        logger.info(f"Running initial technical review for {state.note_path}")
        state.add_history_entry("initial_llm_review", "Starting technical review")

        try:
            result = await run_technical_review(
                note_text=state.current_text,
                note_path=state.note_path,
            )

            updates = {}
            if result.changes_made:
                updates["current_text"] = result.revised_text
                updates["changed"] = True
                logger.info(f"Technical review made changes: {result.explanation}")
                state.add_history_entry(
                    "initial_llm_review",
                    f"Made changes: {result.explanation}",
                    issues_found=result.issues_found,
                )
            else:
                logger.info("No technical issues found")
                state.add_history_entry("initial_llm_review", "No technical issues found")

            return updates

        except Exception as e:
            logger.error(f"Error in technical review: {e}")
            return {
                "error": f"Technical review failed: {e}",
                "completed": True,
            }

    async def _run_validators(self, state: NoteReviewState) -> dict:
        """Node: Run existing validation scripts.

        Args:
            state: Current state

        Returns:
            State updates
        """
        logger.info(f"Running validators (iteration {state.iteration + 1})")
        state.add_history_entry("run_validators", f"Running validation (iteration {state.iteration + 1})")

        try:
            # Parse the current note text to get frontmatter and body
            frontmatter, body = load_frontmatter_text(state.current_text)

            # Create validators
            validators = ValidatorRegistry.create_validators(
                content=body,
                frontmatter=frontmatter or {},
                path=state.note_path,
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
            state.add_history_entry(
                "run_validators",
                f"Found {len(review_issues)} issues",
                issues=[f"{i.severity}: {i.message}" for i in review_issues],
            )

            return {
                "issues": review_issues,
                "iteration": state.iteration + 1,
            }

        except Exception as e:
            logger.error(f"Error running validators: {e}")
            return {
                "error": f"Validation failed: {e}",
                "completed": True,
            }

    async def _llm_fix_issues(self, state: NoteReviewState) -> dict:
        """Node: LLM fixes formatting/structure issues.

        Args:
            state: Current state

        Returns:
            State updates
        """
        logger.info(f"Fixing {len(state.issues)} issues")
        state.add_history_entry("llm_fix_issues", f"Attempting to fix {len(state.issues)} issues")

        try:
            # Convert issues to string descriptions
            issue_descriptions = [
                f"[{issue.severity}] {issue.message}"
                + (f" (field: {issue.field})" if issue.field else "")
                for issue in state.issues
            ]

            result = await run_issue_fixing(
                note_text=state.current_text,
                issues=issue_descriptions,
                note_path=state.note_path,
            )

            updates = {}
            if result.changes_made:
                updates["current_text"] = result.revised_text
                updates["changed"] = True
                logger.info(f"Applied fixes: {', '.join(result.fixes_applied)}")
                state.add_history_entry(
                    "llm_fix_issues",
                    "Applied fixes",
                    fixes=result.fixes_applied,
                )
            else:
                logger.warning("No fixes could be applied")
                state.add_history_entry("llm_fix_issues", "No fixes applied")
                # Stop iteration if no fixes can be applied
                updates["completed"] = True

            return updates

        except Exception as e:
            logger.error(f"Error fixing issues: {e}")
            return {
                "error": f"Fix failed: {e}",
                "completed": True,
            }

    def _should_continue_fixing(self, state: NoteReviewState) -> str:
        """Determine if we should continue the fix loop.

        Args:
            state: Current state

        Returns:
            "continue" or "done"
        """
        # Check if max iterations reached
        if state.iteration >= state.max_iterations:
            logger.warning(f"Max iterations ({state.max_iterations}) reached")
            state.add_history_entry(
                "decision",
                f"Stopping: max iterations ({state.max_iterations}) reached",
            )
            return "done"

        # Check if there are issues to fix
        if not state.has_any_issues():
            logger.success("No issues remaining")
            state.add_history_entry("decision", "Stopping: no issues remaining")
            return "done"

        # Check for errors
        if state.error:
            logger.error(f"Stopping due to error: {state.error}")
            state.add_history_entry("decision", f"Stopping: error occurred: {state.error}")
            return "done"

        # Check if completed flag is set
        if state.completed:
            logger.info("Completed flag set")
            state.add_history_entry("decision", "Stopping: completed flag set")
            return "done"

        # Continue fixing
        logger.info(f"Continuing (iteration {state.iteration}/{state.max_iterations})")
        state.add_history_entry("decision", f"Continuing to iteration {state.iteration + 1}")
        return "continue"

    async def process_note(self, note_path: Path) -> NoteReviewState:
        """Process a single note through the review workflow.

        Args:
            note_path: Path to the note file

        Returns:
            Final state after processing
        """
        # Read the note
        original_text = note_path.read_text(encoding="utf-8")

        # Initialize state
        initial_state = NoteReviewState(
            note_path=str(note_path.relative_to(self.vault_root.parent)),
            original_text=original_text,
            current_text=original_text,
            max_iterations=self.max_iterations,
        )

        # Run the graph
        logger.info(f"Starting review workflow for {note_path}")
        final_state = await self.graph.ainvoke(initial_state)

        logger.success(f"Completed review for {note_path}")
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
    # Discover repo root
    repo_root = vault_root.parent if vault_root.name == "InterviewQuestions" else vault_root

    # Load taxonomy
    logger.debug("Loading taxonomy")
    taxonomy = TaxonomyLoader(repo_root).load()

    # Build note index
    logger.debug("Building note index")
    note_index = build_note_index(vault_root)

    return ReviewGraph(
        vault_root=vault_root,
        taxonomy=taxonomy,
        note_index=note_index,
        max_iterations=max_iterations,
    )
