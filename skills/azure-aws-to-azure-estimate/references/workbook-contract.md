# Contrato do workbook

## Arquivo

Usar nome descritivo e versionado, por exemplo:

`Estimativa_Custos_AWS_Azure_<Periodo>_vN.xlsx`

Nunca sobrescrever uma versao existente sem confirmacao.

## Abas obrigatorias

### Resumo

Uma linha por servico AWS, ordenada por custo AWS decrescente:

| Coluna | Conteudo |
|---|---|
| Servico AWS | Nome observado |
| Provedor | AWS ou Marketplace |
| Custo AWS | Total reconciliado |
| Percentual AWS | Participacao no total comparado |
| Equivalente Azure | Servico ou conjunto de servicos |
| Estimativa Azure | Parcela conhecida no modelo escolhido |
| Delta | Azure menos AWS |
| Delta percentual | Variacao relativa |
| Cobertura | Percentual de cobrancas operacionais precificadas |
| Status | Estado padrao |
| Detalhe | Link interno para a aba do servico |
| Principal ressalva | Maior limitacao da linha |

No topo, exibir:

- periodo;
- total AWS pre-impostos;
- impostos excluidos;
- total final da fatura;
- estimativa Azure conhecida;
- cobertura ponderada;
- moeda;
- regiao principal;
- data-base;
- modelo comercial selecionado.

`A DEFINIR` e `NAO MAPEADO` devem mostrar estimativa Azure em branco. `PARCIAL`
mostra apenas a parcela conhecida. `SEM CUSTO/EXCLUIDO` pode mostrar zero.

### Premissas

Registrar escopo, moeda, regioes, horas, redundancia, sizing, licencas, impostos,
suporte, modelo comercial, descontos e todos os itens **A DEFINIR**.

### Fontes

Uma linha por fonte com titulo, URL ou identificador, secao/medidor, data de
consulta, aplicacao e observacao. Nao criar links externos executaveis no workbook
quando isso comprometer a portabilidade; texto simples e aceitavel.

### Validacao

Exibir resultados de reconciliacao, contagem de servicos, linhas efetivas, erros de
formula, links externos, cobertura, data-base e modelo comercial.

### Abas detalhadas

Criar uma aba para cada servico AWS. Nomes devem ser unicos e ter no maximo 31
caracteres. Incluir no topo:

- nome completo do servico;
- provedor;
- total AWS;
- estimativa Azure conhecida;
- parcela AWS sem estimativa;
- cobertura;
- status;
- modelo comercial;
- principal ressalva.

Colunas minimas:

1. evidencia;
2. regiao AWS;
3. regiao Azure;
4. categoria AWS;
5. descricao AWS;
6. quantidade AWS;
7. unidade AWS;
8. custo AWS;
9. servico Azure;
10. SKU ou medidor;
11. quantidade Azure;
12. unidade Azure;
13. preco Azure;
14. formula;
15. custo Azure;
16. modelo comercial;
17. status;
18. premissa;
19. fonte;
20. tipo de linha;
21. custo AWS operacional;
22. confianca.

## Formatacao

- Moeda e percentuais com formatos numericos, nao texto.
- Negativos entre parenteses.
- Zero pode ser exibido como traco, sem alterar o valor numerico.
- Premissas e lacunas em amarelo.
- Formulas, entradas e links internos visualmente distinguiveis.
- Congelar cabecalhos, aplicar filtros e larguras legiveis.
- Nao criar links para arquivos externos.
