#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create the word-master mirror repositories and push to them.

Usage:
    GITEE_TOKEN=xxxx python scripts/mirror.py --gitee
    GITEE_TOKEN=xxxx ATOMGIT_TOKEN=yyyy python scripts/mirror.py --all

Why this script exists rather than a few shell commands: creating a repo on
Gitee/AtomGit needs an access token, and the repo description, topics and
default branch have to be set at creation time or they end up inconsistent
between the GitHub original and the mirror. This does all of it and is safe to
re-run.

Token setup:
  Gitee   https://gitee.com/profile/personal_access_tokens
          scopes: projects (read/write)
  AtomGit https://atomgit.com/-/profile/personal_access_tokens
          scopes: repo (read/write)

The script never stores the token. Export it for the duration of the command.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

NAME = "word-master"
OWNER_HINT = os.environ.get("MIRROR_OWNER", "NewRudy")

DESCRIPTION = (
    "模板驱动的 Word 工程文档生产线：AI 只写内容，格式由单位模板契约锁定，"
    "确定性脚本注入，fail-closed 门禁把关。"
)

TOPICS = [
    "docx", "word", "ai", "ai-agents", "skill", "template",
    "engineering-report", "ooxml", "python-docx", "claude-code",
    "document-automation", "office-automation",
]


def run(args, cwd=None, check=True):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)


