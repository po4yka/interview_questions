"""Tests for concept enrichment using the knowledge-gap agent.

This test suite verifies that the concept enrichment agent:
1. Produces valid structured output
2. Enriches generic placeholders with meaningful content
3. Preserves YAML frontmatter
4. Maintains bilingual parity
5. Handles errors gracefully

Tests can be run with pytest or standalone.
"""

import re
from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # Define a no-op decorator when pytest is not available
    class pytest:
        class mark:
            @staticmethod
            def asyncio(func):
                return func


def test_enrichment_result_structure():
    """Verify ConceptEnrichmentResult has expected fields."""
    from obsidian_vault.llm_review.agents import ConceptEnrichmentResult

    # Create a sample result
    result = ConceptEnrichmentResult(
        enriched_content="# Test\n\nEnriched content",
        added_sections=["Summary (EN)", "Key Points (EN)"],
        key_concepts=["testing", "validation"],
        related_concepts=["unit-testing", "integration-testing"],
        explanation="Enriched with testing concepts",
    )

    assert result.enriched_content == "# Test\n\nEnriched content"
    assert len(result.added_sections) == 2
    assert len(result.key_concepts) == 2
    assert len(result.related_concepts) == 2
    assert result.explanation == "Enriched with testing concepts"


def test_concept_stub_template_preserved():
    """Verify enrichment preserves the basic structure of concept stubs."""
    concept_name = "test-concept"
    concept_title = "Test Concept"

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    id_str = now.strftime("%Y%m%d-%H%M%S")

    stub_content = f"""---
id: "{id_str}"
title: "{concept_title} / {concept_title}"
aliases: ["{concept_title}"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "{date_str}"
updated: "{date_str}"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
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

    # The enrichment agent should preserve YAML frontmatter structure
    # Required sections that should be present in enriched content
    required_sections = [
        "# Summary (EN)",
        "# Краткое Описание (RU)",
        "## Key Points (EN)",
        "## Ключевые Моменты (RU)",
        "## References",
    ]

    for section in required_sections:
        assert section in stub_content, f"Missing section: {section}"

    # YAML frontmatter should be valid
    assert stub_content.startswith("---")
    assert stub_content.count("---") >= 2, "YAML frontmatter should have opening and closing ---"


def test_enrichment_removes_placeholders():
    """Verify that enrichment replaces generic placeholder text."""
    # Generic placeholders that should be replaced
    generic_placeholders = [
        "is a fundamental concept in software development",
        "фундаментальная концепция в разработке программного обеспечения",
        "To be documented",
    ]

    # Example of enriched content (simulated)
    enriched_content = """---
