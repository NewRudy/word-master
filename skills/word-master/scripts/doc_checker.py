# -*- coding: utf-8 -*-
"""word-master checker: verify built DOCX against template contract.

Fail-closed: any blocking finding exits non-zero. Run after every build.

Usage: doc_checker.py check <project_path> [--json]
"""
import argparse
import json
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from wm_common import REPO, WMError, load_contract, load_project, resolve_project

HAND_HEADING_NUM = re.compile(r"^\s*\d+(\.\d+)+\s")          # "1.1 标题"（编号应为域）
HAND_CAPTION_NUM = re.compile(r"^\s*[图表]\s*\d")             # "图1.1-1 xxx"（编号应为域）
ALLOWED_DIRECT_RPR = {"b", "bCs", "i", "iCs", "vertAlign"}    # run 级直接格式白名单


class Findings:
    def __init__(self):
        self.items = []

    def add(self, level, rule, detail, where=""):
        self.items.append({"level": level, "rule": rule, "detail": detail, "where": where})

    def blocking(self):
        return [f for f in self.items if f["level"] == "blocking"]

    def advisory(self):
        return [f for f in self.items if f["level"] == "advisory"]


def iter_block_items(doc):
    """Yield ('p', element) / ('tbl', element) in body order."""
    for child in doc.element.body:
        tag = child.tag
        if tag == qn("w:p"):
            yield "p", child
        elif tag == qn("w:tbl"):
            yield "tbl", child


def para_style_id(p):
    ppr = p.find(qn("w:pPr"))
    ps = ppr.find(qn("w:pStyle")) if ppr is not None else None
    return ps.get(qn("w:val")) if ps is not None else "1"


