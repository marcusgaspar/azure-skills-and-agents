# Checklist de validacao

Status: **OK**, **Divergente**, **Nao verificado**, **Nao se aplica (motivo)**.
Item parcialmente comprovado permanece Nao verificado, com subverificacoes
confirmadas descritas na evidencia; erro demonstrado permanece Divergente,
mesmo que haja outras lacunas no mesmo item.

| # | Verificacao e criterio |
| --- | --- |
| 1 | Reconciliacao: soma das linhas igual ao total de cada arquivo; todas as quebras por ambiente, componente, grupo, "Sem SKU" e plataforma compartilhada iguais ao resumo. Detectar itens omitidos, repetidos, ocultos ou alocados em mais de um grupo. |
| 2 | Um unico numero por entregavel: planilha/calculadora, apresentacao, proposta e ramp-up usam as mesmas quantidades e totais para a mesma fase/escopo. Cambio unico com fonte, data, direcao da taxa e aplicacao por formula, nao valores locais digitados. Diferencas intencionais de fase/escopo precisam de ponte de reconciliacao. |
| 3 | Preco real e datado: fonte com no maximo 30 dias, mesma data-base em todos os entregaveis, lista varejo/EA/MCA/CSP identificada. Reconstruir preco unitario e conferir SKU/tier, regiao, moeda, unidade, vigencia e consumo faturavel. Separar erro historico de mudanca posterior de preco. |
| 4 | Beneficios: reserva, Savings Plan, reservas de PaaS e AHB com preco real por SKU/servico e elegibilidade comprovada; nunca percentual fixo. Se nao modelados, registrar oportunidade, sem economia presumida. Conferir sobreposicao, licenciamento, escopo, prazo e cobertura. |
| 5 | Horas/regime: 730 h/mes para recursos horarios 24x7. Reducao/desligamento/scale-to-zero so com premissa escrita e automacao definida; mostrar risco a 730 h. Conferir custos que continuam com compute parado, tempo de partida, dependencias e servicos sem scale-to-zero. Respeitar unidade real nos demais medidores. |
| 6 | Unidade/minimos: por cluster, instancia, particao, regiao, GB, operacao, vCore, RU/s ou outra unidade oficial; degraus, franquias, arredondamento, granulos e minimos de autoscale respeitados. Taxa de gerenciamento AKS nao presumida por node pool. |
| 7 | Sizing rastreavel: formula e parametros por componente (TPS/no, RU/operacao, mensagens/transacao, tamanho de payload, GB/dia, retencao, P95 CPU/memoria). Coerencia entre pico, duracao, media e volume diario; nunca pico x 24h sem premissa. Sem medicao/benchmark: estimativa preliminar e acao/dono para obter dados; por alocado: provavelmente superestimado. |
| 8 | Capacidade/limites: pico atendido por instancia/particao e cotas da assinatura/regiao, com crescimento no horizonte. Conferir perda de zona, distribuicao efetiva e capacidade restante; N+1 isolado nao prova resiliencia zonal. Limites teoricos nao sao throughput garantido; benchmark representativo obrigatorio para afirmacoes de desempenho. |
| 9 | Configuracao x preco: pre-requisitos atendidos (ex.: failover por particao Cosmos DB requer configuracao regional compativel; SO efemero requer suporte/capacidade da VM). Redundancia, backup e tier compativeis com RTO/RPO; nao cobrar duas vezes a mesma resiliencia. Recursos adicionais de DR justificados pelo desenho, nao eliminados sem analise. |
| 10 | Ciclo de vida: servicos, SKUs, versoes Kubernetes/engines, SO e dependencias conferidos hoje nas fontes oficiais Azure, Microsoft Lifecycle e Red Hat. Nada aposentado ou com aposentadoria antes do fim do horizonte sem plano; incluir upgrade/migracao, suporte estendido/ESU, elegibilidade e custo quando aplicaveis. |
| 11 | Escopo completo: arquitetura x linhas x DEV/HML/PROD/DR reconciliados. Incluir peering, firewall, ExpressRoute/VPN, NAT, egress e intercloud; observabilidade; Defender, chaves/HSM; backup/DR; storage persistente de containers; registro de imagens; CI/CD; terceiros/licencas; suporte. Identificar recursos compartilhados e criterio de rateio. Rotular recortes. |
| 12 | "O que nao esta no preco" visivel no resumo e completo: terceiros, rede/landing zone compartilhada, suporte, migracao, impostos e cambio; esclarecer inclusao parcial e dono do custo. Nao precificado nao e gratuito. |
| 13 | Nenhum numero sem fonte ou derivacao por script; lacunas A DEFINIR; premissas com dono, data, unidade, ambiente, horizonte e grau de confianca. Valor sintetico/ilustrativo nao pode passar por preco validado. |
| 14 [SUGESTÃO] | Ramp-up e temporalidade: custo mensal por fase e mes, coexistencia on-prem/Azure, replicacao/carga inicial, migracao e descomissionamento. Separar desembolso de compromisso antecipado, equivalente mensal e custo unico; nao contar custo unico em todos os meses nem anualizacao como fatura mensal. |
| 15 [SUGESTÃO] | Compromissos e sensibilidades: utilizacao real de reservas/Savings Plan, consumo descoberto, risco de compromisso ocioso, prazo, flexibilidade e restricoes vigentes. Cenarios de crescimento/cambio/uso identificados e nao cumulativos; combina-los so apos recalculo conjunto sem dupla contagem. |
| 16 [SUGESTÃO] | Bancos de dados e desempenho: engine/edicao/licencas, vCore/DTU/RU, provisionado/serverless, pausabilidade, IOPS/throughput/latencia, storage/auto-growth, temp/log, replicas, HA, backup/PITR/LTR, leitura/escrita e conexoes. Confirmar compatibilidade de migracao e benchmark; limites publicos nao substituem validacao com workload. |

## Severidade e impacto

- **Critico:** arquitetura inviavel, componente essencial fora do ciclo de vida sem
  plano, requisito de resiliencia/capacidade essencial nao atendido, ou erro que
  invalida a decisao. Nao inferir certificacao regulatoria.
- **Alto:** omissao/distorcao relevante de custo, beneficio inelegivel ou premissa
  essencial sem respaldo. Justificar relevancia, sem percentual arbitrario.
- **Medio:** inconsistencias corrigiveis ou riscos condicionais com escopo limitado.
- **Baixo:** clareza/rastreabilidade/documentacao sem impacto funcional demonstrado.

Usar impacto assinado **corrigido - original** em US$/mes: positivo = subestimativa;
negativo = superestimativa. Falta de preco/volume => **A DEFINIR**, nunca zero.
Sem efeito mensal demonstrado, escrever "nao quantificado" e informar a natureza
(custo unico, risco de desempenho, ciclo de vida). Numeros condicionais sao cenarios,
nao achados confirmados. Nao somar achados sobrepostos nem alternativas de economia.
