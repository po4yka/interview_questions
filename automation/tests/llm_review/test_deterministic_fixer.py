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


def test_alias_string_coerced_to_list():
    """String aliases should be split into a normalized list."""

    note = """---
title: Sample
aliases: Retrofit Call Adapter / Продвинутый адаптер | Retrofit Adapter
created: 2024-01-01
updated: 2024-01-01
---
Body
"""

    issues = [
        ReviewIssue(
            severity="ERROR",
            message="ERROR:aliases must be a list",
            field="frontmatter",
        )
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made

    yaml_data, _ = load_frontmatter_text(result.revised_text)
    assert yaml_data["aliases"] == [
        "Retrofit Call Adapter",
        "Продвинутый адаптер",
        "Retrofit Adapter",
    ]


def test_remove_unresolved_related_links():
    """Unresolved related entries should be removed deterministically."""

    note = """---
title: Sample
related: [c-backend, c-retrofit]
created: 2024-01-01
updated: 2024-01-01
---
Body
"""

    issues = [
        ReviewIssue(
            severity="ERROR",
            message="ERROR:related link 'c-backend' cannot be resolved",
            field="frontmatter",
        )
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert "Removed unresolved related link 'c-backend'" in result.fixes_applied

    yaml_data, _ = load_frontmatter_text(result.revised_text)
    assert yaml_data["related"] == ["c-retrofit"]


def test_generic_type_backticks_message():
    """Generic type lint messages should trigger backtick wrapping."""

    note = """---
title: Sample
created: 2024-01-01
updated: 2024-01-01
---
We convert Retrofit responses into Result<T> for better ergonomics.
"""

    issues = [
        ReviewIssue(
            severity="ERROR",
            message=(
                "ERROR:Generic type 'Result<T>' not wrapped in backticks (will be "
                "interpreted as HTML tag). Use: `Result<T>`"
            ),
            field="content",
        )
    ]

    fixer = DeterministicFixer()
    result = fixer.fix(note, issues)

    assert result.changes_made
    assert "`Result<T>`" in result.revised_text
