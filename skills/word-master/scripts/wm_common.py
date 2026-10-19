# -*- coding: utf-8 -*-
"""Shared library for word-master scripts: paths, contract loading, project I/O."""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / "templates" / "docs"
PROJECTS = REPO / "projects"


def resolve_project(project_path):
    """Accept an absolute path, a path relative to cwd, or a bare project name.

    A bare name is looked up under the repo's projects/ directory, so the
    README can document `... check _demo` as well as `... check projects/_demo`.
    """
    p = Path(project_path)
    if p.exists():
        return p
    if not p.is_absolute() and len(p.parts) == 1:
        cand = PROJECTS / p
        if cand.exists():
            return cand
        # `init <name>` creates `<slug>_<YYYYMMDD>`; accept the bare name and
        # resolve to the most recent matching directory (the date suffix sorts
        # lexicographically, so a reverse sort yields the newest project).
        if PROJECTS.is_dir():
            matches = sorted(
                (d for d in PROJECTS.iterdir()
                 if d.is_dir() and (d.name == p.name or d.name.startswith(p.name + "_"))),
                reverse=True,
            )
            if matches:
                return matches[0]
    raise WMError(f"项目不存在: {project_path}（也不是 projects/ 下的目录名）")

FACT_SCHEMA = "word-master.fact-provenance.v1"


class WMError(Exception):
    pass


def load_contract(template_name):
    """Load contract.json for a template package."""
    pkg = TEMPLATES / template_name
    cj = pkg / "contract.json"
    if not cj.exists():
        raise WMError(f"模板契约不存在: {cj}（模板未入库？先走 create-template 路线）")
    return json.loads(cj.read_text(encoding="utf-8"))


def load_project(project_path):
    p = Path(project_path)
    pj = p / "project.json"
    if not pj.exists():
        raise WMError(f"不是有效的 word-master 项目（缺 project.json）: {p}")
    return json.loads(pj.read_text(encoding="utf-8")), p


def save_project(meta, project_path):
    (Path(project_path) / "project.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(name):
    s = re.sub(r"\s+", "_", name.strip())
    s = re.sub(r"[^\w一-鿿\-]", "", s)
    return s or "untitled"


def empty_facts():
    return {"$schema": FACT_SCHEMA, "facts": []}


CONTENT_SKELETON = """@title: （文档主标题）
@template: {template}

<!-- 按确认的大纲写正文。语法见 skills/word-master/references/content-grammar.md -->

# 第一章标题

正文段落……<!-- F001 -->
"""
