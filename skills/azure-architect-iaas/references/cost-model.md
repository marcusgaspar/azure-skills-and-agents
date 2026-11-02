# Modelo de custo e Azure Pricing Calculator

## Regra de preco

Usar preco de varejo publico em USD da Azure Pricing Calculator para a regiao
destino documentada. Sem regiao, usar Brazil South provisoriamente e marcar
regiao, disponibilidade e custo como A DEFINIR. Registrar data/hora da consulta,
URL/pagina, produto, SKU, regiao, SO, medidor, unidade e preco unitario.

Usar a [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
como fonte principal de comparacao/manual review e a
[Azure Retail Prices API](https://learn.microsoft.com/rest/api/cost-management/retail-prices/azure-retail-prices)
somente conforme sua documentacao atual. Nunca selecionar o primeiro resultado
da API sem desambiguar SKU, regiao, Linux/Windows, consumo/compromisso e unidade.
Preco varejo nao prova preco contratado, disponibilidade de capacidade ou
elegibilidade comercial.

Modelar pay-as-you-go e 730 h/mes para todas as VMs. AHB, licencas existentes,
reservas e Savings Plan nao reduzem o baseline sem evidencia de elegibilidade.
Listar cada um como [SUGESTÃO] ou A DEFINIR, sem percentual fixo e sem economia
prometida. Nao incluir imposto, cambio, suporte, rede ou migracao sem escopo e
fonte; mostra-los em "Fora do modelo".

## Linhas obrigatorias do BOM

| Categoria | Unidade/formula | Evidencia necessaria |
| --- | --- | --- |
| Compute de VM | `quantidade x preco horario x horas/mes` | SKU, SO/licenca, regiao, 730 h ou agenda comprovada |
| Managed Disk | `quantidade x preco mensal do tier/capacidade` e medidores adicionais aplicaveis | Tipo, tamanho/performance, regiao, redundancia e fonte |
| Azure Files/ANF/Blob | Unidade e medidores da oferta atual | Tipo, capacidade/pool, transacoes/performance, redundancia, protocolo e fonte |
| Backup | Medidores do desenho confirmado | RPO, retencao, dados protegidos, tier, regiao e fonte |
| DR | Compute/storage/rede do desenho confirmado | RTO/RPO, replica, periodo de teste/failover e fonte |
| Rede/operacao | Somente se desenho comprovar | Fluxos, egress, IP/LB/NAT, monitoramento e fonte |

Separar itens mensais, unicos, fora do modelo e A DEFINIR. Nao anualizar valor
unico para aparentar custo mensal. Nao zerar linha por dado faltante.

## Reconciliacao

Cada VM em escopo tem uma linha ou varias linhas de BOM ligadas por `vm_id_canonico`;
linhas compartilhadas devem indicar grupo, criterio de rateio e custo bruto.
O total de grupos de execucao deve reconciliar com total do BOM, e o custo de cada
grupo deve apontar para as VMs/linhas que o compoem. Backup/DR compartilhado sem
rateio comprovado fica fora do total por grupo e A DEFINIR.

O workbook deve conter fonte por hardcode, formulas por total/subtotal, timestamp
de preco e uma aba `Calculator_Input` com servico, SKU, regiao, quantidade,
horas, configuracoes e URL de consulta. E uma planilha de entrada/revisao manual,
nao uma alegacao de importacao automatica na Calculadora.
