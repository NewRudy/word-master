# word-master — Frequently Asked Questions

[English](./faq.md) | [中文](./faq_CN.md)

## Getting started

### Do I need Microsoft Office?

No. WPS is enough, and LibreOffice works for viewing. The pipeline never automates Word — it writes OOXML directly.

The one thing Office/WPS is needed for: **refreshing fields**. The TOC and cross-references are real Word fields with `w:dirty="true"`. Open the document, `Ctrl+A`, then `F9`. That is a one-second operation, not a build step.

### Do I need to know Python?

No, for daily use. You install Python once so the scripts can run; the agent invokes them.

You do need to be comfortable with a terminal for the *initial* setup (`git clone`, `pip install`).

### Which model should I use?

A model that can (a) follow a ~60-line content grammar precisely and (b) hold a chapter outline across a long document. In practice: Claude Sonnet/Opus, GPT-5-class, Gemini Pro, Kimi K2/K3, DeepSeek-V3-class.

A weak model does not break the gate — it produces text that *passes* the gate but reads poorly. The gate protects format, not prose quality.

### How much does it cost?

The project is free and MIT-licensed. Your only cost is model tokens. A 6000-word report with research typically costs well under a dollar on a mid-tier model; the same on an expensive frontier model with heavy thinking can cost several dollars.

## Concepts

### What exactly is a "template package"?

A directory under `skills/word-master/templates/docs/<name>/` containing:

| File | Role |
|---|---|
| `template_src.docx` | Byte-preserved copy of the unit's original. Never modified. Audit trail. |
| `template.docx` | Cleaned build shell: styles, numbering, page setup, header/footer kept; demo content stripped. |
| `contract.json` | Machine truth: role → styleId mapping, whitelist, blocked list, numbering scheme, checker rules. |
| `template_contract.md` | Human-readable twin of `contract.json`. |
| `analysis.md` | Intake findings: inventory, quirk register, gap list. |

### Why can't the AI just pick fonts and sizes?

Because that is precisely the failure mode the project exists to prevent. Once the model is allowed to make one formatting decision, it makes them inconsistently across chapters and across runs. The contract removes the decision entirely: a role maps to a `styleId`, and the style carries the format.

### Why must sub-level-7 numbers be typed by hand?

This is a unit convention baked into the reference template, not a limitation. The rationale: when several documents are merged into one master document, auto-numbering restarts or renumbers unexpectedly; hand-typed `（1）→ 1) → ① → a)` survives the merge unchanged. The checker enforces it (`C5`).

If your unit does not have this convention, encode your own rule in your template's contract.

### Why are captions on different sides?

Figure captions go **below** the figure; table captions go **above** the table. That is the convention in Chinese engineering documents and it is fixed by the contract (`fig_caption_after_figure`, `tbl_caption_before_table`).

## Usage

### The gate says `BLOCKING [C1] style not in whitelist`

The built document contains a paragraph using a style that is not in `contract.json`'s `whitelist_paragraph_styles`.

Most common cause: you edited `content.md` in a way the builder mapped to a style you did not intend, or you hand-edited the built `.docx` (never do that — rebuild instead).

If the style is legitimately needed, add it to the contract **and** document the role in `template_contract.md`.

### The gate says `BLOCKING [C4] caption looks hand-numbered`

You wrote `图1.1-1 某某图` as the caption text. Write only the caption text (`某某图`) — the number comes from the style's auto-numbering. Same for tables.

### The gate says `BLOCKING [R1] content cites an unregistered fact`

`content.md` contains `<!-- F007 -->` but `facts.json` has no `F007`. Either add the fact with its source, or remove the citation.

The reverse (`R2`, an unused fact) is only advisory.

### The gate says `BLOCKING [C6] figure not followed by caption`

Every `:::figure` block must be immediately followed by its `:::caption fig <slug> …`. No blank paragraph, no body text in between.

### The TOC is empty / shows "Error! Bookmark not defined"

Fields have not been refreshed. Open in WPS or Word, `Ctrl+A`, `F9`. If it still fails, choose "Update entire table" in the dialog.

### My images do not appear

The path in `<img: ...>` is resolved relative to the project directory if it is relative. Check that the file exists and that the format is supported by `python-docx` (PNG, JPEG, GIF, BMP, TIFF).

### Can I edit the generated document afterwards?

Yes — it is a normal `.docx` with your unit's styles. Edit freely in Word/WPS.

But: once you hand-edit, do not rebuild from `content.md` on top of it. Pick one direction. If the edits are substantial, fold them back into `content.md` and rebuild; if they are final polish (cover, signature block), do them last.

### Can it handle my unit's template?

Yes — that is the *Create Template* route. See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-a-template-package) for what a complete package requires.

Caveat: a template that relies on floating images, text boxes, or content controls may not be fully reproducible. The intake analysis will tell you.

## Troubleshooting

### `UnicodeEncodeError` on Windows

Run every script with `-X utf8`:

```bash
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -X utf8 skills/word-master/scripts/doc_checker.py check projects/xxx
```

### `python-docx` not found

```bash
pip install -r requirements.txt
```

If you have several Pythons, install into the one you actually run:

```bash
"<full path to python>" -m pip install -r requirements.txt
```

### The builder says the template shell is missing

`template.docx` was not produced for that package. Complete *Create Template* step 4, or reinstall the package.

### Everything looks right but the reviewer still complains

Check whether the complaint is about **format** (gate territory) or **content** (your territory). The gate cannot know that your chapter 3 contradicts chapter 1, that a number is stale, or that the unit wants a specific cover page.

## Project boundaries

word-master deliberately does **not**:

- generate cover pages, signature blocks, or approval sheets (unit-specific, manual by design)
- automate Word/WPS via COM (planned, not shipped)
- convert PDF to text natively (planned; currently copies the original)
- provide a web UI or a hosted service
- pick a model or a provider for you

See [why-word-master.md](./why-word-master.md) for the reasoning.

### The gate says `advisory [C9] cross-reference not in actual heading numbers`

Body text says `见 9.9 节` but no heading resolves to 9.9. This is advisory (it does not block delivery) because the reference may be intentional or the heading may be added later. Fix the number, or drop the reference.

### The gate says `advisory [C10] body first-line indent overridden`

A body paragraph carries its own `w:ind` that differs from what the style defines. That is exactly the kind of drift the contract exists to prevent, so the checker flags it — but it does not block, because some documents legitimately need a local exception. Remove the override, or if it is a real unit convention, encode it in the template's contract instead.
