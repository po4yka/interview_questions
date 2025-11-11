## Status Badges Guide

Add these GitHub Actions status badges to your repository README.md to show workflow status.

### Adding Badges to README.md

Add this section to the top of your main README.md:

```markdown
# Interview Questions Vault

![Validate Notes](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/validate-notes.yml/badge.svg)
![Vault Health](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/vault-health-report.yml/badge.svg)
![Code Quality](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/code-quality.yml/badge.svg)
![Graph Export](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/graph-export.yml/badge.svg)

> Comprehensive bilingual (EN/RU) interview preparation vault for software engineers
```

**Replace** `YOUR_USERNAME/interview_questions` with your actual GitHub repository path.

---

### Individual Badge URLs

#### Validate Notes

```markdown
![Validate Notes](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/validate-notes.yml/badge.svg)
```

#### Vault Health Report

```markdown
![Vault Health](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/vault-health-report.yml/badge.svg)
```

#### Code Quality

```markdown
![Code Quality](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/code-quality.yml/badge.svg)
```

#### Normalize Concepts

```markdown
![Normalize](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/normalize-concepts.yml/badge.svg)
```

#### Graph Export

```markdown
![Graph Export](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/graph-export.yml/badge.svg)
```

---

### Badge Variants

#### Show status for specific branch (default: main)

```markdown
![Validate Notes](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/validate-notes.yml/badge.svg?branch=main)
```

#### Show status for specific event

```markdown
![Validate Notes](https://github.com/YOUR_USERNAME/interview_questions/actions/workflows/validate-notes.yml/badge.svg?event=push)
```

---

### Custom Badge Styles

#### Shields.io Custom Badges

For more customization, use shields.io:

```markdown
![Vault Status](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/validate-notes.yml?label=validation&logo=github&style=flat-square)
```

**Styles available**:

- `flat` (default)
- `flat-square`
- `plastic`
- `for-the-badge`
- `social`

#### Example with multiple styles:

**Flat Square**:

```markdown
![Validate](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/validate-notes.yml?style=flat-square&label=notes)
![Health](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/vault-health-report.yml?style=flat-square&label=health)
![Quality](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/code-quality.yml?style=flat-square&label=code)
```

**For-the-Badge**:

```markdown
![Validate](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/validate-notes.yml?style=for-the-badge&label=validation)
```

---

### Additional Useful Badges

#### Repository Stats

**Last Commit**:

```markdown
![Last Commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/interview_questions)
```

**License**:

```markdown
![License](https://img.shields.io/github/license/YOUR_USERNAME/interview_questions)
```

**Issues**:

```markdown
![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/interview_questions)
```

**Pull Requests**:

```markdown
![PRs](https://img.shields.io/github/issues-pr/YOUR_USERNAME/interview_questions)
```

**Repository Size**:

```markdown
![Repo Size](https://img.shields.io/github/repo-size/YOUR_USERNAME/interview_questions)
```

**Lines of Code**:

```markdown
![Lines of Code](https://img.shields.io/tokei/lines/github/YOUR_USERNAME/interview_questions)
```

---

### Vault-Specific Badges

Create custom badges for vault statistics:

#### Notes Count (requires setup)

```markdown
![Notes](https://img.shields.io/badge/notes-1069-blue)
```

#### Languages

```markdown
![Languages](https://img.shields.io/badge/languages-EN%20%7C%20RU-green)
```

#### Topics

```markdown
![Topics](https://img.shields.io/badge/topics-22-orange)
```

---

### Full Example README Header

```markdown
# Interview Questions Vault

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/validate-notes.yml?label=validation&style=flat-square" alt="Validation">
  <img src="https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/vault-health-report.yml?label=health&style=flat-square" alt="Health">
  <img src="https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/interview_questions/code-quality.yml?label=quality&style=flat-square" alt="Quality">
  <img src="https://img.shields.io/github/last-commit/YOUR_USERNAME/interview_questions?style=flat-square" alt="Last Commit">
  <img src="https://img.shields.io/github/license/YOUR_USERNAME/interview_questions?style=flat-square" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/notes-1069-blue?style=flat-square" alt="Notes">
  <img src="https://img.shields.io/badge/topics-22-orange?style=flat-square" alt="Topics">
  <img src="https://img.shields.io/badge/languages-EN%20%7C%20RU-green?style=flat-square" alt="Languages">
</p>

> Comprehensive bilingual (EN/RU) interview preparation vault for software engineers

## Features

- 976 interview questions
- 93 concept notes
- 22 technical topics
- Automated validation
- Daily health monitoring
```

---

### Troubleshooting

**Badge shows "failing"**:

- Check the workflow run in Actions tab
- Review the workflow logs
- Fix any issues and push again

**Badge shows "no status"**:

- Workflow has never run
- Trigger the workflow manually or push a change

**Badge not updating**:

- GitHub caches badge status for ~5 minutes
- Force refresh: add `?v=1`, `?v=2`, etc. to URL
- Clear browser cache

---

**Related**:

- [GitHub Actions Badges Documentation](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge)
- [Shields.io Documentation](https://shields.io/)
- [Simple Icons (for logos)](https://simpleicons.org/)
