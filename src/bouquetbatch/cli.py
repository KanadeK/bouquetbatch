from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from bouquetbatch import __version__
from bouquetbatch.input import InputError, load_document
from bouquetbatch.planner import create_plan
from bouquetbatch.render import OutputError, write_outputs


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bouquetbatch",
        description="Allocate perishable flower lots to bouquet recipe requirements.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="create a pick plan from a JSON document")
    plan.add_argument("input", type=Path, help="UTF-8 planning document")
    plan.add_argument("--output", type=Path, required=True, help="new output directory")
    return parser


def run(arguments: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    if args.command != "plan":
        raise AssertionError("argparse returned an unknown command")
    try:
        document = load_document(args.input)
        plan = create_plan(document)
        write_outputs(document, plan, args.output)
    except (InputError, OutputError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(args.output)
    return 1 if plan.shortage_stems else 0


def main() -> None:
    raise SystemExit(run())
