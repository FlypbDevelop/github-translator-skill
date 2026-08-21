# Skill Manifest

## Metadata

- **name:** github-translator
- **description:** Analisa um repositório GitHub para auxiliar tradução sem modificar o projeto original
- **version:** 0.1.0
- **entrypoint:** src/github_translator_skill/cli.py

## Overview

O github-translator é uma skill que analisa repositórios GitHub para auxiliar no processo de tradução. Esta skill respeita a integridade do projeto original e não realiza modificações nos arquivos do repositório analisado.

## Current Capabilities (v0.1.0)

- CLI básica com parâmetros para URL do repositório e idioma alvo
- Modo análise (MVP) - apenas exibe informações recebidas

## Future Capabilities

- Clone e análise de repositórios GitHub
- Identificação de arquivos traduzíveis
- Extração de strings para tradução
- Geração de arquivos de tradução
- Suporte a múltiplos formatos de arquivo
