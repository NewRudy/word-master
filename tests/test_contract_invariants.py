# -*- coding: utf-8 -*-
"""Contract and grammar invariants.

These protect the properties the README claims, so a well-meaning refactor
cannot silently drop them.
"""
import json

import docx_builder
import pytest
from wm_common import WMError


def test_contract_roles_all_resolve_to_real_styles(contract):
    """Every styleId in the contract must exist in the template's stylesheet."""
    from docx import Document

    shell = contract["built_docx"]
    doc = Document(str(docx_builder.TEMPLATES / contract["template"] / shell))
    known = {s.style_id for s in doc.styles}
    for role, sid in contract["styles"].items():
        if isinstance(sid, str):
            assert sid in known, f"role {role} maps to missing styleId {sid}"


def test_contract_whitelist_covers_every_role(contract):
    whitelist = set(contract["whitelist_paragraph_styles"])
    for role, sid in contract["styles"].items():
        if isinstance(sid, str) and role not in ("table",):
            assert sid in whitelist, f"role {role} (styleId {sid}) not in whitelist"


def test_contract_has_no_placeholder_todos(contract):
    assert "_TODO" not in json.dumps(contract, ensure_ascii=False)


def test_heading_levels_are_contiguous(contract):
    levels = contract["numbering"]["heading_levels"]
    for i in range(1, contract["rules"]["max_heading_level"] + 1):
        assert f"h{i}" in levels, f"missing heading level h{i}"


def test_grammar_rejects_unknown_block(demo_project):
    (demo_project / "content.md").write_text(
        "@title: x\n\n:::unknown-block\nfoo\n:::\n", encoding="utf-8"
    )
    with pytest.raises(WMError):
        docx_builder.parse_content((demo_project / "content.md").read_text(encoding="utf-8"))


def test_grammar_rejects_unclosed_figure(demo_project):
    with pytest.raises(WMError):
        docx_builder.parse_content("@title: x\n\n:::figure a\n<img: nope.png>\n")


def test_grammar_rejects_unclosed_table(demo_project):
    with pytest.raises(WMError):
        docx_builder.parse_content(
            "@title: x\n\n:::caption tbl a 表题\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n"
        )


def test_heading_depth_beyond_seven_is_a_grammar_error():
    """8+ hashes must raise, not silently become body text."""
    nl = chr(10)
    with pytest.raises(WMError):
        docx_builder.parse_content("# a" + nl + nl + "#" * 8 + " b" + nl)
    # exactly 7 is the deepest supported level
    items = docx_builder.parse_content("#" * 7 + " g" + nl)
    assert items == [("heading", 7, "g")]


def test_relative_image_paths_resolve_against_project(demo_project):
    """The demo ships a relative <img: assets/location.png>; it must build."""
    class Args:
        project_path = str(demo_project)

    docx_builder.cmd_build(Args)  # raises WMError if resolution is broken
    assert list((demo_project / "exports").glob("*.docx"))
