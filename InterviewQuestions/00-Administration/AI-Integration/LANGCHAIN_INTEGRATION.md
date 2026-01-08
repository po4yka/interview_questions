---\
---\

# LangChain Integration for AI Validation

This document describes the LangChain-based alternative to the direct Ollama/OpenAI validator implementation.

## Overview

The `LangChainValidator` provides the same AI-powered validation features as `LocalAIValidator` but uses LangChain's abstractions for better modularity, caching, and structured outputs.

## Features

### Core Capabilities
- Auto-translation (EN ↔ RU) with structured output parsing
- Code quality checking with Pydantic models
- Answer completeness evaluation with ratings
- Built-in retry mechanisms via LangChain
- `Response` caching (InMemoryCache by default)
- Support for both Ollama and OpenAI-compatible APIs (LM Studio)

### Key Improvements Over LocalAIValidator
1. **Structured Outputs**: Uses Pydantic models for reliable parsing
2. **Caching**: Built-in response caching to reduce API calls
3. **Retry Logic**: Automatic retry on failures
4. **Better Abstractions**: Prompt templates and chain composition
5. **Fallback Parsing**: Gracefully handles both structured and unstructured responses

## Installation

### Required Dependencies

```bash
pip install langchain>=0.3.0
pip install langchain-community>=0.3.0
pip install langchain-ollama>=0.2.0      # For Ollama
pip install langchain-openai>=0.2.0      # For LM Studio/OpenAI
```

Or install from pyproject.toml:

```bash
pip install -e .
```

### Optional: Ollama Setup

```bash
brew install ollama  # macOS
ollama pull qwen2.5-coder:7b-instruct
ollama serve
```

## Usage

### Command Line

#### Basic Translation with LangChain
```bash
python validate_note.py --all --ai-translate --use-langchain
```

#### Full AI Features with LangChain
```bash
python validate_note.py --all \
    --ai-translate \
    --ai-enhance \
    --use-langchain \
    --ai-model qwen2.5-coder:7b-instruct
```

#### Using LM Studio
```bash
python validate_note.py --all \
    --ai-translate \
    --use-langchain \
    --lm-studio-url http://192.168.1.107:11435
```

#### Without LangChain (Original Implementation)
```bash
python validate_note.py --all --ai-translate
# Note: no --use-langchain flag
```

### Python API

```python
from validators import LangChainValidator

# Create validator
validator = LangChainValidator(
    content=note_content,
    frontmatter=frontmatter,
    filepath=filepath,
    model_name="qwen2.5-coder:7b-instruct",
    enable_fixes=True,         # Code review + completeness check
    auto_translate=True,       # EN ↔ RU translation
    use_cache=True             # Enable caching
)

# Run validation
issues = validator.validate()

# Apply fixes
for fix in validator.fixes:
    new_content, new_frontmatter = fix.fix_function()
```

## Architecture

### Pydantic Models

#### TranslationResult
```python
class TranslationResult(BaseModel):
    translated_text: str
```

Ensures translations are properly extracted from LLM responses.

#### CodeReviewResult
```python
class CodeIssue(BaseModel):
    issue: str
    severity: str  # "critical", "warning", "info"

class CodeReviewResult(BaseModel):
    issues: List[CodeIssue]
    summary: str
```

Structured code review with typed issue severity.

#### CompletenessResult
```python
class CompletenessResult(BaseModel):
    rating: int       # 1-5 scale
    explanation: str
```

Structured answer quality ratings.

### Prompt Templates

All prompts use LangChain's `PromptTemplate` or `ChatPromptTemplate` for:
- Variable substitution
- Consistent formatting
- Reusability
- Format instructions injection for Pydantic parsing

Example:

```python
prompt = PromptTemplate(
    template="Translate from {from_lang} to {to_lang}:\n{source_text}",
    input_variables=["from_lang", "to_lang", "source_text"]
)
```

### Chain Composition

LangChain chains combine prompts, models, and parsers:

```python
parser = PydanticOutputParser(pydantic_object=TranslationResult)
chain = prompt | llm | parser
result = chain.invoke({"from_lang": "English", "to_lang": "Russian", ...})
```

