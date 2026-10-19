# -*- coding: utf-8 -*-
"""Shared library for word-master scripts: paths, contract loading, project I/O."""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / "templates" / "docs"
PROJECTS = REPO / "projects"

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
