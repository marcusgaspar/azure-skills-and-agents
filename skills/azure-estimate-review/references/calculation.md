# Calculo reproduzivel

## Entrada e ferramentas

`scripts\recalculate.py` usa somente biblioteca padrao Python e Decimal.
Ele recebe JSON normalizado, nao interpreta XLSX/PPT/PDF nem consulta precos.
Extrair usando ferramentas de formato apropriadas; validar fontes ao vivo
separadamente. Resultado do script comprova aritmetica, nao validade do preco.
Nao instalar pacotes para este script.

Executar da pasta de trabalho da sessao (caminhos absolutos Windows):

```powershell
python "$HOME\.copilot\skills\azure-estimate-review\scripts\recalculate.py" "C:\caminho\da\sessao\review-input.json" --output "C:\caminho\da\sessao\review-result.json"
```

Nao usar a pasta da skill para dados de cliente. Entrada e saida devem ser
arquivos diferentes e saida nao pode existir; o script impede sobrescrita.
Dados invalidos geram erro e codigo 2; arquivo valido com lacunas/divergencias
gera resultado e codigo 1; codigo 0 indica so aritmetica completa/consistente.
Nao declarar checklist OK apenas pelo codigo 0.

## Schema

Valores numericos sao strings decimais, sem simbolos/separadores de milhar:
`"730"`, `"0.20"`; lacuna = `null`. Nunca converter celula vazia para zero.
Todos os fatores monetarios ja estao identificados por evidencia; linha calculada
deve resultar em USD/mes. Para converter custo local, multiplicar por taxa
USD/moeda-local; para apresentar moeda-local, usar inversa em script separado,
com fonte e data. USD/mes nao cobre sizing: executar formulas de capacidade em
script de sessao, tambem com Decimal/dados comprovados, e referenciar resultados.

```json
{
  "rounding": "total",
  "lines": [
    {"id": "base-a", "evidence": "arquivo-sintetico.xlsx!C2:F2", "factors": ["2", "730", "0.20"]},
    {"id": "base-b", "evidence": "arquivo-sintetico.xlsx!C3:F3", "factors": ["10"]},
    {"id": "fixed-a", "evidence": "fonte-sintetica; calculo C2 corrigido", "factors": ["3", "730", "0.20"]},
    {"id": "fixed-b", "evidence": "arquivo-sintetico.xlsx!C3:F3", "factors": ["10"]},
    {"id": "support-a", "evidence": "slides-sinteticos.pptx slide 2", "factors": ["292"]}
  ],
  "portfolios": [
    {"id": "original", "line_ids": ["base-a", "base-b"], "declared_total": "302", "evidence": "arquivo-sintetico.xlsx!F4"},
    {"id": "corrected", "line_ids": ["fixed-a", "fixed-b"], "declared_total": null, "evidence": "recalculo independente"},
    {"id": "component-breakdown", "line_ids": ["support-a"], "declared_total": "292", "evidence": "slides-sinteticos.pptx slide 2"}
  ],
  "comparisons": [
    {"id": "ppt-vs-original", "left": "component-breakdown", "right": "original", "evidence": "slide 2 vs arquivo-sintetico.xlsx!F4"}
  ],
  "impacts": [
    {"id": "capacity-correction", "original": "original", "revised": "corrected", "kind": "correction", "evidence": "capacidade corrigida; exemplo sintetico"}
  ]
}
```

Exemplo inteiramente sintetico: nao e preco Azure. `rounding` obrigatorio:
`line` arredonda cada linha antes de somar; `total` soma precisao completa e
arredonda no total; ROUND_HALF_UP a centavos. Explicar diferencas de arredondamento
da fonte; nao aplicar tolerancia para encobrir erros.

- `lines`: IDs unicos, evidencia nao vazia, `factors` com ao menos um valor.
  Usar quantidade x preco x horas/outros fatores aplicaveis; ou `[valor]` para
  uma linha de apoio transcrita. Campo faltante deve ser null, nao valor presumido.
  Fatores negativos permitidos para creditos explicitos com evidencia.
- `portfolios`: IDs unicos, conjunto sem duplicatas de IDs de linhas, evidencia
  e `declared_total` (string ou null). Total calculado incompleto retorna null e
  subtotal conhecido rotulado; null propagado mesmo se outro fator for zero.
  `declared_total=null` significa total de origem nao informado/intencionalmente
  nao aplicavel a cenario derivado; nunca atesta reconciliacao.
- `comparisons`: igualdade entre portfolios (aba x resumo, arquivo x slide,
  proposta x calculadora, mes/fase x resumo). Conferir pertença/quantidades
  separadamente: total igual pode ocultar duas divergencias compensatorias.
- `impacts`: `revised - original`, `kind` = `correction` ou `alternative`.
  Cenarios completos separados; nao somar alternativas. Nenhum agregado de
  economias e produzido. Se escopo diferente, documentar ponte antes de comparar.

Criar um portfolio para cada quebra independente: ambientes, componentes,
grupos, Sem SKU e compartilhados. Incluir alocacoes rateadas como linhas de
apoio com evidencia; reconciliar rateios com o custo bruto. O script rejeita
duplicacao de ID dentro de um portfolio, mas nao detecta duas linhas distintas
que representam o mesmo medidor; conferir semantica no checklist.

Ao corrigir, usar um portfolio completo com linhas preservadas + alteradas +
adicionadas - removidas; preservar o baseline e explicar cada mudanca.
Cada impacto de achado usa portfolios limitados ao mesmo escopo; impacto
consolidado so em novo cenario conjunto, sem somar deltas sobrepostos.

## Formulas adicionais de sessao

Implementar formulas especificas com parametros documentados e origem, sem
inventar relacoes universais: TPS medio x segundos efetivos/dia; pico e duracao;
operacoes x RU medidas; mensagens x fan-out/retries/operacoes cobradas; GB/dia x
retencao com fatores de replicacao/compressao comprovados; capacidade disponivel
apos perder zona; IOPS/throughput limitado por VM E disco; ramp-up mes a mes.
Limites e margens devem vir da fonte/benchmark/requisito, nao desta skill.

Descontos por SKU exigem dois custos reais comparaveis e comprovacao de
elegibilidade. Economia = custo comparavel original - custo do cenario;
impacto = inverso. Calcular percentual apenas como resultado, nunca premissa.
Separar upfront, equivalente mensal e fatura mensal; prazo usado deve ser
explicito, nao divisor presumido. Nao somar reserva + Savings Plan concorrentes.

Fonte faltante: calcular apenas subtotal conhecido, apresentar total/impacto
como A DEFINIR. Anexar entrada sanitizada autorizada e resultado no relatorio,
sem inserir dados da revisao na skill.
