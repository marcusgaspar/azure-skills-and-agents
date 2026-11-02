"""Return a non-overwriting paired version for IaaS Excel deliverables."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


INVENTORY_PREFIX = "IaaS-Inventario-Consolidado"
COST_PREFIX = "IaaS-Custo-Calculadora"


def next_output_version(directory: Path) -> dict[str, object]:
    if not directory.is_dir():
        raise ValueError("Output directory must already exist")

    expression = re.compile(
        rf"^(?:{re.escape(INVENTORY_PREFIX)}|{re.escape(COST_PREFIX)})-v(\d+)\.xlsx$",
        re.IGNORECASE,
    )
    versions = []
    for path in directory.iterdir():
        match = expression.fullmatch(path.name)
        if match:
            versions.append(int(match.group(1)))

    version = max(versions, default=0) + 1
    while (
        directory / f"{INVENTORY_PREFIX}-v{version}.xlsx"
    ).exists() or (
        directory / f"{COST_PREFIX}-v{version}.xlsx"
    ).exists():
        version += 1

    return {
        "version": version,
        "inventory_file": str(directory / f"{INVENTORY_PREFIX}-v{version}.xlsx"),
        "cost_file": str(directory / f"{COST_PREFIX}-v{version}.xlsx"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(next_output_version(args.output_directory.resolve()), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
