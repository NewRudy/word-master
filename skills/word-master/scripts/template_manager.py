# -*- coding: utf-8 -*-
"""word-master template library: list / analyze / install.

Usage:
  template_manager.py list
  template_manager.py analyze <docx> [--out <dir>]     # 解包分析，产出 analysis 草稿
  template_manager.py install <docx> <name>            # 入库：复制原件+分析+契约骨架
"""
import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from wm_common import TEMPLATES, WMError

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def attr(el, name, default=None):
    if el is None:
        return default
    return el.get(f"{W}{name}", default)


def first(parent, tag):
    if parent is None:
        return None
    return parent.find(f"{W}{tag}")


def rpr_info(rpr):
    if rpr is None:
        return {}
    d = {}
    fonts = first(rpr, "rFonts")
    if fonts is not None:
        for k in ("ascii", "eastAsia", "hAnsi"):
            v = attr(fonts, k)
            if v:
                d[f"font_{k}"] = v
    sz = first(rpr, "sz")
    if sz is not None:
        d["size_pt"] = int(attr(sz, "val", "0")) / 2
    if first(rpr, "b") is not None:
        d["bold"] = True
    color = first(rpr, "color")
    if color is not None:
        d["color"] = attr(color, "val")
    return d


def ppr_info(ppr):
    if ppr is None:
        return {}
    d = {}
    ol = first(ppr, "outlineLvl")
    if ol is not None:
        d["outline_lvl"] = int(attr(ol, "val", "0"))
    numpr = first(ppr, "numPr")
    if numpr is not None:
        nid = attr(first(numpr, "numId"), "val")
        ilvl = attr(first(numpr, "ilvl"), "val", "0")
        if nid is not None:
            d["num"] = f"numId={nid} ilvl={ilvl}"
    jc = first(ppr, "jc")
    if jc is not None:
        d["align"] = attr(jc, "val")
    sp = first(ppr, "spacing")
    if sp is not None:
        d["spacing"] = " ".join(f"{k}={v}" for k in ("before", "after", "line", "lineRule")
                                if (v := attr(sp, k)))
    ind = first(ppr, "ind")
    if ind is not None:
        d["indent"] = " ".join(f"{k}={v}" for k in
                               ("firstLine", "firstLineChars", "left", "leftChars", "hanging")
                               if (v := attr(ind, k)))
    return d


