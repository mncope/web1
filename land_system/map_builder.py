from __future__ import annotations

from pathlib import Path

import folium

from .geocode import Coordinate
from .land_api import LandInfo


def build_map(
    coordinate: Coordinate,
    address: str,
    *,
    land_info: LandInfo | None = None,
    vworld_api_key: str | None = None,
) -> folium.Map:
    """Create a Folium map centered on the parcel."""
    fmap = folium.Map(location=[coordinate.lat, coordinate.lon], zoom_start=17)
    if vworld_api_key:
        folium.TileLayer(
            tiles=f"https://api.vworld.kr/req/wmts/1.0.0/{vworld_api_key}/Satellite/{{z}}/{{y}}/{{x}}.jpeg",
            attr="VWorld Satellite",
            name="VWorld Satellite",
            overlay=True,
            control=True,
        ).add_to(fmap)
    folium.Marker(
        [coordinate.lat, coordinate.lon],
        popup=_popup_html(address, land_info),
        tooltip=address,
    ).add_to(fmap)
    folium.LayerControl().add_to(fmap)
    return fmap


def save_map(
    coordinate: Coordinate,
    address: str,
    output_path: str | Path,
    *,
    land_info: LandInfo | None = None,
    vworld_api_key: str | None = None,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    build_map(coordinate, address, land_info=land_info, vworld_api_key=vworld_api_key).save(str(output))
    return output


def _popup_html(address: str, land_info: LandInfo | None) -> str:
    rows = [f"<b>{address}</b>"]
    if land_info:
        if land_info.land_category:
            rows.append(f"Land category: {land_info.land_category}")
        if land_info.area_square_meters is not None:
            rows.append(f"Area: {land_info.area_square_meters:g} m2")
        if land_info.land_use:
            rows.append(f"Land use: {land_info.land_use}")
        rows.append(f"PNU: {land_info.pnu}")
    return "<br>".join(rows)