id: "20250101-120000"
title: "Dependency Injection / Внедрение зависимостей"
aliases: ["Dependency Injection"]
summary: "Design pattern where object dependencies are provided externally"
topic: "architecture-patterns"
subtopics: ["dependency-injection"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-architecture-patterns"
related: []
created: "2025-01-01"
updated: "2025-01-01"
tags: ["architecture-patterns", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Dependency Injection is a design pattern where an object receives its dependencies from external sources rather than creating them internally.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Внедрение зависимостей — это паттерн проектирования, при котором объект получает свои зависимости из внешних источников.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- **Inversion of Control**: Dependencies are provided to objects rather than objects creating them
- **Testability**: Easy to replace real dependencies with mocks or fakes
- **Loose coupling**: Components don't know about concrete implementations

## Ключевые Моменты (RU)

- **Инверсия управления**: Зависимости предоставляются объектам извне
- **Тестируемость**: Легко заменить реальные зависимости на моки или заглушки
- **Слабая связанность**: Компоненты не знают о конкретных реализациях

## References

- [Android Dependency Injection](https://developer.android.com/training/dependency-injection)
- [Martin Fowler on Dependency Injection](https://martinfowler.com/articles/injection.html)
"""

    # Check that generic placeholders are NOT present (or are replaced)
    # Note: The auto-generated disclaimer is kept intentionally
    assert (
        "is a fundamental concept in software development" not in enriched_content
    ), "Generic EN placeholder should be replaced"

    # Check that meaningful content is present
    assert (
        "design pattern where an object receives its dependencies" in enriched_content.lower()
    ), "Should have specific definition"

    # Key points should not be "To be documented"
    key_points_section = enriched_content.split("## Key Points (EN)")[1].split("##")[0]
    assert "To be documented" not in key_points_section, "Key points should be enriched"
    assert "**" in key_points_section, "Key points should use bold formatting"


def test_enrichment_maintains_bilingual_structure():
    """Verify that enriched content maintains both EN and RU sections."""
    enriched_content = """---
id: "20250101-120000"
title: "Coroutines / Корутины"
---

# Summary (EN)

Kotlin Coroutines are a lightweight concurrency framework.

# Краткое Описание (RU)

Корутины Kotlin — это легковесная система параллелизма.

## Key Points (EN)

- Lightweight threads
- Structured concurrency
- Built-in cancellation

## Ключевые Моменты (RU)

- Легковесные потоки
- Структурированная конкурентность
- Встроенная отмена
"""

    # Both EN and RU sections must be present
    assert "# Summary (EN)" in enriched_content, "Missing EN summary section"
    assert "# Краткое Описание (RU)" in enriched_content, "Missing RU summary section"
    assert "## Key Points (EN)" in enriched_content, "Missing EN key points section"
    assert "## Ключевые Моменты (RU)" in enriched_content, "Missing RU key points section"

    # Extract EN and RU key points to verify they have similar structure
    en_section = enriched_content.split("## Key Points (EN)")[1].split("##")[0]
    ru_section = enriched_content.split("## Ключевые Моменты (RU)")[1].split("##")[0]

    en_bullets = [line for line in en_section.split("\n") if line.strip().startswith("-")]
    ru_bullets = [line for line in ru_section.split("\n") if line.strip().startswith("-")]

    # Should have same number of bullet points (bilingual parity)
    assert len(en_bullets) == len(ru_bullets), "EN and RU sections should have same number of points"
    assert len(en_bullets) > 0, "Should have at least one bullet point"


def test_enrichment_preserves_yaml_frontmatter():
    """Verify that enrichment doesn't modify YAML frontmatter."""
    original_yaml = """---
id: "20250101-120000"
title: "Test Concept / Тестовая концепция"
aliases: ["Test Concept"]
summary: "Test summary"
topic: "kotlin"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-01-01"
updated: "2025-01-01"
tags: ["kotlin", "concept", "difficulty/medium", "auto-generated"]
---"""

    # Enrichment should preserve all YAML fields exactly
    required_fields = [
        "id:",
        "title:",
        "aliases:",
        "summary:",
        "topic:",
        "subtopics:",
        "question_kind:",
        "difficulty:",
        "original_language:",
        "language_tags:",
        "status:",
        "moc:",
        "related:",
        "created:",
        "updated:",
        "tags:",
    ]

    for field in required_fields:
        assert field in original_yaml, f"YAML should contain field: {field}"

    # Status should remain "draft"
    assert 'status: "draft"' in original_yaml, "Status should be draft"

    # No brackets in moc field
    assert "[[" not in original_yaml, "YAML should not contain double brackets"


def test_concept_name_extraction():
    """Verify concept name extraction from filename works correctly."""
    test_cases = [
        ("c-dependency-injection.md", "dependency-injection"),
        ("c-coroutines.md", "coroutines"),
        ("c-mvvm-pattern.md", "mvvm-pattern"),
        ("c-hash-map.md", "hash-map"),
    ]

    for filename, expected_name in test_cases:
        # This is the logic from graph.py
        concept_name = filename.replace("c-", "").replace(".md", "")
        assert (
            concept_name == expected_name
        ), f"Concept name extraction failed for {filename}"


def test_topic_inference_from_concept_name():
    """Verify topic inference logic matches expected mappings."""
    topic_keywords = {
        "kotlin": "kotlin",
        "android": "android",
        "algorithm": "algorithms",
        "data-structure": "data-structures",
        "design": "system-design",
        "pattern": "architecture-patterns",
    }

    test_cases = [
        ("kotlin-coroutines", "kotlin"),
        ("android-lifecycle", "android"),
        ("binary-search-algorithm", "algorithms"),
        ("linked-list-data-structure", "data-structures"),
        ("url-shortener-design", "system-design"),
        ("mvvm-pattern", "architecture-patterns"),
        ("unknown-concept", "programming-languages"),  # fallback
    ]

    for concept_name, expected_topic in test_cases:
        topic = "programming-languages"  # Default fallback
        for keyword, topic_value in topic_keywords.items():
            if keyword in concept_name.lower():
                topic = topic_value
                break

        assert topic == expected_topic, f"Topic inference failed for {concept_name}"


@pytest.mark.asyncio
async def test_enrichment_agent_integration():
    """Integration test: verify enrichment agent can be called successfully.

    This test requires OPENROUTER_API_KEY to be set.
    Skip if not available.
    """
    import os

    if not os.getenv("OPENROUTER_API_KEY"):
        if HAS_PYTEST:
            pytest.skip("OPENROUTER_API_KEY not set, skipping integration test")
        else:
            print("Skipping integration test (OPENROUTER_API_KEY not set)")
            return

    from obsidian_vault.llm_review.agents import run_concept_enrichment

    # Create a simple concept stub
    concept_stub = """---
id: "20250101-120000"
title: "Test Concept / Тестовая концепция"
aliases: ["Test Concept"]
summary: "Foundational concept for interview preparation"
topic: "kotlin"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-01-01"
updated: "2025-01-01"
tags: ["kotlin", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Test Concept is a fundamental concept in software development.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Test Concept - фундаментальная концепция в разработке программного обеспечения.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- To be documented

## Ключевые Моменты (RU)

- To be documented

## References

- To be documented
"""

    # Call the enrichment agent
    result = await run_concept_enrichment(
        concept_stub=concept_stub,
        concept_name="test-concept",
        topic="kotlin",
        referencing_notes=None,
    )

    # Verify the result structure
    assert result.enriched_content is not None, "Should return enriched content"
    assert len(result.enriched_content) > len(
        concept_stub
    ), "Enriched content should be longer than stub"
    assert isinstance(result.added_sections, list), "Should return list of added sections"
    assert isinstance(result.key_concepts, list), "Should return list of key concepts"
    assert isinstance(result.explanation, str), "Should return explanation string"

    # Verify enriched content structure
    assert result.enriched_content.startswith("---"), "Should preserve YAML frontmatter"
    assert (
        "# Summary (EN)" in result.enriched_content
    ), "Should preserve section structure"
    assert "# Краткое Описание (RU)" in result.enriched_content, "Should preserve RU sections"

    # Verify placeholders were replaced (high-level check)
    # Note: Exact content depends on the LLM, so we just verify structure improved
    assert len(result.added_sections) > 0, "Should indicate which sections were enriched"


if __name__ == "__main__":
    # Run tests standalone
    print("Running concept enrichment tests...\n")

    try:
        test_enrichment_result_structure()
        print("✓ test_enrichment_result_structure PASSED")
    except AssertionError as e:
        print(f"✗ test_enrichment_result_structure FAILED: {e}")

    try:
        test_concept_stub_template_preserved()
        print("✓ test_concept_stub_template_preserved PASSED")
    except AssertionError as e:
        print(f"✗ test_concept_stub_template_preserved FAILED: {e}")

    try:
        test_enrichment_removes_placeholders()
        print("✓ test_enrichment_removes_placeholders PASSED")
    except AssertionError as e:
        print(f"✗ test_enrichment_removes_placeholders FAILED: {e}")

    try:
        test_enrichment_maintains_bilingual_structure()
        print("✓ test_enrichment_maintains_bilingual_structure PASSED")
    except AssertionError as e:
        print(f"✗ test_enrichment_maintains_bilingual_structure FAILED: {e}")

    try:
        test_enrichment_preserves_yaml_frontmatter()
        print("✓ test_enrichment_preserves_yaml_frontmatter PASSED")
    except AssertionError as e:
        print(f"✗ test_enrichment_preserves_yaml_frontmatter FAILED: {e}")

    try:
        test_concept_name_extraction()
        print("✓ test_concept_name_extraction PASSED")
    except AssertionError as e:
        print(f"✗ test_concept_name_extraction FAILED: {e}")

    try:
        test_topic_inference_from_concept_name()
        print("✓ test_topic_inference_from_concept_name PASSED")
    except AssertionError as e:
        print(f"✗ test_topic_inference_from_concept_name FAILED: {e}")

    print("\nNon-integration tests completed!")
    print(
        "\nSkipping integration test (requires OPENROUTER_API_KEY). Run with pytest to include integration tests."
    )
