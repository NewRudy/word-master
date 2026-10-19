# Generate DOCX

Produce a new DOCX report from a topic or sources through the active template contract. Steps 1–7.

## Step 1 — Research (conditional)

Topic-only or fact-insufficient input: dispatch an independent research subagent
(general-purpose) with these authorities:

- Source priority (user-fixed): 国家政策 ＞ 政府发文 ＞ 行业法律法规 ＞ 新闻 ＞ 技术博客
- Prefer the latest year data; every fact carries `fact_id` (F001…), URL, and date
- No authoritative recent source → say so; never substitute low-authority sources silently

Product: `projects/<slug>/sources/<slug>.md` + `projects/<slug>/facts.json`
(schema `word-master.fact-provenance.v1`). Facts carry into content citations.

## Step 2 — Project init + import

```bash
project_manager.py init <project_name> [--template qiji_heading]
project_manager.py import-sources <project_path> <sources...>
```

Record the returned absolute project path. Convert imported docx/pdf sources to
text under `sources/converted/` for reading.

## Step 3 — Confirmation ⛔ BLOCKING (chat MVP)

Confirm with the user in chat (confirm_ui server is a later stage):

1. Template (default: the project's `--template`; must be an installed package)
2. Document outline: chapter list (h1 level) with one-line scope each
3. Length target (word count / chapter count), figure/table expectations
4. Fact sources status (researched / to-research / user-supplied)

No generation before this gate closes. The confirmed outline becomes the skeleton
of `content.md`.

## Step 4 — Install contract

Read the template package's `contract.json` and `references/content-grammar.md`.
Write `content.md` per the grammar:

- Front matter: `@title:`, `@template:` directives
- Chapter skeleton from the confirmed outline (h1–h7)
- Content authored to the grammar only — **no format decisions**
- Citations: attach `<!-- F001 -->` after sentences backed by facts; cross-refs as `{{ref:fig:<slug>}}` / `{{ref:tbl:<slug>}}`

## Step 5 — Build

```bash
docx_builder.py build <project_path>
```

Builder deterministically: clears shell body → writes TOC page → renders content
per contract → appends fact source appendix. On builder error: fix `content.md`
or the contract at the owning layer, rebuild. Never hand-edit the built docx.

## Step 6 — Check

```bash
doc_checker.py check <project_path> --json
```

- **blocking** findings → fix in `content.md` (content faults) or contract (mapping faults), rebuild, re-check
- **advisory** findings → report at delivery
- Reconciliation: every `F0xx` cited in content exists in `facts.json`, and vice versa

## Step 7 — Deliver

Report to the user:

1. Paths: built `.docx` (with timestamp) under `exports/`
2. WPS note: open → Ctrl+A → **F9** refreshes TOC/cross-reference fields
3. Checker summary: blocking count (must be 0), advisory count and meaning
4. Fact provenance summary (count, source tier breakdown)
5. What remains manual: cover/signature pages (not yet in template shell)
