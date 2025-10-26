from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils" / "src"))

try:
    import yaml  # type: ignore
except Exception:  # pylint: disable=broad-except
    yaml = None

from utils.yaml_loader import load_yaml  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = ROOT / "InterviewQuestions" / "10-Concepts"

ALLOWED_TOPICS = {
    "algorithms",
    "data-structures",
    "system-design",
    "android",
    "kotlin",
    "programming-languages",
    "architecture-patterns",
    "concurrency",
    "distributed-systems",
    "databases",
    "networking",
    "operating-systems",
    "security",
    "performance",
    "cloud",
    "testing",
    "devops-ci-cd",
    "tools",
    "debugging",
    "ui-ux-accessibility",
    "behavioral",
    "cs",
}

MOC_MAP = {
    "algorithms": "moc-algorithms",
    "data-structures": "moc-algorithms",
    "system-design": "moc-system-design",
    "android": "moc-android",
    "kotlin": "moc-kotlin",
    "programming-languages": "moc-cs",
    "architecture-patterns": "moc-architecture-patterns",
    "concurrency": "moc-cs",
    "distributed-systems": "moc-system-design",
    "databases": "moc-backend",
    "networking": "moc-system-design",
    "operating-systems": "moc-cs",
    "security": "moc-security",
    "performance": "moc-performance",
    "cloud": "moc-cloud",
    "testing": "moc-testing",
    "devops-ci-cd": "moc-devops",
    "tools": "moc-tools",
    "debugging": "moc-tools",
    "ui-ux-accessibility": "moc-android",
    "behavioral": "moc-cs",
    "cs": "moc-cs",
}

ID_PATTERN = re.compile(r"^(\d{8}-\d{6})$")


def normalize_date(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return str(value)


def main():
    concept_files = sorted(CONCEPT_DIR.glob("c-*.md"))
    changed = 0

    for path in concept_files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            header, body = text.split("\n---\n", 1)
        except ValueError:
            continue
        yaml_raw = header[3:]
        data = load_yaml(yaml_raw) or {}

        tags = data.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]

        topic = data.get("topic")
        if topic not in ALLOWED_TOPICS:
            topic = None
        if topic is None:
            for tag in tags:
                candidate = tag.split("/")[-1]
                if candidate in ALLOWED_TOPICS:
                    topic = candidate
                    break
        if topic is None:
            topic = "cs"
        data["topic"] = topic

        subtopics = data.get("subtopics")
        if not isinstance(subtopics, list) or not subtopics:
            subtopics = []
            for tag in tags:
                value = tag.split("/")[-1]
                if value in {topic, "concept"}:
                    continue
                subtopics.append(value)
            if not subtopics:
                subtopics = ["fundamentals"]
        data["subtopics"] = subtopics[:5]

        if data.get("question_kind") not in {"theory", "coding", "system-design", "android"}:
            data["question_kind"] = "theory"

        if data.get("difficulty") not in {"easy", "medium", "hard"}:
            data["difficulty"] = "medium"

        if data.get("original_language") not in {"en", "ru"}:
            data["original_language"] = "en"

        language_tags = data.get("language_tags")
        if not isinstance(language_tags, list) or not language_tags:
            data["language_tags"] = ["en", "ru"]

        if data.get("status") not in {"draft", "reviewed", "ready", "retired"}:
            data["status"] = "draft"

        if data.get("sources") is None:
            data["sources"] = []

        if data.get("related") is None:
            data["related"] = []

        expected_moc = MOC_MAP.get(topic)
        if expected_moc:
            data["moc"] = expected_moc

        raw_id = data.get("id")
        if isinstance(raw_id, str):
            cleaned = raw_id
            if raw_id.startswith("ivc-"):
                cleaned = raw_id[4:]
            elif raw_id.startswith("iv-"):
                cleaned = raw_id[3:]
            if ID_PATTERN.match(cleaned):
                data["id"] = cleaned
        if not isinstance(data.get("id"), str) or not ID_PATTERN.match(data["id"]):
            created = data.get("created")
            if isinstance(created, str) and re.match(r"\d{4}-\d{2}-\d{2}", created):
                data["id"] = created.replace("-", "") + "-000000"
            else:
                data["id"] = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        data["created"] = normalize_date(data.get("created")) or "2025-01-01"
        data["updated"] = normalize_date(data.get("updated")) or data["created"]

        aliases = data.get("aliases")
        if aliases is None:
            data["aliases"] = []
        elif isinstance(aliases, str):
            data["aliases"] = [aliases]

        data["tags"] = tags

        order = [
            "id",
            "title",
            "aliases",
            "summary",
            "topic",
            "subtopics",
            "question_kind",
            "difficulty",
            "original_language",
            "language_tags",
            "sources",
            "status",
            "moc",
            "related",
            "created",
            "updated",
            "tags",
        ]

        ordered_data = {}
        for key in order:
            if key in data:
                ordered_data[key] = data[key]
        for key in data:
            if key not in ordered_data:
                ordered_data[key] = data[key]

        if yaml is not None:
            yaml_text = yaml.safe_dump(ordered_data, sort_keys=False, allow_unicode=True)
        else:
            yaml_text = dump_yaml_manual(ordered_data)
        new_text = "---\n" + yaml_text + "---\n" + body
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1

    print(f"Updated {changed} concept notes out of {len(concept_files)}")


def dump_yaml_manual(data: dict) -> str:
    def format_scalar(value):
        if value is None:
            return "null"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        return json.dumps(str(value), ensure_ascii=False)

    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            elif all(isinstance(item, (str, int, float, bool)) or item is None for item in value):
                items = ", ".join(format_scalar(item) for item in value)
                lines.append(f"{key}: [{items}]")
            elif all(isinstance(item, dict) for item in value):
                lines.append(f"{key}:")
                for item in value:
                    lines.append("  -")
                    for subkey, subval in item.items():
                        lines.append(f"    {subkey}: {format_scalar(subval)}")
            else:
                items = ", ".join(format_scalar(item) for item in value)
                lines.append(f"{key}: [{items}]")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subval in value.items():
                lines.append(f"  {subkey}: {format_scalar(subval)}")
        else:
            lines.append(f"{key}: {format_scalar(value)}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
