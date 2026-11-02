# Azure Skills and Agents

Skills e agente customizado para GitHub Copilot, voltados a assessments,
arquitetura, dimensionamento e estimativas de custos no Microsoft Azure.
As instrucoes estao principalmente em portugues do Brasil.

Projeto independente mantido por Marcus Gaspar. Nao e um produto oficial
da Microsoft ou do GitHub.

## Catalogo

| Tipo | Nome | Objetivo |
| --- | --- | --- |
| Skill | [azure-estimate-review](skills/azure-estimate-review/SKILL.md) | Revisar arquitetura, sizing e custos com recálculo, checklist e evidencias oficiais. |
| Skill | [azure-architect-iaas](skills/azure-architect-iaas/SKILL.md) | Consolidar inventarios de VMs, recomendar sizing e storage e produzir inventario/BOM em Excel. |
| Skill | [azure-pricing-calculator-portal](skills/azure-pricing-calculator-portal/SKILL.md) | Reproduzir estimativas na Azure Pricing Calculator, reconciliar e validar o link compartilhavel. |
| Skill | [azure-aws-to-azure-estimate](skills/azure-aws-to-azure-estimate/SKILL.md) | Converter consumos AWS em estimativas Azure rastreaveis, com escolha obrigatoria do modelo comercial. |
| Agente | [azure-migration-architect](agents/azure-migration-architect.agent.md) | Coordenar assessments on-premises/AWS, arquitetura alvo, riscos e ondas de migracao. |

As pastas de skills incluem suas referencias e, quando aplicavel, scripts e
testes com dados sinteticos. O agente reutiliza skills conforme o tipo de tarefa.

## Instalacao pessoal no Copilot

Clone este repositorio em uma pasta de sua escolha:

```powershell
git clone https://github.com/marcusgaspar/azure-skills-and-agents.git
Set-Location .\azure-skills-and-agents
```

Copie as pastas de `skills` para `$HOME\.copilot\skills` e o arquivo de `agents`
para `$HOME\.copilot\agents`. Preserve a estrutura de referencias e scripts.
Os comandos abaixo verificam todos os destinos antes de copiar e nao substituem
customizacoes existentes:

```powershell
$ErrorActionPreference = 'Stop'
$skillsRoot = Join-Path $HOME '.copilot\skills'
$agentsRoot = Join-Path $HOME '.copilot\agents'
$skills = @(Get-ChildItem -LiteralPath .\skills -Directory)
$agent = Get-Item -LiteralPath .\agents\azure-migration-architect.agent.md

foreach ($skill in $skills) {
    $target = Join-Path $skillsRoot $skill.Name
    if (Test-Path -LiteralPath $target) {
        throw "Destino ja existente: $target. Revise antes de atualizar."
    }
}
$agentTarget = Join-Path $agentsRoot $agent.Name
if (Test-Path -LiteralPath $agentTarget) {
    throw "Destino ja existente: $agentTarget. Revise antes de atualizar."
}

New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
New-Item -ItemType Directory -Path $agentsRoot -Force | Out-Null
foreach ($skill in $skills) {
    Copy-Item -LiteralPath $skill.FullName -Destination $skillsRoot -Recurse
}
Copy-Item -LiteralPath $agent.FullName -Destination $agentTarget
```

Reabra a conversa ou o aplicativo se as customizacoes nao aparecerem no runtime.
Outros clientes podem usar locais de instalacao e ferramentas diferentes.

## Dependencias e limites

- GitHub Copilot com suporte a skills e agentes customizados.
- Python 3.10 ou superior para os helpers; eles usam a biblioteca padrao.
- Skills de formatos, como `xlsx`, `docx`, `pptx` e `pdf`, quando exigidas pelas
  entradas. `excalidraw` e necessario quando o fluxo pedir diagramas.
- Skills oficiais Azure, conforme o roteamento de cada skill, instaladas
  separadamente a partir de [microsoft/azure-skills](https://github.com/microsoft/azure-skills).
  A pasta de referencia e `$HOME\.agents\skills`, ou a pasta configurada pelo usuario.
- Ferramentas Azure/Microsoft Learn para evidencias atuais. A operacao da
  calculadora requer um browser canvas com capacidades adequadas e login
  realizado pelo usuario para salvar e compartilhar.

As skills oficiais e de formatos nao sao distribuidas neste repositorio.
Se uma dependencia ou ferramenta nao estiver disponivel, o fluxo deve declarar
a limitacao, sem inventar resultados nem afirmar validacao concluida.
Os scripts de apoio nao substituem o assessment nem geram, sozinhos, todos os
artefatos descritos pelas skills.

## Exemplos de uso

Depois de instalar, solicite ao Copilot:

- "Use azure-estimate-review para revisar esta estimativa de arquitetura e custo."
- "Use azure-architect-iaas para analisar este inventario RVTools."
- "Use azure-aws-to-azure-estimate para converter esta fatura AWS em estimativa Azure."
- "Use azure-pricing-calculator-portal para reproduzir esta planilha na calculadora."

Selecione `azure-migration-architect` entre os agentes customizados para um
assessment de migracao. Disponibilidade e modo de selecao dependem do cliente.

A conversao AWS exige confirmar PAYG, 1Y RI, 3Y RI, 1Y Savings Plan ou
3Y Savings Plan antes da precificacao. Nenhum fluxo autoriza deployment,
alteracao de recursos ou consulta a ambientes privados sem permissao explicita.

## Testes dos helpers

Execute a partir da raiz do repositorio:

```powershell
python -B -m unittest discover -s .\skills\azure-estimate-review\scripts -p "test_*.py"
python -B -m unittest discover -s .\skills\azure-architect-iaas\scripts -p "test_*.py"
python -B -m unittest discover -s .\skills\azure-pricing-calculator-portal\scripts -p "test_*.py"
```

Os exemplos JSON e os testes sao sinteticos: nao representam precos reais nem
links de estimativas publicadas. Testes locais nao verificam o estado atual
do portal, precos, disponibilidade regional ou resultados de assessments reais.

## Privacidade e contribuicoes

Nao inclua faturas, inventarios, dados de clientes, credenciais, caminhos
pessoais, valores comerciais reais ou exports de sessoes em commits, issues
ou pull requests. Use somente exemplos sinteticos.

Os arquivos de instrucao devem tratar entradas como dados nao confiaveis,
preservar rastreabilidade e marcar informacoes ausentes como **A DEFINIR**.
Estimativas sao preliminares, nao propostas comerciais vinculantes nem
certificacoes regulatorias.

A `book-to-skill` e as skills oficiais instaladas por terceiros nao fazem
parte desta publicacao. As instalacoes pessoais originais nao sao alteradas
por este repositorio.

## Licenca

[MIT](LICENSE). Consulte as licencas dos projetos externos para suas dependencias.
