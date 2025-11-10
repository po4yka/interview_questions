"""Unit tests for text sanitization utility."""

import pytest

from obsidian_vault.utils import sanitize_text_for_yaml


class TestTextSanitization:
    """Test suite for sanitize_text_for_yaml function."""

    def test_removes_null_bytes(self):
        """Test that null bytes are removed from text."""
        text_with_null = "title: Test\x00Note"
        expected = "title: TestNote"
        assert sanitize_text_for_yaml(text_with_null) == expected

    def test_removes_multiple_null_bytes(self):
        """Test that multiple null bytes are removed."""
        text_with_nulls = "hello\x00world\x00test\x00"
        expected = "helloworldtest"
        assert sanitize_text_for_yaml(text_with_nulls) == expected

    def test_preserves_valid_whitespace(self):
        """Test that valid whitespace (tab, newline, space) is preserved."""
        text = "title: Test\n\ttag: kotlin\r\n  nested: value"
        # Should preserve \n, \t, \r, and spaces
        assert sanitize_text_for_yaml(text) == text

    def test_removes_control_characters(self):
        """Test that invalid control characters are removed."""
        # Test various control characters
        text_with_controls = "text\x01with\x02controls\x08and\x0bnull\x00"
        expected = "textwithcontrolsandnull"
        assert sanitize_text_for_yaml(text_with_controls) == expected

    def test_preserves_unicode_content(self):
        """Test that valid Unicode content is preserved."""
        text = "title: Тест\nalias: テスト\ncontent: 测试"
        # Should preserve all Unicode characters
        assert sanitize_text_for_yaml(text) == text

    def test_handles_empty_string(self):
        """Test that empty string is handled correctly."""
        assert sanitize_text_for_yaml("") == ""

    def test_handles_none(self):
        """Test that None is handled correctly."""
        assert sanitize_text_for_yaml(None) is None

    def test_handles_yaml_frontmatter_with_null_bytes(self):
        """Test sanitization of YAML frontmatter with null bytes."""
        text_with_null = """---
id: "test\x00123"
title: "Test\x00 Title"
tags: [kotlin\x00, android]
---

# Content

This is test\x00 content.
"""
        expected = """---
id: "test123"
title: "Test Title"
tags: [kotlin, android]
---

# Content

This is test content.
"""
        assert sanitize_text_for_yaml(text_with_null) == expected

    def test_real_world_llm_output_with_null_bytes(self):
        """Test sanitization of realistic LLM output with embedded null bytes."""
        llm_output = """---
title: Performance Optimization\x00
topic: android
difficulty: medium
---

# Question (EN)

How\x00 do you optimize Android app performance?

## Answer (EN)

Use profiling\x00 tools and follow best practices.
"""
        # After sanitization, null bytes should be removed
        result = sanitize_text_for_yaml(llm_output)
        assert "\x00" not in result
        assert "Performance Optimization" in result
        assert "android" in result
        assert "How do you optimize" in result

    def test_position_71_null_byte_scenario(self):
        """Test the specific scenario from the error: null byte at position 71."""
        # Create text with null byte at position 71
        text = "---\ntitle: Test Note\nalias: [Test]\ntopic: kotlin\ndifficulty: ea\x00sy\n---\n"
        result = sanitize_text_for_yaml(text)
        # Verify no null bytes remain
        assert "\x00" not in result
        # Verify YAML structure is preserved
        assert "difficulty: easy" in result

    def test_handles_mixed_invalid_characters(self):
        """Test handling of multiple types of invalid characters."""
        text = "title: Test\x00\x01\x02\x08\x0b\x0c\x1fNote"
        expected = "title: TestNote"
        assert sanitize_text_for_yaml(text) == expected
