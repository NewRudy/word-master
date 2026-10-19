# -*- coding: utf-8 -*-
"""Derive a new template package from an existing, validated one.

Why this exists: a hand-written `styles.xml` / `numbering.xml` is almost always
subtly invalid, and a template package that Word refuses to open is worse than
no template at all. Deriving from a package that already opens in Word/WPS and
already passes the gate keeps the OOXML valid; only the parts we deliberately
change are touched.

What "derive" can change:
  * role -> styleId mapping stays the same (styleIds are stable inside the
    copied styles.xml), but per-role font/size/alignment can be overridden
  * document title text, TOC depth
  * template name, description, contract metadata

Usage:
  template_derive.py <base> <new_name> [--title ...] [--desc ...]
                     [--set-role ROLE:font=CJK,LATIN;size=PT;bold=true] ...

Example (a plain government-report look, 3 heading levels, no coloured demo
styles, 小四 body, 1.5 line spacing):

  template_derive.py qiji_heading gov_report \
      --desc "政府机关公文/报告模板：三级标题、小四正文" \
      --set-role body:font=仿宋,;size=12
"""
import argparse
import datetime as dt
import json
import re
import shutil
import sys
import zipfile

from wm_common import TEMPLATES, WMError

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# styleId -> role, derived from the base contract at runtime
STYLE_TAG = re.compile(r'<w:style\b[^>]*w:styleId="([^"]+)"[^>]*>(.*?)</w:style>', re.S)


def read_zip_xml(path, member):
    with zipfile.ZipFile(path) as z:
        return z.read(member).decode("utf-8")


def write_zip(pairs, out):
    """Write a .docx from (member, bytes) pairs, preserving order."""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in pairs:
            z.writestr(name, data)


def parse_role_overrides(items, valid_roles=None):
    """ROLE:font=CJK,LATIN;size=12;bold=true -> {role: {font_cjk, font_latin, size, bold}}

    `valid_roles` is checked eagerly so a typo fails before any file is written.
    """
    out = {}
    for item in items or []:
        role, _, spec = item.partition(":")
        if not spec:
            raise WMError(f"--set-role 需要 ROLE:key=value;... 形式，收到: {item}")
        if valid_roles is not None and role not in valid_roles:
            known = ", ".join(sorted(valid_roles))
            raise WMError(f"未知角色 {role!r}；模板契约中的角色: {known}")
        d = {}
        for part in spec.split(";"):
            part = part.strip()
            if not part:
                continue
            k, _, v = part.partition("=")
            k, v = k.strip(), v.strip()
            if k == "font":
                cjk, _, latin = v.partition(",")
                if cjk:
                    d["font_cjk"] = cjk
                if latin:
                    d["font_latin"] = latin
            elif k == "size":
                d["size_pt"] = float(v)
            elif k == "bold":
                d["bold"] = v.lower() in ("1", "true", "yes")
            elif k == "align":
                d["align"] = v
            else:
                raise WMError(f"未知的 --set-role 键: {k}")
        out.setdefault(role, {}).update(d)
    return out


def patch_style_rpr(body, spec):
    """Apply font/size/bold overrides to a <w:style> body string."""
    if "font_cjk" in spec or "font_latin" in spec:
        cjk = spec.get("font_cjk")
        latin = spec.get("font_latin", "Times New Roman")
        rfonts = (f'<w:rFonts w:ascii="{latin}" w:hAnsi="{latin}" '
                  f'w:eastAsia="{cjk}" w:cstheme="minorBidi"/>')
        if "<w:rFonts" in body:
            body = re.sub(r"<w:rFonts\b[^>]*/>", rfonts, body, count=1)
        else:
            body = body.replace("<w:rPr>", "<w:rPr>" + rfonts, 1) if "<w:rPr>" in body \
                else body.replace("</w:style>", "")
            if "<w:rPr>" not in body:
                raise WMError("样式缺少 <w:rPr>，无法注入字体")
    if "size_pt" in spec:
        half = int(round(spec["size_pt"] * 2))
        body = re.sub(r"<w:sz w:val=\"\d+\"/>", f'<w:sz w:val="{half}"/>', body, count=1)
        if "<w:szCs" in body:
            body = re.sub(r"<w:szCs w:val=\"\d+\"/>", f'<w:szCs w:val="{half}"/>', body, count=1)
    if "bold" in spec:
        if spec["bold"] and "<w:b/>" not in body and "<w:b " not in body:
            body = body.replace("<w:rPr>", "<w:rPr><w:b/><w:bCs/>", 1)
        elif not spec["bold"]:
            body = body.replace("<w:b/>", "").replace("<w:bCs/>", "")
    if "align" in spec:
        jc = f'<w:jc w:val="{spec["align"]}"/>'
        if "<w:jc " in body:
            body = re.sub(r"<w:jc\b[^>]*/>", jc, body, count=1)
        else:
            body = body.replace("<w:pPr>", "<w:pPr>" + jc, 1)
    return body


