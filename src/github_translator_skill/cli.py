"""CLI interface for github-translator-skill."""

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile

# Forçar UTF-8 na saída do terminal (corrige acentuação no Windows)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Pastas que indicam conteúdo de tradução
TRANSLATABLE_DIRS = {"docs", "locales", "i18n", "lang"}

# Extensões de arquivos traduzíveis
TRANSLATABLE_EXTENSIONS = {".md"}

# Pastas a ignorar completamente
IGNORED_DIRS = {".git", "node_modules"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="github-translator",
        description="Analisa um repositório GitHub para auxiliar tradução sem modificar o projeto original",
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        default=None,
        help="URL do repositório GitHub a ser analisado",
    )
    parser.add_argument(
        "--target-language",
        type=str,
        default=None,
        help="Idioma alvo para tradução (ex: pt-BR, es, fr)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Formato de saída: text (padrão) ou json",
    )
    parser.add_argument(
        "--read-file",
        type=str,
        default=None,
        help="Caminho relativo de um arquivo para ler (ex: README.md)",
    )
    parser.add_argument(
        "--write-translation",
        type=str,
        default=None,
        help='Caminho do arquivo JSON com "original_path" e "translated_content"',
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./translations",
        help="Pasta de saída para traduções (padrão: ./translations)",
    )
    return parser.parse_args(argv)


def clone_repo(repo_url: str, target_dir: str) -> None:
    """Clone a repository using git clone --depth 1."""
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, target_dir],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Erro desconhecido ao clonar repositório")


def list_root_items(directory: str) -> list[str]:
    """List files and folders at the root of the given directory."""
    try:
        return sorted(os.listdir(directory))
    except OSError as e:
        raise RuntimeError(f"Erro ao listar arquivos: {e}")


def _read_file_text(filepath: str) -> str:
    """Read a file with encoding fallback: utf-8 → latin-1 → ignore errors."""
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(filepath, encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, ValueError):
            continue
    # Fallback final: ignora erros de decodificação
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        return f.read()


def inspect_file(filepath: str, base_dir: str) -> dict:
    """Inspect a single file and return metadata for the x-ray report.

    Returns a dict with:
        - path: relative path from the repository root
        - lines: total number of lines (int)
        - title: first Markdown heading (# ...) or "Sem título"
    """
    relative_path = os.path.relpath(filepath, base_dir)
    content = _read_file_text(filepath)

    # Contar linhas
    lines = len(content.splitlines())

    # Extrair título: primeira linha que comece com "# "
    title = "Sem título"
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break

    return {
        "path": relative_path,
        "lines": lines,
        "title": title,
    }


def find_translatable_files(temp_dir: str) -> list[dict]:
    """Find files that are candidates for translation and inspect each one.

    Rules:
    - Files with .md extension
    - Files inside folders named 'docs', 'locales', 'i18n', or 'lang'
    - Ignores paths containing '.git' or 'node_modules'
    """
    results: list[dict] = []

    for root, dirs, files in os.walk(temp_dir):
        # Ignorar pastas indesejadas (modifica dirs in-place para impedir descida)
        dirs[:] = [
            d for d in dirs
            if d not in IGNORED_DIRS
        ]

        for filename in files:
            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(filepath, temp_dir)

            # Ignorar se caminho contém .git ou node_modules
            if ".git" in relative_path.split(os.sep) or "node_modules" in relative_path.split(os.sep):
                continue

            _, ext = os.path.splitext(filename)
            is_markdown = ext.lower() in TRANSLATABLE_EXTENSIONS

            # Verificar se está dentro de uma pasta traduzível
            path_parts = relative_path.split(os.sep)
            in_translatable_dir = any(part.lower() in TRANSLATABLE_DIRS for part in path_parts)

            if is_markdown or in_translatable_dir:
                try:
                    info = inspect_file(filepath, temp_dir)
                    results.append(info)
                except OSError:
                    # Pula arquivos que não podem ser lidos
                    continue

    return sorted(results, key=lambda item: item["path"])


