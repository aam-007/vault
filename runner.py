#!/usr/bin/env python3
"""
runner.py

Scans the vault/ directory tree and writes vault/manifest.json.
No GitHub API calls — this is meant to be run locally (or in a
GitHub Action / pre-commit hook) before pushing to GitHub Pages,
so index.html only ever reads a static JSON file.

Expected layout:

    <repo root>/
      index.html
      vault/              <- this script lives here
        runner.py
        <semester>/
          <subject>/
            <subject>_Lec<N>.<ext>
            ...

Any folder depth of exactly semester/subject is picked up
automatically — no filenames are hardcoded. Run this after
adding, renaming, or removing files (from anywhere — the script
locates the vault folder from its own file location), then
commit the updated manifest.json alongside your notes.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

# The folder this script lives in IS the vault folder.
VAULT_DIR = os.path.dirname(os.path.abspath(__file__))
# Name of that folder, used as the path prefix in manifest.json so links
# in index.html (which sits one level up, at the repo root) resolve correctly.
VAULT_NAME = os.path.basename(VAULT_DIR.rstrip(os.sep))
MANIFEST_PATH = os.path.join(VAULT_DIR, "manifest.json")
IGNORE = {"manifest.json", ".DS_Store", ".gitkeep", "runner.py"}

# subject_Lec<number> naming convention — used only for natural sort,
# files that don't match are still listed, just sorted alphabetically after.
LEC_PATTERN = re.compile(r"Lec0*(\d+)", re.IGNORECASE)


def natural_key(filename):
    match = LEC_PATTERN.search(filename)
    if match:
        return (0, int(match.group(1)), filename.lower())
    return (1, 0, filename.lower())


def iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().isoformat(
        timespec="seconds"
    )


def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "K", "M", "G"):
        if size < 1024 or unit == "G":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}G"


def scan():
    tree = {}
    newest_file = None  # (mtime, relpath, name)

    semesters = sorted(
        d for d in os.listdir(VAULT_DIR)
        if os.path.isdir(os.path.join(VAULT_DIR, d)) and d not in IGNORE
    )

    for semester in semesters:
        sem_path = os.path.join(VAULT_DIR, semester)
        subjects = sorted(
            d for d in os.listdir(sem_path)
            if os.path.isdir(os.path.join(sem_path, d)) and d not in IGNORE
        )

        tree[semester] = {}

        for subject in subjects:
            subj_path = os.path.join(sem_path, subject)
            files = [
                f for f in os.listdir(subj_path)
                if os.path.isfile(os.path.join(subj_path, f)) and f not in IGNORE
            ]
            files.sort(key=natural_key)

            entries = []
            for f in files:
                fpath = os.path.join(subj_path, f)
                stat = os.stat(fpath)
                rel = "/".join([VAULT_NAME, semester, subject, f])
                entries.append({
                    "name": f,
                    "path": rel,
                    "size": stat.st_size,
                    "size_human": human_size(stat.st_size),
                    "modified": iso(stat.st_mtime),
                })
                if newest_file is None or stat.st_mtime > newest_file[0]:
                    newest_file = (stat.st_mtime, rel, f)

            tree[semester][subject] = entries

    manifest = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "recent_file": (
            {"path": newest_file[1], "name": newest_file[2], "modified": iso(newest_file[0])}
            if newest_file else None
        ),
        "tree": tree,
    }

    with open(MANIFEST_PATH, "w") as fh:
        json.dump(manifest, fh, indent=2)

    total_files = sum(len(files) for subj in tree.values() for files in subj.values())
    print(f"wrote {MANIFEST_PATH} — {total_files} file(s) across {len(tree)} semester(s)")


if __name__ == "__main__":
    scan()