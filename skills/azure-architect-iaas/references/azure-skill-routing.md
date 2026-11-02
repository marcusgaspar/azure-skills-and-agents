# Roteamento de skills Azure oficiais

Verificar a instalacao atual em `$HOME\.agents\skills\` ou na pasta configurada pelo usuario antes de
cada revisao. A tabela usa nomes existentes na data de criacao desta skill;
se uma skill estiver ausente, nao inventar substituto e registrar limitacao.

| Necessidade | Skill oficial | Uso permitido nesta revisao |
| --- | --- | --- |
| Familia, SKU, VM/VMSS, precos varejo e candidatos | `azure-compute` | Obrigatoria para recomendacao de VM. Abrir `vm-recommender` primeiro, usar leitura/documentacao/preco; nunca `vm-creator`. |
| Discos, Azure Files, Blob, tiers e lifecycle storage | `azure-storage` | Obrigatoria quando recomendar storage. Confirmar tipo exato em documentacao atual; nao criar contas/compartilhamentos. |
| Preco, custo e forecast de assinatura | `azure-cost` | Aplicavel para custos reais autorizados, comparacao e fonte de preco. Nao consultar assinatura sem escopo/RBAC. |
| Rightsizing/custo real e recursos ociosos | `azure-cost-optimization` | Aplicavel somente se o usuario autorizou analise de assinatura. Nao rodar azqr ou scans por padrao. |
| Cota e limite efetivo | `azure-quotas` | Aplicavel com assinatura, regiao e leitura autorizadas. So leitura; nunca solicitar aumento. |
| Recursos/dependencias existentes | `azure-resource-lookup` | Aplicavel com escopo explicitamente limitado e acesso Reader. Preferir fonte anexa quando suficiente. |
| Topologia Azure existente | `azure-resource-visualizer` | Aplicavel se a relacao de recursos for necessaria e o escopo Azure for autorizado. Nao criar diagramas especulativos. |
| Metricas Azure Monitor/Log Analytics | `azure-observability` | Aplicavel quando a telemetria nao vier nos anexos e acesso de leitura for autorizado. |
| KQL/ADX para telemetria | `azure-kusto` | Aplicavel somente a dados/cluster autorizados, sempre com filtro temporal e consultas de leitura. |
| Requisitos regulatorio/politica | `azure-compliance` | Aplicavel apenas se solicitado; tratar resultado como evidencia tecnica, nunca certificacao. |

`azure-deploy`, `azure-prepare`, `azure-app-onboard`, `azure-validate`,
`azure-cloud-migrate`, `azure-upgrade` e `azure-reliability` nao sao ativadas
automaticamente: seus fluxos de deploy, codigo, upgrade ou PaaS estao fora desta
recomendacao IaaS. Consultar outra skill somente se o escopo pedir exatamente
sua capacidade e sem executar acoes mutaveis.

No artefato interno, registrar `nome | invocada/consultada | contribuicao |
limitacao`. Nunca alegar que uma skill foi invocada se apenas sua documentacao
foi lida.
