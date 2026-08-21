# Skill Manifest — github-translator

## Metadata

- **name:** github-translator
- **description:** Analisa um repositório GitHub para auxiliar tradução sem modificar o projeto original
- **version:** 0.1.0
- **entrypoint:** src/github_translator_skill/cli.py

---

## Descrição

O `github-translator` é uma skill CLI que analisa repositórios GitHub para auxiliar no processo de tradução. Ela clona o repositório temporariamente, identifica arquivos traduzíveis, lê conteúdo de arquivos específicos e salva traduções com geração automática de patch (.patch). **O repositório original nunca é modificado.**

Projetada para ser consumida por agentes de IA (como OpenCode) via saída JSON estruturada, ou por humanos via saída de texto legível.

---

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/FlypbDevelop/github-translator-skill.git
cd github-translator-skill

# Instalar em modo desenvolvimento (recomendado)
pip install -e .

# Ou instalar normalmente
pip install .
```

### Requisitos

- Python 3.11+
- Git instalado e disponível no PATH

---

## Uso Geral

Após a instalação, a skill pode ser chamada via CLI:

```bash
github-translator [opções]
```

Ou diretamente via módulo:

```bash
python -m src.github_translator_skill.cli [opções]
```

A skill opera em quatro modos principais:

1. **Análise (raio-x):** Clona o repositório e lista arquivos traduzíveis com metadados.
2. **Leitura:** Clona o repositório e retorna o conteúdo de um arquivo específico.
3. **Escrita:** Salva uma tradução na pasta de output com geração de patch.
4. **Escrita sem repo:** Salva uma tradução sem clonar (quando o original não está disponível).

---

## Comandos e Parâmetros

| Argumento | Tipo | Padrão | Obrigatório | Descrição |
|-----------|------|--------|-------------|-----------|
| `--repo-url` | `str` | `None` | Sim (para análise e leitura) | URL do repositório GitHub a ser clonado. |
| `--target-language` | `str` | `None` | Não | Idioma alvo para tradução (ex: `pt-BR`, `es`, `fr`). |
| `--read-file` | `str` | `None` | Não | Caminho relativo de um arquivo para ler dentro do repositório. |
| `--write-translation` | `str` | `None` | Não | Caminho para um arquivo JSON de payload com a tradução. |
| `--output-dir` | `str` | `./translations` | Não | Pasta onde as traduções e patches serão salvos. |
| `--format` | `str` | `text` | Não | Formato de saída: `text` ou `json`. |

### Detalhes dos Modos

#### Modo Análise (raio-x)

Clona o repositório, lista os arquivos/pastas da raiz e identifica arquivos traduzíveis com metadados (caminho, número de linhas, título).

```bash
github-translator --repo-url https://github.com/pallets/flask --target-language pt-BR
github-translator --repo-url https://github.com/pallets/flask --format json
```

#### Modo Leitura

Clona o repositório e retorna o conteúdo completo de um arquivo específico.

```bash
github-translator --repo-url https://github.com/pallets/flask --read-file README.md
github-translator --repo-url https://github.com/pallets/flask --read-file docs/index.rst --format json
```

#### Modo Escrita (com repo)

Clona o repositório, salva a tradução na pasta de output e gera um arquivo `.patch` comparando o original com a tradução. O clone ocorre **antes** da geração do patch, garantindo acesso ao arquivo original.

```bash
github-translator --repo-url https://github.com/pallets/flask \
  --write-translation payload.json \
  --output-dir ./translations \
  --format json
