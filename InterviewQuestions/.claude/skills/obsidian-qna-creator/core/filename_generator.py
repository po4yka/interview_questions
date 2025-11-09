#!/usr/bin/env python3
"""
Filename Generator for Obsidian Interview Questions Vault

Generates valid filenames following vault conventions:
- Q&A: q-[slug]--[topic]--[difficulty].md
- Concept: c-[concept-name].md
- MOC: moc-[topic].md
"""

import re
from typing import Optional


class FilenameGenerator:
    """Generate valid filenames for vault notes"""

    @staticmethod
    def slugify(text: str, max_words: int = 8) -> str:
        """
        Convert text to valid slug

        Args:
            text: Input text
            max_words: Maximum number of words in slug

        Returns:
            Slugified text (lowercase, hyphenated, English only)
        """
        # Convert to lowercase
        slug = text.lower()

        # Remove non-ASCII characters (keep English only)
        slug = slug.encode('ascii', 'ignore').decode('ascii')

        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)

        # Remove special characters except hyphens
        slug = re.sub(r'[^a-z0-9\-]', '', slug)

        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Limit to max_words
        words = slug.split('-')
        if len(words) > max_words:
            slug = '-'.join(words[:max_words])

        return slug

    def generate_qna_filename(
        self,
        slug: str,
        topic: str,
        difficulty: str,
        auto_slugify: bool = True
    ) -> str:
        """
        Generate Q&A filename

        Args:
            slug: Question slug (will be slugified if auto_slugify=True)
            topic: Topic from TAXONOMY.md
            difficulty: easy, medium, or hard
            auto_slugify: Whether to automatically slugify the slug

        Returns:
            Valid Q&A filename

        Example:
            >>> gen = FilenameGenerator()
            >>> gen.generate_qna_filename("What is Coroutine Context", "kotlin", "medium")
            'q-what-is-coroutine-context--kotlin--medium.md'
        """
        if auto_slugify:
            slug = self.slugify(slug)

        # Validate components
        if not slug:
            raise ValueError("Slug cannot be empty")
        if not topic:
            raise ValueError("Topic cannot be empty")
        if difficulty not in ['easy', 'medium', 'hard']:
            raise ValueError(f"Difficulty must be easy, medium, or hard, got: {difficulty}")

        return f"q-{slug}--{topic}--{difficulty}.md"

    def generate_concept_filename(self, concept_name: str, auto_slugify: bool = True) -> str:
        """
        Generate concept filename

        Args:
            concept_name: Concept name
            auto_slugify: Whether to automatically slugify

        Returns:
            Valid concept filename

        Example:
            >>> gen = FilenameGenerator()
            >>> gen.generate_concept_filename("ViewModel")
            'c-viewmodel.md'
        """
        if auto_slugify:
            concept_name = self.slugify(concept_name, max_words=4)

        if not concept_name:
            raise ValueError("Concept name cannot be empty")

        return f"c-{concept_name}.md"

    def generate_moc_filename(self, topic: str, auto_slugify: bool = True) -> str:
        """
        Generate MOC filename

        Args:
            topic: Topic name
            auto_slugify: Whether to automatically slugify

        Returns:
            Valid MOC filename

        Example:
            >>> gen = FilenameGenerator()
            >>> gen.generate_moc_filename("kotlin")
            'moc-kotlin.md'
        """
        if auto_slugify:
            topic = self.slugify(topic, max_words=3)

        if not topic:
            raise ValueError("Topic cannot be empty")

        return f"moc-{topic}.md"

    def parse_qna_filename(self, filename: str) -> Optional[dict]:
        """
        Parse Q&A filename to extract components

        Args:
            filename: Q&A filename to parse

        Returns:
            Dictionary with slug, topic, difficulty or None if invalid

        Example:
            >>> gen = FilenameGenerator()
            >>> gen.parse_qna_filename("q-coroutine-context--kotlin--medium.md")
            {'slug': 'coroutine-context', 'topic': 'kotlin', 'difficulty': 'medium'}
        """
        pattern = r'^q-([a-z0-9\-]+)--([a-z0-9\-]+)--(easy|medium|hard)\.md$'
        match = re.match(pattern, filename)

        if not match:
            return None

        return {
            'slug': match.group(1),
            'topic': match.group(2),
            'difficulty': match.group(3)
        }

    def validate_filename(self, filename: str, note_type: str = 'qna') -> bool:
        """
        Validate filename format

        Args:
            filename: Filename to validate
            note_type: Type of note ('qna', 'concept', 'moc')

        Returns:
            True if valid, False otherwise
        """
        if note_type == 'qna':
            pattern = r'^q-[a-z0-9\-]+--[a-z0-9\-]+--(easy|medium|hard)\.md$'
        elif note_type == 'concept':
            pattern = r'^c-[a-z0-9\-]+\.md$'
        elif note_type == 'moc':
            pattern = r'^moc-[a-z0-9\-]+\.md$'
        else:
            raise ValueError(f"Unknown note_type: {note_type}")

        return bool(re.match(pattern, filename))


def main():
    """Example usage"""
    gen = FilenameGenerator()

    # Generate Q&A filename
    print("Q&A filename:", gen.generate_qna_filename(
        "What is Coroutine Context?",
        "kotlin",
        "medium"
    ))

    # Generate concept filename
    print("Concept filename:", gen.generate_concept_filename("View Model"))

    # Generate MOC filename
    print("MOC filename:", gen.generate_moc_filename("kotlin"))

    # Parse filename
    parsed = gen.parse_qna_filename("q-coroutine-context--kotlin--medium.md")
    print("Parsed:", parsed)

    # Validate filenames
    print("Valid Q&A?", gen.validate_filename("q-test--kotlin--easy.md", "qna"))
    print("Invalid Q&A?", gen.validate_filename("q-test.md", "qna"))


if __name__ == '__main__':
    main()
