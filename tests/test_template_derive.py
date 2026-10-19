# -*- coding: utf-8 -*-
"""Template derivation: a derived package must be loadable and gate-clean.

The derivation tool edits OOXML in place, which is exactly the kind of code
that produces a file Word refuses to open. These tests keep that honest.
"""
import json

import pytest
from wm_common import TEMPLATES, WMError, load_contract


def test_shipped_templates_are_loadable(contract):
    """Every template package in the index must open and have a valid contract."""
    from docx import Document

    index = json.loads((TEMPLATES / "templates_index.json").read_text(encoding="utf-8"))
    assert index["templates"], "template index is empty"

    for entry in index["templates"]:
        pkg = TEMPLATES / entry["name"]
        assert (pkg / "template.docx").exists(), f"{entry['name']}: missing template.docx"
        assert (pkg / "template_src.docx").exists(), f"{entry['name']}: missing template_src.docx"
        assert (pkg / "contract.json").exists(), f"{entry['name']}: missing contract.json"
        assert (pkg / "analysis.md").exists(), f"{entry['name']}: missing analysis.md"
        assert (pkg / "template_contract.md").exists(), f"{entry['name']}: missing template_contract.md"

        doc = Document(str(pkg / "template.docx"))  # raises if the OOXML is broken
        known = {s.style_id for s in doc.styles}
        c = load_contract(entry["name"])
        for role, sid in c["styles"].items():
            if isinstance(sid, str):
                assert sid in known, f"{entry['name']}: role {role} -> missing style {sid}"


def test_derived_contracts_record_their_base():
    """A derived package must say what it came from; the reference one must not."""
    index = json.loads((TEMPLATES / "templates_index.json").read_text(encoding="utf-8"))
    for entry in index["templates"]:
        c = load_contract(entry["name"])
        if entry["name"] == "qiji_heading":
            assert "derived_from" not in c
        else:
            assert c.get("derived_from", {}).get("template"), (
                f"{entry['name']} must record derived_from.template"
            )


def test_derived_templates_keep_the_same_numbering_scheme():
    """Derivation changes presentation, never the numbering contract."""
    base = load_contract("qiji_heading")
    index = json.loads((TEMPLATES / "templates_index.json").read_text(encoding="utf-8"))
    for entry in index["templates"]:
        c = load_contract(entry["name"])
        assert c["numbering"]["heading_auto_numId"] == base["numbering"]["heading_auto_numId"]
        assert c["numbering"]["caption"] == base["numbering"]["caption"]
        assert c["numbering"]["manual_below_h7"] is True


def test_derived_templates_declare_their_own_fonts():
    """A package that overrides a role's font must allow that font in its contract."""
    from docx import Document

    index = json.loads((TEMPLATES / "templates_index.json").read_text(encoding="utf-8"))
    for entry in index["templates"]:
        c = load_contract(entry["name"])
        allowed = set(c["fonts"]["cjk_allowed"]) | set(c["fonts"]["latin_allowed"])
        doc = Document(str(TEMPLATES / entry["name"] / "template.docx"))
        for style in doc.styles:
            el = style.element
            rpr = el.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
            if rpr is None:
                continue
            fonts = rpr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
            if fonts is None:
                continue
            ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            for key in ("ascii", "hAnsi", "eastAsia"):
                v = fonts.get(ns + key)
                if v and v not in allowed:
                    exempt = c["fonts"].get("exempt", {}).get("style", {}).get(style.style_id, [])
                    assert v in exempt, (
                        f"{entry['name']}: style {style.style_id} uses {v!r}, "
                        f"not allowed by the contract"
                    )


def test_unknown_role_override_is_rejected():
    import template_derive

    valid = {"body", "h1", "figure"}
    with pytest.raises(WMError, match="未知角色"):
        template_derive.parse_role_overrides(["no_such_role:size=12"], valid_roles=valid)


def test_bad_role_spec_is_rejected():
    import template_derive

    with pytest.raises(WMError):
        template_derive.parse_role_overrides(["body"])  # missing ":"
    with pytest.raises(WMError):
        template_derive.parse_role_overrides(["body:colour=red"])