### Caching

By default, uses `InMemoryCache` to cache LLM responses:

```python
from langchain.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

set_llm_cache(InMemoryCache())
```

For persistent caching, can use `SQLiteCache`:

```python
from langchain_community.cache import SQLiteCache
set_llm_cache(SQLiteCache(database_path=".langchain.db"))
```

### Fallback Mechanism

If structured parsing fails, falls back to simple string parsing:

```python
try:
    result = structured_chain.invoke(inputs)
    return result.translated_text
except Exception:
    # Fallback to unstructured parsing
    simple_chain = prompt | llm | StrOutputParser()
    return simple_chain.invoke(inputs)
```

## File Structure

```
validators/
├── base.py                      # BaseValidator, Severity, AutoFix
├── local_ai_validator.py        # Original direct Ollama/OpenAI implementation
├── langchain_validator.py       # NEW: LangChain-based implementation
└── __init__.py                  # Exports both validators

validate_note.py                 # UPDATED: Added --use-langchain flag
pyproject.toml                   # UPDATED: Added LangChain dependencies
```

## Comparison: LocalAIValidator Vs LangChainValidator

| Feature | LocalAIValidator | LangChainValidator |
|---------|-----------------|-------------------|
| Translation | Direct API calls | Prompt templates + Pydantic |
| Code Review | Regex parsing | Structured CodeReviewResult |
| Completeness | `String` matching | Structured CompletenessResult |
| Caching | None | Built-in InMemoryCache |
| Retry Logic | Manual | Automatic via LangChain |
| Fallback | None | Graceful degradation |
| Dependencies | ollama, openai | langchain, langchain-ollama/openai |

## Example Outputs

### Translation Issue
```
WARNING: Russian answer translation missing. AI can auto-translate (LangChain).

Available Fix:
Auto-translate Answer (EN) -> Ответ (RU) using LangChain
```

### Code Review Issue
```
WARNING: AI code review (LangChain) found issues: GlobalScope usage detected;
Missing error handling in coroutine
```

### Completeness Issue
```
INFO: AI suggests answer could be improved (LangChain): 3/5 - Answer lacks
concrete code examples and doesn't cover edge cases
```

## Performance Considerations

### Caching Benefits
- First run: 5-10 seconds per translation
- Cached runs: <100ms (instant retrieval)

### Memory Usage
- InMemoryCache: ~10-50 MB for typical vault
- SQLiteCache: Disk-based, no memory overhead

### Model Comparison
| Model | Speed | Quality | Memory |
|-------|-------|---------|--------|
| qwen2.5-coder:7b | Fast | Good | 8 GB |
| qwen2.5-coder:14b | Medium | Better | 16 GB |
| qwen2.5-coder:32b | Slow | Best | 32 GB |

## Troubleshooting

### Import Errors
```
ImportError: No module named 'langchain_ollama'
```

Solution:
```bash
pip install langchain-ollama>=0.2.0
```

### Ollama Connection Failed
```
Error: Could not connect to Ollama
```

Solution:
```bash
ollama serve  # Start Ollama server
ollama list   # Verify model is available
```

### Structured Output Parsing Failed
LangChain validator automatically falls back to string parsing. Check logs:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### LM Studio Connection Issues
```
Error: Connection refused to http://192.168.1.107:11435
```

Solution:
1. Verify LM Studio is running
2. Check server URL in LM Studio settings
3. Ensure model is loaded
4. Test: `curl http://192.168.1.107:11435/v1/models`

## Future Enhancements

Potential improvements:
1. SQLiteCache for persistent caching
2. Streaming support for long translations
3. Batch processing for multiple files
4. Custom callbacks for progress tracking
5. Fine-tuned models for domain-specific terminology
6. Multi-agent workflows for complex reviews

## Contributing

When contributing to LangChain integration:
1. Keep backward compatibility with LocalAIValidator
2. Use Pydantic models for all structured outputs
3. Implement fallback mechanisms for robustness
4. Add docstrings with examples
5. Test with both Ollama and LM Studio

## License

Same as parent project.
