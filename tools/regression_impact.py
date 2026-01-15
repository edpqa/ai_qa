#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable


LEVEL_ORDER = {"low": 1, "medium": 2, "high": 3}


def _as_posix(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    p = PurePosixPath(_as_posix(path))
    return any(p.match(pattern) for pattern in patterns)


@dataclass(frozen=True)
class Component:
    name: str
    description: str
    paths: tuple[str, ...]
    exclude_paths: tuple[str, ...]
    product_impact: bool
    regression_level: str

    def matches(self, changed_path: str) -> bool:
        if self.exclude_paths and _matches_any(changed_path, self.exclude_paths):
            return False
        return _matches_any(changed_path, self.paths)


def _load_rules(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("schema_version") != 1:
        raise ValueError(f"Unsupported schema_version: {data.get('schema_version')}")
    return data


def _parse_components(rules: dict[str, Any]) -> list[Component]:
    components: list[Component] = []
    for raw in rules.get("components", []):
        components.append(
            Component(
                name=raw["name"],
                description=raw.get("description", ""),
                paths=tuple(raw.get("paths", [])),
                exclude_paths=tuple(raw.get("exclude_paths", [])),
                product_impact=bool(raw.get("product_impact", True)),
                regression_level=raw.get("regression_level", rules.get("default_level", "low")),
            )
        )
    return components


def analyze_change_set(*, rules_path: str, changed_files: list[str]) -> dict[str, Any]:
    rules = _load_rules(rules_path)
    components = _parse_components(rules)

    impacted: dict[str, dict[str, Any]] = {}
    for file_path in changed_files:
        matched = [c for c in components if c.matches(file_path)]
        for c in matched:
            impacted.setdefault(
                c.name,
                {
                    "name": c.name,
                    "description": c.description,
                    "product_impact": c.product_impact,
                    "regression_level": c.regression_level,
                    "files": [],
                },
            )["files"].append(_as_posix(file_path))

    product_components = [c for c in impacted.values() if c["product_impact"]]
    if product_components:
        recommended_level = max(
            (c["regression_level"] for c in product_components),
            key=lambda level: LEVEL_ORDER.get(level, 0),
        )
    else:
        recommended_level = rules.get("default_level", "low")

    return {
        "rules_path": _as_posix(rules_path),
        "changed_files": [_as_posix(p) for p in changed_files],
        "impacted_components": sorted(impacted.values(), key=lambda c: c["name"]),
        "recommended_regression_level": recommended_level,
    }


def _read_changed_files_from_stdin() -> list[str]:
    return [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect impacted components and recommend regression testing level.",
    )
    parser.add_argument(
        "--rules",
        default="regression/component_map.json",
        help="Path to component mapping rules (JSON).",
    )
    parser.add_argument(
        "--changed",
        nargs="*",
        default=None,
        help="Changed files (space-separated). If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    changed_files = (
        args.changed
        if args.changed is not None and len(args.changed)
        else _read_changed_files_from_stdin()
    )
    result = analyze_change_set(rules_path=args.rules, changed_files=changed_files)

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"Recommended regression level: {result['recommended_regression_level']}")
    if not result["impacted_components"]:
        print("Impacted components: (none matched)")
        return 0

    print("Impacted components:")
    for component in result["impacted_components"]:
        files = ", ".join(component["files"])
        impact = "product" if component["product_impact"] else "non-product"
        print(
            f"- {component['name']} ({impact}, level={component['regression_level']}): {files}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

