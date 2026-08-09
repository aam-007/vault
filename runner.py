#!/usr/bin/env python3

import json
import os
import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

VAULT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=VAULT_DIR,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()

MANIFEST_PATH = os.path.join(VAULT_DIR, "manifest.json")

IGNORE_FILES = {
    "manifest.json",
    "runner.py",
    ".DS_Store",
    ".gitkeep",
}

LEC_PATTERN = re.compile(r"Lec0*(\d+)", re.IGNORECASE)
IST = ZoneInfo("Asia/Kolkata")


def natural_key(filename):
    match = LEC_PATTERN.search(filename)
    if match:
        return (0, int(match.group(1)), filename.lower())
    return (1, 0, filename.lower())


def iso(ts):
    return datetime.fromtimestamp(ts, IST).isoformat(timespec="seconds")


def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "K", "M", "G"):
        if size < 1024 or unit == "G":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}G"


def visible_dirs(path):
    return sorted(
        d
        for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
        and not d.startswith(".")
    )


def collect_files(path, rel_parts):
    """Recursively collect file path-parts under `path`, depth-first,
    files-before-subdirs, each level naturally sorted."""
    entries = os.listdir(path)

    dirs = sorted(
        d
        for d in entries
        if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")
    )

    files = [
        f
        for f in entries
        if os.path.isfile(os.path.join(path, f))
        and not f.startswith(".")
        and f not in IGNORE_FILES
    ]
    files.sort(key=natural_key)

    results = [rel_parts + [f] for f in files]

    for d in dirs:
        results.extend(collect_files(os.path.join(path, d), rel_parts + [d]))

    return results


def scan():
    tree = {}
    newest_file = None

    for semester in visible_dirs(VAULT_DIR):
        sem_path = os.path.join(VAULT_DIR, semester)
        tree[semester] = {}

        for subject in visible_dirs(sem_path):
            subj_path = os.path.join(sem_path, subject)
            entries = []

            for parts in collect_files(subj_path, []):
                filename = parts[-1]
                folder = "/".join(parts[:-1])  # "" if file sits directly in subject
                full_path = os.path.join(subj_path, *parts)
                stat = os.stat(full_path)

                rel_path = "/".join([semester, subject, *parts])

                entries.append(
                    {
                        "name": filename,
                        "folder": folder,
                        "path": rel_path,
                        "size": stat.st_size,
                        "size_human": human_size(stat.st_size),
                        "modified": iso(stat.st_mtime),
                    }
                )

                if newest_file is None or stat.st_mtime > newest_file["mtime"]:
                    newest_file = {
                        "mtime": stat.st_mtime,
                        "path": rel_path,
                        "name": filename,
                    }

            tree[semester][subject] = entries

    manifest = {
        "generated_at": datetime.now(IST).isoformat(timespec="seconds"),
        "recent_file": (
            {
                "path": newest_file["path"],
                "name": newest_file["name"],
                "modified": iso(newest_file["mtime"]),
            }
            if newest_file
            else None
        ),
        "tree": tree,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_files = sum(
        len(files)
        for semester in tree.values()
        for files in semester.values()
    )

    print(
        f"Wrote {MANIFEST_PATH} — {total_files} file(s) across {len(tree)} semester(s)"
    )


def git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


def git_commit_and_push():
    git("add", ".")

    status = git("status", "--porcelain")

    if not status:
        print("No changes detected.")
        return

    branch = git("branch", "--show-current")

    timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")

    git(
        "commit",
        "-m",
        f"Update vault ({timestamp})",
    )

    git("push", "origin", branch)

    print(f"Committed and pushed to '{branch}'.")


def main():
    scan()
    git_commit_and_push()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        raise