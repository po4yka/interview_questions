"""Validation rules for YAML frontmatter."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import date, datetime

from .base import BaseValidator, Severity
from .registry import ValidatorRegistry


@ValidatorRegistry.register
class YAMLValidator(BaseValidator):
    """Validate YAML frontmatter and high-level metadata rules."""

    REQUIRED_FIELDS = [
        "id",
        "title",
        "aliases",
        "topic",
        "subtopics",
        "question_kind",
        "difficulty",
        "original_language",
        "language_tags",
        "status",
        "moc",
        "related",
        "created",
        "updated",
        "tags",
    ]

    ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
    ALLOWED_LANGUAGES = {"en", "ru"}
    ALLOWED_QUESTION_KINDS = {"coding", "theory", "system-design", "android"}
    # New ID format: <subject>-<serial> (e.g., algo-001, android-134, kotlin-042)
    ID_PATTERN = re.compile(r"^[a-z]+-\d+$")

    # TAXONOMY-aware MOC mapping (from TAXONOMY.md)
    TOPIC_TO_MOC = {
        "algorithms": "moc-algorithms",
        "data-structures": "moc-algorithms",
        "system-design": "moc-system-design",
        "distributed-systems": "moc-system-design",
        "android": "moc-android",
        "kotlin": "moc-kotlin",
        "programming-languages": "moc-kotlin",
        "databases": "moc-backend",
        "networking": "moc-backend",
        "os": "moc-cs",
        "operating-systems": "moc-cs",
        "concurrency": "moc-cs",
        "cs": "moc-cs",
        "tools": "moc-tools",
        "debugging": "moc-tools",
    }

    def validate(self):
        frontmatter = self.frontmatter
        if not frontmatter:
            self.add_issue(Severity.CRITICAL, "Missing YAML frontmatter")
            return self._summary

        self._check_required_fields(frontmatter)
        self._check_id(frontmatter.get("id"))
        self._check_title(frontmatter.get("title"))
        self._check_aliases(frontmatter.get("aliases"))
        self._check_topic(frontmatter.get("topic"))
        self._check_subtopics(frontmatter.get("subtopics"))
        self._check_question_kind(frontmatter.get("question_kind"))
        self._check_difficulty(frontmatter.get("difficulty"))
        self._check_languages(
            frontmatter.get("original_language"),
            frontmatter.get("language_tags"),
        )
        self._check_status(frontmatter.get("status"))
        self._check_moc(frontmatter.get("moc"), frontmatter.get("topic"))
        self._check_related(frontmatter.get("related"))
        self._check_dates(frontmatter.get("created"), frontmatter.get("updated"))
        self._check_tags(frontmatter.get("tags"), frontmatter.get("difficulty"))
        return self._summary

    # Individual checks -------------------------------------------------

    def _check_required_fields(self, frontmatter: dict) -> None:
        missing = [field for field in self.REQUIRED_FIELDS if field not in frontmatter]
        if missing:
            self.add_issue(
                Severity.CRITICAL,
                f"Missing required YAML fields: {', '.join(sorted(missing))}",
            )
        else:
            self.add_passed("All required YAML fields present")

    def _check_id(self, value: str) -> None:
        if not value:
            return
        if not self.ID_PATTERN.match(str(value)):
            self.add_issue(
                Severity.ERROR,
                "id must follow pattern <subject>-<serial> (e.g., algo-001, android-134)",
                field="id",
            )
        else:
            self.add_passed("id format valid")

    def _check_title(self, value: str) -> None:
        if not value:
            self.add_issue(Severity.ERROR, "title missing", field="title")
            return
        if " / " not in value:
            self.add_issue(
                Severity.WARNING,
                "title should contain both EN and RU titles separated by ' / '",
                field="title",
            )
        else:
            self.add_passed("Bilingual title format valid")

    def _check_aliases(self, aliases: Iterable[str] | None) -> None:
        if not aliases or not isinstance(aliases, list):
            self.add_issue(Severity.ERROR, "aliases must be a list", field="aliases")
            return
        if len(aliases) < 2:
            self.add_issue(
                Severity.WARNING,
                "aliases should include both EN and RU variants",
                field="aliases",
            )
        else:
            self.add_passed("aliases list present")

    def _check_topic(self, topic: str | None) -> None:
        if not topic:
            self.add_issue(Severity.ERROR, "topic missing", field="topic")
            return
        topics = self.taxonomy.topics
        if topics and topic not in topics:
            self.add_issue(
                Severity.CRITICAL,
                f"topic '{topic}' not present in TAXONOMY.md",
                field="topic",
            )
        else:
            self.add_passed("topic value valid")

    def _check_subtopics(self, subtopics: list[str] | None) -> None:
        if subtopics is None:
            self.add_issue(Severity.ERROR, "subtopics list missing", field="subtopics")
            return
        if not isinstance(subtopics, list) or not subtopics:
            self.add_issue(Severity.ERROR, "subtopics must be a non-empty list", field="subtopics")
            return
        if len(subtopics) > 3:
            self.add_issue(
                Severity.WARNING,
                "subtopics should contain at most three values",
                field="subtopics",
            )
        else:
            self.add_passed("subtopics count valid")

    def _check_question_kind(self, value: str | None) -> None:
        if value not in self.ALLOWED_QUESTION_KINDS:
            self.add_issue(
                Severity.ERROR,
                f"question_kind must be one of {sorted(self.ALLOWED_QUESTION_KINDS)}",
                field="question_kind",
            )
        else:
            self.add_passed("question_kind valid")

    def _check_difficulty(self, value: str | None) -> None:
        if value not in self.ALLOWED_DIFFICULTIES:
            self.add_issue(
                Severity.ERROR,
                f"difficulty must be one of {sorted(self.ALLOWED_DIFFICULTIES)}",
                field="difficulty",
            )
        else:
            self.add_passed("difficulty value valid")

    def _check_languages(self, original: str | None, tags: list[str] | None) -> None:
        if original not in self.ALLOWED_LANGUAGES:
            self.add_issue(
                Severity.ERROR,
                f"original_language must be one of {sorted(self.ALLOWED_LANGUAGES)}",
                field="original_language",
            )
        if not tags or not isinstance(tags, list):
            self.add_issue(Severity.ERROR, "language_tags must be a list", field="language_tags")
            return
        invalid = [val for val in tags if val not in self.ALLOWED_LANGUAGES]
        if invalid:
            self.add_issue(
                Severity.ERROR,
                f"language_tags contain invalid values: {', '.join(sorted(invalid))}",
                field="language_tags",
            )
        else:
            self.add_passed("language tags valid")
        if original and tags and original not in tags:
            self.add_issue(
                Severity.WARNING,
                "language_tags should include original_language",
                field="language_tags",
            )

    def _check_status(self, value: str | None) -> None:
        allowed_statuses = {"draft", "reviewed", "ready", "retired"}
        if value not in allowed_statuses:
            self.add_issue(
                Severity.ERROR,
                f"status must be one of: {', '.join(sorted(allowed_statuses))}",
                field="status",
            )
        else:
            self.add_passed("status value valid")

    def _check_moc(self, moc: str | None, topic: str | None) -> None:
        if not moc:
            self.add_issue(Severity.ERROR, "moc missing", field="moc")
            return
        if "[" in moc or "]" in moc:
            self.add_issue(Severity.ERROR, "moc must not contain brackets", field="moc")
            return

        # TAXONOMY-aware check: use mapping instead of simple moc-{topic}
        expected = self.TOPIC_TO_MOC.get(topic) if topic else None

        if expected:
            if moc != expected:
                self.add_issue(
                    Severity.WARNING,
                    f"moc should match topic: expected '{expected}' for topic '{topic}'",
                    field="moc",
                )
            else:
                self.add_passed("moc matches topic (TAXONOMY-aware)")
        else:
            # Topic not in mapping, just validate format
            if moc.startswith("moc-"):
                self.add_passed("moc format valid")
            else:
                self.add_issue(
                    Severity.WARNING,
                    f"moc format should start with 'moc-' (current: '{moc}')",
                    field="moc",
                )

    def _check_related(self, related) -> None:
        if related is None:
            self.add_issue(Severity.ERROR, "related field missing", field="related")
            return
        if not isinstance(related, list):
            self.add_issue(Severity.ERROR, "related must be a list of note ids", field="related")
            return
        if not related:
            self.add_issue(
                Severity.WARNING,
                "related list is empty; add concept/question links",
                field="related",
            )
            return
        double_brackets = [item for item in related if "[[" in str(item)]
        if double_brackets:
            self.add_issue(
                Severity.ERROR,
                "related list must not contain double brackets",
                field="related",
            )
        else:
            self.add_passed("related list format valid")

    def _check_dates(self, created: str | None, updated: str | None) -> None:
        self._validate_date(created, "created")
        self._validate_date(updated, "updated")

    def _validate_date(self, value, field: str) -> None:
        if not value:
            # Use WARNING instead of ERROR to be lenient with existing notes
            self.add_issue(
                Severity.WARNING, f"{field} missing (recommended for new notes)", field=field
            )
            return
        # Accept both datetime.date and datetime.datetime objects from YAML parsing
        if isinstance(value, (datetime, date)):
            self.add_passed(f"{field} date format valid")
            return
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                self.add_issue(
                    Severity.ERROR,
                    f"{field} must follow YYYY-MM-DD",
                    field=field,
                )
            else:
                self.add_passed(f"{field} date format valid")
            return
        self.add_issue(
            Severity.ERROR,
            f"{field} must be a date string (YYYY-MM-DD)",
            field=field,
        )

    def _check_tags(self, tags, difficulty: str | None) -> None:
        if tags is None or not isinstance(tags, list) or not tags:
            self.add_issue(Severity.ERROR, "tags must be a non-empty list", field="tags")
            return
        non_ascii = [tag for tag in tags if not self._is_ascii(tag)]
        if non_ascii:
            self.add_issue(
                Severity.ERROR,
                f"tags must be ASCII/English only: {', '.join(non_ascii)}",
                field="tags",
            )
        else:
            self.add_passed("tags contain only ASCII characters")
        if difficulty:
            expected_tag = f"difficulty/{difficulty}"
            if expected_tag not in tags:
                self.add_issue(
                    Severity.ERROR,
                    f"tags must include '{expected_tag}'",
                    field="tags",
                )
            else:
                self.add_passed("difficulty tag present")

    @staticmethod
    def _is_ascii(value: str) -> bool:
        try:
            value.encode("ascii")
            return True
        except UnicodeEncodeError:
            return False
