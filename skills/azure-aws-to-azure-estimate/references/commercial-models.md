# Modelos comerciais Azure

## Regra de selecao

O modelo comercial deve ser confirmado em toda execucao antes da precificacao:

1. `PAYG`
2. `1Y RI`
3. `3Y RI`
4. `1Y Savings Plan`
5. `3Y Savings Plan`

Registrar a escolha nas abas `Resumo`, `Premissas` e `Validacao`.

## PAYG

- Usar preco publico por consumo, sem compromisso.
- Preservar a unidade real do medidor: hora, segundo, GB-mes, operacao, instancia,
  throughput ou outra unidade publicada.
- Nao assumir 730 horas para componentes cujo consumo medido ja esteja disponivel.
- Componentes sem medidor publico ficam **A DEFINIR**.

## 1Y RI e 3Y RI

- Aplicar somente a servicos, familias, SKUs, regioes e quantidades elegiveis para
  reserva Azure na data da consulta.
- Registrar termo, escopo, quantidade reservada, preco total, forma de pagamento
  publicada e custo mensal amortizado.
- A parcela elegivel usa RI; uso excedente e componentes nao elegiveis usam PAYG.
- Sem quantidade estavel, cobertura ou utilizacao demonstravel, marcar a aplicacao
  como **PREMISSA** ou **A DEFINIR**.
- Nao converter reserva em desconto percentual fixo sobre o total.

## 1Y Savings Plan e 3Y Savings Plan

- Aplicar somente ao compute elegivel segundo a documentacao atual.
- Registrar termo, compromisso horario, moeda, regiao/escopo aplicavel, preco
  efetivo e utilizacao esperada.
- Consumo acima do compromisso e servicos nao elegiveis permanecem PAYG.
- Se compromisso horario, cobertura ou utilizacao nao estiverem disponiveis, nao
  inventar o valor. Mostrar a parcela PAYG conhecida e deixar o beneficio como
  **A DEFINIR** ou construir um cenario claramente rotulado como **PREMISSA**.
- Nao aplicar Savings Plan a storage, rede, suporte ou outros medidores sem
  elegibilidade oficial comprovada.

## Regras comuns

- Um consumo recebe no maximo um beneficio comercial no baseline.
- Nao somar RI, Savings Plan, Azure Hybrid Benefit ou desconto contratado sem
  elegibilidade e alocacao separadas.
- Quando Azure Hybrid Benefit for solicitado, tratar como premissa adicional e
  validar direitos de Windows Server, SQL Server ou Linux separadamente.
- Usar a mesma data-base em todas as linhas do cenario. Excecoes devem ser
  destacadas.
- Preco contratado exige evidencia autorizada. Na ausencia, usar preco publico e
  rotular como estimativa de varejo.
