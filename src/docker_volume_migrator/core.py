"""Business logic – repackaged from original monolithic script for reuse & tests."""

from __future__ import annotations

from typing import List

import typer

from .utils import copy_volume, create_volume, list_volumes, ssh, volume_exists

app = typer.Typer(add_completion=True, help="Move Docker volumes between hosts via SSH, step by step.")


@app.command("run")
def run_migrator() -> None:  # noqa: D401
    """Interactive wizard to move Docker volumes between two hosts."""
    typer.echo("""\n🛠️  Docker Volume Mover\n========================\n""")

    src_host = typer.prompt("Enter **source host** (SSH address)")
    try:
        ssh(src_host, "echo connected")
    except SystemExit:
        typer.secho("❌ Unable to SSH into source host. Exiting…", fg=typer.colors.RED)
        raise typer.Exit(1)

    volumes = list_volumes(src_host)
    if not volumes:
        typer.secho("No Docker volumes found on source host", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.echo("\nAvailable volumes:")
    for i, vol in enumerate(volumes, 1):
        typer.echo(f"  {i}. {vol}")

    choice = typer.prompt(f"Select volume(s) [1-{len(volumes)}] (comma-separated indexes or 'all')", default="1")
    choice = choice.strip().lower()
    if choice == "all":
        src_volumes = volumes
    else:
        try:
            indices = [int(c.strip()) - 1 for c in choice.split(",") if c.strip()]
            if any(i < 0 or i >= len(volumes) for i in indices):
                raise ValueError
        except ValueError:
            typer.secho("Invalid selection", fg=typer.colors.RED)
            raise typer.Exit(1)
        src_volumes = [volumes[i] for i in indices]

    dst_host = typer.prompt("Enter **target host** (SSH address)")
    try:
        ssh(dst_host, "echo connected")
    except SystemExit:
        typer.secho("❌ Unable to SSH into target host. Exiting…", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.echo("\nDestination volume options on target host:")
    dst_volumes_existing = list_volumes(dst_host)
    if dst_volumes_existing:
        for v in dst_volumes_existing:
            typer.echo(f"  • {v}")
    else:
        typer.echo("  (no volumes yet)")

    create_new = typer.confirm("Create **new** volume(s)? (No = use/overwrite existing)", default=True)

    dst_volume_map: dict[str, str] = {}
    if create_new:
        for vol in src_volumes:
            if not volume_exists(dst_host, vol):
                create_volume(dst_host, vol)
            else:
                typer.echo(f"Destination volume '{vol}' already exists and will be **overwritten**.")
            dst_volume_map[vol] = vol
    else:
        if not dst_volumes_existing:
            typer.secho("No existing volumes to choose. Aborting …", fg=typer.colors.RED)
            raise typer.Exit(1)

        typer.echo("Select existing destination volumes for each source volume:")
        for src_vol in src_volumes:
            typer.echo(f"\nSource volume: {src_vol}")
            vol_to_idx = {str(i + 1): v for i, v in enumerate(dst_volumes_existing)}
            for num, vol in vol_to_idx.items():
                typer.echo(f"  {num}. {vol}")
            sel = typer.prompt("Enter number")
            dst_vol = vol_to_idx.get(sel)
            if not dst_vol:
                typer.secho("Invalid selection", fg=typer.colors.RED)
                raise typer.Exit(1)
            dst_volume_map[src_vol] = dst_vol

    typer.echo("\nTransfer summary:")
    for s in src_volumes:
        typer.echo(f"  📤 {src_host}:{s}  ==>  📥 {dst_host}:{dst_volume_map[s]}")
    typer.echo()

    if not typer.confirm("Proceed?", default=True):
        typer.echo("Aborted by user.")
        raise typer.Exit()

    for s in src_volumes:
        copy_volume(src_host, s, dst_host, dst_volume_map[s])

    typer.secho("All requested volume transfers completed.", fg=typer.colors.GREEN)
