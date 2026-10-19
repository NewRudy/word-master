# Why word-master — and when you should not use it

[English](./why-word-master.md) | [中文](./why-word-master_CN.md)

## The one-sentence version

Use it when the document must **look like it came out of your organisation**, repeatedly, and a human would otherwise spend hours re-laying it out. Do not use it when you need a one-off document where format does not matter.

## The problem, stated precisely

AI writing is solved. Formatting is not, and formatting is where the hours go — not in producing a document, but in producing a document that survives review.

The failure is structural, not a model quality issue:

| Root cause | Consequence |
|---|---|
| The model has no style source of truth | Every run invents a slightly different look |
| Numbering is text, not fields | Insert a chapter, everything downstream is wrong |
| Captions and cross-references are text | Renumbering means manual search-and-replace |
| "Use the template" is an instruction, not a constraint | One pasted paragraph breaks the chain, silently |

Adding more instructions to the prompt does not fix this. You cannot prompt your way into a deterministic output. You need a **contract** and a **gate**.

## What word-master actually changes

Three properties, each with a mechanical guarantee rather than a promise:

**1. Format decisions are not made by the model.**
The model emits semantic roles (`h1`, `body`, `figure`). The builder maps roles to `styleId`s from `contract.json`. There is no code path where the model sets a font size.

**2. Format violations cannot be delivered.**
`doc_checker.py` runs after every build and exits non-zero on any `blocking` finding. The gate is fail-closed: an unknown style is a failure, not a warning.

**3. The template is the unit's own.**
`template_src.docx` is a byte-preserved copy of the real document your organisation uses. The stylesheet is not regenerated, not approximated, not "inspired by" — it is the same stylesheet.

Property 3 is why this is not a generic "docx skill". The asset is the template package, and it is the thing that is genuinely hard to replicate.

## Where it fits

| Scenario | Fit |
|---|---|
| Engineering feasibility studies, technical reports, review documents | **Excellent** — the reference template was built for this |
| Unit-mandated report templates with a fixed stylesheet | **Excellent** — that is the Create Template route |
| Documents that get merged into a master volume | **Good** — hand-typed sub-level numbering survives merges by design |
| Documents with heavy cross-referencing and figure/table numbering | **Good** — REF fields, auto-numbered captions |
| Long documents where format consistency is reviewed | **Good** — the gate is the point |
| Proposals / bids with a mandated format | **Good** — ingest the template, generate the body |

## Where it does not fit

Be honest about these; they are deliberate boundaries, not gaps waiting to be closed.

| Scenario | Why not |
|---|---|
| A one-off letter, memo, or short note | The setup cost exceeds the benefit. Just write it. |
| Marketing collateral, brochures, designed layouts | Word is the wrong tool, and the contract model fights free layout. |
| Templates built on floating images, text boxes, content controls | Not fully reproducible through the current builder. Intake analysis will flag it. |
| You need the cover page and signature block generated | Deliberately manual. Units differ too much; getting it wrong is worse than leaving it blank. |
| You want a hosted web app | This is a local skill, by design — your documents never leave your machine. |
| You need PDF output as the primary deliverable | DOCX is the deliverable; PDF export is whatever your Word/WPS produces. |
| Your "template" is actually just a visual style, not a stylesheet | There is nothing to lock onto. Build a real template first. |

## Compared with the alternatives

**Prompting a general model to "write a Word document"**
Works for one-offs. Every run differs. Nothing enforces the unit's stylesheet. Cost of a re-layout exceeds the cost of writing.

**Jinja2 / docxtpl**
Excellent at filling placeholders in a fixed document. Has no model of *document structure*: no heading hierarchy, no auto-numbering, no caption pairing, no cross-reference fields, no gate. Use it when your document is a form, not a report.

**Markdown → Pandoc**
Produces a clean, generic stylesheet. Your unit's template is discarded, and there is no gate to tell you that the output drifted. Good for publishing pipelines, wrong for organisational documents.

**Doing it by hand in Word**
Correct output, linear cost, and it is exactly the cost word-master removes.

## The honest limitations

- **Prose quality is your model's job.** The gate guarantees format, not that chapter 3 agrees with chapter 1.
- **The gate is only as good as the contract.** A badly derived contract will happily enforce the wrong thing. That is why *Create Template* has a blocking review step.
- **One template per package.** If your unit has five mandated templates, you need five packages. That is intentional — each package carries its own audit trail.
- **The reference template encodes one unit's conventions** (seven heading levels, hand-typed sub-level numbering, table above caption). If your unit differs, encode your rules — do not fork the checker.

## What "success" looks like

A report that a reviewer reads for content, not for format. If the review comments are about what you wrote and never about how it looks, the tool did its job.
