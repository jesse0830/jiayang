#!/usr/bin/env python3
"""Organize a cluttered working directory by an explicit move plan.

Usage:
  python3 organize_dir.py <ROOT> <PLAN.json> [--trash DIR] [--manifest PATH] [--dry-run]

PLAN.json maps destination (relative to ROOT) -> list of top-level names:
  {
    "01 绩效与人事": ["绩效分析_v1.2.md", "人员清单.xlsx"],
    "_归档/旧版本": ["绩效分析_v1.0.md"],
    "__TRASH__": ["被取代的合并版.docx"]
  }

Rules: never delete; __TRASH__ goes to ~/.Trash/<root>_清理_<date>/
(recoverable via Finder); collisions and missing sources are reported, never
overwritten; every move is written to a manifest so the run can be undone.
"""
import argparse
import datetime
import json
import os
import shutil

TRASH_KEY = "__TRASH__"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("plan")
    ap.add_argument("--trash", default=None)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = os.path.abspath(os.path.expanduser(a.root))
    today = datetime.date.today()
    with open(a.plan, encoding="utf-8") as f:
        plan = json.load(f)

    trash = a.trash or os.path.join(
        os.path.expanduser("~/.Trash"),
        f"{os.path.basename(root)}_清理_{today:%Y%m%d}",
    )
    manifest = a.manifest or os.path.join(root, "_归档", f"整理清单_{today:%Y%m%d}.json")

    def dest_dir(key: str) -> str:
        return trash if key == TRASH_KEY else os.path.join(root, key)

    if not a.dry_run:
        for key in plan:
            if key != TRASH_KEY:
                os.makedirs(dest_dir(key), exist_ok=True)
        if TRASH_KEY in plan:
            os.makedirs(trash, exist_ok=True)

    moved, conflicts = [], []
    for key, names in plan.items():
        for name in names:
            src = os.path.join(root, name)
            dst = os.path.join(dest_dir(key), name)
            if not os.path.exists(src):
                conflicts.append({"file": name, "reason": "源不存在"})
                continue
            if os.path.exists(dst):
                conflicts.append({"file": name, "reason": f"目标已存在：{dst}"})
                continue
            if not a.dry_run:
                shutil.move(src, dst)
            moved.append({"from": src, "to": dst, "group": key})

    if not a.dry_run:
        os.makedirs(os.path.dirname(manifest), exist_ok=True)
        with open(manifest, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "root": root,
                    "trash": trash,
                    "moved": moved,
                    "conflicts": conflicts,
                    "at": datetime.datetime.now().isoformat(timespec="seconds"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    print(("DRY-RUN " if a.dry_run else "") + f"moved={len(moved)} conflicts={len(conflicts)}")
    for c in conflicts:
        print("  !", c["file"], "-", c["reason"])
    if not a.dry_run:
        print("manifest:", manifest)
        print("undo: replay manifest moved[] backwards (to -> from)")
        print("remaining top level:")
        for x in sorted(os.listdir(root)):
            print("  ", x)


if __name__ == "__main__":
    main()
