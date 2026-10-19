# Create Template

Ingest a unit's existing .docx into the template library. Steps 1–5.

## Step 1 — Intake

Copy the source .docx byte-exact into a new package directory:

```
templates/docs/<template_name>/template_src.docx
```

Name: lowercase kebab-case describing the template (`qiji_heading`). Never modify
the source file afterward.

## Step 2 — Unpack + analyze

```bash
template_manager.py analyze <template_src.docx> --out <package_dir>
```

Unpacks to a scratch dir (never inside the package's permanent content) and
produces `analysis.md`: page setup, font baseline, full paragraph-style inventory
(font/size/spacing/numbering/outline level), character and table styles,
numbering definitions (abstractNum → numId), body outline, header/footer,
settings flags, plus a **quirk register** (defects found, each with 影响 + 处置)
and a **gap list** (what a full report shell needs but this scaffold lacks).

## Step 3 — Contract draft ⛔ BLOCKING (review with user)

Derive `contract.json` from the analysis:

- Map roles to styleIds: headings via outline levels + numbering bindings; body/caption/cell styles by name semantics and style chaining (`next` references)
- Whitelist = roles in active use; blocked list = demo/colored/broken styles (with reason)
- Record numbering scheme: which numId drives headings, caption ilvls, bullet numId, manual-numbering zone
- Record unit conventions stated in the template body itself (e.g. "7 级以下序号手打")

Present the draft mapping table to the user for confirmation before proceeding.

## Step 4 — Cleaned shell

Derive `template.docx` from `template_src.docx` (script, never by hand):

- Keep: styles.xml, numbering.xml, settings, headers/footers, page setup
- Body → minimal shell: 目录 heading + TOC field (contract `toc_depth`, dirty) + page break + body anchor
- Remove: demo content, demo tables/images
- Never "fix" style-sheet defects in place — register them in analysis.md quirk register; builder compensates at paragraph level (e.g. explicit `outlineLvl` on h1 paragraphs)

## Step 5 — Document + register

Write `template_contract.md` (human doc of contract.json) and add the template to
`templates/docs/templates_index.json`. State in delivery: what the shell contains,
known quirks, gaps deferred (cover/signature pages, etc.).