def api(url, token, method="GET", payload=None, auth_header="Authorization", auth_scheme="Bearer"):
    """Call a REST endpoint.

    Gitee uses `Authorization: Bearer <token>`; AtomGit (GitLab-compatible)
    expects `private-token: <token>`. Passing the wrong one yields a 401 that
    looks like a bad token, which is a confusing failure to debug.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "word-master-mirror",
    }
    headers[auth_header] = f"{auth_scheme} {token}" if auth_scheme else token
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            return r.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body}


def ensure_remote(remote_url, token, cwd):
    """Push main and tags to a mirror without putting the token on the command line.

    `git push https://user:token@host/...` leaks the token into the process list
    (`ps aux`) and into any error message. Feed it through an environment
    variable and a throwaway credential helper instead.
    """
    env = dict(os.environ)
    env["MIRROR_GIT_TOKEN"] = token
    helper = '!f() { echo "username=oauth2"; echo "password=$MIRROR_GIT_TOKEN"; }; f'
    base = ["git", "-c", f"credential.helper={helper}"]

    for refspec in ("main", None):
        args = base + ["push", "--prune", remote_url]
        args += [refspec] if refspec else ["--tags"]
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            # Scrub anything that looks like a credential, then show the real
            # error. Hiding it entirely makes a transient failure
            # indistinguishable from a broken token.
            err = re.sub(r"(https://)[^@/\s]+@", r"\1***@", proc.stderr or proc.stdout)
            print(f"    push {refspec or '--tags'} 失败 (exit {proc.returncode}):")
            for line in err.strip().splitlines()[-6:]:
                print(f"      {line}")
            if refspec == "main":
                raise RuntimeError("主分支推送失败，镜像未建立")


def mirror_gitee(token, cwd):
    base = "https://gitee.com/api/v5"
    status, me = api(f"{base}/user?access_token={token}", token)
    if status != 200:
        print(f"  Gitee 认证失败 ({status}): {me}")
        return False
    owner = me.get("login")
    print(f"  Gitee 账号: {owner}")

    status, repo = api(f"{base}/repos/{owner}/{NAME}?access_token={token}", token)
    if status == 200:
        print(f"  Gitee 仓库已存在: {repo.get('html_url')}")
    else:
        status, repo = api(f"{base}/user/repos?access_token={token}", token, "POST", {
            "name": NAME,
            "description": DESCRIPTION,
            "private": False,
            "has_issues": True,
            "has_wiki": False,
            "default_branch": "main",
        })
        if status not in (200, 201):
            print(f"  Gitee 建仓失败 ({status}): {repo}")
            return False
        print(f"  Gitee 仓库已创建: {repo.get('html_url')}")

    # topics 在 Gitee 上叫 topics，需要单独接口
    status, _ = api(f"{base}/repos/{owner}/{NAME}/topics?access_token={token}",
                    token, "PUT", {"topics": TOPICS})
    print(f"  Gitee topics: {'ok' if status in (200, 204) else f'failed ({status})'}")

    ensure_remote(f"https://gitee.com/{owner}/{NAME}.git", token, cwd)
    print(f"  Gitee 推送完成: https://gitee.com/{owner}/{NAME}")
    return True


def mirror_atomgit(token, cwd):
    """AtomGit exposes a GitLab-compatible v5 API at atomgit.com/api/v5."""
    base = "https://atomgit.com/api/v5"
    AUTH = {"auth_header": "private-token", "auth_scheme": ""}

    status, me = api(f"{base}/user", token, **AUTH)
    if status != 200:
        print(f"  AtomGit 认证失败 ({status}): {str(me)[:160]}")
        return False
    owner = me.get("login") or me.get("username") or OWNER_HINT
    print(f"  AtomGit 账号: {owner}")

    status, repo = api(f"{base}/repos/{owner}/{NAME}", token, **AUTH)
    if status == 200:
        print(f"  AtomGit 仓库已存在: {repo.get('html_url')}")
        # AtomGit 的 PATCH 要求一组必填字段，缺一个就是 400 且不说明缺哪个
        payload = {"name": NAME, "description": DESCRIPTION, "public": True,
                   "private": False, "default_branch": "main",
                   "visibility": "public", "issues_enabled": True,
                   "wiki_enabled": False, "jobs_enabled": False}
        st, _ = api(f"{base}/repos/{owner}/{NAME}", token, "PATCH", payload, **AUTH)
        print(f"  AtomGit 描述: {'ok' if st == 200 else f'skipped ({st})'}")
    else:
        status, repo = api(f"{base}/user/repos", token, "POST", {
            "name": NAME,
            "description": DESCRIPTION,
            "private": False,
            "default_branch": "main",
        }, **AUTH)
        if status not in (200, 201):
            print(f"  AtomGit 建仓失败 ({status}): {str(repo)[:200]}")
            print("  → 可手动建仓 https://atomgit.com/projects/new （不要初始化 README）后重跑")
            return False
        print(f"  AtomGit 仓库已创建: {repo.get('html_url')}")

    status, _ = api(f"{base}/repos/{owner}/{NAME}/topics", token, "PUT",
                    {"topics": TOPICS}, **AUTH)
    print(f"  AtomGit topics: {'ok' if status in (200, 204) else f'skipped ({status})'}")

    ensure_remote(f"https://atomgit.com/{owner}/{NAME}.git", token, cwd)
    print(f"  AtomGit 推送完成: https://atomgit.com/{owner}/{NAME}")
    return True


def main():
    ap = argparse.ArgumentParser(description="创建并推送 word-master 镜像仓库")
    ap.add_argument("--gitee", action="store_true", help="镜像到 Gitee")
    ap.add_argument("--atomgit", action="store_true", help="镜像到 AtomGit")
    ap.add_argument("--all", action="store_true", help="两个都做")
    ap.add_argument("--repo", default=".", help="本地仓库路径")
    ap.add_argument("--token-file", default=None,
                    help="从文件读取 token（比环境变量更适合交互式终端）")
    args = ap.parse_args()

    do_gitee = args.gitee or args.all
    do_atomgit = args.atomgit or args.all
    if not (do_gitee or do_atomgit):
        ap.error("至少指定 --gitee / --atomgit / --all")

    cwd = os.path.abspath(args.repo)
    status = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd, check=False)
    if status.returncode != 0:
        print(f"不是 git 仓库: {cwd}")
        return 1

    if args.token_file:
        try:
            with open(args.token_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
        except OSError as e:
            print(f"无法读取 --token-file: {e}")
            return 1

    ok = True
    try:
        ok = _run_mirrors(args, do_gitee, do_atomgit, cwd)
    except RuntimeError as e:
        print(f"失败: {e}")
        ok = False

    print()
    if ok:
        print("完成。把镜像链接补回 README.md / README_CN.md 的 Quick Start。")
        return 0
    print("部分失败，见上。")
    return 1


def _run_mirrors(args, do_gitee, do_atomgit, cwd):
    ok = True
    if do_gitee:
        token = os.environ.get("GITEE_TOKEN")
        if not token:
            print("缺少 GITEE_TOKEN（https://gitee.com/profile/personal_access_tokens）")
            ok = False
        else:
            print("== Gitee ==")
            ok &= mirror_gitee(token, cwd)

    if do_atomgit:
        token = os.environ.get("ATOMGIT_TOKEN")
        if not token:
            print("缺少 ATOMGIT_TOKEN（https://atomgit.com/-/profile/personal_access_tokens）")
            ok = False
        else:
            print("== AtomGit ==")
            ok &= mirror_atomgit(token, cwd)

    return ok


if __name__ == "__main__":
    sys.exit(main())
