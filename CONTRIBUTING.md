# Contributing to word-master

[English](./CONTRIBUTING.md) | [中文](./CONTRIBUTING_CN.md)

Thanks for helping. This project has one non-negotiable idea, and everything else follows from it:

> **The template contract is the only style authority.** The AI writes content; deterministic scripts apply format; a fail-closed gate decides whether the result may be delivered.

If a change weakens that chain, it will not be merged, however convenient it looks.

## Ways to contribute

| What | How |
|---|---|
| **Report a bug** | Use the [bug report form](.github/ISSUE_TEMPLATE/bug_report.yml). Include the checker output and, if possible, the built `.docx`. |
| **Request a feature** | Use the [feature request form](.github/ISSUE_TEMPLATE/feature_request.yml). Describe the *format guarantee* you need, not the implementation. |
| **Add a template package** | The highest-value contribution. See below. |
| **Improve docs** | Fixes to `README*.md`, `docs/`, `skills/**/*.md` are always welcome. |
| **Report a wrong gate verdict** | False `blocking` findings are bugs. Show the paragraph and the contract clause it violates (or does not). |

## Adding a template package

A template package is the unit of reuse. It must be reproducible from a byte-preserved original.

1. Put the original at `skills/word-master/templates/docs/<name>/template_src.docx`. **Never modify it afterwards** — it is the audit trail.
2. Run the analysis and commit the derived files:
   ```bash
   python skills/word-master/scripts/template_manager.py analyze <src.docx> --out skills/word-master/templates/docs/<name>
   ```
3. Hand-finish `analysis.md`: the machine draft has the inventory, you must fill the **quirk register** (defects found → impact → disposition) and the **gap list** (what a full report shell needs but this scaffold lacks). Both are required — they are how the next maintainer knows why the builder compensates somewhere.
4. Write `contract.json`. It is the machine truth. Every role must map to a real `styleId` in the template. Do not invent roles the template cannot serve.
5. Write `template_contract.md` as the human-readable twin of the JSON. **Edit the JSON first, then the doc.** They must not drift.
6. Produce `template.docx` (the cleaned shell) with a script, never by hand. Keep `styles.xml`, `numbering.xml`, settings, headers/footers and page setup; strip demo content.
7. Register the package in `templates/docs/templates_index.json`.
8. Prove it works: add or point a project at the template, run `docx_builder.py build` and `doc_checker.py check`, and confirm `blocking = 0`.

> **Licensing**: only contribute a template you have the right to redistribute. A unit's internal template often cannot be published — in that case contribute the *contract structure* with a synthetic stand-in document, and say so in `analysis.md`.

## Changing the builder or the checker

These two scripts are the guarantee. Before changing them:

- **The checker may only get stricter**, unless the relaxation is justified by a contract change that the template itself supports. A "fix" that makes a blocking finding disappear by weakening the rule will be rejected.
- **The builder may not assign formatting that is not in the contract.** No inline font sizes, no direct paragraph spacing, no hard-coded colors. If a template needs it, it belongs in `styles.xml` and the contract.
- Every new rule needs a **failing fixture**: a small project that must be blocked. Add it under `tests/fixtures/`.

## Development setup

```bash
git clone https://github.com/NewRudy/word-master.git
cd word-master
pip install -r requirements.txt
pip install -r requirements-dev.txt   # pytest, ruff

# smoke test: build and gate the bundled demo
python skills/word-master/scripts/docx_builder.py build projects/_demo
python skills/word-master/scripts/doc_checker.py check projects/_demo --json
python -m pytest -q
```

On Chinese Windows, always add `-X utf8` to the Python invocation.

## Code style

- Python 3.10+, no third-party dependency beyond `python-docx` in runtime code.
- Scripts are CLIs with argparse subcommands; keep them runnable standalone.
- User-facing output is Chinese in Chinese docs, English in English docs — never mix two languages in one file.
- No comments that restate the code. Comment *why*, especially where the builder compensates for a template defect.

## Commit messages

Conventional Commits, scoped by area:

```
feat(builder): support multi-paragraph table cells
fix(checker): do not flag figure captions inside table cells
docs(faq): explain why fields need F9 in WPS
feat(template): add 中国电建 gyec report template package
```

## Pull requests

- One concern per PR.
- State what changed in behaviour, and which gate rule (if any) is affected.
- If you touched `contract.json`, say which template and show the diff of the role mapping.
- CI must be green: `pytest` + demo build + demo gate.

## Code of Conduct

By participating you agree to the [Code of Conduct](./CODE_OF_CONDUCT.md).
