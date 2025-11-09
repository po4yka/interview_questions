"""Smart Code Parity Checking - Ignore identifier names, compare structure.

PHASE 3 FIX: This module provides smarter code parity checking that doesn't
flag cosmetic differences like identifier names.

Problem Example:
- EN code: class DataPipeline { fun process() {} }
- RU code: class DataPipelineRu { fun process() {} }
- Parity check flags this as a mismatch
- Fixer renames DataPipelineRu → DataPipeline (wastes iteration)

Solution:
- Normalize code by replacing identifiers with placeholders
- Compare structure (class/fun/val), not names
- Allow different identifiers between RU/EN (localization is OK)
- Only flag actual semantic differences

Example:
- EN: class Foo { fun bar() { return 42 } }
- RU: class Фу { fun бар() { return 42 } }
- After normalization: Both become "class CLASS { fun FUNC() { return 42 } }"
- Result: PARITY OK (structure identical)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from loguru import logger


@dataclass
class CodeBlock:
    """Represents a code block with language and content."""

    language: str  # kotlin, python, java, etc.
    content: str
    is_normalized: bool = False


@dataclass
class CodeParityResult:
    """Result of comparing two code blocks."""

    is_equivalent: bool
    structure_matches: bool
    semantic_differences: list[str]  # Actual differences (not cosmetic)
    cosmetic_differences: list[str]  # Identifier name differences (OK)


class SmartCodeParityChecker:
    """Checks code parity while ignoring identifier names.

    This prevents wasted iterations on renaming classes/functions to
    match between EN and RU when the structure is identical.
    """

    def __init__(self):
        """Initialize smart code parity checker."""
        pass

    def normalize_kotlin_code(self, code: str) -> str:
        """Normalize Kotlin code by replacing identifiers with placeholders.

        This allows comparing code structure while ignoring naming differences.

        Args:
            code: Kotlin code to normalize

        Returns:
            Normalized code with placeholder identifiers
        """
        normalized = code

        # Replace class names: class FooBar → class CLASS
        normalized = re.sub(
            r'\bclass\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'class CLASS',
            normalized
        )

        # Replace object names: object FooBar → object OBJECT
        normalized = re.sub(
            r'\bobject\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'object OBJECT',
            normalized
        )

        # Replace function names: fun fooBar → fun FUNC
        normalized = re.sub(
            r'\bfun\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'fun FUNC',
            normalized
        )

        # Replace val/var names: val fooBar → val VAL / var fooBar → var VAR
        normalized = re.sub(
            r'\bval\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'val VAL',
            normalized
        )
        normalized = re.sub(
            r'\bvar\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'var VAR',
            normalized
        )

        # Replace data class names: data class FooBar → data class CLASS
        normalized = re.sub(
            r'\bdata\s+class\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'data class CLASS',
            normalized
        )

        # Replace sealed class names: sealed class FooBar → sealed class CLASS
        normalized = re.sub(
            r'\bsealed\s+class\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'sealed class CLASS',
            normalized
        )

        return normalized

    def normalize_python_code(self, code: str) -> str:
        """Normalize Python code by replacing identifiers.

        Args:
            code: Python code to normalize

        Returns:
            Normalized code
        """
        normalized = code

        # Replace class names: class FooBar: → class CLASS:
        normalized = re.sub(
            r'\bclass\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'class CLASS',
            normalized
        )

        # Replace function names: def foo_bar → def FUNC
        normalized = re.sub(
            r'\bdef\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'def FUNC',
            normalized
        )

        return normalized

    def normalize_java_code(self, code: str) -> str:
        """Normalize Java code by replacing identifiers.

        Args:
            code: Java code to normalize

        Returns:
            Normalized code
        """
        normalized = code

        # Replace class names: class FooBar → class CLASS
        normalized = re.sub(
            r'\bclass\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'class CLASS',
            normalized
        )

        # Replace interface names: interface FooBar → interface INTERFACE
        normalized = re.sub(
            r'\binterface\s+[A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*',
            'interface INTERFACE',
            normalized
        )

        # Replace method names (simplified): public void fooBar → public void FUNC
        # Note: This is simplistic and may not catch all cases
        normalized = re.sub(
            r'(\b(?:public|private|protected|static|final|void|int|String|boolean|long|double)\s+)+([A-Za-zА-Яа-я_][A-Za-zА-Яа-я0-9_]*)\s*\(',
            lambda m: m.group(1) + 'FUNC(',
            normalized
        )

        return normalized

    def normalize_code(self, code: str, language: str) -> str:
        """Normalize code based on language.

        Args:
            code: Code to normalize
            language: Programming language (kotlin, python, java, etc.)

        Returns:
            Normalized code
        """
        language_lower = language.lower()

        if language_lower in ["kotlin", "kt"]:
            return self.normalize_kotlin_code(code)
        elif language_lower in ["python", "py"]:
            return self.normalize_python_code(code)
        elif language_lower in ["java"]:
            return self.normalize_java_code(code)
        else:
            # For unsupported languages, return as-is
            logger.debug(f"No normalization available for language: {language}")
            return code

    def compare_code_blocks(
        self, en_code: str, ru_code: str, language: str
    ) -> CodeParityResult:
        """Compare two code blocks for structural equivalence.

        Ignores identifier names and focuses on code structure.

        Args:
            en_code: English code block
            ru_code: Russian code block
            language: Programming language

        Returns:
            CodeParityResult with comparison details
        """
        # Normalize both code blocks
        en_normalized = self.normalize_code(en_code, language)
        ru_normalized = self.normalize_code(ru_code, language)

        # Compare normalized versions
        structure_matches = (en_normalized == ru_normalized)

        # If normalized versions match, code is equivalent
        if structure_matches:
            # Check for cosmetic differences (identifier names)
            cosmetic_diffs = []
            if en_code != ru_code:
                cosmetic_diffs.append(
                    "Identifier names differ (EN/RU localization), but structure is identical"
                )

            return CodeParityResult(
                is_equivalent=True,
                structure_matches=True,
                semantic_differences=[],
                cosmetic_differences=cosmetic_diffs,
            )

        # If normalized versions differ, find semantic differences
        semantic_diffs = self._find_semantic_differences(
            en_normalized, ru_normalized, language
        )

        return CodeParityResult(
            is_equivalent=False,
            structure_matches=False,
            semantic_differences=semantic_diffs,
            cosmetic_differences=[],
        )

    def _find_semantic_differences(
        self, en_normalized: str, ru_normalized: str, language: str
    ) -> list[str]:
        """Find semantic differences between normalized code blocks.

        Args:
            en_normalized: Normalized EN code
            ru_normalized: Normalized RU code
            language: Programming language

        Returns:
            List of semantic differences
        """
        differences = []

        # Compare line counts
        en_lines = [line.strip() for line in en_normalized.split('\n') if line.strip()]
        ru_lines = [line.strip() for line in ru_normalized.split('\n') if line.strip()]

        if len(en_lines) != len(ru_lines):
            differences.append(
                f"Line count differs: EN has {len(en_lines)} lines, RU has {len(ru_lines)} lines"
            )

        # Compare structure keywords
        en_keywords = self._extract_keywords(en_normalized, language)
        ru_keywords = self._extract_keywords(ru_normalized, language)

        if en_keywords != ru_keywords:
            differences.append(
                f"Structure keywords differ: EN has {en_keywords}, RU has {ru_keywords}"
            )

        # If no specific differences found but codes don't match
        if not differences:
            differences.append(
                "Code structure differs in ways not easily categorized (possibly whitespace, comments, or minor syntax)"
            )

        return differences

    def _extract_keywords(self, code: str, language: str) -> dict[str, int]:
        """Extract and count structural keywords from code.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Dict mapping keywords to their counts
        """
        keywords = {}

        if language.lower() in ["kotlin", "kt"]:
            kotlin_keywords = [
                "class", "fun", "val", "var", "if", "else", "when",
                "for", "while", "return", "object", "data", "sealed"
            ]
            for keyword in kotlin_keywords:
                pattern = r'\b' + keyword + r'\b'
                count = len(re.findall(pattern, code))
                if count > 0:
                    keywords[keyword] = count

        elif language.lower() in ["python", "py"]:
            python_keywords = [
                "class", "def", "if", "else", "elif", "for", "while",
                "return", "import", "from"
            ]
            for keyword in python_keywords:
                pattern = r'\b' + keyword + r'\b'
                count = len(re.findall(pattern, code))
                if count > 0:
                    keywords[keyword] = count

        return keywords

    def should_ignore_difference(self, result: CodeParityResult) -> bool:
        """Determine if code differences should be ignored.

        Args:
            result: CodeParityResult from comparison

        Returns:
            True if differences are cosmetic and should be ignored
        """
        # If structure matches, ignore cosmetic differences
        if result.structure_matches:
            return True

        # If only cosmetic differences (no semantic differences)
        if len(result.semantic_differences) == 0 and len(result.cosmetic_differences) > 0:
            return True

        return False

    def format_rules_for_prompt(self) -> str:
        """Format code parity rules for inclusion in fixer agent prompt.

        Returns:
            Formatted string with smart code parity rules
        """
        return """
