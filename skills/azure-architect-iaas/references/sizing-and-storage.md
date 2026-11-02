# Sizing de VM, discos e storage

## Sizing de VM

Usar a skill oficial `azure-compute` e seu workflow `vm-recommender` antes de
selecionar familia ou SKU. Consultar documentacao oficial atual por candidato,
regiao e SO; validar quota somente se houver assinatura e permissao de leitura.
Sem acesso, quota fica "Nao verificada antes do deploy", nao presumida suficiente.

Com janela de pelo menos 30 dias que cubra pico conhecido:

- Demanda de CPU = `vCPU configurados x CPU P95% x 1,20`; arredondar para cima
  apenas na selecao de SKU.
- Demanda de memoria = `memoria usada P95 GiB x 1,20`.
- Registrar unidade, agregacao, intervalo de amostragem, quantidade de amostras,
  picos excluidos/incluidos e fonte. CPU P95 percentual sem capacidade atual nao
  permite converter para vCPU.
- Comparar a recomendacao com Azure Migrate: CPU, memoria, disco, series, regiao,
  horas, beneficio e premissas. Explicar diferenca; nao substituir o resultado
  pelo assessment sem validacao.

Sem metrica de CPU/memoria, janela menor que 30 dias, pico nao coberto ou unidade
incompativel: usar configuracao atual apenas como candidato provisiorio de
equivalencia, marcar sizing A DEFINIR e solicitar dados. Nao declarar
rightsizing, economia ou desempenho.

Selecionar a menor opcao elegivel que atenda CPU, memoria, SO/arquitetura,
extensoes, discos, rede, zona, disponibilidade regional e crescimento comprovado.
Apresentar 2-3 opcoes somente se elas forem tecnicamente elegiveis e tiverem
trade-off material. Preco baixo nao compensa requisito nao atendido.

VMSS exige evidencia de instancias equivalentes, carga stateless, balanceamento
e regra de escala. Servidores stateful, unicos ou com configuracao singular
permanecem VM por padrao. Spot so entra como [SUGESTÃO] para workload interrompivel
comprovado; nunca como substituto de capacidade essencial.

## Discos e opcoes de storage

Para cada volume, identificar papel, capacidade, crescimento, sistema de arquivos,
protocolo, compartilhamento, IOPS e throughput separados por leitura/escrita quando
disponivel. Demanda de performance = P95 x 1,20 apenas com dados representativos.
Checar tanto limite do disco/servico como limites agregados da VM; um disco
elegivel nao prova que a VM suporta a soma dos discos.

| Opcao | Considerar quando | Nao concluir sem |
| --- | --- | --- |
| Managed Disks (Standard HDD/SSD, Premium SSD, Premium SSD v2, Ultra) | Disco de bloco por VM, capacidade/IOPS/throughput e resiliencia atendidos | Tipo de workload, limites atuais, zona/regiao, cache, criptografia e compatibilidade de VM/SO |
| Azure Files | Compartilhamento SMB/NFS gerenciado, multiplos consumidores e semantica de file share comprovada | Protocolo, clientes, performance/tier, IOPS, throughput, identidade, backup e rede |
| Azure NetApp Files | NFS/SMB corporativo, alta performance/baixa latencia, snapshots/replicacao ou compartilhamento com requisitos comprovados | Protocolo, capacidade/pool, desempenho, disponibilidade regional/zonal, rede, backup/replicacao e custo |
| Blob/ADLS | Objetos, backup, arquivos de aplicacao ou dados nao montados como volume de baixa latencia | Padrao de acesso, transacao, reidratacao, retencao, egress e compatibilidade de aplicacao |

Azure NetApp Files nao e alternativa padrao para todo volume grande. Recomendar
somente diante de protocolo, compartilhamento, IOPS, throughput, latencia,
snapshot/replicacao ou requisito operacional comprovado que Managed Disks/Azure
Files nao atendam. Com requisito ausente, manter candidato Managed Disk e marcar
decisao de storage A DEFINIR.

Backup, HA e DR exigem criticidade ou RTO/RPO documentado. Modelar custo de
backup, replica, storage secundario e compute de DR somente para desenho
confirmado. Sem requisito, nao incluir baseline silencioso; abrir pergunta.

## Fontes oficiais obrigatorias

Consultar na data da recomendacao e registrar URL, secao e data:

- [Azure VM sizes](https://learn.microsoft.com/azure/virtual-machines/sizes)
- [VM sizes and performance](https://learn.microsoft.com/azure/virtual-machines/sizes)
- [Managed disks types](https://learn.microsoft.com/azure/virtual-machines/disks-types)
- [Disk scalability targets](https://learn.microsoft.com/azure/virtual-machines/disks-scalability-targets)
- [Azure Files](https://learn.microsoft.com/azure/storage/files/storage-files-introduction)
- [Azure NetApp Files](https://learn.microsoft.com/azure/azure-netapp-files/)
- [Azure Backup](https://learn.microsoft.com/azure/backup/)
- [Azure Site Recovery](https://learn.microsoft.com/azure/site-recovery/)
- [Azure Migrate assessment calculation](https://learn.microsoft.com/azure/migrate/concepts-assessment-calculation)

Documento indisponivel, SKU aposentado, versao de SO sem suporte ou recurso nao
disponivel na regiao impede recomendacao validada para o item afetado.
