#!/usr/bin/env python3
"""
YAML Builder for Obsidian Interview Questions Vault

Builds valid YAML frontmatter for Q&A notes following vault conventions.
"""

from datetime import datetime
from typing import List, Optional


class YAMLBuilder:
    """Build YAML frontmatter for vault notes"""

    def __init__(self):
        """Initialize YAML builder"""
        pass

    def build_qna_yaml(
        self,
        id: str,
        title_en: str,
        title_ru: str,
        topic: str,
        subtopics: List[str],
        question_kind: str,
        difficulty: str,
        moc: str,
        related: List[str],
        tags: List[str],
        original_language: str = "en",
        language_tags: Optional[List[str]] = None,
        status: str = "draft",
        created: Optional[str] = None,
        updated: Optional[str] = None,
        additional_aliases: Optional[List[str]] = None
    ) -> str:
        """
        Build Q&A YAML frontmatter

        Args:
            id: Note ID (e.g., "kotlin-001")
            title_en: English title
            title_ru: Russian title
            topic: Topic from TAXONOMY.md
            subtopics: List of subtopics (1-3 items)
            question_kind: Type of question (coding, theory, system-design, android)
            difficulty: easy, medium, or hard
            moc: MOC reference (without brackets)
            related: List of related notes (without brackets)
            tags: List of tags (English only)
            original_language: Original language (en or ru)
            language_tags: Languages present (defaults to [en, ru])
            status: Note status (defaults to draft)
            created: Creation date (YYYY-MM-DD, defaults to today)
            updated: Update date (YYYY-MM-DD, defaults to today)
            additional_aliases: Extra aliases beyond title translations

        Returns:
            YAML frontmatter string
        """
        # Set defaults
        if language_tags is None:
            language_tags = ["en", "ru"]
        if created is None:
            created = datetime.now().strftime("%Y-%m-%d")
        if updated is None:
            updated = datetime.now().strftime("%Y-%m-%d")

        # Build aliases
        aliases = [title_en, title_ru]
        if additional_aliases:
            aliases.extend(additional_aliases)

        # Build YAML
        yaml_parts = [
            "---",
            f"id: {id}",
            f"title: {title_en} / {title_ru}",
            f"aliases: [{', '.join(aliases)}]",
            "",
            "# Classification",
            f"topic: {topic}",
            f"subtopics: [{', '.join(subtopics)}]",
            f"question_kind: {question_kind}",
            f"difficulty: {difficulty}",
            "",
            "# Language",
            f"original_language: {original_language}",
            f"language_tags: [{', '.join(language_tags)}]",
            "",
            "# Workflow",
            f"status: {status}",
            "",
            "# Links (WITHOUT brackets in YAML!)",
            f"moc: {moc}",
            f"related: [{', '.join(related)}]",
            "",
            "# Timestamps",
            f"created: {created}",
            f"updated: {updated}",
            "",
            "# Tags (English only!)",
            f"tags: [{', '.join(tags)}]",
            "---"
        ]

        return "\n".join(yaml_parts)

    def build_concept_yaml(
        self,
        id: str,
        title_en: str,
        title_ru: str,
        summary: str,
        tags: List[str],
        aliases: Optional[List[str]] = None,
        created: Optional[str] = None,
        updated: Optional[str] = None
    ) -> str:
        """
        Build concept YAML frontmatter

        Args:
            id: Concept ID (e.g., "concept-001")
            title_en: English title
            title_ru: Russian title
            summary: Brief one-sentence summary
            tags: List of tags (include "concept" and topic)
            aliases: List of aliases (defaults to translations)
            created: Creation date
            updated: Update date

        Returns:
            YAML frontmatter string
        """
        if aliases is None:
            aliases = [title_en, title_ru]
        if created is None:
            created = datetime.now().strftime("%Y-%m-%d")
        if updated is None:
            updated = datetime.now().strftime("%Y-%m-%d")

        yaml_parts = [
            "---",
            f"id: {id}",
            f"title: {title_en} / {title_ru}",
            f"aliases: [{', '.join(aliases)}]",
            f"summary: {summary}",
            f"tags: [{', '.join(tags)}]",
            f"created: {created}",
            f"updated: {updated}",
            "---"
        ]

        return "\n".join(yaml_parts)

    def validate_yaml_format(self, yaml_dict: dict) -> List[str]:
        """
        Validate YAML frontmatter format

        Args:
            yaml_dict: Parsed YAML dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for brackets in moc field
        moc = yaml_dict.get('moc', '')
        if '[[' in moc or ']]' in moc:
            errors.append("FORBIDDEN: Brackets in 'moc' field. Should be 'moc-name', not '[[moc-name]]'")

        # Check for double brackets in related array
        related = yaml_dict.get('related', [])
        if isinstance(related, list):
            for item in related:
                if '[[' in str(item) or ']]' in str(item):
                    errors.append(f"FORBIDDEN: Double brackets in 'related' item: {item}")
        elif isinstance(related, str) and ('[[' in related or ']]' in related):
            errors.append("FORBIDDEN: Double brackets in 'related' field")

        # Check for Russian in tags
        tags = yaml_dict.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                # Simple check: if tag contains Cyrillic characters
                if any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in str(tag)):
                    errors.append(f"FORBIDDEN: Russian in tags: {tag}")

        # Check topic is not array
        topic = yaml_dict.get('topic')
        if isinstance(topic, list):
            errors.append("FORBIDDEN: 'topic' should be single value, not array")

        # Check difficulty tag present
        if 'difficulty/' not in ' '.join(str(t) for t in tags):
            errors.append("REQUIRED: Tags must include 'difficulty/[level]'")

        return errors


def main():
    """Example usage"""
    builder = YAMLBuilder()

    # Build Q&A YAML
    qna_yaml = builder.build_qna_yaml(
        id="kotlin-015",
        title_en="Coroutine Context",
        title_ru="Контекст корутин",
        topic="kotlin",
        subtopics=["coroutines", "concurrency"],
        question_kind="theory",
        difficulty="medium",
        moc="moc-kotlin",
        related=["c-coroutines", "c-coroutine-scope", "q-coroutine-scope--kotlin--medium"],
        tags=["kotlin", "coroutines", "concurrency", "difficulty/medium"]
    )

    print("Q&A YAML:")
    print(qna_yaml)
    print()

    # Build concept YAML
    concept_yaml = builder.build_concept_yaml(
        id="concept-015",
        title_en="ViewModel",
        title_ru="ViewModel (Модель представления)",
        summary="Architecture component that stores and manages UI-related data in a lifecycle-conscious way",
        tags=["concept", "android", "architecture-patterns", "jetpack"]
    )

    print("Concept YAML:")
    print(concept_yaml)


if __name__ == '__main__':
    main()