SMART CODE PARITY RULES (PHASE 3 FIX - FOLLOW EXACTLY):

1. CODE STRUCTURE VS. CODE NAMES:
   - Structure: class/fun/val keywords, logic flow, control structures
   - Names: Class names, function names, variable names
   - RULE: Structure MUST match, names CAN differ (localization is OK)

2. ALLOWED DIFFERENCES:
   ✓ Different class names (DataPipeline vs DataPipelineRu)
   ✓ Different function names (processData vs processarDatos)
   ✓ Different variable names (result vs результат)
   ✓ Localized comments (// English comment vs // Русский комментарий)

3. NOT ALLOWED DIFFERENCES:
   ✗ Different number of classes
   ✗ Different function signatures (different parameters)
   ✗ Different logic flow (if/else structure differs)
   ✗ Missing code blocks in one language

4. EXAMPLES:

   CORRECT (Structure matches, names differ):
   EN: class UserService { fun getUser(id: Int): User { ... } }
   RU: class СервисПользователя { fun получитьПользователя(id: Int): User { ... } }
   → IGNORE THIS DIFFERENCE (localization is OK)

   INCORRECT (Structure differs):
   EN: class UserService { fun getUser(id: Int): User { ... } }
   RU: class UserService { fun getUser(id: String): User { ... } }  ← Different parameter type!
   → FIX THIS DIFFERENCE (semantic mismatch)

5. WHEN TO RENAME IDENTIFIERS:
   - NEVER rename just to match EN/RU identifier names
   - Only rename if it fixes an actual error or improves clarity
   - Prefer keeping localized names in RU examples

6. WHEN TO FLAG PARITY ISSUES:
   - Different number of code examples
   - Different logic or structure
   - Missing code blocks
   - DO NOT flag identifier name differences
""".strip()
