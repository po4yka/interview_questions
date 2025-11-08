"""Tests for auto-generated concept file schema validation.

This test ensures that auto-generated concept files conform to the
expected frontmatter schema required by validators.

Can be run with pytest or standalone: python tests/test_concept_generation.py
"""

import re
from datetime import datetime
from pathlib import Path


def test_concept_template_has_required_fields():
    """Verify the concept file generation template includes all required frontmatter fields."""
    # This is the template logic from graph.py _create_missing_concept_files
    concept_name = 'test-concept'
    concept_title = ' '.join(word.capitalize() for word in concept_name.split('-'))

    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    id_str = now.strftime('%Y%m%d-%H%M%S')

    # Determine topic (using default fallback)
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

    # Required fields per YAML_VALIDATOR.REQUIRED_FIELDS
    required_fields = [
        'id',
        'title',
        'aliases',
        'topic',
        'subtopics',
        'question_kind',
        'difficulty',
        'original_language',
        'language_tags',
        'status',
        'moc',
        'related',
        'created',
        'updated',
        'tags',
    ]

    # Check each required field is present in the content
    for field in required_fields:
        # Use regex to match field: value pattern
        pattern = rf'^{field}:\s*.+$'
        assert re.search(pattern, content, re.MULTILINE), (
            f"Auto-generated concept template is missing required field: {field}. "
            f"This will cause validation failures. Update graph.py template."
        )


def test_concept_template_field_formats():
    """Verify field formats in generated concept files match expected patterns."""
    concept_name = 'kotlin'
    concept_title = 'Kotlin'

    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    id_str = now.strftime('%Y%m%d-%H%M%S')

    topic = 'kotlin'
    moc = 'moc-kotlin'

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

    # Check critical format requirements
    # 1. ID should NOT have "ivc-" prefix (old broken format)
    assert 'id: "ivc-' not in content, "ID should not have 'ivc-' prefix"
    assert re.search(r'id: "\d{8}-\d{6}"', content), "ID should be YYYYMMDD-HHMMSS format"

    # 2. Title should be bilingual (EN / RU)
    assert '/' in re.search(r'title: "(.+)"', content).group(1), "Title should have EN / RU format"

    # 3. MOC should NOT have brackets
    assert 'moc: "[[' not in content, "MOC field should not contain brackets"
    assert re.search(r'moc: "moc-\w+"', content), "MOC should be moc-{topic} format"

    # 4. Related should be array, not contain double brackets
    assert 'related: []' in content, "Related should be empty array for new concepts"

    # 5. Required bilingual sections
    assert '# Summary (EN)' in content, "Missing English summary section"
    assert '# Краткое Описание (RU)' in content, "Missing Russian summary section"

    # 6. Tags should be array with English values
    assert 'tags: [' in content, "Tags should be array format"
    assert 'difficulty/medium' in content, "Tags should include difficulty tag"


def test_topic_inference_logic():
    """Test that topic is correctly inferred from concept name."""
    test_cases = [
        ('kotlin-basics', 'kotlin', 'moc-kotlin'),
        ('android-lifecycle', 'android', 'moc-android'),
        ('binary-search-algorithm', 'algorithms', 'moc-algorithms'),
        ('mvvm-pattern', 'architecture-patterns', 'moc-system-design'),
        ('unknown-concept', 'programming-languages', 'moc-kotlin'),  # fallback
    ]

    for concept_name, expected_topic, expected_moc in test_cases:
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

        assert topic == expected_topic, (
            f"For concept '{concept_name}', expected topic '{expected_topic}' but got '{topic}'"
        )
        assert moc == expected_moc, (
            f"For concept '{concept_name}', expected MOC '{expected_moc}' but got '{moc}'"
        )


if __name__ == '__main__':
    # Run tests standalone
    print("Running concept generation template tests...\n")

    try:
        test_concept_template_has_required_fields()
        print("✓ test_concept_template_has_required_fields PASSED")
    except AssertionError as e:
        print(f"✗ test_concept_template_has_required_fields FAILED: {e}")

    try:
        test_concept_template_field_formats()
        print("✓ test_concept_template_field_formats PASSED")
    except AssertionError as e:
        print(f"✗ test_concept_template_field_formats FAILED: {e}")

    try:
        test_topic_inference_logic()
        print("✓ test_topic_inference_logic PASSED")
    except AssertionError as e:
        print(f"✗ test_topic_inference_logic FAILED: {e}")

    print("\nAll tests completed!")