def para_text(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def check(docx_path, contract, facts):
    c = contract
    f = Findings()
    doc = Document(str(docx_path))
    styles = c["styles"]
    whitelist = set(c["whitelist_paragraph_styles"])
    blocked_styles = set(c.get("blocked_paragraph_styles", []))
    blocked_numids = set(c["numbering"].get("blocked_numIds", []))
    cjk_ok = set(c["fonts"]["cjk_allowed"])
    latin_ok = set(c["fonts"]["latin_allowed"])
    exempt = c["fonts"].get("exempt", {}).get("style", {})

    role_of = {}
    for role, sid in styles.items():
        if isinstance(sid, str):
            role_of.setdefault(sid, role)

    prev = {"empty": 0}
    last_fig_p = None            # pending figure awaiting caption
    pending_tbl_cap = None       # pending table caption awaiting table
    captioned_tbls = 0
    tbl_count = 0
    seen_figs = []

    for bi, (kind, elx) in enumerate(iter_block_items(doc), 1):
        where = f"body#{bi}"
        if kind == "p":
            sid = para_style_id(elx)
            text = para_text(elx)

            # C1 whitelist / blocked
            if sid in blocked_styles:
                f.add("blocking", "C1", f"使用了禁用样式 styleId={sid}", where)
            elif sid not in whitelist:
                f.add("blocking", "C1", f"样式不在契约白名单: styleId={sid}", where)

            # C5 blocked auto-numbering
            ppr = elx.find(qn("w:pPr"))
            numpr = ppr.find(qn("w:numPr")) if ppr is not None else None
            if numpr is not None:
                nid_el = numpr.find(qn("w:numId"))
                nid = int(nid_el.get(qn("w:val"))) if nid_el is not None else None
                if nid in blocked_numids:
                    f.add("blocking", "C5", f"7级以下使用了自动编号 numId={nid}（应手打序号）", where)

            # C4 hand-typed numbering prefixes
            role = role_of.get(sid, "")
            if role.startswith("h") and HAND_HEADING_NUM.match(text):
                f.add("blocking", "C4", f"标题疑似手打编号: {text[:24]!r}", where)
            if role in ("fig_caption", "table_caption") and HAND_CAPTION_NUM.match(text):
                f.add("blocking", "C4", f"题注疑似手打编号: {text[:24]!r}", where)

            # C2/C3 run-level fonts & direct formatting
            for rpr in elx.iter(qn("w:rPr")):
                exempt_ok = set(exempt.get(sid, []))
                for fonts in rpr.findall(qn("w:rFonts")):
                    for k in ("ascii", "hAnsi", "eastAsia", "cs"):
                        v = fonts.get(qn(f"w:{k}"))
                        if v and v not in (cjk_ok | latin_ok | exempt_ok):
                            f.add("blocking", "C2",
                                  f"run 字体越权: {v!r}（样式 {sid}）", where)
                for child in rpr:
                    tag = child.tag.replace(qn("w:"), "")
                    if tag not in ALLOWED_DIRECT_RPR and not tag.startswith(("rFonts", "sz")):
                        if tag in ("sz", "szCs", "color", "highlight", "u", "strike", "shd"):
                            f.add("blocking", "C3", f"run 直接格式越权: <w:{tag}>（样式 {sid}）", where)

            # C8 consecutive empties (structural paras w/ fields or page breaks exempt)
            structural = (elx.find(f".//{qn('w:fldChar')}") is not None
                          or elx.find(f".//{qn('w:br')}") is not None)
            if not text.strip() and structural:
                prev["empty"] = 0
            elif not text.strip():
                prev["empty"] += 1
                if prev["empty"] > 1:
                    f.add("advisory", "C8", f"连续空段落 {prev['empty']}", where)
            else:
                prev["empty"] = 0

            # C6 figure → caption adjacency
            if sid == styles["figure"]:
                if last_fig_p is not None:
                    f.add("blocking", "C6", f"图片段（{last_fig_p}）之后不是图名", where)
                last_fig_p = where
            elif sid == styles["fig_caption"]:
                if last_fig_p is None:
                    f.add("blocking", "C6", "图名前没有相邻图片段", where)
                seen_figs.append((last_fig_p, where))
                last_fig_p = None
            elif sid == styles["table_caption"]:
                if pending_tbl_cap is not None:
                    f.add("blocking", "C6", f"表题（{pending_tbl_cap}）之后没有表格", where)
                pending_tbl_cap = where
            else:
                if last_fig_p is not None:
                    f.add("blocking", "C6", f"图片段（{last_fig_p}）之后不是图名", where)
                    last_fig_p = None
                if pending_tbl_cap is not None and text.strip():
                    f.add("blocking", "C6", f"表题（{pending_tbl_cap}）之后没有表格", where)
                    pending_tbl_cap = None

        else:  # table
            tbl_count += 1
            tblpr = elx.find(qn("w:tblPr"))
            tstyle = tblpr.find(qn("w:tblStyle")) if tblpr is not None else None
            sid = tstyle.get(qn("w:val")) if tstyle is not None else None
            # C7 table style
            if sid != styles["table"]:
                f.add("blocking", "C7", f"表格样式非契约指定样式: {sid}", where)
            # C7 cell paragraph style
            for p in elx.iter(qn("w:p")):
                psid = para_style_id(p)
                if psid != styles["table_cell"]:
                    f.add("blocking", "C7", f"单元格段落样式非 {styles['table_cell']}: {psid}", where)
                    break
            # C6 caption above table
            if pending_tbl_cap is None:
                f.add("blocking", "C6", f"表格（{where}）上方没有表题", where)
            else:
                captioned_tbls += 1
                pending_tbl_cap = None

    if last_fig_p is not None:
        f.add("blocking", "C6", f"图片段（{last_fig_p}）之后不是图名", last_fig_p)
    if pending_tbl_cap is not None:
        f.add("blocking", "C6", f"表题（{pending_tbl_cap}）之后没有表格", pending_tbl_cap)

    # facts reconciliation: content.md citations vs facts.json
    cpath = docx_path.parent.parent / "content.md"
    if cpath.exists():
        cited = set(re.findall(r"<!--\s*(F\d+)\s*-->", cpath.read_text(encoding="utf-8")))
        known = {x.get("id") for x in facts.get("facts", [])}
        for miss in sorted(cited - known):
            f.add("blocking", "R1", f"content 引用未登记事实: {miss}")
        for orphan in sorted(known - cited):
            f.add("advisory", "R2", f"facts.json 中事实未被引用: {orphan}")

    return f, {"figs": len(seen_figs), "tbls": tbl_count, "captioned_tbls": captioned_tbls}


def cmd_check(args):
    meta, ppath = load_project(resolve_project(args.project_path))
    contract = load_contract(meta["template"])
    exports = sorted((ppath / "exports").glob("*.docx"))
    if not exports:
        raise WMError("exports/ 下没有构建产物，先跑 docx_builder.py build")
    target = exports[-1]
    facts = json.loads((ppath / "facts.json").read_text(encoding="utf-8"))

    f, stats = check(target, contract, facts)
    try:
        # 仓库内产物写相对路径，报告可安全提交/分享
        target_ref = target.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        target_ref = str(target.resolve())
    report = {
        "$schema": "word-master.check-report.v1",
        "target": target_ref,
        "template": meta["template"],
        "blocking": len(f.blocking()),
        "advisory": len(f.advisory()),
        "stats": stats,
        "findings": f.items,
    }
    if args.json:
        (ppath / "check_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[CHECK] {target.name}  模板={meta['template']}")
    print(f"  图 {stats['figs']} 张（含图名）  表 {stats['tbls']} 张（含表题 {stats['captioned_tbls']}）")
    for x in f.blocking():
        print(f"  BLOCKING [{x['rule']}] {x['detail']}  @{x['where']}")
    for x in f.advisory():
        print(f"  advisory [{x['rule']}] {x['detail']}  @{x['where']}")
    verdict = "PASS" if not f.blocking() else "FAIL"
    print(f"  => {verdict}  blocking={len(f.blocking())} advisory={len(f.advisory())}"
          + ("  （报告已写 check_report.json）" if args.json else ""))
    sys.exit(0 if not f.blocking() else 1)


def main():
    ap = argparse.ArgumentParser(description="word-master 质量门禁")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("check")
    sp.add_argument("project_path")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_check)
    args = ap.parse_args()
    try:
        args.fn(args)
    except WMError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
