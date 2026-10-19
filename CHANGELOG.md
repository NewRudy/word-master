# Changelog

All notable changes to word-master are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Staged confirmation UI (`confirm_ui`) replacing the chat-only `⛔ BLOCKING` gate
- PDF → text source conversion (currently the original is copied only)
- WPS COM field refresh so TOC/REF update without manual `Ctrl+A` → `F9`
- Additional template packages (public-sector, bid, acceptance-report)

## [0.2.0] — 2026-10-19

Documentation and distribution release. No breaking change to the content
grammar or the contract schema.

### Added
- `README_CN.md` — full Chinese README, the primary entry point for this audience
- `docs/assets/before-after.png` + `scripts/make_compare_image.py` — the
  format-drift comparison figure used at the top of both READMEs
- `docs/faq.md`, `docs/faq_CN.md` — troubleshooting, model choice, cost,
  gate-rule explanations, and the project's deliberate boundaries
- `docs/why-word-master.md`, `docs/why-word-master_CN.md` — positioning,
  fit / non-fit scenarios, and an honest comparison with prompt-only,
  docxtpl, and Pandoc approaches
- `CONTRIBUTING.md`, `CONTRIBUTING_CN.md` — including the template-package
  acceptance checklist and the rule that the checker may only get stricter
- `CODE_OF_CONDUCT.md`, `SECURITY.md`
- `SPONSORING.md`, `SPONSORING_CN.md` — sponsor tiers, minimum term, and the
  explicit list of things sponsorship does not buy
- `.github/ISSUE_TEMPLATE/` — bug report, feature request, contact links
- `.github/workflows/ci.yml` — builds and gates the bundled demo on every push
- `tests/` — pytest smoke tests plus failing fixtures for gate rules
- `requirements-dev.txt`
- `CHANGELOG.md` (this file)
- `projects/_demo/` — the smoke-test project is now the curated, committed
  demo; its figure ships with the repo as `assets/location.png`

### Changed
- `README.md` restructured around the before/after figure, with a Quick Start
  that matches the commands the scripts actually accept
- `projects/` is now a workspace: everything under it is gitignored except
  `README.md` and `_demo/`. Built `.docx` artifacts are never committed.
- `docx_builder.py`: relative `<img: ...>` paths now resolve against the
  project directory, so the demo works from a fresh clone
- `docx_builder.py`: the fact-source appendix uses an optional
  `sources_heading` contract role instead of borrowing the TOC heading style
- `doc_checker.py`: `check_report.json` records the build artifact path
  relative to the repository when possible, so reports can be committed safely
- Version bumped to `0.2.0` in `SKILL.md`

### Removed
- Committed build artifacts under `projects/` (188 KB × 2 smoke-test builds,
  and a 81 MB working project). They are reproducible with one command and
  should never have been in git history going forward.

## [0.1.0] — 2026-10-19

Initial release.

### Added
- Three routes: **Generate DOCX**, **Create Template**, **Edit Native DOCX**
- Deterministic toolchain: `project_manager.py`, `template_manager.py`,
  `docx_builder.py`, `doc_checker.py`, `wm_common.py`
- `qiji_heading` template package — a seven-heading-level engineering report
  scaffold with `contract.json` as the single style authority
- Fail-closed quality gate: style whitelist, field-only numbering, caption
  side enforcement, font override detection, fact-provenance reconciliation
- Content grammar (`references/content-grammar.md`): headings, body,
  manual-numbering zone, bullets, figures, tables, captions, cross-references,
  fact citations
- Fact provenance schema (`word-master.fact-provenance.v1`) with source tiers
- End-to-end smoke-test project
