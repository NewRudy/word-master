# projects/

Workspace for user projects. Each project is one directory: `<slug>_<YYYYMMDD>/`, created by `project_manager.py init`.

```
<project>/
├── project.json      # metadata (name / template / status / timeline)
├── sources/          # raw source material (converted/ holds text conversions)
├── assets/           # images referenced by content.md
├── facts.json        # fact provenance (word-master.fact-provenance.v1)
├── content.md        # AI-authored content in the content grammar
├── check_report.json # last gate verdict
└── exports/          # build artifacts (timestamped, never overwritten)
```

## What is committed

`projects/*` is **gitignored**, with two exceptions:

- `projects/README.md` (this file)
- `projects/_demo/` — the curated end-to-end example that CI builds and gates

Built `.docx` files are never committed: they are large binaries and are
reproducible with one command.

## Creating a project

```bash
python skills/word-master/scripts/project_manager.py init 我的报告
```

Then put your material into `projects/我的报告_YYYYMMDD/sources/` and talk to the
agent, or run the scripts directly:

```bash
python skills/word-master/scripts/docx_builder.py build 我的报告
python skills/word-master/scripts/doc_checker.py check 我的报告 --json
```

Both scripts also accept a bare project name (looked up under `projects/`) or a
path.

## The demo project

`_demo/` is a small feasibility-study report that exercises every feature:

- four heading levels plus the manual-numbering zone below level 7
- one figure (relative path: `assets/location.png`) with a caption below it
- one table with a caption above it
- two cross-references (`{{ref:fig:location}}`, `{{ref:tbl:proj_items}}`)
- two cited facts (`F001`, `F002`) with provenance

Its `check_report.json` must show `blocking: 0`. If it does not, the shipped
example is broken — see `tests/test_demo_build.py`.
