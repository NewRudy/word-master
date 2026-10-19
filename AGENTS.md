# AGENTS.md

This file is the project entry point for AI agents working in the word-master repository.

**You MUST read [`skills/word-master/SKILL.md`](skills/word-master/SKILL.md) before any document generation task or repo modification.** It owns global execution discipline and route selection; the selected route authority owns its steps and gates.

## Project Overview

word-master turns source material into natively editable DOCX engineering documents through a **fixed template + style library** pipeline. The AI authors content only — every visual/structural format decision comes from a template contract (`contract.json`), applied deterministically by `docx_builder.py` and verified by `doc_checker.py`. This is the mechanism that prevents format drift.

Three routes:

- **Generate DOCX** — topic/sources → researched, contract-templated report. Authority: [`workflows/generate-docx.md`](skills/word-master/workflows/generate-docx.md)
- **Create Template** — ingest a unit's existing .docx into the template library (byte-preserved source + analysis + contract). Authority: [`workflows/create-template.md`](skills/word-master/workflows/create-template.md)
- **Edit Native DOCX** — targeted edits to an existing document, everything else byte-preserved. Authority: [`workflows/edit-native-docx.md`](skills/word-master/workflows/edit-native-docx.md)

## Environment Facts

- Python: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` (not on PATH); always run with `-X utf8`
- Windows 10 + WPS; **no Microsoft Office**. TOC/page-number fields refresh with Ctrl+A → F9 in WPS (WPS COM automation is a future option)
- Tests: `python -m pytest -q`; lint: `python -m ruff check .`

## Required Conventions

- **Contract is truth**: `templates/docs/<name>/contract.json` is the machine authority for all style decisions; `template_contract.md` is its human-readable documentation. Keep both in sync — edit JSON first, then the doc.
- **Source preservation**: `template_src.docx` (the ingested original) is never modified. Derivatives are new files.
- **Numbering discipline**: heading and caption numbers come from auto-numbering fields only; below heading level 7, sequence numbers are hand-typed text per the unit convention (（1）→ 1) → ① → a)).
- **One language per file** for docs; scripts emit UTF-8.
- **Gate rules may only get stricter** unless the relaxation is backed by a contract change the template itself supports. Every new rule needs a failing fixture under `tests/`.

## Command Quick Reference

```bash
PY="python"   # Windows: "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -X utf8

"$PY" skills/word-master/scripts/template_manager.py list
"$PY" skills/word-master/scripts/template_manager.py analyze <docx> --out <dir>
"$PY" skills/word-master/scripts/template_manager.py install <docx> <name>
"$PY" skills/word-master/scripts/project_manager.py init <name> [--template qiji_heading]
"$PY" skills/word-master/scripts/project_manager.py import-sources <proj> <sources...>
"$PY" skills/word-master/scripts/project_manager.py validate <proj>
"$PY" skills/word-master/scripts/project_manager.py list
"$PY" skills/word-master/scripts/docx_builder.py build <proj>
"$PY" skills/word-master/scripts/doc_checker.py check <proj> --json
```

`<proj>` accepts an absolute path, a path relative to the current directory, or a bare project directory name under `projects/`.

## Repository Layout

```
skills/word-master/     the skill (authority files, scripts, template packages)
projects/               user workspaces (gitignored) + _demo/ (committed)
docs/                   user-facing documentation (FAQ, positioning, assets)
scripts/                repo maintenance scripts (not part of the skill)
tests/                  pytest suite; gate-rule fixtures
.github/                CI and issue templates
```