def save_translation(original_path: str, translated_content: str, output_dir: str) -> dict:
    """Save a translation to the output directory.

    Returns a dict with status, original_path, saved_path, and message.
    Raises RuntimeError on failure.
    """
    # Normalizar caminho para evitar path traversal
    safe_path = os.path.normpath(original_path)
    full_output_path = os.path.join(output_dir, safe_path)

    # Verificar se o caminho normalizado não sai da pasta de output
    real_output_dir = os.path.realpath(output_dir)
    real_full_path = os.path.realpath(full_output_path)
    if not real_full_path.startswith(real_output_dir + os.sep) and real_full_path != real_output_dir:
        raise RuntimeError("Invalid path: translation path escapes output directory.")

    # Criar diretórios necessários
    os.makedirs(os.path.dirname(full_output_path) if os.path.dirname(full_output_path) else output_dir, exist_ok=True)

    # Salvar arquivo
    with open(full_output_path, "w", encoding="utf-8") as f:
        f.write(translated_content)

    return {
        "status": "success",
        "original_path": original_path,
        "saved_path": full_output_path,
        "message": "Translation saved successfully",
    }


def generate_patch(
    original_lines: list[str],
    translated_lines: list[str],
    original_path: str,
    output_dir: str,
) -> str | None:
    """Generate a unified diff patch between original and translated content.

    Returns the path where the .patch file was saved, or None if no diff.
    Raises OSError on write failure.
    """
    diff = list(difflib.unified_diff(
        original_lines,
        translated_lines,
        fromfile=f"a/{original_path}",
        tofile=f"b/{original_path}",
    ))

    if not diff:
        return None

    patch_path = os.path.join(output_dir, os.path.normpath(original_path) + ".patch")

    # Criar diretórios necessários
    os.makedirs(os.path.dirname(patch_path) if os.path.dirname(patch_path) else output_dir, exist_ok=True)

    with open(patch_path, "w", encoding="utf-8") as f:
        f.writelines(diff)

    return patch_path


def _error_exit(message: str, fmt: str, repo_url: str | None = None) -> int:
    """Helper to print an error and return exit code 1."""
    if fmt == "json":
        output = {"status": "error", "message": message}
        if repo_url:
            output["repo_url"] = repo_url
        print(json.dumps(output, ensure_ascii=False))
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    args = parse_args(argv)

    # Modo escrita de tradução SEM repo-url (sem geração de patch)
    if args.write_translation and not args.repo_url:
        return _handle_write_only(args)

    # Modo escrita de tradução COM repo-url (gera patch a partir do clone)
    if args.write_translation and args.repo_url:
        return _handle_write_with_repo(args)

    # Modo clone (read-file ou raio-x)
    if args.repo_url:
        return _handle_repo(args)

    # Sem nenhum argumento útil
    if args.format == "json":
        output = {
            "status": "success",
            "repo_url": args.repo_url,
            "target_language": args.target_language,
            "files": [],
            "translatable_files": [],
            "message": "Skill is ready for analysis.",
        }
        print(json.dumps(output, ensure_ascii=False))
    else:
        print("github-translator skill - modo análise (MVP)")
        print(f"repo-url: {args.repo_url}")
        print(f"target-language: {args.target_language}")

    return 0


def _load_translation_payload(args: argparse.Namespace) -> tuple[dict | None, int]:
    """Load and validate the JSON file from --write-translation.

    Returns (translation_data, exit_code). If exit_code != 0, an error was already printed.
    """
    if not os.path.isfile(args.write_translation):
        _error_exit(f"File not found: {args.write_translation}", args.format)
        return None, 1

    try:
        with open(args.write_translation, encoding="utf-8-sig") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        _error_exit(f"Invalid JSON file: {e}", args.format)
        return None, 1

    original_path = data.get("original_path")
    translated_content = data.get("translated_content")

    if not original_path or translated_content is None:
        _error_exit("JSON must contain 'original_path' and 'translated_content' keys.", args.format)
        return None, 1

    return data, 0


