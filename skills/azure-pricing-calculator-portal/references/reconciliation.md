# Reconciliacao

## Valores

Calcular com `Decimal`:

- `expected_total`: soma dos custos conhecidos de todos os componentes;
- `represented_expected`: soma dos componentes referenciados por modulos;
- `unrepresented_expected`: soma dos componentes fora dos modulos;
- `portal_module_total`: soma dos subtotais online;
- `portal_total`: total declarado pela pagina;
- `pricing_rule_delta = portal_total - represented_expected`;
- `net_delta = portal_total - expected_total`.

Identidade esperada:

```text
net_delta = pricing_rule_delta - unrepresented_expected
```

O script verifica tambem:

```text
portal_total = soma dos modulos online
pricing_rule_delta = soma dos ajustes explicados
```

## Resultado do portal

```json
{
  "estimate_name": "Estimativa Azure",
  "currency": "USD",
  "query_date": "2026-02-01",
  "total_portal": "105.00",
  "modules": [
    {
      "id": "M001",
      "actual_monthly_cost": "105.00",
      "evidence": "Subtotal renderizado no modulo M001"
    }
  ],
  "adjustments": [
    {
      "id": "A001",
      "category": "CURRENT_PRICE",
      "amount": "5.00",
      "component_ids": ["C001"],
      "evidence": "Preco online consultado na data da execucao."
    }
  ],
  "share_url": "https://azure.com/e/example",
  "link_validation": {
    "observed_estimate_name": "Estimativa Azure",
    "observed_currency": "USD",
    "observed_total": "105.00",
    "evidence": "Link aberto em nova sessao."
  }
}
```

Categorias de ajuste:

- `CURRENT_PRICE`
- `FREE_TIER`
- `MINIMUM`
- `BILLING_BLOCK`
- `MONTH_HOURS`
- `ROUNDING`
- `OTHER_VERIFIED`

`amount` sempre usa o sinal `online - esperado representado`.

## Interpretacao

- `PREPARED`: plano valido antes da coleta do portal.
- `RECONCILED_NOT_SHARED`: modulos e explicacoes fecham, mas nao ha link validado.
- `RECONCILED_AND_VALIDATED`: aritmetica fecha e o link foi reaberto com nome,
  moeda e total corretos.
- `A DEFINIR`: ha custo ausente, representabilidade indefinida, modulo faltante,
  total de modulos divergente, ajuste inexplicado ou falha na validacao do link.

## Tolerancia

Usar a tolerancia declarada no plano, normalmente `0.01` na moeda da estimativa.
Nao ampliar a tolerancia para ocultar diferenca material. Se a pagina arredondar
somente a exibicao, capturar o valor mais preciso disponivel e documentar.

## O que nao fazer

- nao criar linha de ajuste no portal;
- nao alterar quantidade para reproduzir um preco historico;
- nao misturar itens excluidos com ajustes de preco;
- nao tratar item sem preco como zero;
- nao declarar reconciliado apenas porque o total parece proximo.
