# github-translator-skill

Uma skill para analisar repositórios GitHub e auxiliar no processo de tradução, sem modificar o projeto original.

## Sobre

O `github-translator-skill` é uma ferramenta em fase inicial de desenvolvimento (MVP) que tem como objetivo:

- Analisar a estrutura de um repositório GitHub
- Identificar arquivos e textos passíveis de tradução
- Fornecer suporte para o processo de tradução do projeto

> ⚠️ **Atenção:** Este é um MVP inicial. A funcionalidade de tradução e a integração com GitHub ainda não foram implementadas.

## Requisitos

- Python 3.11+
- Git instalado e disponível no PATH

## Instalação

```bash
# Clonar o repositório
git clone <repository-url>
cd github-translator-skill

# Criar ambiente virtual (opcional)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Instalação em agentes de IA (OpenCode e compatíveis)

O `SKILL.md` deste repositório segue o formato padrão de *Agent Skills* com frontmatter YAML (`name` + `description`), tornando a skill auto-discovery em ferramentas como **OpenCode**, **Claude Code** e outros agentes que suportem esse formato.

### OpenCode — instalação global (todos os projetos)

```powershell
# 1. Clonar a skill na pasta global do OpenCode
git clone https://github.com/FlypbDevelop/github-translator-skill.git "$env:USERPROFILE\.config\opencode\skill\github-translator"

# 2. Instalar o CLI usado pela skill
pip install -e "$env:USERPROFILE\.config\opencode\skill\github-translator"

# 3. Reiniciar o OpenCode para carregar a skill
```

> **Nota:** o nome da pasta (`github-translator`) deve corresponder ao campo `name` do frontmatter do `SKILL.md`.

### OpenCode — instalação por projeto

```powershell
git clone https://github.com/FlypbDevelop/github-translator-skill.git .opencode/skill/github-translator
pip install -e .opencode/skill/github-translator
```

Após reiniciar o agente, basta pedir algo como *"analise o repositório X para tradução para pt-BR"* e a skill será acionada automaticamente.

### Outros agentes (Claude Code, etc.)

```bash
# Claude Code lê skills de ~/.claude/skills/
git clone https://github.com/FlypbDevelop/github-translator-skill.git ~/.claude/skills/github-translator
pip install -e ~/.claude/skills/github-translator
```

## Uso

```bash
python -m src.github_translator_skill.cli --repo-url <url-do-repositorio> --target-language <idioma>
```

## Estrutura do Projeto

```
github-translator-skill/
├── README.md
├── SKILL.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── src/
│   └── github_translator_skill/
│       ├── __init__.py
│       └── cli.py
└── tests/
    └── __init__.py
```

## Licença

Licença a ser definida.
