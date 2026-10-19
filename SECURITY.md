# Security Policy

[English](./SECURITY.md) | [中文](./SECURITY_CN.md)

## Scope

word-master runs entirely on your machine with the permissions of the user who
starts it. It reads and writes files, executes local scripts, and calls the AI
model provider you configured.

**In scope:**

- A malicious template package that achieves code execution through the builder
  or the checker (e.g. via XML entity expansion, external entity resolution, or
  a path-traversal in image handling)
- A crafted `content.md` or `facts.json` that escapes the project directory or
  executes code
- A path traversal in `project_manager.py import-sources` or in the
  `<img: ...>` resolution in `docx_builder.py`
- Any case where the checker reports a clean build for a document that violates
  the contract (a gate bypass)

**Out of scope:**

- Prompt injection from source documents. The AI reading your material is the
  intended behaviour; a document that tells the model to do something is a
  content problem, not a vulnerability in word-master.
- Malicious content in a template you chose to ingest. Reviewing a template
  before running *Create Template* on it is your responsibility — same as
  opening any `.docx`.
- Data sent to your AI provider. That traffic is between you and the provider.
- Anything that requires an attacker to already have write access to your
  project directory or your Python environment.

## Reporting a vulnerability

Email **1344591831@qq.com** with:

- A description of the issue and its impact
- Steps to reproduce, ideally a minimal project directory or a crafted `.docx`
- The word-master version (`git rev-parse HEAD` or the release tag)
- Your Python version and OS

Please **do not open a public issue** for a security report. You will get an
acknowledgement within a few days. If the report is valid, a fix and a release
will follow, and you will be credited unless you prefer otherwise.

## Handling untrusted documents

The pipeline processes `.docx` files. A `.docx` is a ZIP archive of XML, and
OOXML has a long history of parser quirks. If you ingest a document from an
untrusted source:

- Open it once in Word/WPS with macro execution disabled before ingesting it
- Prefer the *Create Template* route only for templates you are willing to
  trust — the resulting package becomes part of every future build
- Run the pipeline in a container or a dedicated user account if you process
  third-party documents in bulk

## Handling untrusted AI output

The AI writes `content.md`. `content.md` cannot execute code — the builder
parses a fixed grammar and rejects anything outside it. It can, however:

- reference an image path outside the project (`<img: C:\...>`), which the
  builder will read
- cite fact IDs that do not exist (blocked by the gate)

If you run the pipeline unattended on model output you have not reviewed, treat
the resulting document as you would any AI-generated file: read it before you
send it to someone.

## Supported versions

Security fixes land on the latest release. There are no maintained back-branches
at this stage of the project.
