from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .pnu import PNUError, validate_pnu


LAND_CHARACTERISTICS_URL = (
    "https://apis.data.go.kr/1611000/nsdi/LandCharacteristicsService/attr/getLandCharacteristics"
)


class LandAPIError(RuntimeError):
    """Raised for public land API request or response failures."""


class NoLandDataError(LandAPIError):
    """Raised when the public land API returns no usable record."""


@dataclass(frozen=True)
class LandInfo:
    pnu: str
    address_name: str | None = None
    land_category: str | None = None
    area_square_meters: float | None = None
    land_use: str | None = None
    terrain_height: str | None = None
    terrain_shape: str | None = None
    road_side: str | None = None
    standard_year: str | None = None
    raw: dict[str, Any] | None = None


def fetch_land_info(
    pnu: str,
    api_key: str,
    *,
    session: requests.Session | None = None,
    timeout: float = 10.0,
) -> LandInfo:
    """Fetch and normalize land-characteristics information from data.go.kr."""
    try:
        pnu = validate_pnu(pnu)
    except PNUError as exc:
        raise LandAPIError(str(exc)) from exc
    if not api_key:
        raise LandAPIError("LAND_API_KEY is required")

    client = session or requests.Session()
    response = client.get(
        LAND_CHARACTERISTICS_URL,
        params={
            "serviceKey": api_key,
            "pnu": pnu,
            "format": "json",
            "numOfRows": 10,
            "pageNo": 1,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return parse_land_response(payload, requested_pnu=pnu)


def parse_land_response(payload: dict[str, Any], *, requested_pnu: str) -> LandInfo:
    _raise_for_api_status(payload)
    items = _extract_items(payload)
    if not items:
        raise NoLandDataError(f"land API returned no data for pnu={requested_pnu}")

    item = items[0]
    if not isinstance(item, dict):
        raise LandAPIError("land API item has an unexpected format")

    item_pnu = str(item.get("pnu") or item.get("PNU") or requested_pnu)
    if item_pnu and item_pnu != requested_pnu:
        raise LandAPIError(f"land API returned pnu={item_pnu}, expected {requested_pnu}")

    return LandInfo(
        pnu=requested_pnu,
        address_name=_first_text(item, "ldCodeNm", "ldCodeNmFull", "addr", "address"),
        land_category=_first_text(item, "lndcgrCodeNm", "landCategory", "jimok"),
        area_square_meters=_first_float(item, "lndpclAr", "area", "parea"),
        land_use=_first_text(item, "ladUseSittnNm", "landUse", "prposArea1Nm"),
        terrain_height=_first_text(item, "tpgrphHgCodeNm", "terrainHeight"),
        terrain_shape=_first_text(item, "tpgrphFrmCodeNm", "terrainShape"),
        road_side=_first_text(item, "roadSideCodeNm", "roadSide"),
        standard_year=_first_text(item, "stdrYear", "year"),
        raw=item,
    )


def _raise_for_api_status(payload: dict[str, Any]) -> None:
    response = payload.get("response")
    if isinstance(response, dict):
        header = response.get("header")
        if isinstance(header, dict):
            code = str(header.get("resultCode", "00"))
            if code not in {"00", "0", "NORMAL_CODE"}:
                msg = header.get("resultMsg") or header.get("returnAuthMsg") or "public land API failed"
                raise LandAPIError(f"public land API error {code}: {msg}")
        status = str(response.get("status", "")).upper()
        if status and status not in {"OK", "SUCCESS"}:
            raise LandAPIError(f"public land API failed with status={status}")

    code = str(payload.get("resultCode", "00"))
    if code not in {"00", "0", "NORMAL_CODE"}:
        raise LandAPIError(f"public land API error {code}: {payload.get('resultMsg', 'unknown error')}")


def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    response = payload.get("response")
    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, dict):
            items = body.get("items")
            if isinstance(items, dict):
                return _as_list(items.get("item"))
            if isinstance(items, list):
                return items

        result = response.get("result")
        if isinstance(result, dict):
            features = result.get("featureCollection", {}).get("features") if isinstance(result.get("featureCollection"), dict) else None
            if isinstance(features, list):
                return [feature.get("properties", {}) for feature in features if isinstance(feature, dict)]
            for key in ("items", "item"):
                if key in result:
                    return _as_list(result[key])

    for key in ("items", "item", "data"):
        if key in payload:
            return _as_list(payload[key])
    return []


def _as_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def _first_text(item: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _first_float(item: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = item.get(key)
        if value in (None, ""):
            continue
        try:
            return float(str(value).replace(",", ""))
        except ValueError:
            continue
    return None
