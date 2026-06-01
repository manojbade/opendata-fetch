"""Command-line interface for opendata-fetch.

    opendata-fetch list                       Show all available sources
    opendata-fetch fetch <slug> [<slug>...]   Download one or more sources
    opendata-fetch fetch --all                Download every source
    opendata-fetch verify <slug> [<slug>...]  Re-download and compare against on-disk copies
"""

from __future__ import annotations

import argparse
import logging
import sys

from opendata_fetch.engine import DownloadError
from opendata_fetch.registry import RegistryError, list_sources
from opendata_fetch.runner import fetch_source


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
    )


def _cmd_list(args: argparse.Namespace) -> int:
    sources = list_sources()
    print(f"{len(sources)} sources:\n")
    for s in sources:
        kind = "custom" if s.is_custom else f"{len(s.files)} file(s)"
        print(f"  {s.slug:<24} {s.agency}")
        print(f"  {'':<24} {s.dataset}")
        print(f"  {'':<24} [{kind}]")
        if s.update_cadence:
            print(f"  {'':<24} update: {s.update_cadence}")
        print()
    return 0


def _resolve_slugs(args: argparse.Namespace) -> list[str]:
    if getattr(args, "all", False):
        return [s.slug for s in list_sources()]
    return args.slugs


def _cmd_fetch(args: argparse.Namespace) -> int:
    slugs = _resolve_slugs(args)
    if not slugs:
        print("error: pass one or more source slugs, or --all", file=sys.stderr)
        return 2

    failures: list[str] = []
    for slug in slugs:
        try:
            paths = fetch_source(
                slug, dest=args.dest, force=args.force, extract=args.extract
            )
            print(f"[{slug}] OK — {len(paths)} file(s) in {args.dest}/{slug}/")
        except (DownloadError, RegistryError) as e:
            print(f"[{slug}] FAILED — {e}", file=sys.stderr)
            failures.append(slug)

    if failures:
        print(f"\n{len(failures)} source(s) failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    # Imported here so `list`/`fetch` don't pay for it.
    from opendata_fetch.verify import verify_sources

    slugs = _resolve_slugs(args)
    if not slugs:
        print("error: pass one or more source slugs, or --all", file=sys.stderr)
        return 2
    return verify_sources(slugs, dest=args.dest)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opendata-fetch",
        description="Download U.S. government open datasets as the agencies ship them.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="show all available sources")
    p_list.set_defaults(func=_cmd_list)

    p_fetch = sub.add_parser("fetch", help="download one or more sources")
    p_fetch.add_argument("slugs", nargs="*", help="source slugs, e.g. 05-cdc-svi")
    p_fetch.add_argument("--all", action="store_true", help="download every source")
    p_fetch.add_argument("--dest", default="data", help="download root (default: data)")
    p_fetch.add_argument("--force", action="store_true", help="re-download existing files")
    p_fetch.add_argument("--extract", action="store_true", help="unzip downloaded archives")
    p_fetch.set_defaults(func=_cmd_fetch)

    p_verify = sub.add_parser(
        "verify", help="re-download and compare against the on-disk copy"
    )
    p_verify.add_argument("slugs", nargs="*", help="source slugs to verify")
    p_verify.add_argument("--all", action="store_true", help="verify every source")
    p_verify.add_argument("--dest", default="data", help="download root (default: data)")
    p_verify.set_defaults(func=_cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RegistryError as e:
        print(f"registry error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
