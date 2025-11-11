from obsidian_vault.validators.code_format_validator import CodeFormatValidator


def _run_validator(content: str):
    validator = CodeFormatValidator(
        content=content, frontmatter={}, path="note.md", taxonomy=None
    )
    return validator.validate()


def test_type_name_warning_ignored_in_heading():
    """Headings containing words like 'Short' should not trigger warnings."""

    content = "## Short Version\nBody text here."

    summary = _run_validator(content)

    assert all("Short" not in issue.message for issue in summary.issues)


def test_type_name_warning_still_reported_in_body():
    """Type names in regular text should continue to trigger warnings."""

    content = "In Kotlin, Short is a 16-bit signed integer."

    summary = _run_validator(content)

    assert any("Short" in issue.message for issue in summary.issues)
