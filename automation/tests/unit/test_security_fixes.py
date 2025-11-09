"""Test security fixes for path traversal and input validation."""

import pytest
from pathlib import Path

from obsidian_vault.utils import (
    safe_resolve_path,
    ensure_vault_exists,
    validate_choice,
)


class TestSafeResolvePath:
    """Test safe_resolve_path function prevents path traversal attacks."""

    def test_safe_path_within_base(self, tmp_path):
        """Test resolving safe path within base directory."""
        base = tmp_path / "vault"
        base.mkdir()

        # Create a subdirectory
        (base / "40-Android").mkdir()

        # Should succeed - path within base
        result = safe_resolve_path("40-Android", base)
        assert result == base / "40-Android"

    def test_path_traversal_blocked_simple(self, tmp_path):
        """Test that simple path traversal is blocked."""
        base = tmp_path / "vault"
        base.mkdir()

        # Should raise ValueError - tries to go outside base
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            safe_resolve_path("../etc/passwd", base)

    def test_path_traversal_blocked_complex(self, tmp_path):
        """Test that complex path traversal is blocked."""
        base = tmp_path / "vault"
        base.mkdir()
        (base / "InterviewQuestions").mkdir()

        # Should raise ValueError - tries to escape vault
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            safe_resolve_path("InterviewQuestions/../../etc/passwd", base)

    def test_path_traversal_blocked_absolute(self, tmp_path):
        """Test that absolute paths outside base are blocked."""
        base = tmp_path / "vault"
        base.mkdir()

        # Should raise ValueError - absolute path outside base
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            safe_resolve_path("/etc/passwd", base)

    def test_safe_nested_path(self, tmp_path):
        """Test resolving nested safe paths."""
        base = tmp_path / "vault"
        base.mkdir()
        (base / "InterviewQuestions").mkdir()
        (base / "InterviewQuestions" / "40-Android").mkdir()

        # Should succeed - nested path within base
        result = safe_resolve_path("InterviewQuestions/40-Android", base)
        assert result == base / "InterviewQuestions" / "40-Android"

    def test_symlink_attack_blocked(self, tmp_path):
        """Test that symlink attacks are blocked."""
        base = tmp_path / "vault"
        base.mkdir()

        # Create a directory outside base
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret data")

        # Create a symlink inside base pointing outside
        symlink_path = base / "malicious_link"
        symlink_path.symlink_to(outside)

        # Should raise ValueError - resolves outside base
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            safe_resolve_path("malicious_link/secret.txt", base)


class TestEnsureVaultExists:
    """Test ensure_vault_exists function."""

    def test_vault_exists(self, tmp_path):
        """Test when vault directory exists."""
        repo_root = tmp_path
        (repo_root / "InterviewQuestions").mkdir()

        # Should return vault path
        vault_dir = ensure_vault_exists(repo_root)
        assert vault_dir == repo_root / "InterviewQuestions"

    def test_vault_missing(self, tmp_path):
        """Test when vault directory is missing."""
        repo_root = tmp_path

        # Should raise ValueError
        with pytest.raises(ValueError, match="InterviewQuestions directory not found"):
            ensure_vault_exists(repo_root)


class TestValidateChoice:
    """Test validate_choice function for input validation."""

    def test_valid_choice_case_insensitive(self):
        """Test valid choice with case-insensitive matching."""
        result = validate_choice("GEXF", {"gexf", "json", "csv"})
        assert result == "gexf"

    def test_valid_choice_exact_match(self):
        """Test valid choice with exact match."""
        result = validate_choice("json", {"gexf", "json", "csv"})
        assert result == "json"

    def test_invalid_choice(self):
        """Test invalid choice raises ValueError."""
        with pytest.raises(ValueError, match="Invalid choice 'invalid'"):
            validate_choice("invalid", {"gexf", "json", "csv"})

    def test_valid_choice_case_sensitive(self):
        """Test valid choice with case-sensitive matching."""
        result = validate_choice("UPPERCASE", {"UPPERCASE", "lowercase"}, case_sensitive=True)
        assert result == "UPPERCASE"

    def test_invalid_choice_case_sensitive(self):
        """Test invalid choice with case-sensitive matching."""
        with pytest.raises(ValueError, match="Invalid choice 'uppercase'"):
            validate_choice("uppercase", {"UPPERCASE", "lowercase"}, case_sensitive=True)

    def test_choice_with_whitespace(self):
        """Test that whitespace is stripped in case-insensitive mode."""
        result = validate_choice("  gexf  ", {"gexf", "json", "csv"})
        assert result == "gexf"

    def test_algorithm_validation(self):
        """Test community detection algorithm validation."""
        # Valid algorithms
        assert validate_choice("louvain", {"louvain", "greedy", "label_propagation"}) == "louvain"
        assert validate_choice("GREEDY", {"louvain", "greedy", "label_propagation"}) == "greedy"

        # Invalid algorithm
        with pytest.raises(ValueError, match="Invalid choice 'invalid_algo'"):
            validate_choice("invalid_algo", {"louvain", "greedy", "label_propagation"})

    def test_export_format_validation(self):
        """Test export format validation."""
        # Valid formats
        assert validate_choice("GEXF", {"gexf", "graphml", "json", "csv"}) == "gexf"
        assert validate_choice("json", {"gexf", "graphml", "json", "csv"}) == "json"

        # Invalid format
        with pytest.raises(ValueError, match="Invalid choice 'xml'"):
            validate_choice("xml", {"gexf", "graphml", "json", "csv"})


class TestIntegration:
    """Integration tests combining security features."""

    def test_safe_validation_workflow(self, tmp_path):
        """Test complete safe validation workflow."""
        # Setup vault structure
        repo_root = tmp_path
        vault_dir = repo_root / "InterviewQuestions"
        vault_dir.mkdir()

        android_dir = vault_dir / "40-Android"
        android_dir.mkdir()

        note_file = android_dir / "q-test--android--easy.md"
        note_file.write_text("# Test note")

        # 1. Ensure vault exists
        checked_vault = ensure_vault_exists(repo_root)
        assert checked_vault == vault_dir

        # 2. Safely resolve path to note
        safe_note_path = safe_resolve_path("40-Android/q-test--android--easy.md", vault_dir)
        assert safe_note_path == note_file
        assert safe_note_path.exists()

        # 3. Validate format choice
        fmt = validate_choice("JSON", {"gexf", "json", "csv"})
        assert fmt == "json"

    def test_attack_scenarios_blocked(self, tmp_path):
        """Test that various attack scenarios are blocked."""
        repo_root = tmp_path
        vault_dir = repo_root / "InterviewQuestions"
        vault_dir.mkdir()

        # Attack 1: Path traversal to /etc/passwd
        with pytest.raises(ValueError):
            safe_resolve_path("../../../etc/passwd", vault_dir)

        # Attack 2: Path traversal to parent directory
        with pytest.raises(ValueError):
            safe_resolve_path("../sensitive_file.txt", vault_dir)

        # Attack 3: Absolute path outside vault
        with pytest.raises(ValueError):
            safe_resolve_path("/tmp/malicious", vault_dir)

        # Attack 4: Invalid format injection
        with pytest.raises(ValueError):
            validate_choice("json; rm -rf /", {"gexf", "json"})
