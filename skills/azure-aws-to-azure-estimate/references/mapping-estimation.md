# Mapeamento e estimativa

## Principio

Um nome parecido nao comprova equivalencia. Validar funcao, capacidade, resiliencia,
desempenho, operacao, seguranca, licenca e unidade de cobranca.

Para cada componente, registrar:

| Campo | Conteudo |
|---|---|
| Componente atual | Servico, SKU ou usage type AWS |
| Evidencia | Arquivo e referencia de origem |
| Servico Azure | Destino recomendado |
| Estrategia | rehost, relocate, replatform, repurchase, refactor ou rearchitect |
| Justificativa | Motivo tecnico e financeiro |
| Pre-requisitos | Dados, licencas, rede e dependencias |
| Risco | Incompatibilidade, sizing ou operacao |
| Alternativa | Opcao conservadora ou moderna |
| Status | CONFIRMADO, PREMISSA, SUGESTAO ou A DEFINIR |

## Pontos de partida

Validar cada item em documentacao atual:

| AWS | Possiveis destinos Azure |
|---|---|
| EC2, Auto Scaling | Virtual Machines, VM Scale Sets |
| EBS, snapshots | Managed Disks, incremental snapshots |
| S3, Glacier | Blob Storage, Data Lake Storage |
| EFS, FSx | Azure Files, Elastic SAN ou Azure NetApp Files |
| RDS, Aurora | Azure SQL, SQL Managed Instance, PostgreSQL/MySQL Flexible Server |
| DynamoDB, DocumentDB | Cosmos DB ou servico de banco compativel |
| ElastiCache | Azure Managed Redis |
| Lambda | Azure Functions |
| ECS/Fargate | Container Apps ou AKS |
| EKS | AKS |
| ECR | Azure Container Registry |
| CloudWatch, X-Ray | Azure Monitor, Log Analytics, Application Insights |
| CloudTrail | Activity Log, resource logs, Log Analytics e opcionalmente Sentinel |
| VPC, NAT, endpoints | Virtual Network, NAT Gateway, Private Link |
| ELB | Load Balancer, Application Gateway ou Front Door |
| Route 53, CloudFront | Azure DNS, Traffic Manager, Front Door |
| SQS, SNS, EventBridge | Service Bus e Event Grid |
| Kinesis, MSK | Event Hubs, Stream Analytics ou oferta Kafka compativel |
| Direct Connect | ExpressRoute |
| GuardDuty, Security Hub | Defender for Cloud e Microsoft Sentinel |
| KMS, Secrets Manager, CloudHSM | Key Vault e Managed HSM |
| Backup | Azure Backup |
| DMS | Azure Database Migration Service |
| WorkSpaces | Azure Virtual Desktop |
| Cognito | Microsoft Entra External ID |
| CloudFormation | Bicep ou Terraform |
| Cost Explorer, Budgets | Cost Management |

Produtos Marketplace, assistentes de IA e software de terceiros exigem avaliacao
de licenca e funcionalidade. Sem equivalencia comprovada, usar **NAO MAPEADO** ou
**A DEFINIR**, nunca um destino apenas por semelhanca de nome.

## Calculo por linha

Toda linha estimada deve conter:

- quantidade Azure;
- unidade Azure;
- SKU ou medidor;
- preco unitario;
- formula;
- custo mensal;
- modelo comercial;
- status;
- premissa;
- fonte oficial;
- data da consulta;
- confianca.

Usar scripts para calculos, arredondamento e distribuicao de custos compartilhados.
Nao calcular de cabeca. Manter precisao interna e arredondar somente na exibicao.

## Cobertura

Cobertura ponderada usa apenas cobrancas operacionais positivas no denominador.
Descontos, creditos, impostos e ajustes excluidos nao aumentam a cobertura.

- todas as cobrancas positivas conhecidas: `ESTIMADO` ou `PREMISSA`;
- parte conhecida e parte desconhecida: `PARCIAL`;
- nenhuma cobranca positiva precificavel: `A DEFINIR`;
- nenhuma equivalencia defensavel: `NAO MAPEADO`;
- item financeiro removido para evitar dupla contagem: `SEM CUSTO/EXCLUIDO`.
