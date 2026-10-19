# Routing

Resolve the request to exactly one route. Do not add a route-choice question when this file resolves the request.

## Route Selection

| Input | Route |
|---|---|
| Topic, sources (md/docx/pdf/text), or an outline; goal = a new report | **Generate DOCX** → [`generate-docx.md`](generate-docx.md) |
| A unit .docx/.dotx to add to the template library (first use of a template) | **Create Template** → [`create-template.md`](create-template.md) |
| An existing finished DOCX needing wording/section/content edits, other pages/parts untouched | **Edit Native DOCX** → [`edit-native-docx.md`](edit-native-docx.md) |

## Precedence Rules

- Generation requested with an unregistered template → Create Template first (for that unit's template), then return to Generate.
- "改一下这份报告" (edit an existing report) with substantive re-generation of whole sections → Edit Native DOCX; with a rewrite from sources → Generate DOCX.
- Source conversion of docx/pdf into text for research is part of Generate Step 2, not a separate route.

## Route Boundaries

- Generate never edits an existing finished document; it builds new files from the template shell.
- Create Template never produces user deliverables; it produces library packages.
- Edit Native DOCX never assigns styles beyond what the host document already declares; when styles are missing, stop and report — do not invent formatting.
