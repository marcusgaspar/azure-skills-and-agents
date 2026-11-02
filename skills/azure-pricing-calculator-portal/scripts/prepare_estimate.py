"""Validate an Azure Pricing Calculator plan and reconcile portal results."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path


SCHEMA_VERSION = "1.0"
SKILL_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_ROOT = SKILL_ROOT / "examples"
DECIMAL_PATTERN = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
CURRENCY_PATTERN = re.compile(r"[A-Z]{3}")
SHARE_URL_PATTERN = re.compile(r"https://azure\.com/e/[A-Za-z0-9_-]+/?")

STATUS_VALUES = {"CONFIRMADO", "PREMISSA", "SUGESTAO", "A DEFINIR"}
REPRESENTABILITY_VALUES = {
    "DIRECT",
    "DERIVED",
    "NOT_REPRESENTABLE",
    "A_DEFINIR",
}
ADJUSTMENT_CATEGORIES = {
    "CURRENT_PRICE",
    "FREE_TIER",
    "MINIMUM",
    "BILLING_BLOCK",
    "MONTH_HOURS",
    "ROUNDING",
    "OTHER_VERIFIED",
}

PLAN_KEYS = {
    "schema_version",
    "estimate_name",
    "currency",
    "price_reference_date",
    "purchase_scenario",
    "tolerance_usd",
    "declared_expected_total",
    "components",
    "calculator_modules",
}
COMPONENT_KEYS = {
    "id",
    "source_reference",
    "source_service",
    "azure_product",
    "display_name",
    "region",
    "quantity",
    "unit",
    "expected_monthly_cost",
    "status",
    "representability",
    "notes",
}
MODULE_KEYS = {
    "id",
    "component_ids",
    "calculator_product",
    "display_name",
    "region",
    "configuration",
    "derivation",
}
PORTAL_KEYS = {
    "estimate_name",
    "currency",
    "query_date",
    "total_portal",
    "modules",
    "adjustments",
    "share_url",
    "link_validation",
}
PORTAL_MODULE_KEYS = {"id", "actual_monthly_cost", "evidence"}
ADJUSTMENT_KEYS = {"id", "category", "amount", "component_ids", "evidence"}
LINK_KEYS = {
    "observed_estimate_name",
    "observed_currency",
    "observed_total",
    "evidence",
}


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_unknown_keys(value, allowed, path):
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"{path}: unknown field(s): {', '.join(unknown)}")


def required_text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: nonempty text is required")
    return value.strip()


def optional_text(value, path):
    if value is None:
        return None
    return required_text(value, path)


def decimal_value(value, path, *, allow_null=False, non_negative=False):
    if value is None:
        if allow_null:
            return None
        raise ValueError(f"{path}: decimal string is required")
    if not isinstance(value, str) or not DECIMAL_PATTERN.fullmatch(value):
        raise ValueError(f"{path}: numbers must be decimal strings or null")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{path}: invalid decimal {value!r}") from exc
    if not parsed.is_finite():
        raise ValueError(f"{path}: non-finite numbers are not allowed")
    if len(parsed.as_tuple().digits) > 40 or abs(parsed.as_tuple().exponent) > 40:
        raise ValueError(f"{path}: decimal precision or exponent is too large")
    if non_negative and parsed < 0:
        raise ValueError(f"{path}: value must not be negative")
    return parsed


def decimal_text(value):
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def iso_date(value, path, *, allow_null=False):
    if value is None and allow_null:
        return None
    text = required_text(value, path)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{path}: expected ISO date YYYY-MM-DD") from exc
    return text


def record_array(value, path):
    if not isinstance(value, list):
        raise ValueError(f"{path}: array is required")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}]: object is required")
    return value


def validate_configuration(value, path):
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_configuration(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{path}: configuration keys must be nonempty text")
            validate_configuration(item, f"{path}.{key}")
        return
    raise ValueError(
        f"{path}: use strings for numbers; only objects, arrays, strings, "
        "booleans and null are allowed"
    )


def sum_known(values):
    return sum((value for value in values if value is not None), Decimal(0))


def validate_plan(data):
    if not isinstance(data, dict):
        raise ValueError("Plan root must be an object")
    reject_unknown_keys(data, PLAN_KEYS, "plan")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")

    estimate_name = required_text(data.get("estimate_name"), "estimate_name")
    currency = required_text(data.get("currency"), "currency")
    if not CURRENCY_PATTERN.fullmatch(currency):
        raise ValueError("currency must be a three-letter uppercase code")
    price_reference_date = iso_date(
        data.get("price_reference_date"),
        "price_reference_date",
        allow_null=True,
    )
    purchase_scenario = required_text(
        data.get("purchase_scenario"), "purchase_scenario"
    )
    tolerance = decimal_value(
        data.get("tolerance_usd", "0.01"),
        "tolerance_usd",
        non_negative=True,
    )
    if tolerance == 0:
        raise ValueError("tolerance_usd must be greater than zero")
    declared_expected = decimal_value(
        data.get("declared_expected_total"),
        "declared_expected_total",
        allow_null=True,
        non_negative=True,
    )

    components = []
    component_map = {}
    for index, item in enumerate(record_array(data.get("components"), "components")):
        path = f"components[{index}]"
        reject_unknown_keys(item, COMPONENT_KEYS, path)
        identifier = required_text(item.get("id"), f"{path}.id")
        if identifier in component_map:
            raise ValueError(f"{path}.id: duplicate component id {identifier!r}")
        status = required_text(item.get("status"), f"{path}.status")
        if status not in STATUS_VALUES:
            raise ValueError(f"{path}.status: unsupported value {status!r}")
        representability = required_text(
            item.get("representability"), f"{path}.representability"
        )
        if representability not in REPRESENTABILITY_VALUES:
            raise ValueError(
                f"{path}.representability: unsupported value {representability!r}"
            )
        if "expected_monthly_cost" not in item:
            raise ValueError(f"{path}.expected_monthly_cost: field is required")
        expected = decimal_value(
            item.get("expected_monthly_cost"),
            f"{path}.expected_monthly_cost",
            allow_null=True,
            non_negative=True,
        )
        quantity = decimal_value(
            item.get("quantity"),
            f"{path}.quantity",
            allow_null=True,
            non_negative=True,
        )
        unit = optional_text(item.get("unit"), f"{path}.unit")
        if (quantity is None) != (unit is None):
            raise ValueError(f"{path}: quantity and unit must be supplied together")
        component = {
            "id": identifier,
            "source_reference": required_text(
                item.get("source_reference"), f"{path}.source_reference"
            ),
            "source_service": optional_text(
                item.get("source_service"), f"{path}.source_service"
            ),
            "azure_product": required_text(
                item.get("azure_product"), f"{path}.azure_product"
            ),
            "display_name": required_text(
                item.get("display_name"), f"{path}.display_name"
            ),
            "region": required_text(item.get("region"), f"{path}.region"),
            "quantity": decimal_text(quantity),
            "unit": unit,
            "expected_monthly_cost": decimal_text(expected),
            "status": status,
            "representability": representability,
            "notes": optional_text(item.get("notes"), f"{path}.notes"),
        }
        components.append(component)
        component_map[identifier] = {
            "normalized": component,
            "expected": expected,
            "reference_count": 0,
        }
    if not components:
        raise ValueError("components must contain at least one entry")

    modules = []
    module_ids = set()
    for index, item in enumerate(
        record_array(data.get("calculator_modules"), "calculator_modules")
    ):
        path = f"calculator_modules[{index}]"
        reject_unknown_keys(item, MODULE_KEYS, path)
        identifier = required_text(item.get("id"), f"{path}.id")
        if identifier in module_ids:
            raise ValueError(f"{path}.id: duplicate module id {identifier!r}")
        module_ids.add(identifier)
        component_ids = item.get("component_ids")
        if (
            not isinstance(component_ids, list)
            or not component_ids
            or any(not isinstance(value, str) or not value for value in component_ids)
        ):
            raise ValueError(f"{path}.component_ids: nonempty string array required")
        if len(component_ids) != len(set(component_ids)):
            raise ValueError(f"{path}.component_ids: duplicate component reference")
        expected_values = []
        has_derived = False
        for component_id in component_ids:
            component_state = component_map.get(component_id)
            if component_state is None:
                raise ValueError(
                    f"{path}.component_ids: unknown component {component_id!r}"
                )
            representation = component_state["normalized"]["representability"]
            if representation not in {"DIRECT", "DERIVED"}:
                raise ValueError(
                    f"{path}: component {component_id!r} is {representation}"
                )
            component_state["reference_count"] += 1
            expected_values.append(component_state["expected"])
            has_derived |= representation == "DERIVED"
        configuration = item.get("configuration")
        if not isinstance(configuration, dict) or not configuration:
            raise ValueError(f"{path}.configuration: nonempty object required")
        validate_configuration(configuration, f"{path}.configuration")
        derivation = required_text(item.get("derivation"), f"{path}.derivation")
        if has_derived and len(derivation) < 10:
            raise ValueError(f"{path}.derivation: explain the derived configuration")
        modules.append(
            {
                "id": identifier,
                "component_ids": component_ids,
                "calculator_product": required_text(
                    item.get("calculator_product"), f"{path}.calculator_product"
                ),
                "display_name": required_text(
                    item.get("display_name"), f"{path}.display_name"
                ),
                "region": required_text(item.get("region"), f"{path}.region"),
                "configuration": configuration,
                "derivation": derivation,
                "expected_source_subtotal": (
                    None
                    if any(value is None for value in expected_values)
                    else decimal_text(sum_known(expected_values))
                ),
                "missing_cost_component_ids": [
                    component_id
                    for component_id, value in zip(component_ids, expected_values)
                    if value is None
                ],
            }
        )

    for component_id, state in component_map.items():
        representation = state["normalized"]["representability"]
        reference_count = state["reference_count"]
        if representation in {"DIRECT", "DERIVED"} and reference_count != 1:
            raise ValueError(
                f"component {component_id!r} must be referenced by exactly one module"
            )
        if representation in {"NOT_REPRESENTABLE", "A_DEFINIR"} and reference_count:
            raise ValueError(
                f"component {component_id!r} must not be referenced by a module"
            )

    expected_values = [state["expected"] for state in component_map.values()]
    represented_ids = {
        component_id for module in modules for component_id in module["component_ids"]
    }
    represented_values = [
        state["expected"]
        for component_id, state in component_map.items()
        if component_id in represented_ids
    ]
    unrepresented_values = [
        state["expected"]
        for component_id, state in component_map.items()
        if component_id not in represented_ids
    ]
    missing_cost_ids = [
        component_id
        for component_id, state in component_map.items()
        if state["expected"] is None
    ]
    unresolved_representation_ids = [
        component_id
        for component_id, state in component_map.items()
        if state["normalized"]["representability"] == "A_DEFINIR"
    ]
    a_definir_status_ids = [
        component_id
        for component_id, state in component_map.items()
        if state["normalized"]["status"] == "A DEFINIR"
    ]
    not_representable_ids = [
        component_id
        for component_id, state in component_map.items()
        if state["normalized"]["representability"] == "NOT_REPRESENTABLE"
    ]
    expected_total = (
        None if missing_cost_ids else sum_known(expected_values)
    )
    represented_missing = any(value is None for value in represented_values)
    unrepresented_missing = any(value is None for value in unrepresented_values)
    represented_expected = (
        None if represented_missing else sum_known(represented_values)
    )
    unrepresented_expected = (
        None if unrepresented_missing else sum_known(unrepresented_values)
    )

    issues = []
    if missing_cost_ids:
        issues.append(
            {
                "code": "MISSING_EXPECTED_COST",
                "ids": missing_cost_ids,
                "message": "Expected monthly cost is A DEFINIR.",
            }
        )
    if unresolved_representation_ids:
        issues.append(
            {
                "code": "UNRESOLVED_REPRESENTABILITY",
                "ids": unresolved_representation_ids,
                "message": "Representability is A DEFINIR.",
            }
        )
    if a_definir_status_ids:
        issues.append(
            {
                "code": "COMPONENT_STATUS_A_DEFINIR",
                "ids": a_definir_status_ids,
                "message": "Component evidence or configuration is A DEFINIR.",
            }
        )
    declared_delta = None
    if declared_expected is not None and expected_total is not None:
        declared_delta = expected_total - declared_expected
        if abs(declared_delta) > tolerance:
            issues.append(
                {
                    "code": "DECLARED_TOTAL_MISMATCH",
                    "ids": [],
                    "message": (
                        "Component total differs from declared_expected_total by "
                        f"{decimal_text(declared_delta)} {currency}."
                    ),
                }
            )

    normalized = {
        "schema_version": SCHEMA_VERSION,
        "estimate_name": estimate_name,
        "currency": currency,
        "price_reference_date": price_reference_date,
        "purchase_scenario": purchase_scenario,
        "tolerance_usd": decimal_text(tolerance),
        "declared_expected_total": decimal_text(declared_expected),
        "components": components,
        "calculator_modules": modules,
    }
    summary = {
        "component_count": len(components),
        "module_count": len(modules),
        "expected_total": decimal_text(expected_total),
        "represented_expected": decimal_text(represented_expected),
        "unrepresented_expected": decimal_text(unrepresented_expected),
        "missing_cost_component_ids": missing_cost_ids,
        "unresolved_representability_ids": unresolved_representation_ids,
        "status_a_definir_component_ids": a_definir_status_ids,
        "not_representable_component_ids": not_representable_ids,
        "declared_total_delta": decimal_text(declared_delta),
    }
    state = {
        "normalized": normalized,
        "component_map": component_map,
        "module_ids": module_ids,
        "represented_ids": represented_ids,
        "expected_total": expected_total,
        "represented_expected": represented_expected,
        "unrepresented_expected": unrepresented_expected,
        "tolerance": tolerance,
        "issues": issues,
        "summary": summary,
    }
    return state


def validate_portal(data, plan_state):
    if not isinstance(data, dict):
        raise ValueError("Portal result root must be an object")
    reject_unknown_keys(data, PORTAL_KEYS, "portal_results")
    plan = plan_state["normalized"]
    estimate_name = required_text(data.get("estimate_name"), "portal.estimate_name")
    if estimate_name != plan["estimate_name"]:
        raise ValueError("portal estimate_name does not match the plan")
    currency = required_text(data.get("currency"), "portal.currency")
    if currency != plan["currency"]:
        raise ValueError("portal currency does not match the plan")
    query_date = iso_date(data.get("query_date"), "portal.query_date")
    total_portal = decimal_value(
        data.get("total_portal"), "portal.total_portal", non_negative=True
    )

    portal_modules = []
    portal_module_map = {}
    for index, item in enumerate(record_array(data.get("modules"), "portal.modules")):
        path = f"portal.modules[{index}]"
        reject_unknown_keys(item, PORTAL_MODULE_KEYS, path)
        identifier = required_text(item.get("id"), f"{path}.id")
        if identifier in portal_module_map:
            raise ValueError(f"{path}.id: duplicate portal module id {identifier!r}")
        actual = decimal_value(
            item.get("actual_monthly_cost"),
            f"{path}.actual_monthly_cost",
            non_negative=True,
        )
        normalized = {
            "id": identifier,
            "actual_monthly_cost": decimal_text(actual),
            "evidence": required_text(item.get("evidence"), f"{path}.evidence"),
        }
        portal_modules.append(normalized)
        portal_module_map[identifier] = actual
    expected_module_ids = plan_state["module_ids"]
    actual_module_ids = set(portal_module_map)
    missing_modules = sorted(expected_module_ids - actual_module_ids)
    extra_modules = sorted(actual_module_ids - expected_module_ids)
    if missing_modules or extra_modules:
        raise ValueError(
            "portal module ids differ from the plan; "
            f"missing={missing_modules}, extra={extra_modules}"
        )

    portal_module_total = sum_known(portal_module_map.values())
    module_total_delta = portal_module_total - total_portal
    tolerance = plan_state["tolerance"]
    issues = []
    if abs(module_total_delta) > tolerance:
        issues.append(
            {
                "code": "PORTAL_MODULE_TOTAL_MISMATCH",
                "ids": sorted(actual_module_ids),
                "message": (
                    "Sum of portal modules differs from total_portal by "
                    f"{decimal_text(module_total_delta)} {currency}."
                ),
            }
        )

    adjustments = []
    adjustment_ids = set()
    adjustment_total = Decimal(0)
    for index, item in enumerate(
        record_array(data.get("adjustments", []), "portal.adjustments")
    ):
        path = f"portal.adjustments[{index}]"
        reject_unknown_keys(item, ADJUSTMENT_KEYS, path)
        identifier = required_text(item.get("id"), f"{path}.id")
        if identifier in adjustment_ids:
            raise ValueError(f"{path}.id: duplicate adjustment id {identifier!r}")
        adjustment_ids.add(identifier)
        category = required_text(item.get("category"), f"{path}.category")
        if category not in ADJUSTMENT_CATEGORIES:
            raise ValueError(f"{path}.category: unsupported value {category!r}")
        component_ids = item.get("component_ids")
        if (
            not isinstance(component_ids, list)
            or not component_ids
            or any(not isinstance(value, str) or not value for value in component_ids)
        ):
            raise ValueError(f"{path}.component_ids: nonempty string array required")
        if len(component_ids) != len(set(component_ids)):
            raise ValueError(f"{path}.component_ids: duplicate component reference")
        unknown = sorted(set(component_ids) - set(plan_state["component_map"]))
        if unknown:
            raise ValueError(f"{path}.component_ids: unknown components {unknown}")
        amount = decimal_value(item.get("amount"), f"{path}.amount")
        adjustment_total += amount
        adjustments.append(
            {
                "id": identifier,
                "category": category,
                "amount": decimal_text(amount),
                "component_ids": component_ids,
                "evidence": required_text(item.get("evidence"), f"{path}.evidence"),
            }
        )

    represented_expected = plan_state["represented_expected"]
    expected_total = plan_state["expected_total"]
    unrepresented_expected = plan_state["unrepresented_expected"]
    pricing_rule_delta = None
    unexplained_delta = None
    net_delta = None
    identity_delta = None
    if represented_expected is None:
        issues.append(
            {
                "code": "REPRESENTED_COST_A_DEFINIR",
                "ids": [],
                "message": "Represented expected subtotal is A DEFINIR.",
            }
        )
    else:
        pricing_rule_delta = total_portal - represented_expected
        unexplained_delta = pricing_rule_delta - adjustment_total
        if abs(unexplained_delta) > tolerance:
            issues.append(
                {
                    "code": "UNEXPLAINED_PORTAL_DELTA",
                    "ids": [],
                    "message": (
                        "Explained adjustments differ from the portal pricing "
                        f"delta by {decimal_text(unexplained_delta)} {currency}."
                    ),
                }
            )
    if (
        expected_total is not None
        and unrepresented_expected is not None
        and pricing_rule_delta is not None
    ):
        net_delta = total_portal - expected_total
        identity_delta = net_delta - (
            pricing_rule_delta - unrepresented_expected
        )
        if abs(identity_delta) > tolerance:
            issues.append(
                {
                    "code": "RECONCILIATION_IDENTITY_MISMATCH",
                    "ids": [],
                    "message": (
                        "Net delta identity differs by "
                        f"{decimal_text(identity_delta)} {currency}."
                    ),
                }
            )

    share_url = data.get("share_url")
    link_validation = data.get("link_validation")
    link_validated = False
    normalized_link = None
    if share_url is not None:
        share_url = required_text(share_url, "portal.share_url")
        if not SHARE_URL_PATTERN.fullmatch(share_url):
            raise ValueError("portal.share_url is not an Azure calculator share URL")
        if link_validation is None:
            issues.append(
                {
                    "code": "SHARE_LINK_NOT_VALIDATED",
                    "ids": [],
                    "message": "Share URL exists but link_validation is missing.",
                }
            )
        else:
            if not isinstance(link_validation, dict):
                raise ValueError("portal.link_validation must be an object")
            reject_unknown_keys(link_validation, LINK_KEYS, "portal.link_validation")
            observed_name = required_text(
                link_validation.get("observed_estimate_name"),
                "portal.link_validation.observed_estimate_name",
            )
            observed_currency = required_text(
                link_validation.get("observed_currency"),
                "portal.link_validation.observed_currency",
            )
            observed_total = decimal_value(
                link_validation.get("observed_total"),
                "portal.link_validation.observed_total",
                non_negative=True,
            )
            evidence = required_text(
                link_validation.get("evidence"),
                "portal.link_validation.evidence",
            )
            link_issues = []
            if observed_name != estimate_name:
                link_issues.append("estimate name")
            if observed_currency != currency:
                link_issues.append("currency")
            if abs(observed_total - total_portal) > tolerance:
                link_issues.append("total")
            if link_issues:
                issues.append(
                    {
                        "code": "SHARE_LINK_CONTENT_MISMATCH",
                        "ids": [],
                        "message": (
                            "Shared link differs from the saved estimate: "
                            + ", ".join(link_issues)
                            + "."
                        ),
                    }
                )
            else:
                link_validated = True
            normalized_link = {
                "observed_estimate_name": observed_name,
                "observed_currency": observed_currency,
                "observed_total": decimal_text(observed_total),
                "evidence": evidence,
            }
    elif link_validation is not None:
        raise ValueError("portal.link_validation requires portal.share_url")

    normalized = {
        "estimate_name": estimate_name,
        "currency": currency,
        "query_date": query_date,
        "total_portal": decimal_text(total_portal),
        "modules": portal_modules,
        "adjustments": adjustments,
        "share_url": share_url,
        "link_validation": normalized_link,
    }
    summary = {
        "portal_module_total": decimal_text(portal_module_total),
        "portal_module_total_delta": decimal_text(module_total_delta),
        "pricing_rule_delta": decimal_text(pricing_rule_delta),
        "explained_adjustment_total": decimal_text(adjustment_total),
        "unexplained_delta": decimal_text(unexplained_delta),
        "net_delta": decimal_text(net_delta),
        "identity_delta": decimal_text(identity_delta),
        "share_link_validated": link_validated,
    }
    return {"normalized": normalized, "summary": summary, "issues": issues}


def prepare(plan_data, portal_data=None):
    with localcontext() as context:
        context.prec = 200
        plan_state = validate_plan(plan_data)
        issues = list(plan_state["issues"])
        result = {
            "schema_version": SCHEMA_VERSION,
            "estimate_name": plan_state["normalized"]["estimate_name"],
            "currency": plan_state["normalized"]["currency"],
            "purchase_scenario": plan_state["normalized"]["purchase_scenario"],
            "plan": plan_state["normalized"],
            "plan_summary": plan_state["summary"],
            "portal_results": None,
            "portal_summary": None,
            "issues": issues,
        }
        if portal_data is None:
            status = "A DEFINIR" if issues else "PREPARED"
        else:
            portal = validate_portal(portal_data, plan_state)
            result["portal_results"] = portal["normalized"]
            result["portal_summary"] = portal["summary"]
            issues.extend(portal["issues"])
            result["issues"] = issues
            if issues:
                status = "A DEFINIR"
            elif portal["summary"]["share_link_validated"]:
                status = "RECONCILED_AND_VALIDATED"
            else:
                status = "RECONCILED_NOT_SHARED"
        result["status"] = status
        return result


def read_json(path):
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=unique_keys,
    )


def validate_input_path(path, label):
    resolved = path.resolve()
    if resolved.is_relative_to(SKILL_ROOT) and not resolved.is_relative_to(
        EXAMPLES_ROOT
    ):
        raise ValueError(f"{label} must not be stored in the skill directory")
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--portal-results", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        plan_path = validate_input_path(args.plan, "Plan")
        portal_path = (
            validate_input_path(args.portal_results, "Portal results")
            if args.portal_results
            else None
        )
        output_path = args.output.resolve() if args.output else None
        if output_path:
            if output_path in {plan_path, portal_path}:
                raise ValueError("Output must differ from every input")
            if output_path.is_relative_to(SKILL_ROOT):
                raise ValueError("Output must not be stored in the skill directory")
        result = prepare(
            read_json(plan_path),
            read_json(portal_path) if portal_path else None,
        )
        text = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
        if output_path:
            with output_path.open("x", encoding="utf-8") as stream:
                stream.write(text)
        else:
            print(text, end="")
        return 1 if result["status"] == "A DEFINIR" else 0
    except (OSError, ValueError, InvalidOperation, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
