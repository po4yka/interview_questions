---
date created: Tuesday, November 25th 2025, 8:42:34 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Administration Documentation

This folder contains all administrative documentation for the Interview Questions vault, organized into logical subfolders for better navigation.

## Folder Structure

### AI-Agents/
AI agent guidelines, checklists, and prompts for automated content creation and validation.

- `AI-Agents/AGENT-CHECKLIST.md` - Quick reference checklist for AI agents
- `AI-Agents/NOTE-REVIEW-PROMPT.md` - Prompts for note review and validation

### AI-Integration/
Setup and integration guides for AI tools and services.

- `AI-Integration/LM-STUDIO-QUICKSTART.md` - LM Studio setup guide for local AI processing
- `AI-Integration/LANGCHAIN_INTEGRATION.md` - LangChain-based AI validation implementation

### Domain-Guides/
Domain-specific guides and checklists for different technical areas.

- `Domain-Guides/ANDROID-INTERVIEWER-GUIDE.md` - Android system design interview guide
- `Domain-Guides/ANDROID-SYSTEM-DESIGN-CHECKLIST.md` - Android system design checklist

### Index/
Documentation index and navigation files.

- `Index/DOCUMENTATION-INDEX.md` - Complete documentation index and quick start guides

### Linking-System/
Documentation related to the vault's linking strategy, health monitoring, and navigation.

- `Linking-System/00-MOC-Start-Here.md` - Main entry point and topic overview
- `Linking-System/LINK-HEALTH-DASHBOARD.md` - Automated link health monitoring dashboard
- `Linking-System/LINK-MONITORING-GUIDE.md` - Guide for link health monitoring
- `Linking-System/LINKING-STRATEGY.md` - Comprehensive linking strategy and implementation

### Validation/
Documentation for the validation system and tools.

- `Validation/VALIDATION-README.md` - Complete validation system documentation
- `Validation/VALIDATION-QUICKSTART.md` - Quick start guide for validation commands

### Vault-Rules/
Core rules, standards, and controlled vocabularies for the vault.

- `Vault-Rules/FILE-NAMING-RULES.md` - Core file naming conventions
- `Vault-Rules/NAMING-EXAMPLES.md` - Detailed naming examples and patterns
- `Vault-Rules/NAMING-VALIDATION.md` - Validation scripts and tools
- `Vault-Rules/TAXONOMY.md` - Controlled vocabularies reference
- `Vault-Rules/ANDROID-SUBTOPICS.md` - Android-specific subtopics list
- `Vault-Rules/YAML-EXAMPLES.md` - Complete YAML examples by topic

## Quick Access

For common tasks:
- **New to the vault?** → `Index/DOCUMENTATION-INDEX.md`
- **AI agent setup?** → `AI-Agents/AGENT-CHECKLIST.md`
- **Validation needed?** → `Validation/VALIDATION-QUICKSTART.md`
- **Check link health?** → `Linking-System/LINK-HEALTH-DASHBOARD.md`

## AI Tools Integration

This documentation system integrates with multiple AI tools:
- **Cursor AI**: Uses `.cursor/rules/` for automated assistance
- **Claude Code**: Follows `CLAUDE.md` workflows
- **Gemini CLI**: Uses `GEMINI.md` for command-line operations
- **LM Studio**: Local AI processing via `AI-Integration/LM-STUDIO-QUICKSTART.md`

## Related Files

- Root `README.md` - Main project overview
- `AGENTS.md` - General AI agent guidelines
- `GEMINI.md` - Gemini CLI specific guidance
- `CLAUDE.md` - Claude Code integration
- `.gitignore` - Excludes AI artifacts and sensitive files

## Maintenance

When adding new documentation:
1. Determine the appropriate subfolder based on content
2. Update this README if adding new subfolders
3. Update cross-references in other documents as needed
4. Test AI tool integrations if adding new workflows

Last updated: 2025-11-25
