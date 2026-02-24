"""DLNA media control module."""

import asyncio
from dataclasses import dataclass
from typing import Optional

from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.client_factory import UpnpFactory

# DLNA service type for AVTransport
AVTRANSPORT_SERVICE_TYPE = "urn:schemas-upnp-org:service:AVTransport:1"


@dataclass
class DLNADevice:
    """Wrapper for DLNA MediaRenderer device."""

    name: str
    model_name: str
    location: str
    udn: str

    def __repr__(self):
        return f"DLNADevice(name='{self.name}', model='{self.model_name}')"


async def discover_devices(timeout: int = 5) -> list[DLNADevice]:
    """Discover DLNA MediaRenderer devices on the network.

    Args:
        timeout: Scan timeout in seconds

    Returns:
        List of DLNA MediaRenderer devices
    """
    from async_upnp_client.search import async_search
    from async_upnp_client.ssdp import SSDP_ST_ALL

    devices_found = {}

    async def on_response(response):
        """Handle SSDP response."""
        st = response.get("ST", "")
        location = response.get("LOCATION", "")
        usn = response.get("USN", "")

        # Only care about MediaRenderer devices
        if "MediaRenderer" not in st or not location:
            return

        # Avoid duplicates
        if usn in devices_found:
            return

        try:
            # Connect to device and get info
            requester = AiohttpRequester()
            factory = UpnpFactory(requester)
            device = await factory.async_create_device(location)

            # Verify it has AVTransport service
            if device.find_service(service_type=AVTRANSPORT_SERVICE_TYPE):
                dlna_device = DLNADevice(
                    name=device.name or device.friendly_name or "Unknown DLNA Device",
                    model_name=device.model_name or "Unknown",
                    location=location,
                    udn=device.udn or "",
                )
                devices_found[usn] = dlna_device
                print(f"Found: {dlna_device.name}")

        except Exception as e:
            print(f"Failed to connect to {location}: {e}")

    await async_search(
        async_callback=on_response,
        timeout=timeout,
        search_target=SSDP_ST_ALL,
    )

    return list(devices_found.values())


async def _get_av_transport(device: DLNADevice):
    """Get AVTransport service from device."""
    requester = AiohttpRequester()
    factory = UpnpFactory(requester)
    upnp_device = await factory.async_create_device(device.location)

    av_transport = upnp_device.find_service(service_type=AVTRANSPORT_SERVICE_TYPE)
    if not av_transport:
        raise Exception("AVTransport service not found on device")

    return av_transport


async def play_url(device: DLNADevice, url: str) -> None:
    """Play a URL on a DLNA device.

    Args:
        device: DLNA device
        url: Media URL to play (http:// or file://)

    Raises:
        Exception: If playback fails
    """
    av_transport = await _get_av_transport(device)

    # Stop any current playback
    try:
        await av_transport.action("Stop").async_call(InstanceID=0)
    except:
        pass

    await av_transport.action("SetAVTransportURI").async_call(
        InstanceID=0,
        CurrentURI=url,
        CurrentURIMetaData="",
    )
    await av_transport.action("Play").async_call(InstanceID=0, Speed="1")
    print(f"Playback started: {url}")


async def stop(device: DLNADevice) -> None:
    """Stop playback on a DLNA device.

    Args:
        device: DLNA device
    """
    av_transport = await _get_av_transport(device)
    await av_transport.action("Stop").async_call(InstanceID=0)
    print("Playback stopped")


@dataclass
class PlaybackStatus:
    """Playback status information."""

    state: str  # PLAYING, STOPPED, PAUSED_PLAYBACK, etc.


async def get_status(device: DLNADevice) -> PlaybackStatus:
    """Get playback status from a DLNA device.

    Args:
        device: DLNA device

    Returns:
        PlaybackStatus object
    """
    av_transport = await _get_av_transport(device)

    try:
        info = await av_transport.action("GetTransportInfo").async_call(InstanceID=0)
        state = info.get("CurrentTransportState", "UNKNOWN")
        return PlaybackStatus(state=state)
    except Exception as e:
        return PlaybackStatus(state=f"ERROR: {e}")
