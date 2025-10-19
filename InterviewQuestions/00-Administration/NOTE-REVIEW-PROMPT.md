# Note Review Prompt

Review the provided note for correctness, completeness, and compliance.

## YAML Validation

Check presence and format:

- `id`: YYYYMMDD-HHmmss format
- `title`: Contains "EN / RU" format
- `aliases`: Array with both languages
- `topic`: Exactly one value from TAXONOMY.md
- `subtopics`: 1-3 values, controlled list if Android
- `question_kind`: coding | theory | system-design | android
- `difficulty`: easy | medium | hard
- `original_language`: en | ru
- `language_tags`: [en], [ru], or [en, ru]
- `status`: draft | reviewed | ready | retired
- `moc`: Single value, no brackets
- `related`: Array with 2+ items, no double brackets
- `created`: YYYY-MM-DD
- `updated`: YYYY-MM-DD
- `tags`: Array, English only

Verify Android-specific requirements if `topic: android`:

- `subtopics` from Android controlled list in TAXONOMY.md
- Tags include `android/<subtopic>` for each subtopic
- `moc: moc-android`

Additionally validate MOC mapping by topic:

- `moc` matches the note's topic MOC (e.g., `moc-algorithms`, `moc-system-design`, `moc-android`, `moc-kotlin`, `moc-backend`, `moc-cs`, `moc-tools`)

Check forbidden patterns:

- No brackets in `moc` field
- No double brackets in `related` field
- No Russian in `tags`
- No multiple topics
- No emoji anywhere
- No specific dependency versions (avoid version numbers entirely)

## File Organization

Verify:

- Filename matches pattern: `q-<slug>--<topic>--<difficulty>.md`
- File location matches `topic` field
- Folder mapping correct per TAXONOMY.md

## Content Structure

Confirm sections exist:

- `# Question (EN)`
- `# Вопрос (RU)`
- `## Answer (EN)`
- `## Ответ (RU)`
- `## Follow-ups`
- `## References`
- `## Related Questions`

## Links and Connections

Validate cross-linking and link integrity:

- At least one Concept link present in the content body: `[[c-*]]` (e.g., `[[c-hash-map]]`)
- YAML `moc` present, a single value, no brackets, and correct for the topic (see mapping in YAML Validation)
- YAML `related` contains 2–5 items, no double brackets; items correspond to existing notes
- "Related Questions" section contains internal links that resolve
- All internal links in the note resolve to existing files (no broken links)
- The referenced MOC includes (or is updated to include) a link back to this note
- Use Obsidian link health: see `00-Administration/LINK-HEALTH-DASHBOARD.md`

## Technical Accuracy

Verify answer correctness:

- Algorithm complexity analysis accurate
- Code examples compile and run
- Technical terms used correctly
- Approach solves stated problem
- Trade-offs identified accurately
- No factual errors in explanations

Check code quality:

- Syntax valid for specified language
- Logic implements described algorithm
- Edge cases handled or noted
- Complexity claims match implementation
- No off-by-one errors
- Variable names clear

Validate complexity analysis:

- Time complexity correct for algorithm
- Space complexity accounts for all allocations
- Best/average/worst cases distinguished if relevant
- Big-O notation accurate

## Bilingual Equivalence

Compare EN and RU content:

- Questions semantically equivalent
- Answers cover same points
- Technical depth matches
- Code examples identical
- No information loss in translation
- No additional content in one language only

## Formatting

Check compliance:

- No emoji in content
- Code blocks specify language
- Markdown syntax correct
- No trailing whitespace
- Lists formatted consistently
- Tables valid if present

## Content Style

Verify compact, factual approach:

- Concrete and minimal language
- Laconic phrasing over style
- No filler, caveats, or repetition
- No preamble or conclusions
- No questions back to user
- Bullets only for enumeration
- Code snippets only if truly useful
- Direct statements without hedging

## Factual Verification

For algorithms:

- Algorithm name matches implementation
- Published complexity correct
- Credited correctly if standard algorithm
- LeetCode problem number accurate if cited
- Example inputs produce stated outputs

For system design:

- Component interactions accurate
- Scalability claims realistic
- Technology choices appropriate
- Trade-offs reflect industry practice
- No outdated information

For Android:

- API versions specified if relevant
- Jetpack component usage correct
- Lifecycle methods accurate
- Deprecated APIs flagged
- Best practices current
- No specific dependency versions (avoid version numbers entirely)

For Kotlin:

- Language features exist in stated version
- Standard library usage correct
- Coroutine patterns valid
- Flow operators accurate
- Syntax matches current spec

## Output Format

Report findings in order:

**CRITICAL**: Issues violating REQUIRED rules

- State violation
- Specify location (line number or section)
- Provide correct value

**WARNINGS**: Missing RECOMMENDED elements

- Identify gap
- Suggest improvement

**ERRORS**: Factual inaccuracies

- Quote incorrect statement
- State correct fact
- Cite source if applicable

**PASSED**: Compliant elements

- List only if all checks pass

After reporting findings, provide corrected note:

```markdown
[Complete corrected Q&A note with all YAML frontmatter and content sections, no whitespace errors]
```

Do not include:

- Preambles or introductions
- Concluding summaries
- Positive reinforcement
- Questions to user
- Suggestions to "consider" changes
- Emoji or formatting decorations
- Caveats about review scope
- Apologies or hedging language

State facts. Report violations. Specify corrections. Provide corrected text.
