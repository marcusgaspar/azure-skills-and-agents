# Campos e armadilhas por produto

Estas orientacoes sao pontos de partida. A interface e as regras podem mudar;
validar sempre a pagina corrente e a documentacao oficial.

| Produto | Dimensoes minimas | Validacoes |
| --- | --- | --- |
| Virtual Machines | regiao, SO, serie/SKU, quantidade, horas, compra | SKU existe na regiao; PAYG/reserva/Savings Plan nao misturados; discos separados ou explicitamente incluidos |
| Managed Disks | regiao, tipo, tamanho, quantidade, horas; IOPS/throughput quando aplicavel | Premium SSD v2 usa tamanho, horas, IOPS e throughput; confirmar franquias incluidas |
| MySQL Flexible Server | regiao, tier/SKU, vCores, horas, HA, storage, backup | HA pode alterar numero de nos e storage; burstable sem telemetria permanece PREMISSA |
| Storage Accounts | regiao, redundancia, tier, capacidade, operacoes, retrieval/egress | separar GB-month, transacoes e transferencia; nao misturar Blob, Files e Queue |
| Azure Monitor | regiao, ingestao, retencao, consultas/exportacao | considerar franquias e retencao incluida; nao somar logs duplicados |
| Application Gateway | tier, horas, capacity units ou dimensoes de compute/conexao/throughput | a capacidade efetiva pode ser o maximo das dimensoes; documentar a derivacao |
| Load Balancer | SKU, horas/base, regras e dados | pode haver custo-base mensal e minimo que impede reproduzir horas parciais |
| VPN Gateway | SKU, gateway-hours, conexoes/tuneis e dados | validar subtotal; internals observados podem ser case-sensitive |
| Public IP / Private Link | SKU, horas e/ou dados processados | distinguir IP, endpoint, connection e data processing |
| Container Apps | requests, duracao, concorrencia, vCPU, memoria, replicas e ambiente | derivar vCPU-s/GiB-s de forma explicita; aplicar franquias apenas uma vez |
| Functions | execucoes e GB-s | aplicar franquia atual; confirmar plano de hospedagem |
| Key Vault | operacoes por categoria e certificados quando aplicavel | cobranca pode arredondar por blocos; operacoes nao sao segredos armazenados |
| Event Grid | operacoes/eventos e entregas | confirmar unidade em milhao e franquia |
| Event Hubs | tier, throughput/capacity units, horas, ingress/retencao | nao confundir eventos com unidades-hora |
| Container Registry | tier, dias/mes, storage e transferencia | confirmar se replicas geograficas estao incluidas |
| Communication Services | canal, unidade, pais/destino e volume | tarifas dependem do tipo de comunicacao e destino |
| AI / Foundry | modelo, modalidade, tokens/unidades, regiao | verificar se o modelo existe no catalogo da calculadora; proxy por valor e proibido |

## Casos frequentemente nao representaveis

### Azure Backup com somente armazenamento

GB armazenados sem workload, instancia protegida, tamanho protegido, politica e
retencao nao formam uma configuracao equivalente. Marcar `NOT_REPRESENTABLE` ou
`A DEFINIR`; nao substituir por Storage comum.

### Modelo de terceiro ausente

Se um modelo do Microsoft Foundry nao estiver disponivel como produto direto,
nao usar Azure OpenAI nem outra linha como proxy financeiro. Manter separado.

### Transferencia entre zonas

Se a calculadora nao oferecer o medidor correspondente, manter
`NOT_REPRESENTABLE`; nao converter automaticamente em internet egress.

### Environment management

Se o custo de gerenciamento de ambiente do Container Apps nao possuir campo
equivalente, manter separado mesmo que consumo de vCPU e memoria seja
representavel.

## Derivacoes permitidas

Uma derivacao e aceitavel quando:

- usa somente dados da entrada;
- preserva unidade e semantica do medidor;
- exibe a formula;
- nao depende de um preco usado como quantidade;
- pode ser refeita e auditada.

Exemplo:

```text
capacity_units_medias = capacity_unit_hours / gateway_hours
```

Se `gateway_hours` for zero ou ausente, a configuracao e **A DEFINIR**.
