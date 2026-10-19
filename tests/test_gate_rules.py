# -*- coding: utf-8 -*-
"""Gate rules: each blocking rule must fire on a document that violates it.

These tests are the contract's teeth. If a rule stops firing, the gate has been
weakened and this file should fail loudly.
"""
import doc_checker
import docx_builder


def _build(project):
    class Args:
        project_path = str(project)

    docx_builder.cmd_build(Args)


def _check(project):
    class Args:
        project_path = str(project)
        json = False

    try:
        doc_checker.cmd_check(Args)
    except SystemExit as e:
        return e.code
    return 0


def _rewrite(project, old, new):
    p = project / "content.md"
    text = p.read_text(encoding="utf-8")
    assert old in text, f"fixture drift: {old!r} not in content.md"
    p.write_text(text.replace(old, new), encoding="utf-8")


def test_hand_typed_caption_prefix_is_blocked(demo_project):
    _rewrite(demo_project, ":::caption fig location 某河道工程地理位置图",
             ":::caption fig location 图1.1-1 某河道工程地理位置图")
    _build(demo_project)
    assert _check(demo_project) != 0


def test_hand_typed_heading_number_is_blocked(demo_project):
    _rewrite(demo_project, "# 概述", "# 1.1 概述")
    _build(demo_project)
    assert _check(demo_project) != 0


def test_uncited_fact_is_blocked(demo_project):
    _rewrite(demo_project, "<!-- F001 -->", "<!-- F999 -->")
    _build(demo_project)
    assert _check(demo_project) != 0


def test_figure_without_caption_is_blocked(demo_project):
    _rewrite(demo_project, ":::caption fig location 某河道工程地理位置图", "")
    _build(demo_project)
    assert _check(demo_project) != 0


def test_caption_without_table_is_blocked(demo_project):
    """A table caption with no table under it must fail C6.

    The grammar cannot express an uncaptioned table at all (a bare pipe table
    is just a paragraph), so the reachable violation is the inverse: a caption
    whose table body is empty.
    """
    import re

    p = demo_project / "content.md"
    text = p.read_text(encoding="utf-8")
    stripped = re.sub(
        r"(:::caption tbl[^\n]*\n)(?:.*?)(\n:::\n)",
        r"\1\2",
        text,
        count=1,
        flags=re.S,
    )
    assert stripped != text, "fixture drift: table block not found"
    p.write_text(stripped, encoding="utf-8")
    _build(demo_project)
    assert _check(demo_project) != 0


def test_unregistered_fact_in_facts_json_is_advisory_only(demo_project):
    """An unused fact must not block delivery (rule R2)."""
    import json

    p = demo_project / "facts.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["facts"].append({
        "id": "F900",
        "claim": "未被引用的事实",
        "url": "https://example.com/unused",
        "date": "2026-10",
        "source_tier": "项目资料",
    })
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _build(demo_project)
    assert _check(demo_project) == 0
