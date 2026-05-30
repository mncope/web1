from pathlib import Path

from land_system.geocode import Coordinate
from land_system.land_api import LandInfo
from land_system.map_builder import save_map


def test_save_map_creates_html_file(tmp_path: Path) -> None:
    output = tmp_path / "land_info_map.html"
    land_info = LandInfo(pnu="4420037031108200000", land_category="전", area_square_meters=1234.5)

    save_map(Coordinate(lon=126.95471242, lat=36.856220258), "충청남도 아산시 영인면 성내리 820", output, land_info=land_info)

    html = output.read_text(encoding="utf-8")
    assert output.exists()
    assert "충청남도 아산시 영인면 성내리 820" in html
    assert "4420037031108200000" in html
