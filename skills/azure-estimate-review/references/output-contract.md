# Contrato de saida

## Origem da estimativa

**[SUGESTÃO]** Sem tabela de referencia fornecida pelo usuario, usar provisoriamente
as regras abaixo e avisar sobre essa lacuna; nao alegar reproduzir a referencia original.

| Origem confirmada | Linguagem do veredito |
| --- | --- |
| Equipe interna | Apta para encaminhamento / Apta com ressalvas / Requer revisao / Inconclusiva. Parecer independente para o usuario solicitante. |
| Parceiro | Consistente no escopo verificado / Consistente com ressalvas / Requer esclarecimentos e revisao / Inconclusiva. Sem julgamento do parceiro. |
| Cliente | Consistente no escopo verificado / Consistente com pontos a confirmar / Recomenda-se revisao das premissas / Inconclusiva. Usar linguagem consultiva abaixo. |
| A DEFINIR | Origem A DEFINIR; veredito tecnico provisório, sem inferir autoria. |

Sem ressalvas apenas se todos os itens aplicaveis foram comprovados e nao ha erro
ou lacuna material. Lacuna material = dado que pode mudar capacidade, elegibilidade,
resiliencia ou total da decisao; justificar. Erro conhecido exige revisao, mesmo
quando coexistem lacunas. So lacunas materiais, sem erro demonstrado = Inconclusiva.
Ressalvas ficam limitadas ao escopo efetivamente comprovado; nao sao autorizacao
para publicar. Indicar uso de regras [SUGESTÃO] ate aprovacao.

## Padrao: chat curto em Markdown

**Veredito:** <origem + conclusao + principal razao>.
**Base:** <arquivos/revisoes; data da revisao e data-base do preco; regiao; lista;
moeda; horizonte; escopo>. Ausencias sao A DEFINIR.
**Skills Azure utilizadas:** <nome, invocada/consultada e contribuicao; limitacoes
relevantes em itens nao verificados>. Nao expor caminhos locais na versao externa.
**US$/mes:** original <valor> | corrigido <valor ou A DEFINIR> |
delta <valor assinado ou A DEFINIR>. Se escopo incompleto, rotular subtotal conhecido,
nao total. Nao apresentar cenario de otimizacao como correcao obrigatoria.

| Item | Status | Evidencia | Correcao sugerida |
| --- | --- | --- | --- |
| <cada item 1-16> | <status> | <arquivo/aba/celula/slide/pagina; URL/secao/data para regras oficiais> | <acao ou nenhuma; [SUGESTÃO] quando nao aprovada> |

**Principais achados:** tabela curta, sem duplicar o checklist.

| Achado | Severidade | Impacto US$/mes (corrigido - original) | Evidencia/acao |
| --- | --- | --- | --- |
| <erro/risco/oportunidade/lacuna identificado> | <Critico/Alto/Medio/Baixo> | <delta, intervalo calculado ou A DEFINIR; cenario rotulado> | <origem e referencia ao calculo> |

**O que nao esta no preco:** exclusoes, custo parcial e dono; nao precificado nao e zero.

**O que nao pode ser verificado:** item, motivo, dado/fonte faltante, dono e acao.
Indicar expressamente indisponibilidade de fonte, arquivo ou ferramenta.

Nao esconder ressalvas em anexos. Tabela com uma linha por item; sem evidencia,
Nao verificado. Citar resultado do script e referencia de entrada para todo delta.
Quando achados compartilham linhas, nao publicar soma; usar cenario consolidado
recalculado que deduplica componentes.

## Versao para cliente ou parceiro

**[SUGESTÃO]** Sem referencia da versao para cliente fornecida pelo usuario,
este modelo provisório nao a substitui. Manter o parecer com o usuario solicitante.

Antes de preparar conteudo externo, confirmar com o usuario destinatario, escopo e
conteudo autorizado. Publicar/enviar e uma acao separada, fora desta skill.
Usar varejo e fontes publicas oficiais, mesmo se a revisao interna usou contrato.
Recalcular cenario publico antes de reutilizar totais/deltas; ocultar a taxa negociada
nao basta se o total permite deduzi-la.

Usar "Pontos a confirmar" no lugar de "O que nao pode ser verificado".
Descrever divergencia observavel, impacto, premissa e alternativa; evitar acusacoes
e comentarios sobre competencia ou interesses de equipe/parceiro/cliente.
Nao transmitir comentarios internos, condicoes comerciais, descontos negociados,
dados identificaveis de outros clientes ou certificacoes regulatorias.
Manter "A DEFINIR" e [SUGESTÃO] visiveis; nao suavizar um erro tecnico
como conformidade. A versao privada pode manter severidade interna em secao separada
que nunca compoe o artefato destinado ao destinatario externo.

## Relatorio completo (somente solicitado)

HTML ou Word no destino acordado, com:

1. Resumo executivo/veredito; original, corrigido e delta por escopo/moeda.
2. Origem, inventario, exclusoes, datas, horizonte e premissas com donos.
3. Checklist completo e achados com evidencia e impacto.
4. Memoria de calculo e reconciliacoes entre arquivos/abas/slides.
5. Sizing, capacidade sob falha, crescimento, RTO/RPO e limites.
6. Matriz de ciclo de vida e plano/custo pendente de upgrade/ESU/migracao.
7. Cenarios independentes e oportunidades, sem somar economias alternativas.
8. O que nao esta no preco; itens nao verificados/Pontos a confirmar.
9. Fontes oficiais com URL/secao/data de consulta e anexos sanitizados autorizados.

HTML deve ser estatico: escapar texto extraido, sem scripts, rastreadores ou
recursos remotos. Artefatos externos seguem aprovacao e sanitizacao acima.
