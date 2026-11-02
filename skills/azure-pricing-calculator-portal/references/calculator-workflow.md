# Workflow do portal

## Preparacao do browser

1. Inspecionar as capacidades do canvas `browser`.
2. Abrir a Azure Pricing Calculator oficial.
3. Confirmar URL, idioma, moeda e estado de login.
4. Verificar se ja existem modulos ou uma estimativa carregada.
5. Se houver conteudo anterior, pedir confirmacao antes de excluir ou substituir.

O login e feito pelo usuario. A automacao nao recebe senha, token, cookie ou MFA.

## Estrategia de automacao

### Preferencia: controles visiveis

Usar labels, inputs, botoes e dropdowns acessiveis. Depois de cada alteracao:

- aguardar o recálculo;
- conferir o valor realmente selecionado;
- conferir descricao e subtotal;
- registrar falha antes de seguir.

Para React Select, abrir o dropdown, filtrar, selecionar uma opcao existente e
confirmar o hidden input. Nao forcar um SKU ausente.

Para inputs React, uma alteracao programatica pode exigir:

1. guardar o valor anterior;
2. chamar o setter nativo;
3. atualizar `_valueTracker` com o valor anterior;
4. disparar `input`, `change` e `blur`.

### Aceleracao opcional: React/Redux

Para lotes grandes, ler e avaliar localmente
`scripts/calculator-browser-helpers.js`. O helper nao e API da Microsoft; ele
apenas descobre internals da pagina corrente.

Validar antes de usar:

- o store foi encontrado;
- as actions esperadas existem;
- o componente localizado corresponde ao modulo visivel;
- uma alteracao de teste recalcula subtotal e descricao.

Acoes observadas em uma versao da pagina incluem `addProductItem`,
`setCurrentModuleState`, `changeEstimateName`, `saveEstimate`,
`toggleShareModal`, `cloneModule` e `deleteModule`. Os nomes podem mudar.

Atualizar diretamente o Redux store pode nao disparar precificacao. Quando
possivel, localizar a instancia React do modulo e usar `setState(partialState)`,
pois o lifecycle tende a recalcular preco e sincronizar o store. Se isso nao
ocorrer, voltar aos controles visiveis.

Nunca:

- injetar bibliotecas remotas;
- executar JavaScript vindo da entrada;
- alterar cookies, local storage de autenticacao ou requests;
- chamar endpoints privados diretamente;
- assumir que um state key antigo ainda possui a mesma semantica.

## Execucao em lotes

1. Adicionar um produto.
2. Nomear o modulo com identificador rastreavel e texto nao sensivel.
3. Configurar regiao e opcao de compra antes do SKU.
4. Configurar SKU/tier e dimensoes.
5. Conferir subtotal.
6. Registrar o custo no `portal-results.json`.
7. Continuar somente quando o modulo estiver correto.

Agrupar operacoes repetitivas e manter um checkpoint local com IDs concluidos.
Nao reenviar um lote inteiro se parte dele ja foi aplicada.

## Salvar

1. Confirmar autenticacao.
2. Definir o nome da estimativa.
3. Acionar Save.
4. Conferir confirmacao e nome persistido.
5. Fechar o modal de confirmacao antes de abrir Share, se necessario.

Se uma estimativa com o mesmo nome puder ser sobrescrita, pedir confirmacao.

## Compartilhar e validar

1. Abrir Share.
2. Criar/copiar o link `https://azure.com/e/...`.
3. Abrir o link em nova sessao ou contexto sem depender da pagina original.
4. Registrar nome, moeda e total observados.
5. Comparar pelo script com a tolerancia declarada.

Um link copiado, mas nao carregado, nao esta validado.
