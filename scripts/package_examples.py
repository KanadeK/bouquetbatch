from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
ASSET_PATHS = (
    Path("examples/README.md"),
    Path("examples/complete.json"),
    Path("examples/shortage.json"),
    Path("examples/invalid.json"),
    Path("examples/generated/complete/plan.json"),
    Path("examples/generated/complete/pick-list.csv"),
    Path("examples/generated/complete/report.html"),
    Path("examples/generated/shortage/plan.json"),
    Path("examples/generated/shortage/pick-list.csv"),
    Path("examples/generated/shortage/report.html"),
)


def create_archive(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for relative_path in ASSET_PATHS:
            info = ZipInfo(
                f"bouquetbatch-v0.1.0/{relative_path.as_posix()}",
                date_time=(2026, 8, 27, 0, 0, 0),
            )
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, (ROOT / relative_path).read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the versioned examples archive.")
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    create_archive(arguments.output)
    print(arguments.output)


if __name__ == "__main__":
    main()
