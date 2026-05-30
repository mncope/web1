from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


VWORLD_GEOCODE_URL = "https://api.vworld.kr/req/address"


class GeocodingError(RuntimeError):
    """Raised when VWorld cannot geocode the address."""


@dataclass(frozen=True)
class Coordinate:
    lon: float
    lat: float


def geocode_address(
    address: str,
    api_key: str,
    *,
    session: requests.Session | None = None,
    timeout: float = 10.0,
) -> Coordinate:
    """Return longitude and latitude for a parcel address using VWorld."""
    if not address.strip():
        raise GeocodingError("address is required")
    if not api_key:
        raise GeocodingError("VWORLD_API_KEY is required")

    client = session or requests.Session()
    response = client.get(
        VWORLD_GEOCODE_URL,
        params={
            "service": "address",
            "request": "getcoord",
            "format": "json",
            "type": "PARCEL",
            "address": address,
            "key": api_key,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return parse_geocode_response(payload)


def parse_geocode_response(payload: dict[str, Any]) -> Coordinate:
    response = payload.get("response")
    if not isinstance(response, dict):
        raise GeocodingError("VWorld response is missing 'response'")

    status = str(response.get("status", "")).upper()
    if status and status != "OK":
        message = response.get("error", {}).get("text") if isinstance(response.get("error"), dict) else None
        raise GeocodingError(message or f"VWorld geocoding failed with status={status}")

    try:
        point = response["result"]["point"]
        lon = float(point["x"])
        lat = float(point["y"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GeocodingError("VWorld response does not contain a valid coordinate point") from exc

    return Coordinate(lon=lon, lat=lat)
