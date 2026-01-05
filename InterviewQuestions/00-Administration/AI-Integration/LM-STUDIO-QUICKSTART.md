---
---

# LM Studio Integration

**Local AI processing for note translation and review**

**Last Updated**: 2025-11-25

## Prerequisites

- LM Studio installed and running
- Compatible model loaded (e.g., Qwen3-VL-30B, Llama 3, Mistral)
- Server URL: `http://localhost:11435` (default) or custom IP

## Setup

### 1. Install LM Studio

Download from [lmstudio.ai](https://lmstudio.ai/) and install for your platform.

### 2. Load a Model

1. Open LM Studio
2. Go to **Search** tab
3. Download a capable model (recommended: 7B+ parameters for translation quality)
4. Load the model in **Chat** tab

### 3. Start Local Server

1. Go to **Local Server** tab (left sidebar)
2. Click **Start Server**
3. Note the server URL (default: `http://localhost:11435`)

## Usage

### Single File Translation

```bash
python validate_note.py <file> --ai-translate --fix
```

### Bulk Directory Translation

```bash
python validate_note.py <directory>/ --ai-translate --fix
```

### Custom Configuration

```bash
python validate_note.py <path> \
  --ai-translate \
  --lm-studio-url http://your-ip:11435 \
  --ai-model "qwen/qwen3-vl-30b" \
  --fix
```

### Dry Run (Preview Changes)

```bash
python validate_note.py <path> --ai-translate --dry-run
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--lm-studio-url` | `http://localhost:11435` | LM Studio server URL |
| `--ai-model` | Auto-detect | Model identifier |
| `--ai-translate` | Off | Enable AI translation |
| `--fix` | Off | Apply fixes automatically |
| `--dry-run` | Off | Preview without changes |

## Recommended Models

| Model | Size | Quality | Speed |
|-------|------|---------|-------|
| Qwen3-VL-30B | 30B | Excellent | Slow |
| Llama 3 8B | 8B | Good | Fast |
| Mistral 7B | 7B | Good | Fast |
| Gemma 2 9B | 9B | Good | Medium |

## Troubleshooting

### Connection Refused

```
Error: Connection refused at localhost:11435
```

**Solution**: Ensure LM Studio server is running. Check **Local Server** tab.

### Model Not Loaded

```
Error: No model loaded
```

**Solution**: Load a model in LM Studio before starting the server.

### Slow Response

- Use a smaller model (7B-8B)
- Reduce context window in LM Studio settings
- Process files in smaller batches

### Out of Memory

- Close other applications
- Use a quantized model (Q4, Q5)
- Reduce batch size with `--batch-size 1`

## Integration with Validation

LM Studio integrates with the vault validation system:

```bash
# Validate and translate in one pass
uv run --project utils python -m utils.validate_note <path> --ai-translate --fix

# Translate only files with missing translations
uv run --project utils python -m utils.validate_note <directory>/ --ai-translate --fix --filter missing-translation
```

## See Also

- **[[VALIDATION-QUICKSTART]]** - Validation commands
- **[[AGENT-CHECKLIST]]** - AI agent guidelines
- **[[NOTE-REVIEW-PROMPT]]** - Full review prompt
