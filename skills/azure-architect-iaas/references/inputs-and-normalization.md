# Entrada, identidade e consolidacao

## Fontes aceitas

| Fonte | Usar principalmente para | Nao assumir |
| --- | --- | --- |
| RVTools | VM, host, vCPU, memoria configurada, discos, capacidade alocada, SO, power state e metadados VMware | P95 de consumo, destino Azure, dependencia aplicacional, preco ou elegibilidade de licenca |
| Azure Migrate assessment/export | Configuracao descoberta, metrica/periodo, recomendacao do assessment, regiao/assumptions quando presentes | Recomendacao como verdade absoluta, preco atual, RTO/RPO, agrupamento aplicacional ou disponibilidade de quota |
| CMDB | Aplicacao, servico, ambiente, dono, criticidade, dependencias, destino e exclusao declarada | Configuracao/telemetria tecnica sem evidencia de coleta |
| Telemetria autorizada | CPU, memoria, IOPS, throughput, read/write, amostragem, janela e pico | Identidade se nao houver chave de VM verificavel |
| Diagramas, propostas ou entrevistas | Hipoteses, destinos, RTO/RPO e excecoes documentadas | Fato tecnico sem fonte/owner/data |

Aceitar XLSX, CSV, JSON, PDF e documentos suportados pelas skills de formato.
Registrar arquivo, aba/tabela, linha/celula ou pagina/slide de cada campo usado.
Formula sem valor recalculado e macro nunca sao executadas; extrair valor exibido
e marcar a fonte como nao verificada quando isso impedir reconciliacao.

## Associacao de identidade

1. Preferir UUID de VM/BIOS, instance UUID, MoRef, asset ID imutavel ou identificador
   Azure Migrate verificavel.
2. Na ausencia, aceitar FQDN ou hostname normalizado somente se for unico no
   conjunto, ambiente/organizacao forem compativeis e configuracao corroborar.
3. IP, nome parcial, endereco MAC, cluster ou semelhanca textual sao apenas
   pistas; nao sao chave suficiente para mesclar registros.
4. Colisao, conflito de chave ou duvida gera registros separados e pergunta no
   questionario. Nao somar CPU, memoria, discos ou custos de registros ambiguos.

Guardar `vm_id_canonico`, chaves de origem, confianca de associacao, fontes e
conflitos em abas separadas. Uma VM pode ter varias fontes, mas cada campo precisa
ter uma fonte vencedora ou status A DEFINIR.

## Precedencia por atributo

| Atributo | Fonte primaria | Tratamento de conflito |
| --- | --- | --- |
| Aplicacao, servico, ambiente, dono, criticidade, dependencias, destino/exclusao | CMDB | Manter conflito material como A DEFINIR; nao sobrescrever pelo nome da VM |
| vCPU, memoria, discos, power state, SO e configuracao | RVTools ou Azure Migrate mais recente/documentado | Mostrar ambos e marcar A DEFINIR se diferenca afetar sizing/custo |
| CPU, memoria, IOPS, throughput e janela | Azure Migrate/telemetria com periodo e unidade documentados | Sem 30 dias ou pico conhecido: estimativa preliminar/A DEFINIR |
| SKU Azure/recursos, preco e limite | Documentacao/preco oficial atual | Export antigo e apenas baseline, nao fonte final |

## Grupos de execucao

1. Usar aplicacao ou servico da CMDB com correspondencia verificada: confianca
   100%.
2. Sem aplicacao/servico, usar ambiente mais dependencias documentadas:
   confianca 50% **[SUGESTÃO]**.
3. Somente ambiente, nome inferido, dependencia incompleta ou conflito:
   confianca abaixo de 50%, grupo rotulado A DEFINIR.

Nao inferir dependencia por proximidade de IP, host, datastore ou padrao de nome.
Nao usar grupo de execucao como prova de RTO/RPO ou afinidade de zona.

## Modelo normalizado minimo

Criar JSON normalizado somente na pasta de trabalho da sessao para o script:

```json
{
  "target_region": null,
  "vms": [
    {
      "id": "vm-001",
      "name": "app-01",
      "source_refs": ["rvtools.xlsx!vInfo row 42", "cmdb.xlsx!CMDB row 8"],
      "migration_destination": "azure-iaas",
      "exclude_reason": null,
      "cmdb": {
        "application": "billing",
        "service": null,
        "environment": "prod",
        "dependencies": ["database-service"]
      },
      "inventory": {"vcpu": "4", "memory_gib": "16", "os": "Linux"},
      "metrics": {
        "observation_days": "30",
        "peak_covered": true,
        "cpu_p95_pct": "50",
        "memory_p95_gib": "10"
      },
      "disks": [
        {
          "id": "disk-01",
          "role": "data",
          "capacity_gib": "512",
          "iops_p95": "1200",
          "throughput_mbps_p95": "80",
          "shared_requirement": null,
          "protocol": null
        }
      ],
      "rto_minutes": null,
      "rpo_minutes": null
    }
  ]
}
```

Numeros sao strings decimais sem separador de milhar. `null` significa
desconhecido, nunca zero. A referencia de origem deve apontar para local
verificavel. O exemplo e sintetico e nao representa cliente, SKU ou preco.