def apply_style_overrides(styles_xml, role_to_sid, overrides):
    """Rewrite the named styles in styles.xml."""
    if not overrides:
        return styles_xml
    missing = [r for r in overrides if r not in role_to_sid]
    if missing:
        raise WMError(f"契约里没有这些角色，无法覆盖: {', '.join(missing)}")

    def repl(m):
        sid, body = m.group(1), m.group(2)
        for role, spec in overrides.items():
            if role_to_sid[role] == sid:
                body = patch_style_rpr(body, spec)
        return m.group(0).replace(m.group(2), body, 1)

    return STYLE_TAG.sub(repl, styles_xml)


def rewrite_shell(document_xml, title_text):
    """Replace the shell's TOC heading text (the only text in the shell)."""
    # the shell contains exactly one run of visible text: the 目 录 heading
    return re.sub(r'(<w:pStyle w:val="17"/></w:pPr><w:r><w:t xml:space="preserve">)[^<]*(</w:t>)',
                  lambda m: m.group(1) + title_text + m.group(2), document_xml, count=1)


def verify_package(pkg_dir):
    """Fail loudly if the derived package is not a loadable, consistent package."""
    import xml.etree.ElementTree as ET

    from docx import Document

    docx_path = pkg_dir / "template.docx"
    contract = json.loads((pkg_dir / "contract.json").read_text(encoding="utf-8"))

    # 1) every XML part must still parse
    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                try:
                    ET.fromstring(z.read(name))
                except ET.ParseError as e:
                    raise WMError(f"{name} 不是合法 XML: {e}") from e

    # 2) python-docx must be able to open it
    try:
        doc = Document(str(docx_path))
    except Exception as e:
        raise WMError(f"派生出的 template.docx 无法打开: {e}") from e

    # 3) every contract role must point at a style that still exists
    known = {s.style_id for s in doc.styles}
    missing = [f"{r}={sid}" for r, sid in contract["styles"].items()
               if isinstance(sid, str) and sid not in known]
    if missing:
        raise WMError(f"契约角色指向不存在的样式: {', '.join(missing)}")

    # 4) whitelist must cover every role
    wl = set(contract["whitelist_paragraph_styles"])
    outside = [f"{r}={sid}" for r, sid in contract["styles"].items()
               if isinstance(sid, str) and r != "table" and sid not in wl]
    if outside:
        raise WMError(f"角色样式不在白名单: {', '.join(outside)}")


