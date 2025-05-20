import argparse
from collections import defaultdict
import functools
import json
import logging
from pathlib import Path
import shlex
import sqlite3
import subprocess
import sys
import time
from typing import Any
import jinja2

logging.basicConfig(format="{msg}", style="{", level=logging.INFO)


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    logging.info(f"$ {shlex.join(args)}")
    process = subprocess.run(
        args=args,
        stdout=subprocess.PIPE,
        check=True,
        encoding="utf8",
    )
    return process


@functools.cache
def resolve_nixos_channel(channel_name: str) -> str:
    args = [
        "nix",
        "eval",
        "--impure",
        "-I",
        f"nixpkgs=channel:{channel_name}",
        "--expr",
        "toString <nixpkgs>",
        "--raw",
    ]
    process = run(args)
    return process.stdout


def get_channel_packages(
    channel_name: str,
    name: str | None = None,
    attribute: str | None = None,
) -> dict[str, Any]:
    channel_path = resolve_nixos_channel(channel_name)
    args = [
        "nix-env",
        "--json",
        "-f",
        "<nixpkgs>",
        "-I",
        f"nixpkgs={channel_path}",
        "--arg",
        "config",
        "import <nixpkgs/pkgs/top-level/packages-config.nix>",
        "--query",
        "--available",
        "--meta",
    ]
    if name:
        args.append(name)
    elif attribute:
        args.append("--attr")
        args.append(attribute)
    process = run(args)

    return json.loads(process.stdout)


def get_channel_programs(channel_name: str) -> dict[str, set[str]]:
    channel_path = resolve_nixos_channel(channel_name)
    db = Path(channel_path) / "programs.sqlite"
    if not db.exists():
        raise RuntimeError(
            f"Missing programs.sqlite in channel {channel_name} {channel_path}"
        )
    programs = defaultdict(set)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("select name, package from Programs")
    for program, package in cur.fetchall():
        programs[package].add(program)
    return programs


def generate_pages(
    out: Path,
    pkgs: dict[str, dict[str, Any]],
) -> None:
    env = jinja2.Environment(loader=jinja2.PackageLoader(__package__ or "staticgen"))
    package = env.get_template("package.jinja")
    pkg_dir = out / "packages"

    start = time.perf_counter()
    for name, pkg in pkgs.items():
        file_name = f"{name}.html"
        file_path = pkg_dir / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform some field normalizations up front to make the template cleaner
        package_set = "No package set"
        if "." in name:
            package_set, _ = name.rsplit(".", 1)

        licenses = pkg.get("meta", {}).get("license", [])
        if isinstance(licenses, dict):
            licenses = [licenses]

        file_path.write_text(
            package.render(
                name=name,
                pkg=pkg,
                package_set=package_set,
                licenses=licenses,
            )
        )
    end = time.perf_counter()

    logging.info(f"Wrote {len(pkgs)} packages to {pkg_dir} in {end - start:0.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser()

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--channel", help="Load packages from a channel")
    source.add_argument(
        "--from-json", help="Load packages from a previous staticgen run"
    )
    filter = parser.add_mutually_exclusive_group()
    filter.add_argument(
        "--name", default=None, help="Filter to packages matching this name"
    )
    filter.add_argument("--attr", default=None, help="Filter to this attribute")

    parser.add_argument(
        "--write-json", help="Write the loaded package data to a file, - for stdout"
    )
    parser.add_argument("--out", help="Generate static pages in this directory")

    args = parser.parse_args()

    channel: str | None = args.channel
    from_json: str | None = args.from_json
    name: str | None = args.name
    attr: str | None = args.attr
    write_json: str | None = args.write_json
    out: str | None = args.out

    if not channel and not from_json:
        logging.error("One of --channel or --from-json is required")
        sys.exit(1)
    if not write_json and not out:
        logging.error("At least one of --write-json and --out is required")
        sys.exit(1)

    if channel:
        start = time.perf_counter()
        pkgs = get_channel_packages(
            channel_name=args.channel, name=name, attribute=attr
        )
        progs = get_channel_programs(channel_name=channel)
        for pkg_name, pkg in pkgs.items():
            if pkg_progs := progs.get(pkg_name):
                if "meta" not in pkg:
                    pkg["meta"] = {}
                pkg["meta"]["programs"] = list(sorted(pkg_progs))
        end = time.perf_counter()
        logging.info(
            f"Loaded {len(pkgs)} packages from channel {channel} in {end - start:0.2f}s"
        )
    elif from_json:
        with open(from_json) as f:
            pkgs = json.load(f)

    if write_json == "-":
        json.dump(pkgs, sys.stdout)
    elif write_json:
        with open(write_json, "w") as f:
            json.dump(pkgs, f)

    if out:
        generate_pages(Path(out), pkgs)
