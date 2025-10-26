from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils" / "src"))

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


def _listify(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalize_date(value) -> str:
    if value is None or value == "":
        return "2025-01-01"
    if isinstance(value, _dt.date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        return value
    return str(value)


def _dump_yaml(data: dict) -> str:
    def format_scalar(value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        return json.dumps(str(value), ensure_ascii=False)

    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            elif all(isinstance(item, (str, int, float, bool)) or item is None for item in value):
                rendered = ", ".join(format_scalar(item) for item in value)
                lines.append(f"{key}: [{rendered}]")
            else:
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append("  -")
                        for subkey, subval in item.items():
                            lines.append(f"    {subkey}: {format_scalar(subval)}")
                    else:
                        lines.append(f"  - {format_scalar(item)}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subval in value.items():
                lines.append(f"  {subkey}: {format_scalar(subval)}")
        else:
            lines.append(f"{key}: {format_scalar(value)}")
    return "\n".join(lines) + "\n"


def normalize_concepts():
    files = sorted(CONCEPT_DIR.glob("c-*.md"))
    updated = 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            header, body = text.split("\n---\n", 1)
        except ValueError:
            continue
        frontmatter = load_yaml(header[3:]) or {}

        tags = _listify(frontmatter.get("tags"))
        tags = [t for t in tags if t]

        topic = frontmatter.get("topic")
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

        subtopics = [s for s in _listify(frontmatter.get("subtopics")) if s]
        if not subtopics:
            for tag in tags:
                candidate = tag.split("/")[-1]
                if candidate not in {topic, "concept"}:
                    subtopics.append(candidate)
        if not subtopics:
            subtopics = ["fundamentals"]
        subtopics = list(dict.fromkeys(subtopics))[:3]

        question_kind = frontmatter.get("question_kind")
        if question_kind not in {"theory", "coding", "system-design", "android"}:
            question_kind = "theory"

        difficulty = frontmatter.get("difficulty")
        if difficulty not in {"easy", "medium", "hard"}:
            difficulty = "medium"

        original_language = frontmatter.get("original_language")
        if original_language not in {"en", "ru"}:
            original_language = "en"

        language_tags = _listify(frontmatter.get("language_tags")) or ["en", "ru"]

        status = frontmatter.get("status")
        if status not in {"draft", "reviewed", "ready", "retired"}:
            status = "draft"

        sources = frontmatter.get("sources")
        if isinstance(sources, list):
            normalized_sources = sources
        else:
            normalized_sources = []

        related = frontmatter.get("related")
        if isinstance(related, list):
            normalized_related = related
        else:
            normalized_related = []

        moc = MOC_MAP.get(topic, "moc-cs")

        raw_id = frontmatter.get("id")
        note_id = None
        if isinstance(raw_id, str):
            candidate = raw_id
            if raw_id.startswith("ivc-"):
                candidate = raw_id[4:]
            elif raw_id.startswith("iv-"):
                candidate = raw_id[3:]
            if ID_PATTERN.match(candidate):
                note_id = candidate
        if note_id is None:
            created_raw = frontmatter.get("created")
            if isinstance(created_raw, str) and re.match(r"\d{4}-\d{2}-\d{2}", created_raw):
                note_id = created_raw.replace("-", "") + "-000000"
            else:
                note_id = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")

        created = _normalize_date(frontmatter.get("created"))
        updated_date = _normalize_date(frontmatter.get("updated")) or created

        aliases = _listify(frontmatter.get("aliases"))

        if "concept" not in tags:
            tags.insert(0, "concept")
        diff_tag = f"difficulty/{difficulty}"
        if diff_tag not in tags:
            tags.append(diff_tag)
        tags = list(dict.fromkeys(tags))[:8]

        ordered = {
            "id": note_id,
            "title": frontmatter.get("title", ""),
            "aliases": aliases,
            "summary": frontmatter.get("summary", ""),
            "topic": topic,
            "subtopics": subtopics,
            "question_kind": question_kind,
            "difficulty": difficulty,
            "original_language": original_language,
            "language_tags": language_tags,
            "sources": normalized_sources,
            "status": status,
            "moc": moc,
            "related": normalized_related,
            "created": created,
            "updated": updated_date,
            "tags": tags,
        }

        yaml_text = _dump_yaml(ordered)
        new_text = "---\n" + yaml_text + "---\n" + body
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1

    print(f"Updated {updated} concept notes out of {len(files)}")


if __name__ == "__main__":
    normalize_concepts()
