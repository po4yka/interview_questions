"""Guard tests for LangChain AgentExecutor import paths."""

import importlib

import pytest

pytest.importorskip(
    "langchain_classic",
    reason="langchain-classic provides the AgentExecutor used for technical validation",
)


def test_agent_executor_available_from_langchain_module():
    """Ensure the canonical AgentExecutor symbol remains available."""

    module = importlib.import_module("langchain_classic.agents")
    assert hasattr(module, "AgentExecutor"), "Expected AgentExecutor to be exported"


def test_technical_validation_imports_canonical_agent_executor():
    """Ensure our flow module references the canonical AgentExecutor."""

    langchain_module = importlib.import_module("langchain_classic.agents")
    flow_module = importlib.import_module("obsidian_vault.technical_validation.flow")
    assert flow_module.AgentExecutor is langchain_module.AgentExecutor
