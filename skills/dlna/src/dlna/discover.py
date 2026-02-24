"""Device discovery utilities."""

from .player import discover_devices, DLNADevice
from .config import get_default_device


async def find_device(name: str | None = None, timeout: int = 5) -> DLNADevice | None:
    """Find a specific DLNA device by name.

    If name is not provided, uses the default device from config.

    Args:
        name: Device name to search for (case-insensitive, partial match).
              If None, uses default device from config.
        timeout: Scan timeout in seconds

    Returns:
        DLNADevice if found, None otherwise
    """
    # Use default device if no name provided
    if name is None:
        name = get_default_device()
        if name is None:
            print("No device specified and no default device configured.")
            print("Use: dlna config --device <device_name>")
            return None
        print(f"Using default device: {name}")

    devices = await discover_devices(timeout=timeout)
    name_lower = name.lower()

    # Exact match first
    for device in devices:
        if device.name.lower() == name_lower:
            return device

    # Partial match
    for device in devices:
        if name_lower in device.name.lower():
            return device

    return None
