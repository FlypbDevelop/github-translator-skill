"""CLI interface for github-translator-skill."""

import argparse
import sys


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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    args = parse_args(argv)

    print("github-translator skill - modo análise (MVP)")
    print(f"repo-url: {args.repo_url}")
    print(f"target-language: {args.target_language}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
