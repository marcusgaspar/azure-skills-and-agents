"""Reconcile normalized monthly USD estimates; never infer missing values."""

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path


CENT = Decimal("0.01")


def money(value):
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def number(value):
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
        raise ValueError("Numbers must be decimal strings or null")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal: {value!r}") from exc
    if not result.is_finite():
        raise ValueError("Non-finite numbers are not allowed")
    if len(result.as_tuple().digits) > 30 or abs(result.as_tuple().exponent) > 30:
        raise ValueError("Decimal precision or exponent exceeds supported range")
    return result


def records(data, name):
    items = data.get(name)
    if not isinstance(items, list):
        raise ValueError(f"{name} must be an array")
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{name} entries must be objects")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen:
            raise ValueError(f"{name}: empty or duplicate id")
        seen.add(identifier)
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            raise ValueError(f"{name}/{identifier}: evidence is required")
    return items


def referenced(mapping, identifier):
    if not isinstance(identifier, str) or identifier not in mapping:
        raise ValueError(f"Unknown reference: {identifier!r}")
    return mapping[identifier]


def review(data):
    if not isinstance(data, dict) or data.get("rounding") not in ("line", "total"):
        raise ValueError("rounding must be explicitly 'line' or 'total'")
    lines = {}
    line_results = []
    with localcontext() as context:
        context.prec = 600
        for item in records(data, "lines"):
            factors = item.get("factors")
            if not isinstance(factors, list) or not 1 <= len(factors) <= 8:
                raise ValueError(f"{item['id']}: supply 1-8 factors")
            parsed = [number(factor) for factor in factors]
            value = None
            if all(factor is not None for factor in parsed):
                value = Decimal(1)
                for factor in parsed:
                    value *= factor
            lines[item["id"]] = value
            line_results.append({
                "id": item["id"], "evidence": item["evidence"],
                "monthly_usd": None if value is None else money(value),
                "status": "A DEFINIR" if value is None else "calculated",
            })
        if not lines:
            raise ValueError("At least one estimate line is required")

        portfolios = {}
        portfolio_results = []
        incomplete = any(value is None for value in lines.values())
        divergent = False
        for item in records(data, "portfolios"):
            ids = item.get("line_ids")
            if not isinstance(ids, list) or not ids or any(not isinstance(i, str) for i in ids):
                raise ValueError(f"{item['id']}: nonempty line_ids required")
            if len(ids) != len(set(ids)):
                raise ValueError(f"{item['id']}: duplicate line reference")
            values = [referenced(lines, identifier) for identifier in ids]
            missing = [identifier for identifier in ids if lines[identifier] is None]
            if "declared_total" not in item:
                raise ValueError(f"{item['id']}: declared_total must be explicit")
            declared = number(item["declared_total"])
            known = [value for value in values if value is not None]
            if data["rounding"] == "line":
                known = [value.quantize(CENT, rounding=ROUND_HALF_UP) for value in known]
            subtotal = sum(known, Decimal(0)).quantize(CENT, rounding=ROUND_HALF_UP)
            total = None if missing else subtotal
            portfolios[item["id"]] = total
            delta = None if total is None or declared is None else total - declared
            status = "Nao verificado" if delta is None else ("OK" if delta == 0 else "Divergente")
            divergent |= status == "Divergente"
            incomplete |= bool(missing)
            portfolio_results.append({
                "id": item["id"], "evidence": item["evidence"],
                "monthly_usd": None if total is None else money(total),
                "known_subtotal_usd": money(subtotal),
                "missing_line_ids": missing,
                "declared_total_usd": None if declared is None else str(declared),
                "delta_usd": None if delta is None else str(delta),
                "reconciliation_status": status,
                "reason": ("Missing line factors" if missing else
                           "Declared total unavailable or derived scenario" if declared is None else
                           "Exact comparison under stated rounding policy"),
            })
        if not portfolios:
            raise ValueError("At least one portfolio is required")

        comparisons = []
        for item in records(data, "comparisons"):
            left = referenced(portfolios, item.get("left"))
            right = referenced(portfolios, item.get("right"))
            delta = None if left is None or right is None else left - right
            status = "Nao verificado" if delta is None else ("OK" if delta == 0 else "Divergente")
            incomplete |= delta is None
            divergent |= status == "Divergente"
            comparisons.append({
                **item, "delta_usd": None if delta is None else money(delta), "status": status,
            })

        impacts = []
        for item in records(data, "impacts"):
            if item.get("kind") not in ("correction", "alternative"):
                raise ValueError(f"{item['id']}: impact kind must be correction or alternative")
            original = referenced(portfolios, item.get("original"))
            revised = referenced(portfolios, item.get("revised"))
            delta = None if original is None or revised is None else revised - original
            incomplete |= delta is None
            impacts.append({
                **item, "monthly_delta_usd": None if delta is None else money(delta),
                "status": "A DEFINIR" if delta is None else "calculated",
            })

    return {
        "currency": "USD", "period": "month", "rounding": data["rounding"],
        "lines": line_results, "portfolios": portfolio_results,
        "comparisons": comparisons, "impacts": impacts,
        "has_missing_values": incomplete, "has_divergences": divergent,
        "notice": "Arithmetic only; sources, scope, eligibility and capacity require independent verification. Impacts must not be summed.",
    }


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        root = Path(__file__).resolve().parent.parent
        source = args.input.resolve()
        if source.is_relative_to(root):
            raise ValueError("Customer input must not be stored in the skill directory")
        if args.output:
            output = args.output.resolve()
            if output == source or output.is_relative_to(root):
                raise ValueError("Output must differ from input and be outside the skill directory")
        data = json.loads(source.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
        result = review(data)
        text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(text)
        else:
            print(text, end="")
        return 1 if result["has_missing_values"] or result["has_divergences"] else 0
    except (OSError, ValueError, InvalidOperation) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
