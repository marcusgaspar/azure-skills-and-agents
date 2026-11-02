# Checklist de validacao

## Entrada e reconciliacao

- [ ] Todos os arquivos foram inventariados e preservados.
- [ ] O periodo e a moeda foram confirmados.
- [ ] Linhas por servico reconciliam com os subtotais.
- [ ] Servicos reconciliam com o total pre-impostos.
- [ ] Impostos e total final reconciliam separadamente.
- [ ] Duplicidades e exclusoes possuem evidencia e impacto documentados.

## Gate comercial

- [ ] O usuario respondeu ao gate obrigatorio.
- [ ] O modelo e exatamente PAYG, 1Y RI, 3Y RI, 1Y Savings Plan ou 3Y Savings Plan.
- [ ] O modelo aparece em Resumo, Premissas e Validacao.
- [ ] Elegibilidade foi verificada por SKU e servico.
- [ ] Nao foi aplicado desconto percentual generico.
- [ ] Parcela nao elegivel permanece PAYG.

## Mapeamento e precos

- [ ] Cada servico possui destino, justificativa, risco e alternativa.
- [ ] Itens sem destino defensavel estao `NAO MAPEADO`.
- [ ] Itens sem dados suficientes estao `A DEFINIR`.
- [ ] Cada preco possui fonte, data, regiao, moeda, unidade e modelo.
- [ ] Sizing sem telemetria esta marcado `PREMISSA`.
- [ ] Custos desconhecidos estao em branco, nao em zero.
- [ ] Descontos, creditos e ajustes nao contam como consumo precificado.

## Workbook

- [ ] Existem Resumo, Premissas, Fontes e Validacao.
- [ ] Existe uma aba detalhada por servico AWS.
- [ ] Toda linha do Resumo aponta para a aba correta.
- [ ] Totais das abas detalhadas reconciliam com o Resumo.
- [ ] Formulas foram recalculadas.
- [ ] Nao existem `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`, `#NULL!` ou `#NUM!`.
- [ ] Nao existem links externos.
- [ ] Cobertura exclui impostos, descontos, creditos e ajustes financeiros.
- [ ] O total Azure conhecido soma somente parcelas calculadas.
- [ ] O arquivo final existe no destino combinado e nao sobrescreveu versao anterior.

## Entrega

Informar de forma concisa:

- caminho ou link do arquivo;
- total AWS comparado;
- estimativa Azure conhecida;
- cobertura;
- modelo comercial;
- principais itens `A DEFINIR` e `NAO MAPEADO`;
- impostos, suporte, licencas ou descontos excluidos;
- limitacoes de validacao, se houver.
