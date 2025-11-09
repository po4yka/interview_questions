#!/usr/bin/env python3
"""
Note Validator for Obsidian Interview Questions Vault

Comprehensive validation of notes against vault rules.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Validation severity levels"""
    REQUIRED = "REQUIRED"  # Must pass
    FORBIDDEN = "FORBIDDEN"  # Must not occur
    WARNING = "WARNING"  # Should fix
    NOTE = "NOTE"  # Suggestion


@dataclass
class ValidationIssue:
    """Single validation issue"""
    severity: Severity
    category: str
    message: str
    suggestion: Optional[str] = None


class NoteValidator:
    """Validate notes against vault rules"""

    def __init__(self, valid_topics: Optional[List[str]] = None):
        """
        Initialize validator

        Args:
            valid_topics: List of valid topics from TAXONOMY.md
        """
        self.valid_topics = valid_topics or [
            'algorithms', 'data-structures', 'system-design', 'android', 'kotlin',
            'programming-languages', 'architecture-patterns', 'concurrency',
            'distributed-systems', 'databases', 'networking', 'operating-systems',
            'security', 'performance', 'cloud', 'testing', 'devops-ci-cd',
            'tools', 'debugging', 'ui-ux-accessibility', 'behavioral', 'cs'
        ]

        self.valid_difficulties = {'easy', 'medium', 'hard'}
        self.valid_question_kinds = {'coding', 'theory', 'system-design', 'android'}
        self.valid_statuses = {'draft', 'reviewed', 'ready', 'retired'}

    def validate_note(
        self,
        yaml_dict: dict,
        content: str,
        file_path: str,
        is_ai_created: bool = True
    ) -> List[ValidationIssue]:
        """
        Validate complete note

        Args:
            yaml_dict: Parsed YAML frontmatter
            content: Note content (markdown)
            file_path: Path to note file
            is_ai_created: Whether note was created by AI

        Returns:
            List of validation issues
        """
        issues = []

        # Run all validation checks
        issues.extend(self._check_yaml_completeness(yaml_dict))
        issues.extend(self._check_topic_validity(yaml_dict))
        issues.extend(self._check_folder_placement(yaml_dict, file_path))
        issues.extend(self._check_content_structure(content, yaml_dict))
        issues.extend(self._check_link_requirements(yaml_dict))
        issues.extend(self._check_tag_requirements(yaml_dict))
        issues.extend(self._check_forbidden_violations(yaml_dict, content, is_ai_created))
        issues.extend(self._check_android_specific(yaml_dict))
        issues.extend(self._check_warnings(yaml_dict, content))

        return issues

    def _check_yaml_completeness(self, yaml_dict: dict) -> List[ValidationIssue]:
        """Check all required YAML fields are present"""
        issues = []
        required_fields = [
            'id', 'title', 'aliases', 'topic', 'subtopics',
            'difficulty', 'original_language', 'language_tags',
            'status', 'moc', 'related', 'created', 'updated', 'tags'
        ]

        for field in required_fields:
            if field not in yaml_dict:
                issues.append(ValidationIssue(
                    severity=Severity.REQUIRED,
                    category="YAML Completeness",
                    message=f"Missing required field: {field}",
                    suggestion=f"Add '{field}:' to YAML frontmatter"
                ))

        # Check question_kind for Q&A notes
        if 'id' in yaml_dict and not yaml_dict['id'].startswith('concept'):
            if 'question_kind' not in yaml_dict:
                issues.append(ValidationIssue(
                    severity=Severity.REQUIRED,
                    category="YAML Completeness",
                    message="Missing 'question_kind' field for Q&A note",
                    suggestion="Add 'question_kind: coding | theory | system-design | android'"
                ))

        return issues

    def _check_topic_validity(self, yaml_dict: dict) -> List[ValidationIssue]:
        """Validate topic and related fields"""
        issues = []

        topic = yaml_dict.get('topic')
        if topic:
            # Check if topic is valid
            if topic not in self.valid_topics:
                issues.append(ValidationIssue(
                    severity=Severity.REQUIRED,
                    category="Topic Validation",
                    message=f"Invalid topic: '{topic}'",
                    suggestion=f"Must be one of: {', '.join(self.valid_topics[:5])}..."
                ))

            # Check if topic is array (FORBIDDEN)
            if isinstance(topic, list):
                issues.append(ValidationIssue(
                    severity=Severity.FORBIDDEN,
                    category="Topic Validation",
                    message="Topic field is array",
                    suggestion="Use single value: 'topic: kotlin' not 'topic: [kotlin]'"
                ))

        # Check difficulty
        difficulty = yaml_dict.get('difficulty')
        if difficulty and difficulty not in self.valid_difficulties:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Topic Validation",
                message=f"Invalid difficulty: '{difficulty}'",
                suggestion="Must be: easy, medium, or hard"
            ))

        # Check question_kind
        question_kind = yaml_dict.get('question_kind')
        if question_kind and question_kind not in self.valid_question_kinds:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Topic Validation",
                message=f"Invalid question_kind: '{question_kind}'",
                suggestion="Must be: coding, theory, system-design, or android"
            ))

        # Check status
        status = yaml_dict.get('status')
        if status and status not in self.valid_statuses:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Topic Validation",
                message=f"Invalid status: '{status}'",
                suggestion="Must be: draft, reviewed, ready, or retired"
            ))

        return issues

    def _check_folder_placement(self, yaml_dict: dict, file_path: str) -> List[ValidationIssue]:
        """Check file is in correct folder for its topic"""
        issues = []

        topic = yaml_dict.get('topic')
        if not topic:
            return issues

        path = Path(file_path)
        folder = path.parent.name

        # Simple folder-topic mapping
        topic_folder_map = {
            'algorithms': '20-Algorithms',
            'system-design': '30-System-Design',
            'android': '40-Android',
            'databases': '50-Backend',
            'operating-systems': '60-CompSci',
            'kotlin': '70-Kotlin',
            'tools': '80-Tools'
        }

        expected_folder = topic_folder_map.get(topic)
        if expected_folder and folder != expected_folder:
            issues.append(ValidationIssue(
                severity=Severity.FORBIDDEN,
                category="Folder Placement",
                message=f"File in wrong folder: '{folder}' for topic '{topic}'",
                suggestion=f"Move to {expected_folder}/"
            ))

        return issues

    def _check_content_structure(self, content: str, yaml_dict: dict) -> List[ValidationIssue]:
        """Check bilingual content structure"""
        issues = []

        # Check for required sections
        required_sections = [
            (r'# Question \(EN\)', "# Question (EN)"),
            (r'# Вопрос \(RU\)', "# Вопрос (RU)"),
            (r'## Answer \(EN\)', "## Answer (EN)"),
            (r'## Ответ \(RU\)', "## Ответ (RU)")
        ]

        for pattern, section_name in required_sections:
            if not re.search(pattern, content):
                issues.append(ValidationIssue(
                    severity=Severity.REQUIRED,
                    category="Content Structure",
                    message=f"Missing section: {section_name}",
                    suggestion=f"Add {section_name} section"
                ))

        # Check both languages have substantial content
        en_content = re.search(r'# Question \(EN\)(.*?)(?:# Вопрос|$)', content, re.DOTALL)
        ru_content = re.search(r'# Вопрос \(RU\)(.*?)(?:## Answer|$)', content, re.DOTALL)

        if en_content and len(en_content.group(1).strip()) < 20:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                category="Content Structure",
                message="English content is very short",
                suggestion="Add more detailed content"
            ))

        if ru_content and len(ru_content.group(1).strip()) < 20:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                category="Content Structure",
                message="Russian content is very short",
                suggestion="Add more detailed content"
            ))

        return issues

    def _check_link_requirements(self, yaml_dict: dict) -> List[ValidationIssue]:
        """Check MOC and related links"""
        issues = []

        # Check moc field
        moc = yaml_dict.get('moc')
        if not moc:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Link Requirements",
                message="Missing 'moc' field",
                suggestion="Add 'moc: moc-[topic]'"
            ))
        elif '[[' in str(moc) or ']]' in str(moc):
            issues.append(ValidationIssue(
                severity=Severity.FORBIDDEN,
                category="Link Requirements",
                message="Brackets in 'moc' field",
                suggestion=f"Change '{moc}' to just the note name (e.g., 'moc-kotlin')"
            ))

        # Check related field
        related = yaml_dict.get('related', [])
        if not related:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Link Requirements",
                message="Missing 'related' field",
                suggestion="Add at least 2 related notes"
            ))
        elif len(related) < 2:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Link Requirements",
                message="Need at least 2 related links",
                suggestion="Add more related concepts or questions"
            ))
        elif isinstance(related, list):
            for item in related:
                if '[[' in str(item) or ']]' in str(item):
                    issues.append(ValidationIssue(
                        severity=Severity.FORBIDDEN,
                        category="Link Requirements",
                        message=f"Double brackets in related item: {item}",
                        suggestion="Use array format: [item1, item2], not [[item1]], [[item2]]"
                    ))

        return issues

    def _check_tag_requirements(self, yaml_dict: dict) -> List[ValidationIssue]:
        """Check tag conventions"""
        issues = []

        tags = yaml_dict.get('tags', [])
        if not tags:
            issues.append(ValidationIssue(
                severity=Severity.REQUIRED,
                category="Tag Requirements",
                message="Missing 'tags' field or empty",
                suggestion="Add relevant tags"
            ))
            return issues

        # Check for Russian in tags
        for tag in tags:
            if any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in str(tag)):
                issues.append(ValidationIssue(
                    severity=Severity.FORBIDDEN,
                    category="Tag Requirements",
                    message=f"Russian in tags: {tag}",
                    suggestion="Use English only in tags, put Russian in 'aliases'"
                ))

        # Check for difficulty tag
        difficulty = yaml_dict.get('difficulty')
        if difficulty:
            difficulty_tag = f"difficulty/{difficulty}"
            if difficulty_tag not in tags:
                issues.append(ValidationIssue(
                    severity=Severity.REQUIRED,
                    category="Tag Requirements",
                    message=f"Missing difficulty tag: {difficulty_tag}",
                    suggestion=f"Add '{difficulty_tag}' to tags"
                ))

        return issues

    def _check_forbidden_violations(
        self,
        yaml_dict: dict,
        content: str,
        is_ai_created: bool
    ) -> List[ValidationIssue]:
        """Check for forbidden violations"""
        issues = []

        # Check for emoji
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+"
        )
        if emoji_pattern.search(content):
            issues.append(ValidationIssue(
                severity=Severity.FORBIDDEN,
                category="Forbidden Violations",
                message="Emoji found in content",
                suggestion="Remove emoji and use text equivalents"
            ))

        # Check AI status restrictions
        if is_ai_created:
            status = yaml_dict.get('status')
            if status in ['reviewed', 'ready']:
                issues.append(ValidationIssue(
                    severity=Severity.FORBIDDEN,
                    category="Forbidden Violations",
                    message=f"AI cannot set status to '{status}'",
                    suggestion="Use 'status: draft' only"
                ))

        return issues

    def _check_android_specific(self, yaml_dict: dict) -> List[ValidationIssue]:
        """Check Android-specific rules"""
        issues = []

        topic = yaml_dict.get('topic')
        if topic != 'android':
            return issues

        subtopics = yaml_dict.get('subtopics', [])
        tags = yaml_dict.get('tags', [])

        # Check subtopics are mirrored to tags
        for subtopic in subtopics:
            android_tag = f"android/{subtopic}"
            if android_tag not in tags:
                issues.append(ValidationIssue(
                    severity=Severity.REQUIRED,
                    category="Android-Specific",
                    message=f"Android subtopic not mirrored to tags: {subtopic}",
                    suggestion=f"Add 'android/{subtopic}' to tags"
                ))

        return issues

    def _check_warnings(self, yaml_dict: dict, content: str) -> List[ValidationIssue]:
        """Check warning-level issues"""
        issues = []

        # Check for Follow-ups section
        if '## Follow-ups' not in content:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                category="Content Quality",
                message="Missing '## Follow-ups' section",
                suggestion="Add common variations and edge cases"
            ))

        # Check related links count
        related = yaml_dict.get('related', [])
        if len(related) < 3:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                category="Link Quality",
                message=f"Only {len(related)} related links (recommend 3-5)",
                suggestion="Add more related concepts or questions"
            ))

        return issues


def main():
    """Example usage"""
    validator = NoteValidator()

    # Example YAML with issues
    yaml_dict = {
        'id': 'kotlin-001',
        'title': 'Test',
        'topic': 'kotlin',
        'difficulty': 'medium',
        'status': 'draft',
        'moc': '[[moc-kotlin]]',  # FORBIDDEN: has brackets
        'related': ['c-coroutines'],  # REQUIRED: need 2+
        'tags': ['kotlin', 'корутины']  # FORBIDDEN: Russian in tags
    }

    content = """
# Question (EN)
Test question

## Answer (EN)
Test answer
"""

    issues = validator.validate_note(yaml_dict, content, "70-Kotlin/test.md")

    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"[{issue.severity.value}] {issue.category}: {issue.message}")
        if issue.suggestion:
            print(f"  → {issue.suggestion}")


if __name__ == '__main__':
    main()
