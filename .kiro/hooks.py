#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repository hooks for crude_oil_schedules_with_RL.

用法：
    python .kiro/hooks.py pre-commit   # 检查已 staged 的改动（可直接被 git 调用）
    python .kiro/hooks.py install      # 把本脚本装成 .git/hooks/pre-commit
    python .kiro/hooks.py check-all    # 全仓库语法体检，不依赖 git 状态

只依赖标准库，Windows / Linux 均可直接跑。
"""
import ast
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_MB = 20
BLOCKED_SUFFIX = (".pth", ".pt", ".ckpt", ".pyc", ".pyo", ".log")
BLOCKED_DIR = ("__pycache__", ".ipynb_checkpoints")


def git(*args):
    p = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    return p.stdout.strip().splitlines()


def staged_files():
    return [f for f in git("diff", "--cached", "--name-only", "--diff-filter=ACM") if f]


def all_py():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git",) and d not in BLOCKED_DIR]
        for f in files:
            if f.endswith(".py"):
                out.append(os.path.relpath(os.path.join(base, f), ROOT))
    return out


def check_python(files):
    bad = []
    for rel in files:
        if not rel.endswith(".py"):
            continue
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "rb") as fh:
                ast.parse(fh.read(), filename=rel)
        except SyntaxError as e:
            bad.append(f"{rel}:{e.lineno}: {e.msg}")
    return bad


def check_artifacts(files):
    bad = []
    for rel in files:
        parts = rel.replace("\\", "/").split("/")
        if any(p in BLOCKED_DIR for p in parts):
            bad.append(f"{rel}: 编译缓存/检查点目录不应入库")
            continue
        if rel.lower().endswith(BLOCKED_SUFFIX):
            bad.append(f"{rel}: 训练产物不应入库（用 .gitignore 排除）")
            continue
        path = os.path.join(ROOT, rel)
        if os.path.exists(path) and os.path.getsize(path) > MAX_MB * 1024 * 1024:
            bad.append(f"{rel}: 超过 {MAX_MB} MB")
    return bad


def check_meta(files):
    bad = []
    for rel in files:
        name = os.path.basename(rel)
        if name == "agents.json":
            try:
                with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                    json.load(fh)
            except Exception as e:  # noqa: BLE001
                bad.append(f"{rel}: JSON 解析失败 -> {e}")
        if name.endswith(".yaml"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    s = line.rstrip("\n")
                    if "\t" in s:
                        bad.append(f"{rel}:{i}: YAML 不允许制表符缩进")
    return bad


def report(title, problems):
    if not problems:
        return True
    print(f"[hooks] {title}")
    for p in problems:
        print("   ✗", p)
    return False


def pre_commit():
    files = staged_files() or all_py()
    ok = True
    ok &= report("语法检查失败", check_python(files))
    ok &= report("文件检查失败", check_artifacts(files))
    ok &= report("元数据检查失败", check_meta(files))
    if ok:
        print(f"[hooks] OK — 检查 {len(files)} 个文件")
    return 0 if ok else 1


def install():
    hook = os.path.join(ROOT, ".git", "hooks", "pre-commit")
    os.makedirs(os.path.dirname(hook), exist_ok=True)
    body = "#!/bin/sh\npython \"$(git rev-parse --show-toplevel)/.kiro/hooks.py\" pre-commit\n"
    with open(hook, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    try:
        os.chmod(hook, 0o755)
    except OSError:
        pass
    print(f"[hooks] installed -> {hook}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pre-commit"
    if cmd == "install":
        sys.exit(install())
    if cmd in ("pre-commit", "check-all"):
        sys.exit(pre_commit())
    print(__doc__)
    sys.exit(2)
