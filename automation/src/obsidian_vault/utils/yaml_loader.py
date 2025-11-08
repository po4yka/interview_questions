"""Minimal YAML loader with optional PyYAML support."""

from __future__ import annotations

from typing import Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None


def load_yaml(text: str) -> dict:
    """Load YAML frontmatter, falling back to a lightweight parser."""

    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except Exception:
            return {}
        return data or {}
    return _simple_yaml_parse(text.splitlines())


def _simple_yaml_parse(lines: list[str]) -> dict[str, Any]:
    """Parse a limited subset of YAML (sufficient for the vault schema)."""

    result: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            i = _consume_block_value(lines, i, key, result, indent=len(raw) - len(raw.lstrip()))
        else:
            result[key] = _coerce_scalar(value)
    return result


def _consume_block_value(
    lines: list[str], index: int, key: str, result: dict[str, Any], indent: int
) -> int:
    items: list[Any] = []
    temp_index = index
    while temp_index < len(lines):
        raw = lines[temp_index]
        leading = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if not stripped:
            temp_index += 1
            continue
        if leading < indent or not stripped.startswith("-"):
            break
        entry = stripped[1:].strip()
        temp_index += 1
        if not entry:
            obj, temp_index = _consume_nested_dict(lines, temp_index, indent + 2)
            items.append(obj)
            continue
        if ":" in entry:
            nested_key, nested_val = entry.split(":", 1)
            nested_dict = {nested_key.strip(): _coerce_scalar(nested_val.strip())}
            temp_index = _consume_additional_kv(lines, temp_index, nested_dict, indent + 2)
            items.append(nested_dict)
        else:
            items.append(_coerce_scalar(entry))
    result[key] = items
    return temp_index


def _consume_nested_dict(lines: list[str], index: int, indent: int):
    obj: dict[str, Any] = {}
    temp_index = index
    while temp_index < len(lines):
        raw = lines[temp_index]
        leading = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if not stripped:
            temp_index += 1
            continue
        if leading < indent or ":" not in stripped:
            break
        key, value = stripped.split(":", 1)
        obj[key.strip()] = _coerce_scalar(value.strip())
        temp_index += 1
    return obj, temp_index


def _consume_additional_kv(
    lines: list[str], index: int, accumulator: dict[str, Any], indent: int
) -> int:
    temp_index = index
    while temp_index < len(lines):
        raw = lines[temp_index]
        leading = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if not stripped:
            temp_index += 1
            continue
        if leading < indent or ":" not in stripped:
            break
        key, value = stripped.split(":", 1)
        accumulator[key.strip()] = _coerce_scalar(value.strip())
        temp_index += 1
    return temp_index


def _coerce_scalar(value: str):
    if not value:
        return ""
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_coerce_scalar(item.strip()) for item in inner.split(",")]
    if value.isdigit():
        return int(value)
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value
