#!/usr/bin/env python3
import argparse
import tempfile
import zipfile
from pathlib import Path

import requests


IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
}


def should_skip(relative_path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in relative_path.parts)


def zip_dir(source: Path, target_zip: Path) -> None:
    source = source.resolve()

    if not (source / "Dockerfile").exists():
        raise SystemExit(f"Dockerfile not found in: {source}")

    with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for file in source.rglob("*"):
            relative = file.relative_to(source)
            if file.is_file() and not should_skip(relative):
                z.write(file, relative)


def main():
    parser = argparse.ArgumentParser(description="Submit solution to TUSUR judge")
    parser.add_argument("--server", required=True, help="Judge server URL, for example http://1.2.3.4:8000")
    parser.add_argument("--team", required=True, help="Team name")
    parser.add_argument("--task", required=True, help="Task slug, for example 04-arena-scheduler")
    parser.add_argument("--path", required=True, help="Path to solution directory")
    args = parser.parse_args()

    source = Path(args.path)
    if not source.exists():
        raise SystemExit(f"Path not found: {source}")

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "solution.zip"
        zip_dir(source, zip_path)

        url = args.server.rstrip("/") + "/submit_zip"
        with zip_path.open("rb") as f:
            response = requests.post(
                url,
                data={
                    "team": args.team,
                    "task": args.task,
                },
                files={
                    "archive": ("solution.zip", f, "application/zip"),
                },
                timeout=600,
            )

    print("Status:", response.status_code)
    try:
        print(response.json())
    except Exception:
        print(response.text)


if __name__ == "__main__":
    main()