def unpack(docx, outdir):
    outdir = Path(outdir)
    res = subprocess.run(["unzip", "-o", "-q", str(docx), "-d", str(outdir)],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise WMError(f"解包失败: {res.stderr}")
    return outdir


def analyze_unpack(unpacked):
    """Return structured analysis dict from an unpacked docx dir."""
    r = {}
    sroot = ET.parse(Path(unpacked) / "word" / "styles.xml").getroot()
    dd = first(sroot, "docDefaults")
    if dd is not None:
        rprd = first(dd, "rPrDefault")
        r["doc_defaults"] = rpr_info(first(rprd, "rPr")) if rprd is not None else {}
    styles = {}
    for st in sroot.findall(f"{W}style"):
        stype = attr(st, "type")
        sid = attr(st, "styleId")
        name = attr(first(st, "name"), "val", "")
        if stype == "paragraph":
            styles[sid] = {"name": name,
                           "basedOn": attr(first(st, "basedOn"), "val"),
                           "next": attr(first(st, "next"), "val"),
                           **ppr_info(first(st, "pPr")),
                           **rpr_info(first(st, "rPr"))}
        else:
            styles.setdefault(f"_{stype}", []).append(f"{sid}={name}")
    r["styles"] = styles

    npath = Path(unpacked) / "word" / "numbering.xml"
    if npath.exists():
        nroot = ET.parse(npath).getroot()
        abstracts = {}
        for an in nroot.findall(f"{W}abstractNum"):
            aid = attr(an, "abstractNumId")
            lvls = []
            for lvl in an.findall(f"{W}lvl"):
                lvls.append({"ilvl": attr(lvl, "ilvl"),
                             "fmt": attr(first(lvl, "numFmt"), "val"),
                             "text": attr(first(lvl, "lvlText"), "val")})
            abstracts[aid] = lvls
        nummap = {attr(n, "numId"): attr(first(n, "abstractNumId"), "val")
                  for n in nroot.findall(f"{W}num")}
        r["numbering"] = {"abstracts": abstracts, "numId_map": nummap}

    droot = ET.parse(Path(unpacked) / "word" / "document.xml").getroot()
    body = first(droot, "body")
    outline, tables = [], 0
    for el_ in body:
        tag = el_.tag.replace(W, "")
        if tag == "p":
            ppr = first(el_, "pPr")
            text = "".join(t.text or "" for t in el_.iter(f"{W}t"))
            outline.append({"style": attr(first(ppr, "pStyle"), "val", "(Normal)"),
                            "text": text[:60]})
        elif tag == "tbl":
            tables += 1
            outline.append({"style": "<TABLE>", "text": f"rows={len(el_.findall(f'{W}tr'))}"})
    r["body_outline"] = outline
    r["body_table_count"] = tables

    sect = first(body, "sectPr") or body.find(f"{W}sectPr")
    if sect is not None:
        pg, mar = first(sect, "pgSz"), first(sect, "pgMar")
        r["page"] = {"size": {k: attr(pg, k) for k in ("w", "h", "orient")}, } if pg is not None else {}
        if mar is not None:
            r["page"]["margins"] = {k: attr(mar, k) for k in
                                    ("top", "bottom", "left", "right", "header", "footer")}
    return r


def format_analysis(r, src_name):
    L = [f"# 模板分析（机器草稿）— {src_name}", "",
         f"> 生成时间：{dt.datetime.now().isoformat(timespec='seconds')}；"
         "本文件为 template_manager analyze 产出的草稿，quirk/gap 判断需人工复核补充。", ""]
    L.append(f"## 文档默认字体\n\n{json.dumps(r.get('doc_defaults', {}), ensure_ascii=False)}\n")
    L.append("## 段落样式\n")
    L.append("| styleId | 名称 | basedOn | next | outline | 编号 | 对齐 | 间距 | 缩进 | 字体/字号 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for sid, s in r["styles"].items():
        if sid.startswith("_"):
            continue
        f_ = " ".join(f"{k}={v}" for k, v in s.items() if k.startswith("font") or k == "size_pt" or k == "bold")
        L.append(f"| {sid} | {s['name']} | {s.get('basedOn','')} | {s.get('next','')} "
                 f"| {s.get('outline_lvl','')} | {s.get('num','')} | {s.get('align','')} "
                 f"| {s.get('spacing','')} | {s.get('indent','')} | {f_} |")
    L.append("\n## 其他样式\n")
    for k, v in r["styles"].items():
        if k.startswith("_"):
            L.append(f"- {k[1:]}: {', '.join(v)}")
    if "numbering" in r:
        L.append("\n## 编号体系\n")
        nm = r["numbering"]["numId_map"]
        for aid, lvls in r["numbering"]["abstracts"].items():
            used_by = [nid for nid, a in nm.items() if a == aid]
            L.append(f"### abstractNum {aid}（numId: {', '.join(used_by)}）\n")
            for lv in lvls:
                L.append(f"- L{lv['ilvl']}: {lv['fmt']} `{lv['text']}`")
            L.append("")
    L.append("## 正文大纲\n")
    for i, o in enumerate(r["body_outline"], 1):
        L.append(f"{i:3d}. [{o['style']}] {o['text']}")
    if "page" in r:
        L.append(f"\n## 页面设置\n\n```json\n{json.dumps(r['page'], ensure_ascii=False, indent=2)}\n```\n")
    L.append("\n## 瑕疵登记（人工填写）\n\n| 瑕疵 | 影响 | 处置 |\n|---|---|---|\n| | | |")
    L.append("\n## 缺口清单（人工填写）\n\n1. ")
    return "\n".join(L)


def cmd_analyze(args):
    with tempfile.TemporaryDirectory(prefix="wm_analyze_") as td:
        unpacked = unpack(args.docx, td)
        r = analyze_unpack(unpacked)
    text = format_analysis(r, Path(args.docx).name)
    if args.out:
        out = Path(args.out) / "analysis.md"
        out.write_text(text, encoding="utf-8")
        print(f"分析草稿已写入: {out}")
    else:
        print(text)


def cmd_install(args):
    pkg = TEMPLATES / args.name
    if pkg.exists():
        raise WMError(f"模板包已存在: {pkg}")
    pkg.mkdir(parents=True)
    src = pkg / "template_src.docx"
    shutil.copy2(args.docx, src)
    with tempfile.TemporaryDirectory(prefix="wm_install_") as td:
        unpacked = unpack(src, td)
        r = analyze_unpack(unpacked)
    (pkg / "analysis.md").write_text(format_analysis(r, src.name), encoding="utf-8")
    # contract skeleton: auto-fill headings via outline+num, rest TODO
    heading_roles = {}
    for sid, s in r["styles"].items():
        if sid.startswith("_"):
            continue
        if s["name"].startswith("heading") and "num" in s:
            lvl = s.get("outline_lvl", int(s["name"].split()[-1]) - 1)
            heading_roles[f"h{lvl + 1}"] = sid
    contract = {
        "$schema": "word-master.template-contract.v1",
        "template": args.name,
        "version": 0,
        "date": dt.date.today().isoformat(),
        "source_docx": "template_src.docx",
        "built_docx": "template.docx",
        "doc": "template_contract.md",
        "styles": {**heading_roles, "_TODO": "body/figure/fig_caption/table_caption/table_cell/table/toc 等角色人工补齐"},
        "whitelist_paragraph_styles": sorted(heading_roles.values()),
        "blocked_paragraph_styles": [],
        "fonts": {"_TODO": "从 analysis 的 doc_defaults 与样式表归纳"},
        "numbering": {"_TODO": "从 analysis 归纳标题/题注/项目符号 numId"},
        "rules": {"_TODO": "题注方位、目录深度等人工确认"},
    }
    (pkg / "contract.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
    print(f"模板包骨架已建: {pkg}")
    print("  - template_src.docx（原件字节副本）")
    print("  - analysis.md（机器草稿，需人工补 quirk/gap）")
    print(f"  - contract.json（骨架，heading 已自动映射 {len(heading_roles)} 项，其余 _TODO 待补）")
    print("  下一步: 走 create-template.md Step 3（契约评审 ⛔）→ Step 4 清理壳 → Step 5 文档化")


def cmd_list(_args):
    if not TEMPLATES.exists():
        print("（模板库为空）")
        return
    for pkg in sorted(TEMPLATES.iterdir()):
        cj = pkg / "contract.json"
        if cj.exists():
            c = json.loads(cj.read_text(encoding="utf-8"))
            todo = json.dumps(c).count("_TODO")
            print(f"{pkg.name}  v{c.get('version')}  {c.get('date')}  " +
                  ("（契约含未补齐 _TODO）" if todo else "OK"))
        elif (pkg / "template_src.docx").exists():
            print(f"{pkg.name}  （未完成入库：缺 contract.json）")


def main():
    ap = argparse.ArgumentParser(description="word-master 模板库管理")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("list")
    sp.set_defaults(fn=cmd_list)
    sp = sub.add_parser("analyze")
    sp.add_argument("docx")
    sp.add_argument("--out", default=None)
    sp.set_defaults(fn=cmd_analyze)
    sp = sub.add_parser("install")
    sp.add_argument("docx")
    sp.add_argument("name")
    sp.set_defaults(fn=cmd_install)
    args = ap.parse_args()
    try:
        args.fn(args)
    except WMError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
