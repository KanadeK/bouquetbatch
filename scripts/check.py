from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    print("+", subprocess.list2cmdline(command), flush=True)
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != expected:
        raise SystemExit(
            f"expected exit {expected}, got {result.returncode}: {subprocess.list2cmdline(command)}"
        )
    return result


def environment_python(environment: Path) -> Path:
    directory = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return environment / directory / executable


def main() -> None:
    run([sys.executable, "-m", "ruff", "format", "--check", "."])
    run([sys.executable, "-m", "ruff", "check", "."])
    run([sys.executable, "-m", "mypy"])
    run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=bouquetbatch",
            "--cov-report=term-missing",
            "--cov-fail-under=90",
        ]
    )

    with tempfile.TemporaryDirectory(prefix=".bouquetbatch-check-", dir=ROOT) as temp:
        workspace = Path(temp)
        complete_output = workspace / "complete"
        shortage_output = workspace / "shortage"
        invalid_output = workspace / "invalid"
        run(
            [
                sys.executable,
                "-m",
                "bouquetbatch",
                "plan",
                "examples/complete.json",
                "--output",
                str(complete_output),
            ]
        )
        run(
            [
                sys.executable,
                "-m",
                "bouquetbatch",
                "plan",
                "examples/shortage.json",
                "--output",
                str(shortage_output),
            ],
            expected=1,
        )
        run(
            [
                sys.executable,
                "-m",
                "bouquetbatch",
                "plan",
                "examples/invalid.json",
                "--output",
                str(invalid_output),
            ],
            expected=2,
        )
        if invalid_output.exists():
            raise SystemExit("invalid input created an output directory")

        distribution = workspace / "dist"
        run(
            [
                "uv",
                "build",
                "--wheel",
                "--sdist",
                "--offline",
                "--out-dir",
                str(distribution),
            ]
        )
        wheels = list(distribution.glob("bouquetbatch-*.whl"))
        source_distributions = list(distribution.glob("bouquetbatch-*.tar.gz"))
        if len(wheels) != 1 or len(source_distributions) != 1:
            raise SystemExit("build did not create exactly one wheel and one source archive")

        clean_environment = workspace / "clean-venv"
        venv.EnvBuilder(with_pip=True).create(clean_environment)
        clean_python = environment_python(clean_environment)
        run(
            [
                str(clean_python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-index",
                str(wheels[0]),
            ]
        )
        run([str(clean_python), "-m", "bouquetbatch", "--version"])
        run(
            [
                str(clean_python),
                "-m",
                "bouquetbatch",
                "plan",
                "examples/complete.json",
                "--output",
                str(workspace / "installed-plan"),
            ]
        )

    print("BOUQUETBATCH_CHECK=PASS")


if __name__ == "__main__":
    main()
