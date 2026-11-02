# Fontes oficiais e armadilhas por servico

Estes links sao pontos de partida, nao evidencias de uma revisao. Abrir a pagina
oficial atual, seguir referencias especificas e registrar regra, escopo e data.
Se movido, localizar no dominio oficial; se indisponivel, A DEFINIR. Nao citar
resultado de busca como regra. Nao embutir precos, limites ou datas fixos na skill.

## Precos, disponibilidade e ciclo de vida

- Calculator: https://azure.microsoft.com/pricing/calculator/
- Precos por produto: https://azure.microsoft.com/pricing/
- Retail Prices API: https://learn.microsoft.com/rest/api/cost-management/retail-prices/azure-retail-prices
- Reservas: https://learn.microsoft.com/azure/cost-management-billing/reservations/
- Savings Plan: https://learn.microsoft.com/azure/cost-management-billing/savings-plan/
- AHB: https://azure.microsoft.com/pricing/hybrid-benefit/
- Limites gerais: https://learn.microsoft.com/azure/azure-resource-manager/management/azure-subscription-service-limits
- Disponibilidade regional: https://azure.microsoft.com/explore/global-infrastructure/products-by-region/
- Azure Updates: https://azure.microsoft.com/updates/
- Microsoft Lifecycle: https://learn.microsoft.com/lifecycle/
- Red Hat support/lifecycle: https://access.redhat.com/support/policy/updates/openshift

Na API de varejo conferir paginacao, effectiveStartDate, currencyCode, armRegionName,
armSkuName, productName, skuName, meterName, unitOfMeasure e type.
Nao selecionar o primeiro resultado sem desambiguar Linux/Windows, spot/normal,
reserva/consumo, prazo ou medidores complementares. unitPrice/retailPrice requerem
interpretacao conforme documentacao atual. Reserva pode apresentar valor do prazo,
nao preco horario. A API nao prova preco contratado nem elegibilidade.
Sem acesso autenticado a contrato/cota real, indicar limitacao; nao substituir
cota da assinatura por limite teorico publico.

Documentar status GA/preview, disponibilidade/retirada de SKU e suporte de
engine/versao/SO separadamente. Obter data efetiva e transicao oficial; existir
no catalogo de precos nao significa estar disponivel para nova implantacao.

## Matriz de verificacoes

