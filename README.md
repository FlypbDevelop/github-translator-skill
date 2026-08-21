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
