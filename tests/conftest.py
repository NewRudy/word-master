# -*- coding: utf-8 -*-
"""Shared pytest fixtures: import the scripts as modules without installing."""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills" / "word-master" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture(scope="session")
def repo():
    return REPO


@pytest.fixture(scope="session")
def scripts():
    return SCRIPTS


@pytest.fixture(scope="session")
def contract():
    import wm_common

    return wm_common.load_contract("qiji_heading")


@pytest.fixture()
def demo_project(tmp_path):
    """A copy of the bundled demo project, so tests never mutate the repo."""
    import shutil

    src = REPO / "projects" / "_demo"
    dst = tmp_path / "demo"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("exports", "*.docx"))
    (dst / "exports").mkdir(exist_ok=True)
    return dst