def main():
    ap = argparse.ArgumentParser(description="从已验证的模板包派生新模板包")
    ap.add_argument("base", help="基础模板包名（如 qiji_heading）")
    ap.add_argument("new_name", help="新模板包名（小写 kebab-case）")
    ap.add_argument("--desc", default="", help="模板包描述")
    ap.add_argument("--title", default=None, help="壳里目录标题文字（默认沿用基础模板）")
    ap.add_argument("--set-role", action="append", default=[],
                    metavar="ROLE:key=value;...",
                    help="覆盖角色的字体/字号/加粗/对齐，可重复")
    ap.add_argument("--toc-depth", type=int, default=None)
    ap.add_argument("--max-heading-level", type=int, default=None,
                    help="允许的最深标题级别（1-7）；更深的标题会被 builder 拒绝")
    args = ap.parse_args()

    base_dir = TEMPLATES / args.base
    out_dir = TEMPLATES / args.new_name
    if not (base_dir / "contract.json").exists():
        raise WMError(f"基础模板不存在或未入库: {base_dir}")
    if out_dir.exists():
        raise WMError(f"目标模板包已存在: {out_dir}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", args.new_name):
        raise WMError("模板名只能是小写字母、数字、下划线和连字符")

    contract = json.loads((base_dir / "contract.json").read_text(encoding="utf-8"))
    role_to_sid = {r: s for r, s in contract["styles"].items() if isinstance(s, str)}
    overrides = parse_role_overrides(args.set_role, valid_roles=set(role_to_sid))

    out_dir.mkdir(parents=True)
    shutil.copy2(base_dir / "template_src.docx", out_dir / "template_src.docx")

    # ---- template.docx: copy every member, patch styles + shell text ----
    styles_xml = read_zip_xml(base_dir / "template.docx", "word/styles.xml")
    patched_styles = apply_style_overrides(styles_xml, role_to_sid, overrides)

    doc_xml = read_zip_xml(base_dir / "template.docx", "word/document.xml")
    if args.title:
        doc_xml = rewrite_shell(doc_xml, args.title)

    pairs = []
    with zipfile.ZipFile(base_dir / "template.docx") as z:
        for info in z.infolist():
            data = z.read(info.filename)
            if info.filename == "word/styles.xml":
                data = patched_styles.encode("utf-8")
            elif info.filename == "word/document.xml":
                data = doc_xml.encode("utf-8")
            pairs.append((info.filename, data))
    write_zip(pairs, out_dir / "template.docx")

    # ---- contract.json ----
    # 样式级字体由契约定义，因此覆盖后必须同步白名单，否则 run 级校验
    # 会与样式表脱节（builder 写入的 run 不设字体，但手改文档时会漏检）。
    for spec in overrides.values():
        for key in ("font_cjk", "font_latin"):
            f = spec.get(key)
            if not f:
                continue
            bucket = "cjk_allowed" if key == "font_cjk" else "latin_allowed"
            allowed = contract["fonts"].setdefault(bucket, [])
            if f not in allowed:
                allowed.append(f)

    contract["template"] = args.new_name
    contract["version"] = 1
    contract["date"] = dt.date.today().isoformat()
    if args.desc:
        contract["description"] = args.desc
    if args.toc_depth is not None:
        contract["rules"]["toc_depth"] = args.toc_depth
    if args.max_heading_level is not None:
        lvl = args.max_heading_level
        if not 1 <= lvl <= 7:
            raise WMError("--max-heading-level 必须在 1-7 之间")
        contract["rules"]["max_heading_level"] = lvl
    # record what was overridden so the human doc can explain it
    contract["derived_from"] = {"template": args.base, "overrides": overrides or {}}
    (out_dir / "contract.json").write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- analysis.md + template_contract.md: derived, not re-analysed ----
    base_analysis = (base_dir / "analysis.md").read_text(encoding="utf-8")
    # Retitle so a reader does not mistake the derived package's analysis for
    # the base package's.
    base_analysis = re.sub(
        r"^# 模板分析[^\n]*",
        f"# 模板分析 — {args.new_name}（派生自 {args.base}）",
        base_analysis,
        count=1,
        flags=re.M,
    )
    limits = []
    if args.max_heading_level is not None:
        limits.append(f"标题最深 {args.max_heading_level} 级")
    if args.toc_depth is not None:
        limits.append(f"目录深度 {args.toc_depth}")
    note_lines = [
        f"> **派生说明**（{dt.date.today().isoformat()}）",
        ">",
        f"> 本包由 `template_derive.py` 从 `{args.base}` 派生。"
        "`template_src.docx` 与基础包是同一份单位原件（字节副本），"
        "样式表、编号体系、页面设置、页眉页脚完全一致；"
        "只有下列角色被覆盖，以及模板级规则被调整。",
        ">",
        "> **覆盖的角色**",
        ">",
    ]
    if overrides:
        note_lines += [f"> - `{r}`: {json.dumps(s, ensure_ascii=False)}" for r, s in overrides.items()]
    else:
        note_lines.append("> - （无样式覆盖）")
    if limits:
        note_lines += [">", f"> **模板级规则**：{'、'.join(limits)}"]
    note_lines += [
        ">",
        "> 基础包的**瑕疵登记**与**缺口清单**原样适用；"
        "如需修改样式表本身，请改基础包或走 Create Template 重新入库。",
        "",
        "",
    ]
    note = "\n".join(note_lines)

    (out_dir / "analysis.md").write_text(note + base_analysis, encoding="utf-8")

    base_doc = (base_dir / "template_contract.md").read_text(encoding="utf-8")
    base_doc = re.sub(
        r"^# template_contract[^\n]*",
        f"# template_contract — {args.new_name}（派生自 {args.base}）",
        base_doc,
        count=1,
        flags=re.M,
    )
    (out_dir / "template_contract.md").write_text(note + base_doc, encoding="utf-8")


    # ---- register in the index ----
    idx_path = TEMPLATES / "templates_index.json"
    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    idx["templates"] = [t for t in idx["templates"] if t["name"] != args.new_name]
    idx["templates"].append({
        "name": args.new_name,
        "dir": args.new_name,
        "version": 1,
        "date": dt.date.today().isoformat(),
        "description": args.desc or f"由 {args.base} 派生",
        "source": f"派生自 {args.base}（template_derive.py）",
    })
    idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    verify_package(out_dir)

    print(f"模板包已派生: {out_dir}")
    print(f"  基础: {args.base}  覆盖角色: {len(overrides)}")
    print("  下一步: 建一个项目指向它，跑 build + check，确认 blocking=0")


if __name__ == "__main__":
    try:
        main()
    except WMError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
