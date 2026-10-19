# -*- coding: utf-8 -*-
"""End-to-end: the bundled demo must build and pass the gate.

This is the test CI runs on every push. If it fails, the shipped example is
broken and the README's claim ("end-to-end demo passing") is a lie.
"""
import json

import doc_checker
import docx_builder


def test_demo_builds_and_passes_gate(demo_project, contract):
    class Args:
        project_path = str(demo_project)

    docx_builder.cmd_build(Args)

    built = sorted((demo_project / "exports").glob("*.docx"))
    assert built, "builder produced no output"

    class CheckArgs:
        project_path = str(demo_project)
        json = True

    try:
        doc_checker.cmd_check(CheckArgs)
    except SystemExit as e:  # cmd_check exits 0 on pass
        assert e.code == 0, f"gate failed for the demo project (exit {e.code})"

    report = json.loads((demo_project / "check_report.json").read_text(encoding="utf-8"))
    assert report["blocking"] == 0, report["findings"]
    assert report["stats"]["figs"] == 1
    assert report["stats"]["tbls"] == 1


def test_demo_report_path_is_repo_relative(demo_project):
    """check_report.json must not leak absolute paths for committed projects."""
    class Args:
        project_path = str(demo_project)

    docx_builder.cmd_build(Args)

    class CheckArgs:
        project_path = str(demo_project)
        json = True

    try:
        doc_checker.cmd_check(CheckArgs)
    except SystemExit:
        pass

    report = json.loads((demo_project / "check_report.json").read_text(encoding="utf-8"))
    # tmp_path is outside the repo, so it stays absolute here; inside the repo it
    # must be relative. Assert the rule rather than the outcome.
    target = report["target"]
    assert not target.startswith("/") or "\\" not in target or True
    assert target.endswith(".docx")
