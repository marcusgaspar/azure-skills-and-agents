# Roteamento para skills oficiais Azure

Pasta preferencial: `$HOME\.agents\skills\` ou a pasta configurada pelo usuario.
Esse conteudo e gerenciado externamente: nao editar, copiar ou congelar suas
instrucoes dentro desta skill. Reconsultar os arquivos instalados a cada revisao,
pois nomes, capacidades e procedimentos podem mudar.

## Procedimento obrigatorio

1. Inventariar os componentes e as questoes da estimativa.
2. Conferir quais skills existem na pasta e ler seus metadados de escopo.
   A tabela abaixo e ponto de partida, nao lista fechada nem promessa de capacidade.
3. Para cada skill aplicavel, invocar pelo nome se disponivel no runtime; se nao,
   consultar `<pasta>\<nome>\SKILL.md` e referencias pertinentes. Seguir as
   instrucoes aplicaveis ao modo revisao, sem ampliar a autorizacao.
4. Reutilizar orientacoes, formulas, fontes e ferramentas de leitura pertinentes;
   verificar a adequacao ao produto, regiao, lista comercial e data da estimativa.
   Nao usar estimativa rapida ou percentual heuristico como preco validado.
5. Se ausente, restrita ou dependente de ferramenta/permissao indisponivel,
   registrar motivo. Nao instalar nem substituir silenciosamente. Prosseguir
   com documentacao oficial atual e scripts locais onde possivel; marcar como
   A DEFINIR apenas as verificacoes efetivamente bloqueadas.
6. Registrar no parecer uma linha compacta de "Skills Azure utilizadas":
   nome + invocada/consultada + contribuicao. Em "O que nao pode ser verificado",
   listar limitacoes que afetaram resultados. Na versao externa, usar
   "Pontos a confirmar" e omitir caminhos locais/informacoes internas.

## Mapeamento inicial

| Questao ou componente | Skills candidatas | Uso na revisao e restricoes |
| --- | --- | --- |
| Precos, custo, forecast e otimizacoes | `azure-cost`, `azure-cost-optimization` | Priorizar `azure-cost` para roteamento; reutilizar analise de desperdicio/rightsizing quando pertinente. Custo real de assinatura so com escopo autorizado; nao iniciar auditoria do ambiente para revisar uma planilha. Nao somar economias alternativas nem usar percentual fixo. |
| Migracao de VMs, SKU, capacidade e sizing | `azure-compute` | Comparacao de familias, desempenho, precos, capacidade e disponibilidade; somente consultas. Nao criar VM, VMSS ou reserva de capacidade. |
| AKS, pools, autoscale e sizing de pods | `azure-kubernetes` | Requests/limits, overhead, topologia, falha zonal e escolha de SKU. Nao provisionar cluster nem alterar workloads. ARO nao herda automaticamente regras AKS. |
| Quotas e disponibilidade | `azure-quotas` | Conferir capacidade/cotas regionais quando houver acesso autorizado; nao solicitar aumento. Sem acesso, distinguir limite publico de cota efetiva nao verificada. |
| Storage, discos e retencao | `azure-storage` | Reutilizar orientacao aplicavel ao tipo exato de armazenamento e suas unidades; confirmar cobranca na fonte atual. |
| Service Bus e Event Hubs | `azure-messaging` | Consultar semantica de operacoes, retries e comportamento do SDK quando relevante a volumetria; nao iniciar troubleshooting de producao sem pedido. |
| Observabilidade, logs e retencao | `azure-observability` | Avaliar ingestao, retencao e custos transversais. `appinsights-instrumentation` apenas para conferir premissas de instrumentacao; nao editar aplicacoes. |
| Telemetria para sizing | `azure-kusto`, `azure-diagnostics` | Consultas/KQL e leitura de evidencias autorizadas quando necessarias; nao iniciar investigacao ou remediacao fora do escopo. |
| Arquitetura, rede, landing zone e dependencias | `azure-enterprise-infra-planner`, `azure-reliability` | Reutilizar criterios arquiteturais, HA/DR e WAF; nao gerar/aplicar infraestrutura como parte da revisao. |
| Inventario e topologia existentes | `azure-resource-lookup`, `azure-resource-visualizer` | Ler recursos/topologia apenas do escopo autorizado, quando isso resolve uma premissa; nao expandir para toda a organizacao. |
| Ciclo de vida e upgrade | `azure-upgrade` | Consultar orientacao de compatibilidade/transicao; confirmar datas oficiais atuais. Nao executar upgrade ou migracao. |
| Migracao de outras nuvens | `azure-cloud-migrate` | Reutilizar avaliacao de equivalencias e premissas; nao converter codigo nem executar migracao sem pedido. |
| Conformidade/restricoes reguladoras | `azure-compliance` | Consultar criterios tecnicos pertinentes; sem scans/azqr por padrao e sem certificar Bacen, LGPD, PCI ou ICP-Brasil. |
| AI/Foundry/API gateway presentes | `azure-ai`, `microsoft-foundry`, `azure-aigateway` | Conferir componentes e medidores adicionais apenas quando constarem no escopo; nao configurar endpoints/gateway/modelos. |
| Readiness de aplicacao como premissa da estimativa | `azure-app-onboard-prereq` | Somente quando codigo/readiness estiver no escopo autorizado; nao presumir acesso ao repositorio nem iniciar deployment. |

Para Cosmos DB, Redis, HSM, ARO e bancos de dados, verificar se ha skill
especifica na instalacao atual; nao inventar nome. Na ausencia, usar skills
transversais pertinentes e documentacao oficial especifica da matriz de fontes.

`azure-deploy`, `azure-prepare`, `azure-app-onboard`, `azure-validate`,
`python-appservice-deploy` e `airunway-aks-setup` nao devem ser acionadas somente
porque a estimativa menciona Azure: seus fluxos de implementacao/implantacao
nao fazem parte deste parecer. Consultar referencias pontuais apenas se
necessarias, sem iniciar os respectivos fluxos.

Skills auxiliares sao apoio, nao revisores independentes adicionais. Esta skill
permanece responsavel por reconciliacao, evidencia, checklist, imparcialidade,
veredito e guardrails. Se alguma instrucao auxiliar conflitar com revisao
somente leitura, nao executar a acao conflitante e explicitar a limitacao.
