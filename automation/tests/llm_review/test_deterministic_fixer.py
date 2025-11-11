from __future__ import annotations

from datetime import datetime

from obsidian_vault.llm_review.deterministic_fixer import DeterministicFixer
from obsidian_vault.llm_review.state import ReviewIssue
from obsidian_vault.utils.frontmatter import load_frontmatter_text


def test_future_timestamp_fix_clamps_to_today():
    """Deterministic fixer should correct future-dated timestamps."""

    note = """---
title: Sample
created: 2999-01-01
updated: 2999-01-02
---
Content
"""

    issues = [
        ReviewIssue(
            severity="WARNING",
            message="[Metadata] created timestamp is in the future",
            field="frontmatter",
        ),
        ReviewIssue(
            severity="WARNING",
            message="[Metadata] updated timestamp is in the future",
            field="frontmatter",
        ),
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert any("Corrected future timestamps" in desc for desc in result.fixes_applied)
    # Both issue messages should be marked as fixed
    assert set(result.issues_fixed) == {
        "[Metadata] created timestamp is in the future",
        "[Metadata] updated timestamp is in the future",
    }

    yaml_data, _ = load_frontmatter_text(result.revised_text)
    today = datetime.now().date().strftime("%Y-%m-%d")

    assert yaml_data["created"] == today
    assert yaml_data["updated"] == today


def test_type_name_backticks_skip_urls():
    """Type name wrapping should not alter URLs containing the name."""

    note = """---
title: Sample
created: 2024-01-01
updated: 2024-01-01
---
See Bundle docs at https://developer.android.com/reference/android/os/Bundle.
Parcelable details are similar.
"""

    issues = [
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Bundle' found without backticks.",
            field="content",
        ),
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Parcelable' found without backticks.",
            field="content",
        ),
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert "`Bundle`" in result.revised_text
    assert "`Parcelable`" in result.revised_text
    assert "https://developer.android.com/reference/android/os/Bundle" in result.revised_text


def test_type_name_backticks_plural_variants():
    """Plural mentions of type names should also gain backticks."""

    note = """---
title: Sample
created: 2024-01-01
updated: 2024-01-01
---
Legacy applications juggle Activities across modules while background Services
handle work in the foreground and background simultaneously.
"""

    issues = [
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Activity' found without backticks.",
            field="content",
        ),
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Service' found without backticks.",
            field="content",
        ),
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert "`Activities`" in result.revised_text
    assert "`Services`" in result.revised_text


def test_normalizes_optional_version_headings():
    """Headings for optional versions should be normalized deterministically."""

    note = """---
title: Sample
created: 2024-01-01
updated: 2024-01-01
---
### Краткая версия
RU short body.
### Подробная версия
RU detailed body.
### Short Version
EN short body mentioning Short type in the flow.
### Detailed version
EN detailed body.
"""

    issues = [
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Short' found without backticks.",
            field="content",
        )
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert "## Краткая Версия" in result.revised_text
    assert "## Подробная Версия" in result.revised_text
    assert "## Short Version" in result.revised_text
    assert "## Detailed Version" in result.revised_text
    assert "`Short` type" in result.revised_text
    assert "## `Short` Version" not in result.revised_text


def test_normalizes_optional_heading_synonyms():
    """Synonym headings such as 'Краткий вариант' should be normalized."""

    note = """---
title: Sample
created: 2024-01-01
updated: 2024-01-01
---
### Краткий вариант
RU short body.
### Подробный вариант
RU detailed body.
### Short answer
EN short body mentioning Short type reference.
### Detailed answer
EN detailed body.
"""

    issues = [
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Short' found without backticks.",
            field="content",
        )
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert "## Краткая Версия" in result.revised_text
    assert "## Подробная Версия" in result.revised_text
    assert "## Short Version" in result.revised_text
    assert "## Detailed Version" in result.revised_text
    assert "## `Short` Version" not in result.revised_text


def test_type_name_not_wrapped_in_setext_heading():
    """Setext headings like 'Short Version' + underline must stay unwrapped."""

    note = """---
title: Sample
created: 2024-01-01
updated: 2024-01-01
---
Short Version
-------------
Detailed guidance on the Short primitive mirrors the Kotlin `Short` type.
"""

    issues = [
        ReviewIssue(
            severity="WARNING",
            message="WARNING:Type name 'Short' found without backticks.",
            field="content",
        )
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    lines = result.revised_text.splitlines()
    heading_line = next(line for line in lines if "Short Version" in line)
    assert "`Short`" not in heading_line
    assert "the `Short` primitive" in result.revised_text
