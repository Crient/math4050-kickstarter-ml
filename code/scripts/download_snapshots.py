"""Download dated Web Robots archives into raw_snapshots/."""

import argparse
import json
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from urllib.request import urlopen
from zipfile import ZipFile


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "raw_snapshots"


def validate_archive(path, snapshot):
    actual_bytes = path.stat().st_size
    if actual_bytes != snapshot["bytes"]:
        raise ValueError(
            f"{path.name} is {actual_bytes:,} bytes. Expected {snapshot['bytes']:,}. "
            "Move the incomplete or different ZIP out of raw_snapshots and try again."
        )

    with ZipFile(path) as archive:
        csv_parts = sum(name.lower().endswith(".csv") for name in archive.namelist())
        if csv_parts != snapshot["csv_parts"]:
            raise ValueError(
                f"{path.name} contains {csv_parts} CSV parts. "
                f"Expected {snapshot['csv_parts']}."
            )


def download_snapshot(snapshot):
    target = RAW_DIR / snapshot["filename"]
    if target.exists():
        validate_archive(target, snapshot)
        print(f"Ready: {target.name}")
        return

    size_mib = snapshot["bytes"] / 1024**2
    print(f"Downloading {target.name} ({size_mib:.0f} MiB)", flush=True)
    with TemporaryDirectory(prefix=".download-", dir=RAW_DIR) as temp_dir:
        partial = Path(temp_dir) / target.name
        with urlopen(snapshot["url"], timeout=90) as response, partial.open("wb") as output:
            copyfileobj(response, output, length=1024**2)
        validate_archive(partial, snapshot)
        partial.replace(target)

    print(f"Saved: {target.name}", flush=True)


def main():
    snapshots = json.loads((PROJECT_DIR / "sources.json").read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "month",
        nargs="?",
        default="2026-01",
        choices=[*snapshots, "all"],
        help="a snapshot month (default: 2026-01) or all ten snapshots",
    )
    month = parser.parse_args().month
    selected = snapshots.values() if month == "all" else [snapshots[month]]

    RAW_DIR.mkdir(exist_ok=True)
    for snapshot in selected:
        download_snapshot(snapshot)


if __name__ == "__main__":
    main()
