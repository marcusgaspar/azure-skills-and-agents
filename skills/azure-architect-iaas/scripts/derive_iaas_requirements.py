"""Derive IaaS sizing requirements and data-gap questions from normalized JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP, localcontext
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DECIMAL = re.compile(r"-?\d+(?:\.\d+)?")
MARGIN = Decimal("1.20")
HUNDRED = Decimal("100")
HUNDREDTH = Decimal("0.01")


def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def decimal_value(value: Any, field: str, *, positive: bool = False) -> Decimal | None:
    if value is None:
        return None
    if not isinstance(value, str) or not DECIMAL.fullmatch(value):
        raise ValueError(f"{field} must be a decimal string or null")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not a valid decimal") from exc
    if not number.is_finite() or len(number.as_tuple().digits) > 30:
        raise ValueError(f"{field} is outside supported precision")
    if positive and number <= 0:
        raise ValueError(f"{field} must be greater than zero")
    if not positive and number < 0:
        raise ValueError(f"{field} cannot be negative")
    return number


def text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string or null")
    return value.strip()


def money_number(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value.quantize(HUNDREDTH, rounding=ROUND_HALF_UP))


def whole_number(value: Decimal) -> str:
    return str(value.quantize(Decimal("1"), rounding=ROUND_CEILING))


def add_question(
    questions: list[dict[str, Any]],
    *,
    identifier: str,
    priority: str,
    question: str,
    reason: str,
    affected: list[str],
    evidence: str,
) -> None:
    key = (identifier, tuple(sorted(affected)))
    if any((item["id"], tuple(sorted(item["affected_vm_ids"]))) == key for item in questions):
        return
    questions.append(
        {
            "id": identifier,
            "priority": priority,
            "question": question,
            "reason": reason,
            "affected_vm_ids": affected,
            "evidence_needed": evidence,
        }
    )


def group_for(vm: dict[str, Any]) -> dict[str, str]:
    supplied = vm.get("execution_group")
    if supplied is not None:
        if not isinstance(supplied, dict):
            raise ValueError("execution_group must be an object or null")
        name = text(supplied.get("name"), "execution_group.name")
        confidence = decimal_value(supplied.get("confidence_pct"), "execution_group.confidence_pct")
        method = text(supplied.get("method"), "execution_group.method")
        if name is not None and confidence is not None and method is not None:
            if confidence > HUNDRED:
                raise ValueError("execution_group.confidence_pct cannot exceed 100")
            return {
                "name": name,
                "confidence_pct": money_number(confidence),
                "method": method,
            }

    cmdb = vm.get("cmdb") or {}
    if not isinstance(cmdb, dict):
        raise ValueError("cmdb must be an object or null")
    application = text(cmdb.get("application"), "cmdb.application")
    service = text(cmdb.get("service"), "cmdb.service")
    environment = text(cmdb.get("environment"), "cmdb.environment")
    dependencies = cmdb.get("dependencies") or []
    if not isinstance(dependencies, list) or any(not isinstance(item, str) or not item.strip() for item in dependencies):
        raise ValueError("cmdb.dependencies must be an array of nonempty strings")

    if application:
        return {"name": f"Aplicacao: {application}", "confidence_pct": "100.00", "method": "CMDB application"}
    if service:
        return {"name": f"Servico: {service}", "confidence_pct": "100.00", "method": "CMDB service"}
    if environment and dependencies:
        return {
            "name": f"Ambiente: {environment} (dependencias documentadas)",
            "confidence_pct": "50.00",
            "method": "Environment plus dependencies [SUGESTAO]",
        }
    if environment:
        return {
            "name": f"A DEFINIR: Ambiente {environment}",
            "confidence_pct": "40.00",
            "method": "Environment only [SUGESTAO]",
        }
    return {"name": "A DEFINIR: Sem grupo", "confidence_pct": "0.00", "method": "No grouping evidence"}


def scope_for(vm: dict[str, Any]) -> tuple[str, str | None]:
    exclusion = text(vm.get("exclude_reason"), "exclude_reason")
    destination = text(vm.get("migration_destination"), "migration_destination")
    if exclusion:
        return "excluded", exclusion
    if destination is None:
        return "excluded", "A DEFINIR: destino de migracao ausente"
    return "in_scope", None


def derive_disk(disk: dict[str, Any], telemetry_ok: bool) -> dict[str, Any]:
    identifier = text(disk.get("id"), "disk.id")
    if identifier is None:
        raise ValueError("disk.id is required")
    capacity = decimal_value(disk.get("capacity_gib"), "disk.capacity_gib", positive=True)
    iops = decimal_value(disk.get("iops_p95"), "disk.iops_p95")
    throughput = decimal_value(disk.get("throughput_mbps_p95"), "disk.throughput_mbps_p95")
    shared = disk.get("shared_requirement")
    if shared is not None and not isinstance(shared, bool):
        raise ValueError("disk.shared_requirement must be boolean or null")
    protocol = text(disk.get("protocol"), "disk.protocol")
    status = "ready" if telemetry_ok and iops is not None and throughput is not None and capacity is not None else "A DEFINIR"
    return {
        "id": identifier,
        "role": text(disk.get("role"), "disk.role"),
        "capacity_gib": money_number(capacity),
        "iops_p95": money_number(iops),
        "throughput_mbps_p95": money_number(throughput),
        "required_iops": money_number(iops * MARGIN) if status == "ready" else None,
        "required_throughput_mbps": money_number(throughput * MARGIN) if status == "ready" else None,
        "shared_requirement": shared,
        "protocol": protocol,
        "storage_direction": (
            "Evaluate Azure Files/Azure NetApp Files with documented requirements"
            if shared is True
            else "Managed Disk candidate; validate tier and VM aggregate caps"
            if shared is False
            else "A DEFINIR: shared/protocol requirement"
        ),
        "status": status,
    }


def derive_vm(vm: dict[str, Any], questions: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(vm, dict):
        raise ValueError("vms entries must be objects")
    identifier = text(vm.get("id"), "vm.id")
    name = text(vm.get("name"), "vm.name")
    if identifier is None or name is None:
        raise ValueError("vm.id and vm.name are required")
    source_refs = vm.get("source_refs") or []
    if not isinstance(source_refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in source_refs):
        raise ValueError("source_refs must be an array of nonempty strings")
    scope, exclusion_reason = scope_for(vm)
    group = group_for(vm)
    inventory = vm.get("inventory") or {}
    metrics = vm.get("metrics") or {}
    if not isinstance(inventory, dict) or not isinstance(metrics, dict):
        raise ValueError("inventory and metrics must be objects or null")
    vcpu = decimal_value(inventory.get("vcpu"), "inventory.vcpu", positive=True)
    memory = decimal_value(inventory.get("memory_gib"), "inventory.memory_gib", positive=True)
    operating_system = text(inventory.get("os"), "inventory.os")
    observation_days = decimal_value(metrics.get("observation_days"), "metrics.observation_days")
    peak_covered = metrics.get("peak_covered")
    if peak_covered is not None and not isinstance(peak_covered, bool):
        raise ValueError("metrics.peak_covered must be boolean or null")
    cpu_p95 = decimal_value(metrics.get("cpu_p95_pct"), "metrics.cpu_p95_pct")
    memory_p95 = decimal_value(metrics.get("memory_p95_gib"), "metrics.memory_p95_gib")
    if cpu_p95 is not None and cpu_p95 > HUNDRED:
        raise ValueError("metrics.cpu_p95_pct cannot exceed 100")
    telemetry_ok = (
        observation_days is not None
        and observation_days >= Decimal("30")
        and peak_covered is True
        and cpu_p95 is not None
        and memory_p95 is not None
        and vcpu is not None
        and memory is not None
    )
    required_vcpu = None
    required_memory = None
    if telemetry_ok:
        required_vcpu = (vcpu * cpu_p95 / HUNDRED * MARGIN).quantize(Decimal("1"), rounding=ROUND_CEILING)
        required_memory = memory_p95 * MARGIN
    sizing_status = "ready" if telemetry_ok else "A DEFINIR"

    disks = vm.get("disks") or []
    if not isinstance(disks, list):
        raise ValueError("disks must be an array")
    derived_disks = [derive_disk(disk, telemetry_ok) for disk in disks]
    if len({disk["id"] for disk in derived_disks}) != len(derived_disks):
        raise ValueError("disk IDs must be unique within a VM")

    if not source_refs:
        add_question(
            questions, identifier="source-evidence", priority="P0",
            question=f"Qual e a fonte verificavel dos atributos da VM {name}?",
            reason="Nao ha referencia de origem para a VM.",
            affected=[identifier], evidence="Arquivo, aba/tabela e linha/celula ou pagina/slide.",
        )
    if scope == "excluded" and exclusion_reason and "destino" in exclusion_reason:
        add_question(
            questions, identifier="migration-destination", priority="P0",
            question=f"Qual e o destino de migracao da VM {name}?",
            reason="Sem destino documentado, a VM foi excluida do sizing/custo.",
            affected=[identifier], evidence="CMDB, plano de migracao ou confirmacao do owner.",
        )
    if Decimal(group["confidence_pct"]) < Decimal("50"):
        add_question(
            questions, identifier="execution-group", priority="P0",
            question=f"Qual aplicacao/servico e quais dependencias definem o grupo de execucao da VM {name}?",
            reason="Confianca de agrupamento abaixo de 50%.",
            affected=[identifier], evidence="CMDB atualizada e mapa de dependencias validado.",
        )
    if not telemetry_ok and scope == "in_scope":
        add_question(
            questions, identifier="vm-telemetry", priority="P0",
            question=f"Pode fornecer CPU P95 e memoria usada P95 da VM {name} em pelo menos 30 dias que cubram o pico?",
            reason="Sizing de VM nao pode ser validado com as metricas atuais.",
            affected=[identifier],
            evidence="Export de Azure Migrate/monitoramento com unidade, periodo, intervalo e pico.",
        )
    if operating_system is None and scope == "in_scope":
        add_question(
            questions, identifier="operating-system", priority="P1",
            question=f"Qual e o SO, versao e licenciamento da VM {name}?",
            reason="SO e licenca afetam SKU, suporte e preco.",
            affected=[identifier], evidence="Inventario/RVTools/CMDB com versao e edicao.",
        )
    rto = decimal_value(vm.get("rto_minutes"), "rto_minutes", positive=True)
    rpo = decimal_value(vm.get("rpo_minutes"), "rpo_minutes", positive=True)
    if (rto is None or rpo is None) and scope == "in_scope":
        add_question(
            questions, identifier="rto-rpo", priority="P1",
            question=f"Quais sao RTO, RPO e criticidade da VM {name}?",
            reason="Backup, HA e DR nao podem ser dimensionados sem requisito.",
            affected=[identifier], evidence="Requisito aprovado pelo owner de aplicacao.",
        )
    for disk in derived_disks:
        if disk["status"] == "A DEFINIR" and scope == "in_scope":
            add_question(
                questions, identifier=f"storage-performance-{disk['id']}", priority="P0",
                question=f"Pode fornecer capacidade, IOPS P95 e throughput P95 do volume {disk['id']} da VM {name}?",
                reason="Tier de disco/storage nao pode ser validado.",
                affected=[identifier],
                evidence="Telemetria de pelo menos 30 dias cobrindo pico, com unidade e leitura/escrita quando disponivel.",
            )
        if disk["shared_requirement"] is None and scope == "in_scope":
            add_question(
                questions, identifier=f"storage-protocol-{disk['id']}", priority="P1",
                question=f"O volume {disk['id']} da VM {name} precisa ser compartilhado? Se sim, qual protocolo e quais clientes?",
                reason="Avaliacao de Managed Disks, Azure Files ou Azure NetApp Files esta incompleta.",
                affected=[identifier], evidence="Requisito de NFS/SMB, clientes, latencia e operacao.",
            )

    suggestions = []
    if operating_system and "windows" in operating_system.lower():
        suggestions.append("[SUGESTÃO] Validar elegibilidade de Azure Hybrid Benefit; baseline permanece PAYG.")
    if any(disk["shared_requirement"] is True for disk in derived_disks):
        suggestions.append("[SUGESTÃO] Comparar Azure Files e Azure NetApp Files somente com requisitos de protocolo/performance comprovados.")
    if vm.get("replatform_candidate") is True:
        suggestions.append("[SUGESTÃO] Avaliar PaaS/containers em trabalho separado; esta saida mantem IaaS e nao precifica alternativa.")

    return {
        "id": identifier,
        "name": name,
        "source_refs": source_refs,
        "scope": scope,
        "exclusion_reason": exclusion_reason,
        "execution_group": group,
        "current_vcpu": money_number(vcpu),
        "current_memory_gib": money_number(memory),
        "operating_system": operating_system,
        "observation_days": money_number(observation_days),
        "peak_covered": peak_covered,
        "cpu_p95_pct": money_number(cpu_p95),
        "memory_p95_gib": money_number(memory_p95),
        "required_vcpu": whole_number(required_vcpu) if required_vcpu is not None else None,
        "required_memory_gib": money_number(required_memory),
        "sizing_status": sizing_status,
        "disks": derived_disks,
        "rto_minutes": money_number(rto),
        "rpo_minutes": money_number(rpo),
        "suggestions": suggestions,
    }


def derive(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Root JSON value must be an object")
    target_region = text(data.get("target_region"), "target_region")
    vms = data.get("vms")
    if not isinstance(vms, list):
        raise ValueError("vms must be an array")
    questions: list[dict[str, Any]] = []
    if target_region is None:
        add_question(
            questions, identifier="target-region", priority="P0",
            question="Qual e a regiao Azure de destino por VM ou grupo de execucao?",
            reason="Brazil South sera usada provisoriamente para o baseline.",
            affected=[], evidence="Plano de migracao ou decisao de arquitetura aprovada.",
        )
    with localcontext() as context:
        context.prec = 100
        derived_vms = [derive_vm(vm, questions) for vm in vms]
    if len({vm["id"] for vm in derived_vms}) != len(derived_vms):
        raise ValueError("VM IDs must be unique")
    groups: dict[str, list[dict[str, Any]]] = {}
    for vm in derived_vms:
        if vm["scope"] == "in_scope":
            groups.setdefault(vm["execution_group"]["name"], []).append(vm)
    group_result = [
        {
            "name": name,
            "vm_count": len(items),
            "confidence_pct": min(Decimal(item["execution_group"]["confidence_pct"]) for item in items).quantize(HUNDREDTH),
            "status": "A DEFINIR" if any(Decimal(item["execution_group"]["confidence_pct"]) < Decimal("50") for item in items) else "ready",
            "vm_ids": [item["id"] for item in items],
        }
        for name, items in sorted(groups.items())
    ]
    for group in group_result:
        group["confidence_pct"] = money_number(group["confidence_pct"])
    return {
        "schema_version": 1,
        "settings": {
            "target_region": target_region or "Brazil South",
            "target_region_status": "documented" if target_region else "A DEFINIR",
            "hours_per_month": "730",
            "pricing_baseline": "Public retail PAYG in USD",
            "cpu_memory_margin_pct": "20.00",
        },
        "summary": {
            "input_vm_count": len(derived_vms),
            "in_scope_vm_count": sum(vm["scope"] == "in_scope" for vm in derived_vms),
            "excluded_vm_count": sum(vm["scope"] == "excluded" for vm in derived_vms),
            "sizing_ready_vm_count": sum(vm["sizing_status"] == "ready" for vm in derived_vms),
        },
        "vms": derived_vms,
        "execution_groups": group_result,
        "questionnaire": questions,
        "notice": (
            "This output derives requirements only. SKU, price, quota, lifecycle, "
            "storage eligibility and architecture must be validated independently."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        source = args.input.resolve()
        if source.is_relative_to(SKILL_ROOT):
            raise ValueError("Customer input must not be stored in the skill directory")
        if not source.is_file():
            raise ValueError("Input JSON file does not exist")
        data = json.loads(source.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
        result = derive(data)
        payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            output = args.output.resolve()
            if output == source or output.is_relative_to(SKILL_ROOT):
                raise ValueError("Output must differ from input and be outside the skill directory")
            if not output.parent.is_dir():
                raise ValueError("Output directory must already exist")
            with output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            print(payload, end="")
        return 0
    except (OSError, ValueError, InvalidOperation, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
