---
name: word-master
description: >
  Template-driven Word document production line for engineering reports and
  technical files. Turns a topic or source material into a natively editable
  DOCX whose every format decision comes from a unit template contract —
  headings, captions, tables and numbering are applied by deterministic
  builder scripts and verified by a blocking quality gate. Also ingests a
  unit's existing .docx into the template library, and performs targeted
  edits on existing documents. Use when the user asks to create, generate,
  template, or edit a Word document, DOCX, report, or 报告/文档, or mentions
  word-master.
metadata:
  version: "0.1.0"
  license: "MIT"
---

# Word Master Skill

word-master is a routed document workflow. This entry owns global execution
discipline and route selection; each route authority owns its procedure.

## Mandatory Load Order

1. Read this file.
2. Read [`workflows/routing.md`](workflows/routing.md) and select exactly one route.
3. Read only the selected route authority and the references it triggers.

| Route | Runtime authority |
|---|---|
| Generate DOCX | [`workflows/generate-docx.md`](workflows/generate-docx.md) |
| Create Template | [`workflows/create-template.md`](workflows/create-template.md) |
| Edit Native DOCX | [`workflows/edit-native-docx.md`](workflows/edit-native-docx.md) |

## Global Execution Discipline

1. **Serial execution** — follow the selected authority's steps in order.
2. **Blocking means stop** — at every `⛔ BLOCKING` gate, wait for explicit user confirmation. Do not decide on the user's behalf.
3. **Contract is the only style authority** — the AI never assigns fonts, sizes, spacing, or numbering by itself. Roles map to styles only through the active template's `contract.json`. Content markup (`#`, `:::figure`, …) carries semantics; the builder carries format.
4. **Template first** — no generation without an installed template package. If the unit's template is not in the library, route to Create Template first.
5. **Source preservation** — `template_src.docx` and user sources are never modified; derivatives are new files.
6. **Gates fail closed** — `doc_checker.py` blocking findings stop delivery. Fix at the owning layer (content.md for content faults, contract for mapping faults) and re-run.
7. **Act at the owning layer** — on failure, repair at the shallowest layer that owns the fault, then resume from the route's declared pointer.

## Vocabulary

| Term | Meaning |
|---|---|
| **Template package** | One directory under `templates/docs/`: `template_src.docx` (byte-preserved original), `template.docx` (cleaned build shell), `contract.json` (machine truth), `template_contract.md` (human doc), `analysis.md` (intake findings) |
| **Contract** | `contract.json`: role→styleId mapping, whitelist/blocked lists, numbering scheme, checker rules |
| **Role** | Semantic slot in content (`h1`–`h7`, `body`, `figure`, `fig_caption`, `table_caption`, `table_cell`, …) |
| **Content grammar** | The markdown-superset defined in [`references/content-grammar.md`](references/content-grammar.md) — the only format the AI authors |
| **Builder** | `docx_builder.py`: parses content grammar, injects into the template shell deterministically |
| **Checker** | `doc_checker.py`: verifies the built DOCX against the contract; blocking / advisory findings |
| **Fact ID** | `F001`-style provenance IDs in `facts.json`, cited by content and reconciled at delivery |
| **Manual numbering zone** | Below heading level 7: sequence numbers （1）→ 1) → ① → a) are hand-typed text per unit convention — never auto-numbering |

## Hard Rules (unit conventions, violating = rejected)

1. Heading and caption numbers are produced **only** by auto-numbering fields. Hand-typed `1.1` prefixes on headings, `图x.x-x` prefixes on captions → blocking.
2. Below heading level 7, sequence numbers are **hand-typed** （1）→ 1) → ① → a) — auto-numbering there → blocking.
3. Figure captions sit **below** figures; table captions sit **above** tables (template-fixed).
4. Fonts: CJK 宋体/黑体 only; Latin Times New Roman only (contract exempt lists excepted). Run-level direct formatting limited to bold/italic/vertAlign.
5. Images are inline (嵌入型), never floating.
