"""Command-line presentation adapter."""

import argparse


def main() -> None:
    """Expose a deliberately small operational CLI foundation."""
    parser = argparse.ArgumentParser(prog="phoenix", description="Phoenix AI X platform CLI")
    parser.add_argument("--version", action="store_true", help="Print version information")
    args = parser.parse_args()
    if args.version:
        from phoenix_ai import __version__

        print(__version__)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

