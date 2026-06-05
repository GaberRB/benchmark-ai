# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma

Sempre responda em **português brasileiro (pt-BR)** neste projeto, independentemente do idioma da pergunta.

## Ferramenta Principal

Este projeto usa o **specify** (GitHub Spec Kit — toolkit para desenvolvimento orientado a especificações).

### Comandos disponíveis

```powershell
specify init [NOME_PROJETO]         # Inicializar novo projeto Specify
specify init --here --integration claude  # Inicializar no diretório atual com Claude
specify check                       # Verificar ferramentas necessárias instaladas
specify integration install <nome>  # Instalar uma integração
specify integration list            # Listar integrações disponíveis
specify workflow                    # Gerenciar e executar workflows de automação
specify preset                      # Gerenciar presets do spec-kit
specify self upgrade                # Atualizar o próprio specify
```

## Gerenciamento de Pacotes

Este projeto usa `uv` para gerenciamento de ferramentas Python.

Instalar uv (caso não esteja presente):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Instalar/atualizar o specify:

```powershell
uv tool install specify-cli
```

## Permissões Pré-autorizadas

Os seguintes comandos não exigem confirmação (configurados em `.claude/settings.local.json`):

- `specify <args>`
- `uv tool <args>`
- Instalação do uv via PowerShell
