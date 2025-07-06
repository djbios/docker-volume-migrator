"""Utility functions reused across modules."""

from __future__ import annotations

import subprocess
import sys
from typing import List

import typer


def run(cmd: List[str] | str, *, silent: bool = False) -> str:
    """Run a shell command and return stdout."""
    if isinstance(cmd, str):
        shell = True
    else:
        shell = False
    if not silent:
        typer.echo(typer.style("$ " + (cmd if isinstance(cmd, str) else " ".join(cmd)), fg=typer.colors.BRIGHT_BLACK))
    try:
        output = subprocess.check_output(cmd, shell=shell, text=True)
        return output.strip()
    except subprocess.CalledProcessError as exc:
        typer.secho(f"Command failed with exit code {exc.returncode}: {exc.cmd}", fg=typer.colors.RED)
        sys.exit(exc.returncode)


def ssh(host: str, remote_cmd: str) -> str:
    """Run *remote_cmd* on *host* via SSH and return stdout."""
    return run(["ssh", host, remote_cmd], silent=True)


# Volume helpers

def list_volumes(host: str) -> List[str]:
    out = ssh(host, "docker volume ls -q")
    return [v for v in out.splitlines() if v]


def volume_exists(host: str, name: str) -> bool:
    return name in list_volumes(host)


def create_volume(host: str, name: str) -> None:
    ssh(host, f"docker volume create {name}")
    typer.secho(f"✔ Created volume '{name}' on {host}", fg=typer.colors.GREEN)


def copy_volume(src_host: str, src_vol: str, dst_host: str, dst_vol: str) -> None:
    typer.echo("📦 Beginning data transfer … this may take a while ⏳\n")
    pipeline = (
        f"ssh {src_host} 'docker run --rm -v {src_vol}:/from alpine:3.20 tar czf - -C /from .' "
        f"| ssh {dst_host} 'docker run --rm -i -v {dst_vol}:/to alpine:3.20 tar xzf - -C /to'"
    )
    run(pipeline)
    typer.secho("🎉 Transfer complete!", fg=typer.colors.GREEN)
