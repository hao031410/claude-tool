"""DLNA CLI - Control DLNA MediaRenderer devices."""

import asyncio

import click

from . import (
    discover_devices,
    find_device,
    play_url,
    stop,
    get_status,
    set_default_device,
    clear_default_device,
    show_config,
)


@click.group()
def cli():
    """DLNA Media Renderer control tool."""
    pass


@cli.command()
@click.option("--timeout", "-t", default=5, help="Scan timeout in seconds")
def discover(timeout: int):
    """Discover DLNA devices on the network."""
    async def _discover():
        devices = await discover_devices(timeout=timeout)

        if not devices:
            click.echo("No DLNA devices found.")
            return

        click.echo(f"\nFound {len(devices)} device(s):\n")
        for i, device in enumerate(devices, 1):
            click.echo(f"  {i}. {device.name}")
            click.echo(f"     Model: {device.model_name}")
            click.echo(f"     Address: {device.location}")
            click.echo()

    asyncio.run(_discover())


@cli.command()
@click.argument("url")
@click.argument("device_name", required=False)
def play(url: str, device_name: str | None):
    """Play a media URL on a DLNA device.

    URL: Media URL to play (http://...)
    DEVICE_NAME: Name of the DLNA device (optional, uses default if not provided)
    """
    async def _play():
        device = await find_device(device_name)
        if not device:
            if device_name:
                click.echo(f"Device '{device_name}' not found", err=True)
            return

        click.echo(f"Found: {device.name}")
        await play_url(device, url)

    asyncio.run(_play())


@cli.command()
@click.argument("device_name", required=False)
def stop_cmd(device_name: str | None):
    """Stop playback on a DLNA device.

    DEVICE_NAME: Name of the DLNA device (optional, uses default if not provided)
    """
    async def _stop():
        device = await find_device(device_name)
        if not device:
            if device_name:
                click.echo(f"Device '{device_name}' not found", err=True)
            return

        await stop(device)

    asyncio.run(_stop())


@cli.command()
@click.argument("device_name", required=False)
def status(device_name: str | None):
    """Get playback status of a DLNA device.

    DEVICE_NAME: Name of the DLNA device (optional, uses default if not provided)
    """
    async def _status():
        device = await find_device(device_name)
        if not device:
            if device_name:
                click.echo(f"Device '{device_name}' not found", err=True)
            return

        result = await get_status(device)
        click.echo(f"State: {result.state}")

    asyncio.run(_status())


@cli.command()
@click.option("--device", "-d", help="Set default device name")
@click.option("--unset-device", is_flag=True, help="Clear default device")
@click.option("--show", "-s", is_flag=True, help="Show current configuration")
def config(device: str | None, unset_device: bool, show: bool):
    """Manage DLNA configuration."""
    if device:
        set_default_device(device)
        click.echo(f"Default device set to: {device}")
    elif unset_device:
        clear_default_device()
        click.echo("Default device cleared")
    else:
        show_config()


def main():
    cli()


if __name__ == "__main__":
    main()