| Servico | Documentacao inicial oficial | Conferir na revisao |
| --- | --- | --- |
| VMs/migracao | https://learn.microsoft.com/azure/virtual-machines/ ; https://learn.microsoft.com/azure/migrate/ | vCPU/memoria/arquitetura; CPU medida x alocada; series e disponibilidade; discos locais/efemeros; limites VM+disco IOPS/throughput; discos gerenciados e snapshots; aceleracao/burst credit; Windows/Linux/SQL/licencas; AHB/ESU; compute desligado vs desalocado; backup, DR e coexistencia. |
| AKS | https://learn.microsoft.com/azure/aks/ ; https://azure.microsoft.com/pricing/details/kubernetes-service/ | Tier e taxa por cluster conforme regra vigente, nao por pool; system/user pools, SO, overhead/DaemonSets, requests/limits, autoscaler minimo; replicas/topologia sob falha; IPs, load balancer, NAT, discos/PVs, ACR, logs, Defender; versao/LTS e suporte. |
| ARO | https://learn.microsoft.com/azure/openshift/ ; https://azure.microsoft.com/pricing/details/openshift/ | Cobranca de infraestrutura e plataforma/licenca sem duplicar; control plane/workers, tamanhos/minimos vigentes, storage e rede; topologia/regiao; versao OpenShift/suporte Microsoft+Red Hat; nao aplicar automaticamente regras AKS. |
| Cosmos DB | https://learn.microsoft.com/azure/cosmos-db/ ; https://azure.microsoft.com/pricing/details/cosmos-db/ | API e modelo de cobranca (RU ou vCore conforme produto); RU medido por operacao, indexacao, distribuicao/skew e limites de particao; provisionado/autoscale/serverless, minimo por container/banco/volume; regioes e write mode; failover por particao e pre-requisitos; storage, backup, replicacao e elegibilidade de reservas. |
| Service Bus | https://learn.microsoft.com/azure/service-bus-messaging/ ; https://azure.microsoft.com/pricing/details/service-bus/ | Basic/Standard/Premium, unidade mensagem/operacao/MU, granularidade e minimo; fan-out, retries, settlement, batch e payload; conexoes e quotas; particionamento, zonas, geo-replicacao/DR e diferenca entre metadados e mensagens; benchmark nao throughput universal. |
| Redis | https://learn.microsoft.com/azure/redis/ ; https://learn.microsoft.com/azure/azure-cache-for-redis/ ; https://azure.microsoft.com/pricing/details/managed-redis/ | Identificar Azure Managed Redis vs Azure Cache for Redis e SKU exato; aposentadoria/migracao vigente; memoria util/overhead, replicas/shards, persistencia, HA/zonas e backup; conectividade; elegibilidade atual de reserva, sem presumir entre produtos. |
| HSM/chaves | https://learn.microsoft.com/azure/key-vault/managed-hsm/ ; https://learn.microsoft.com/azure/dedicated-hsm/ ; https://learn.microsoft.com/azure/cloud-hsm/ ; https://azure.microsoft.com/pricing/details/key-vault/ | Distinguir Key Vault, Managed HSM, Dedicated HSM e Cloud HSM; cobranca por pool/dispositivo/operacao conforme produto; TPS por algoritmo/tamanho/chave e latencia; minimo/HA/capacidade sob falha; backup/licencas/rede; ciclo de vida. Nao converter disponibilidade do produto em certificacao ICP-Brasil/PCI. |
| Storage | https://learn.microsoft.com/azure/storage/ ; https://azure.microsoft.com/pricing/details/storage/ | Tipo, tier, redundancia, GB/TB decimal vs GiB/TiB, media mensal x capacidade alocada; operacoes/read/write/list, retrieval, reidratacao, retencao minima/exclusao antecipada; versionamento, soft delete, snapshots, replicacao, egress; Files/Blob/ADLS/discos nao intercambiaveis. |
| Rede | https://learn.microsoft.com/azure/networking/ ; https://azure.microsoft.com/pricing/details/bandwidth/ | Matriz origem-destino e direcao, volume/frequencia; peering intra/inter-regiao, interzona e regras atuais (nao assumir taxa antiga); internet/intercloud; ExpressRoute porta/circuito/provedor, VPN/gateways; Firewall/NAT/LB/private endpoints por hora e dados; evitar contar o mesmo fluxo duas vezes. |
| SQL Database/MI/SQL em VM | https://learn.microsoft.com/azure/azure-sql/ ; https://azure.microsoft.com/pricing/details/azure-sql-database/ ; https://azure.microsoft.com/pricing/details/azure-sql-managed-instance/ | Modelo vCore/DTU, tier/hardware, storage/log/temp, IOPS e limites; serverless/auto-pause/restricoes; HA/replicas de leitura/DR, PITR/LTR e consumo backup; licenca incluida/AHB, reservas elegiveis; limites e compatibilidade de migracao; SQL VM com preco compute+licenca separado. |
| PostgreSQL/MySQL | https://learn.microsoft.com/azure/postgresql/ ; https://learn.microsoft.com/azure/mysql/ | Produto/engine/versao, tier e tamanho, burst, memoria/conexoes, storage/IOPS/auto-growth, HA e replicas, backup/PITR, egress; suporte estendido e aposentadoria; minimos/pausa/autoscale/reservas especificos. |
| Demais PaaS/DB | https://learn.microsoft.com/azure/ ; https://azure.microsoft.com/pricing/ | Identificar produto exato (nao "banco Azure" generico), plano/instancias/minimos, escala/regiao, request/compute/storage/licenca, versao/suporte, limites e backup. Buscar documentacao especifica antes de concluir. |
| Transversais | https://learn.microsoft.com/azure/azure-monitor/ ; https://learn.microsoft.com/azure/defender-for-cloud/ ; https://learn.microsoft.com/azure/backup/ ; https://learn.microsoft.com/azure/site-recovery/ | Ingestao/retencao/exportacao e duplicacao logs; planos Defender por recurso; protegido/storage/backup e DR; ACR/CI-CD, landing zone, chaves, licencas, suporte. Franquia ou compartilhamento requer regra de rateio, nao custo zero presumido. |

## Evidencia minima por regra

Guardar na pasta da sessao: ID do item, arquivo/aba/celula ou pagina/slide,
URL oficial, titulo/secao, trecho factual curto, data de consulta, data efetiva,
produto/SKU/regiao/versao, unidade e premissa relacionada.
Benchmark interno autorizado pode fundamentar sizing, mas nao substitui fonte
oficial de preco/limite/ciclo de vida; nao expor benchmark privado a terceiros.