def _handle_write_only(args: argparse.Namespace) -> int:
    """Handle --write-translation without --repo-url (no patch possible)."""
    data, exit_code = _load_translation_payload(args)
    if exit_code != 0:
        return exit_code

    try:
        result = save_translation(data["original_path"], data["translated_content"], args.output_dir)
    except OSError as e:
        return _error_exit(f"Failed to save file: {e}", args.format)
    except RuntimeError as e:
        return _error_exit(str(e), args.format)

    result["patch_file"] = None
    result["message"] = "Translation saved successfully (no patch: --repo-url not provided)"

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"Translation saved successfully: {result['saved_path']}")
        print("No .patch generated (--repo-url not provided).")

    return 0


def _handle_write_with_repo(args: argparse.Namespace) -> int:
    """Handle --write-translation WITH --repo-url (clone, save, generate patch)."""
    data, exit_code = _load_translation_payload(args)
    if exit_code != 0:
        return exit_code

    original_path = data["original_path"]
    translated_content = data["translated_content"]

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            clone_repo(args.repo_url, tmp_dir)

            # Salvar tradução na pasta de output
            try:
                result = save_translation(original_path, translated_content, args.output_dir)
            except (OSError, RuntimeError) as e:
                return _error_exit(f"Failed to save translation: {e}", args.format, args.repo_url)

            # Ler arquivo original do clone para gerar patch
            original_full_path = os.path.join(tmp_dir, os.path.normpath(original_path))

            if os.path.isfile(original_full_path) and os.path.realpath(original_full_path).startswith(
                os.path.realpath(tmp_dir)
            ):
                original_text = _read_file_text(original_full_path)
                original_lines = original_text.splitlines(keepends=True)
                translated_lines = translated_content.splitlines(keepends=True)

                patch_file = generate_patch(original_lines, translated_lines, original_path, args.output_dir)
                result["patch_file"] = patch_file
            else:
                result["patch_file"] = None
                result["message"] = "Translation saved successfully (original file not found for patch)"

            # Imprimir resultado
            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False))
            else:
                print(f"Translation saved successfully: {result['saved_path']}")
                if result["patch_file"]:
                    print(f"Patch file generated: {result['patch_file']}")
                else:
                    print("No .patch generated (original file not found in repository).")

    except RuntimeError as e:
        return _error_exit(str(e), args.format, args.repo_url)

    return 0


def _handle_repo(args: argparse.Namespace) -> int:
    """Handle --repo-url without --write-translation (read-file or x-ray)."""
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            clone_repo(args.repo_url, tmp_dir)

            # Modo leitura de arquivo específico
            if args.read_file:
                file_path = os.path.normpath(args.read_file)
                full_path = os.path.join(tmp_dir, file_path)

                # Verificar se o arquivo existe e está dentro do repositório
                if not os.path.isfile(full_path) or not os.path.realpath(full_path).startswith(
                    os.path.realpath(tmp_dir)
                ):
                    return _error_exit("File not found in the cloned repository.", args.format, args.repo_url)

                content = _read_file_text(full_path)

                if args.format == "json":
                    output = {
                        "status": "success",
                        "repo_url": args.repo_url,
                        "file_path": file_path,
                        "content": content,
                    }
                    print(json.dumps(output, ensure_ascii=False))
                else:
                    print(content, end="")

            # Modo raio-x (listar arquivos)
            else:
                files = list_root_items(tmp_dir)
                translatable_files = find_translatable_files(tmp_dir)

                if args.format == "json":
                    output = {
                        "status": "success",
                        "repo_url": args.repo_url,
                        "target_language": args.target_language,
                        "files": files,
                        "translatable_files": translatable_files,
                        "message": "Repositório clonado com sucesso em pasta temporária.",
                    }
                    print(json.dumps(output, ensure_ascii=False))
                else:
                    print("Repositório clonado com sucesso em pasta temporária")
                    print(f"Arquivos/pastas encontrados na raiz: {files}")
                    print()
                    print(f"Arquivos traduzíveis encontrados ({len(translatable_files)}):")
                    for item in translatable_files:
                        print(f"  - {item['path']} ({item['lines']} linhas): {item['title']}")

    except RuntimeError as e:
        return _error_exit(str(e), args.format, args.repo_url)

    return 0


if __name__ == "__main__":
    sys.exit(main())
