# Contrato de saida

## Arquivos Excel

Na pasta dos anexos, descobrir a proxima versao comum usando:

- `IaaS-Inventario-Consolidado-vN.xlsx`
- `IaaS-Custo-Calculadora-vN.xlsx`

Usar o maior `N` existente entre os dois prefixos mais um. Se qualquer arquivo
do par ja existir, incrementar novamente. Nunca sobrescrever, renomear ou apagar
arquivo de entrada/saida. Usar `scripts/next_output_version.py` antes de criar e
revalidar inexistencia imediatamente antes de salvar.

Ativar a skill `xlsx` para ambos. Usar fonte profissional consistente, filtros,
congelamento de cabecalho, larguras legiveis e formatos de numero adequados.
Inputs editaveis em azul, formulas em preto, links internos em verde e premissas
criticas em amarelo, salvo se o usuario fornecer modelo com convencao propria.
Todos os calculos devem ser formulas Excel; usar recalculo/validacao da skill
`xlsx` e entregar zero erros de formula.

### IaaS-Inventario-Consolidado-vN.xlsx

| Aba | Conteudo minimo |
| --- | --- |
| Resumo | Data, fontes, regiao, VMs em escopo/excluidas, grupos, status de quota e snapshot reconciliado do total de custo |
| Inventario Consolidado | Uma linha por VM, ID canonico, fontes, aplicacao, ambiente, destino, configuracao atual, SO, status e confianca de identidade |
| Arquitetura IaaS | Modelo VM/VMSS, zona/HA, storage, backup/DR, pre-requisitos de rede e status de evidencia por grupo |
| Discos e Storage | Uma linha por volume: capacidade, papel, P95, demanda com margem, candidato e status |
| Sizing VM | Atual, P95, demanda, candidatos elegiveis, SKU recomendado, Azure Migrate, divergencia, evidencia e status |
| Grupos de Execucao | Grupo, metodo, confianca, VMs, custo mensal ligado ao BOM e observacoes |
| Excluidas | VM, motivo, evidencia e acao para reavaliar |
| A DEFINIR | Lacuna, VMs/grupos afetados, impacto, dono, evidencia necessaria e prioridade |
| Questionario | Pergunta, motivo, impacto, VMs/grupos, dono sugerido, evidencia pedida e prioridade |
| Fontes e Validacao | Fontes, skills Azure usadas, datas, regras oficiais, testes de reconciliacao e resultado |

### IaaS-Custo-Calculadora-vN.xlsx

| Aba | Conteudo minimo |
| --- | --- |
| Resumo | Total mensal USD, total por grupo, itens excluidos, fora do modelo e A DEFINIR |
| Premissas | Regiao, 730 h, moeda, precificacao PAYG, data das fontes e campos de premissa |
| BOM | Uma linha por medidor: VM/grupo, categoria, SKU, quantidade, unidade, preco, horas, formula, custo, fonte e status |
| Precos | Preco unitario, unidade, data, URL e parametros que o distinguem |
| Calculator_Input | Servico, configuracao e valores para revisao/digitacao manual na Calculadora |
| Backup_HA_DR | Apenas itens com requisitos comprovados; demais lacunas referenciadas |
| Fora_do_Modelo | Rede, suporte, impostos, cambio, migracao e outros itens sem escopo/fonte |
| A DEFINIR | Linhas de custo nao calculaveis e perguntas para completar o BOM |
| Validacao | Reconciliacao BOM-resumo-grupo e resultado do recalculo sem erros |

O snapshot de custo no inventario deve indicar arquivo/aba/celulas de origem,
data e delta de reconciliacao. Por padrao, nao usar formulas com links externos
entre os dois workbooks; ambos precisam abrir sem atualizar vinculos. Se o usuario
pedir vinculos externos, formatar e validar conforme a skill `xlsx`.

## Resumo no chat

Entregar apenas a tabela curta abaixo, seguida de "A DEFINIR" e "[SUGESTÃO]
aplicadas". Usar `A DEFINIR`, nao `0`, quando custo, grupo ou escopo nao puder
ser comprovado.

| Grupo de execucao / status | VMs | Custo mensal (USD) | Evidencia e observacao |
| --- | ---: | ---: | --- |
| Em escopo - <grupo> | <qtd> | <valor ou A DEFINIR> | <metodo/confianca e principal ressalva> |
| Excluidas | <qtd> | Nao precificado | <motivos documentados> |
| Total em escopo | <qtd> | <valor ou A DEFINIR> | <reconciliacao do BOM> |

**A DEFINIR:** lista curta de lacunas materiais, VMs/grupos afetados e impacto.

**[SUGESTÃO] aplicadas:** listar somente as que foram usadas, incluindo motivo e
VM/grupo. Se nenhuma, escrever "Nenhuma".

**Arquivos:** informar os dois nomes/versionamento criados. O questionario
completo fica na aba `Questionario`; no chat citar somente perguntas bloqueadoras.
