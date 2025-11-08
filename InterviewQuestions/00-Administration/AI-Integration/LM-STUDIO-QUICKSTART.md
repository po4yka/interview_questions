# LM Studio Integration

**Local AI processing with Qwen3-VL-30B model**

## Prerequisites
- LM Studio installed and running
- Qwen3-VL-30B model loaded
- Server URL: `http://localhost:11435` (or custom IP)

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
  --ai-model "qwen/qwen3-vl-30b"
  --fix \
