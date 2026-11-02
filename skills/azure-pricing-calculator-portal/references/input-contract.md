# Contrato de entrada

## Objetivo

Normalizar Excel ou JSON heterogeneo em um plano deterministico. O plano fica na
pasta de trabalho da sessao, nunca nesta skill.

## Estrutura

```json
{
  "schema_version": "1.0",
  "estimate_name": "Estimativa Azure",
  "currency": "USD",
  "price_reference_date": "2026-01-31",
  "purchase_scenario": "PAYG",
  "tolerance_usd": "0.01",
  "components": [
    {
      "id": "C001",
      "source_reference": "Consolidado!A12",
      "source_service": "Origem opcional",
      "azure_product": "Virtual Machines",
      "display_name": "VM de aplicacao",
      "region": "Brazil South",
      "quantity": "744",
      "unit": "hour",
      "expected_monthly_cost": "100.00",
      "status": "PREMISSA",
      "representability": "DIRECT",
      "notes": "Validar com telemetria."
    },
    {
      "id": "C002",
      "source_reference": "Consolidado!A13",
      "azure_product": "Azure Backup",
      "display_name": "Retencao sem politica definida",
      "region": "Brazil South",
      "quantity": "1000",
      "unit": "GiB-month",
      "expected_monthly_cost": "20.00",
      "status": "A DEFINIR",
      "representability": "NOT_REPRESENTABLE",
      "notes": "Faltam workload, instancia protegida e politica."
    }
  ],
  "calculator_modules": [
    {
      "id": "M001",
      "component_ids": ["C001"],
      "calculator_product": "Virtual Machines",
      "display_name": "VM de aplicacao",
      "region": "Brazil South",
      "configuration": {
        "operatingSystem": "linux",
        "size": "f4sv2",
        "count": "1",
        "hours": "744",
        "computeBillingOption": "pay-as-you-go"
      },
      "derivation": "Configuracao direta da linha C001."
    }
  ]
}
```

## Regras

- Todos os valores numericos sao strings decimais ou `null`; nao usar float JSON.
- `expected_monthly_cost` deve existir. `null` significa **A DEFINIR**, nunca zero.
- Custo zero confirmado deve ser `"0"`.
- `source_reference` identifica arquivo/aba/celula, linha JSON ou outra evidencia.
- IDs de componentes e modulos sao unicos.
- Cada componente `DIRECT` ou `DERIVED` aparece em exatamente um modulo.
- `NOT_REPRESENTABLE` e `A_DEFINIR` nao aparecem em modulos.
- Um modulo pode referenciar varios componentes somente quando todos pertencem
  ao mesmo produto e a configuracao preserva as dimensoes tarifarias.
- `configuration` usa apenas objetos, listas, strings, booleanos e `null`.
  Numeros permanecem strings para preservar precisao.
- `derivation` explica agrupamentos e formulas; para `DERIVED`, ela e obrigatoria.

## Valores controlados

`status`:

- `CONFIRMADO`
- `PREMISSA`
- `SUGESTAO`
- `A DEFINIR`

`representability`:

- `DIRECT`
- `DERIVED`
- `NOT_REPRESENTABLE`
- `A_DEFINIR`

## Excel

Ao normalizar Excel:

- usar a skill `xlsx`;
- preservar formula e valor recalculado;
- registrar aba e celula;
- ler abas de detalhe quando o consolidado nao tiver SKU, unidade ou premissa;
- nao somar custos de cenarios alternativos;
- nao transformar branco, erro de formula ou texto em zero;
- confirmar se o total e mensal, anual, unico ou amortizado.

## JSON de origem

O JSON de origem pode usar outra estrutura. Converter por mapeamento explicito;
nao copiar campos desconhecidos para `configuration` sem entender sua semantica.
Rejeitar chaves duplicadas e numeros nao finitos.
