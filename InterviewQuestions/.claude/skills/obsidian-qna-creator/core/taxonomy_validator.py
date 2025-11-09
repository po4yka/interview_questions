#!/usr/bin/env python3
"""
Taxonomy Validator for Obsidian Interview Questions Vault

Validates topics, subtopics, and other controlled vocabulary values
against TAXONOMY.md definitions.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Set


class TaxonomyValidator:
    """Validator for controlled vocabularies from TAXONOMY.md"""

    def __init__(self, taxonomy_path: str = "00-Administration/Vault-Rules/TAXONOMY.md"):
        """
        Initialize validator with path to TAXONOMY.md

        Args:
            taxonomy_path: Relative path to TAXONOMY.md from vault root
        """
        self.taxonomy_path = Path(taxonomy_path)
        self.valid_topics: Set[str] = set()
        self.valid_difficulties: Set[str] = {'easy', 'medium', 'hard'}
        self.valid_question_kinds: Set[str] = {'coding', 'theory', 'system-design', 'android'}
        self.valid_statuses: Set[str] = {'draft', 'reviewed', 'ready', 'retired'}
        self.valid_languages: Set[str] = {'en', 'ru'}
        self.android_subtopics: Set[str] = set()
        self.folder_topic_mapping: Dict[str, str] = {}

        self._load_taxonomy()

    def _load_taxonomy(self) -> None:
        """Load and parse TAXONOMY.md"""
        if not self.taxonomy_path.exists():
            # Provide default values if file doesn't exist
            self.valid_topics = {
                'algorithms', 'data-structures', 'system-design', 'android', 'kotlin',
                'programming-languages', 'architecture-patterns', 'concurrency',
                'distributed-systems', 'databases', 'networking', 'operating-systems',
                'security', 'performance', 'cloud', 'testing', 'devops-ci-cd',
                'tools', 'debugging', 'ui-ux-accessibility', 'behavioral', 'cs'
            }

            self.android_subtopics = {
                'ui-compose', 'ui-views', 'ui-navigation', 'ui-state', 'ui-animation',
                'architecture-mvvm', 'architecture-mvi', 'di-hilt',
                'lifecycle', 'activity', 'fragment', 'service',
                'coroutines', 'flow', 'threads-sync',
                'room', 'datastore', 'files-media',
                'testing-unit', 'testing-instrumented', 'testing-ui'
            }

            self.folder_topic_mapping = {
                '20-Algorithms': 'algorithms',
                '30-System-Design': 'system-design',
                '40-Android': 'android',
                '50-Backend': 'databases',
                '60-CompSci': 'operating-systems',
                '70-Kotlin': 'kotlin',
                '80-Tools': 'tools'
            }
            return

        # Parse TAXONOMY.md (simplified - in production, parse markdown properly)
        content = self.taxonomy_path.read_text(encoding='utf-8')

        # Extract valid topics (look for topic names in comments)
        topic_pattern = r'^([a-z\-]+)\s+#'
        for line in content.split('\n'):
            match = re.match(topic_pattern, line.strip())
            if match:
                self.valid_topics.add(match.group(1))

        # If no topics found in parsing, use defaults
        if not self.valid_topics:
            self.valid_topics = {
                'algorithms', 'data-structures', 'system-design', 'android', 'kotlin',
                'programming-languages', 'architecture-patterns', 'concurrency',
                'distributed-systems', 'databases', 'networking', 'operating-systems',
                'security', 'performance', 'cloud', 'testing', 'devops-ci-cd',
                'tools', 'debugging', 'ui-ux-accessibility', 'behavioral', 'cs'
            }

    def validate_topic(self, topic: str) -> bool:
        """
        Check if topic is valid

        Args:
            topic: Topic value to validate

        Returns:
            True if valid, False otherwise
        """
        return topic in self.valid_topics

    def validate_difficulty(self, difficulty: str) -> bool:
        """Check if difficulty is valid"""
        return difficulty in self.valid_difficulties

    def validate_question_kind(self, kind: str) -> bool:
        """Check if question_kind is valid"""
        return kind in self.valid_question_kinds

    def validate_status(self, status: str) -> bool:
        """Check if status is valid"""
        return status in self.valid_statuses

    def validate_language(self, language: str) -> bool:
        """Check if language is valid"""
        return language in self.valid_languages

    def validate_android_subtopic(self, subtopic: str) -> bool:
        """Check if subtopic is valid for Android topic"""
        return subtopic in self.android_subtopics

    def get_valid_topics(self) -> List[str]:
        """Get list of all valid topics"""
        return sorted(list(self.valid_topics))

    def get_similar_topics(self, topic: str, max_results: int = 3) -> List[str]:
        """
        Find topics similar to given string (for suggestions)

        Args:
            topic: Topic string to match
            max_results: Maximum number of suggestions

        Returns:
            List of similar valid topics
        """
        # Simple similarity: topics that start with same letters
        similar = [t for t in self.valid_topics if t.startswith(topic[:3])]
        return sorted(similar)[:max_results]

    def validate_folder_topic_match(self, folder: str, topic: str) -> bool:
        """
        Check if file folder matches topic

        Args:
            folder: Folder path (e.g., "70-Kotlin")
            topic: Topic value

        Returns:
            True if folder-topic mapping is correct
        """
        folder_name = Path(folder).name
        expected_topic = self.folder_topic_mapping.get(folder_name)

        # If exact mapping exists, use it
        if expected_topic:
            return expected_topic == topic

        # Otherwise, check if folder name contains topic
        return topic in folder_name.lower()

    def get_folder_for_topic(self, topic: str) -> Optional[str]:
        """
        Get recommended folder for a topic

        Args:
            topic: Topic value

        Returns:
            Folder path or None if no clear mapping
        """
        # Reverse lookup in folder_topic_mapping
        for folder, folder_topic in self.folder_topic_mapping.items():
            if folder_topic == topic:
                return folder

        # Fallback mappings
        topic_to_folder = {
            'algorithms': '20-Algorithms',
            'data-structures': '20-Algorithms',
            'system-design': '30-System-Design',
            'distributed-systems': '30-System-Design',
            'android': '40-Android',
            'databases': '50-Backend',
            'networking': '50-Backend',
            'operating-systems': '60-CompSci',
            'concurrency': '60-CompSci',
            'cs': '60-CompSci',
            'kotlin': '70-Kotlin',
            'programming-languages': '70-Kotlin',
            'tools': '80-Tools',
            'devops-ci-cd': '80-Tools'
        }

        return topic_to_folder.get(topic)


def main():
    """Example usage"""
    validator = TaxonomyValidator()

    # Test topic validation
    print("Valid topics:", validator.get_valid_topics()[:5], "...")
    print("Is 'kotlin' valid?", validator.validate_topic('kotlin'))
    print("Is 'invalid-topic' valid?", validator.validate_topic('invalid-topic'))

    # Test difficulty
    print("Is 'medium' valid difficulty?", validator.validate_difficulty('medium'))
    print("Is 'super-hard' valid difficulty?", validator.validate_difficulty('super-hard'))

    # Test folder mapping
    print("Folder for 'kotlin':", validator.get_folder_for_topic('kotlin'))
    print("Does '70-Kotlin' match 'kotlin'?", validator.validate_folder_topic_match('70-Kotlin', 'kotlin'))


if __name__ == '__main__':
    main()
