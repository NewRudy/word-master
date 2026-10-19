# Edit Native DOCX

Targeted edits to an existing finished DOCX. Unchanged content stays byte-preserved.

## Procedure

1. **Copy** the original into the project workspace (`projects/<slug>/work/<name>.docx`). The original file is never opened for writing.
2. **Plan** the edit: list target paragraphs/tables/figures by locating anchor text (unpack `word/document.xml` and search; python-docx for reading).
3. ⛔ **BLOCKING**: confirm the edit plan (what changes, what visibly does not) with the user.
4. **Edit** through python-docx on the copy:
   - Wording changes: replace run text in place; keep runs' rPr untouched
   - New paragraphs: clone the pPr from the neighboring paragraph of the same role — never invent formatting
   - Deletions: remove whole paragraphs/tables only
   - If the target role requires a style the document does not define → **stop and report**; route to Generate DOCX instead
5. **Verify**: re-open the result; diff paragraph count and text around every edit site; confirm untouched regions identical (unpack both, compare XML outside edit anchors).
6. **Deliver**: report the copy's path, the edit list, and any residual risk (e.g. numbering scope the host document controls).

## Boundary

This route never re-styles, never re-numbers, never re-layouts. If the request
implies any of those, say so and route to Generate DOCX with the original as a
source, or Create Template if the document should become the new library template.