```

#### Modo Escrita (sem repo)

Salva a tradução na pasta de output sem clonar o repositório. Nenhum patch é gerado (o original não está disponível).

```bash
github-translator --write-translation payload.json --format json
```

---

## Formato do Payload (`--write-translation`)

O argumento `--write-translation` recebe o **caminho de um arquivo JSON** com a tradução. O arquivo deve conter duas chaves obrigatórias:

### Estrutura

```json
{
  "original_path": "<caminho relativo do arquivo original>",
  "translated_content": "<conteúdo traduzido do arquivo>"
}
```

### Exemplo (`payload.json`)

```json
{
  "original_path": "README.md",
  "translated_content": "# Flask\n\nFlask é um framework leve para web.\n\n## Exemplo\n\n```python\nfrom flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Olá, Mundo!'\n```\n"
}
```

### Exemplo com subpasta

```json
{
  "original_path": "docs/install.md",
  "translated_content": "# Instalação\n\n## Pré-requisitos\n\n- Python 3.11+\n- pip\n\n## Instalação\n\n```bash\npip install flask\n```\n"
}
```

> **Nota:** O encoding do arquivo é lido como `utf-8-sig`, o que ignora automaticamente o BOM (Byte Order Mark) que o Windows/PowerShell pode adicionar.

---

## Formato da Saída (JSON)

Quando `--format json` é usado, a skill retorna JSON válido no stdout. Abaixo estão os formatos de resposta para cada modo.

### Resposta de Análise (raio-x)

```json
{
  "status": "success",
  "repo_url": "https://github.com/pallets/flask",
  "target_language": "pt-BR",
  "files": [
    "README.md",
    "docs",
    "src",
    "pyproject.toml"
  ],
  "translatable_files": [
    {
      "path": "README.md",
      "lines": 53,
      "title": "Flask"
    },
    {
      "path": "docs/api.rst",
      "lines": 708,
      "title": "Sem título"
    },
    {
      "path": "docs/index.rst",
      "lines": 89,
      "title": "Sem título"
    }
  ],
  "message": "Repositório clonado com sucesso em pasta temporária."
}
```

### Resposta de Leitura de Arquivo

```json
{
  "status": "success",
  "repo_url": "https://github.com/pallets/flask",
  "file_path": "README.md",
  "content": "# Flask\n\nFlask is a lightweight WSGI web application framework..."
}
```

### Resposta de Escrita de Tradução (com repo)

```json
{
  "status": "success",
  "original_path": "README.md",
  "saved_path": "./translations/README.md",
  "patch_file": "./translations/README.md.patch",
  "message": "Translation saved successfully"
}
```

### Resposta de Escrita de Tradução (sem repo)

```json
{
  "status": "success",
  "original_path": "README.md",
  "saved_path": "./translations/README.md",
  "patch_file": null,
  "message": "Translation saved successfully (no patch: --repo-url not provided)"
}
```

### Resposta de Erro

```json
{
  "status": "error",
  "message": "File not found in the cloned repository."
}
```

```json
{
  "status": "error",
  "message": "Invalid JSON file: Expecting value: line 1 column 1 (char 0)"
}
```

---

## Geração de Patch

Quando `--write-translation` é combinado com `--repo-url`, a skill:

1. Clona o repositório em um diretório temporário.
2. Salva o arquivo traduzido na pasta de output.
3. Lê o arquivo original do clone.
4. Gera um diff unificado (`difflib.unified_diff`) comparando original vs tradução.
5. Salva o diff como `<original_path>.patch` na pasta de output.
6. Remove o diretório temporário do clone.

O patch gerado segue o formato padrão `unified diff`:

```diff
--- a/README.md
+++ b/README.md
@@ -1,53 +1,3 @@
-<div align="center"><img src="..." alt="" height="150"></div>
-
 # Flask

-Flask is a lightweight WSGI web application framework...
+Flask é um framework leve para web.
```

---

## Regras de Detecção de Arquivos Traduzíveis

A skill identifica automaticamente arquivos candidatos a tradução:

| Regra | Descrição |
|-------|-----------|
| `.md` | Arquivos Markdown (Readme.md, History.md, etc.) |
| `docs/` | Qualquer arquivo dentro da pasta `docs` |
| `locales/` | Qualquer arquivo dentro da pasta `locales` |
| `i18n/` | Qualquer arquivo dentro da pasta `i18n` |
| `lang/` | Qualquer arquivo dentro da pasta `lang` |
| ❌ `.git` | Ignorado completamente |
| ❌ `node_modules` | Ignorado completamente |

---

## Segurança

- **Path traversal:** Todos os caminhos de arquivo são normalizados com `os.path.normpath()` e validados com `os.path.realpath()` para impedir acesso fora dos diretórios permitidos.
- **Diretórios temporários:** O clone é feito em `tempfile.TemporaryDirectory()` que é automaticamente removido após o uso.
- **Encoding:** Leitura com fallback `utf-8` → `latin-1` → `errors="ignore"` para evitar falhas em arquivos com encoding não padrão.
- **BOM:** Arquivos JSON são lidos com `utf-8-sig` para ignorar BOM do Windows.

---

## Arquitetura

```
github-translator-skill/
├── README.md
├── SKILL.md                    # Este arquivo
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── src/
│   └── github_translator_skill/
│       ├── __init__.py         # __version__ = "0.1.0"
│       └── cli.py              # CLI principal
└── tests/
    └── __init__.py
```

### Funções Principais (`cli.py`)

| Função | Descrição |
|--------|-----------|
| `parse_args()` | Parse dos argumentos CLI via argparse |
| `clone_repo()` | Clona repositório via `git clone --depth 1` |
| `list_root_items()` | Lista arquivos/pastas na raiz do clone |
| `_read_file_text()` | Lê arquivo com fallback de encoding |
| `inspect_file()` | Retorna metadados de um arquivo (path, lines, title) |
| `find_translatable_files()` | Encontra e inspeciona arquivos traduzíveis |
| `save_translation()` | Salva tradução na pasta de output |
| `generate_patch()` | Gera diff unificado com `difflib.unified_diff` |
| `_load_translation_payload()` | Lê e valida o JSON de payload |
| `_handle_write_only()` | Modo escrita sem repo |
| `_handle_write_with_repo()` | Modo escrita com repo (gera patch) |
| `_handle_repo()` | Modo leitura/raio-x |
| `main()` | Entry point que despacha para os modos corretos |
