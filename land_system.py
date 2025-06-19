import requests
import folium

ADDRESS = "충청남도 아산시 영인면 성내리 820"
VWORLD_API_KEY = "YOUR_VWORLD_API_KEY"
LAND_API_KEY = "YOUR_LAND_API_KEY"

def geocode_address(address: str) -> tuple[float, float]:
    """Return longitude and latitude for the given address using VWorld."""
    geocode_url = (
        "https://api.vworld.kr/req/address"
        f"?service=address&request=getcoord&format=json&type=PARCEL&address={address}&key={VWORLD_API_KEY}"
    )
    res = requests.get(geocode_url)
    res.raise_for_status()
    point = res.json()['response']['result']['point']
    return float(point['x']), float(point['y'])

def generate_pnu(sgg_code: str, bjd_code: str, main_num: int, sub_num: int = 0) -> str:
    """Generate a PNU code from region codes and lot numbers."""
    main = str(main_num).zfill(4)
    sub = str(sub_num).zfill(4)
    return sgg_code + bjd_code + main + sub

def fetch_land_info(pnu_code: str) -> dict:
    """Fetch land ledger information from the public data API."""
    land_url = (
        "https://apis.data.go.kr/1611000/nsdi/LandCharacteristicsService/attr/getLandCharacteristics"
        f"?serviceKey={LAND_API_KEY}&pnu={pnu_code}&format=json"
    )
    # res = requests.get(land_url)
    # res.raise_for_status()
    # return res.json()
    return {}

def build_map(lat: float, lon: float, address: str) -> folium.Map:
    """Create a folium map with a marker and satellite imagery."""
    m = folium.Map(location=[lat, lon], zoom_start=17)
    folium.TileLayer(
        tiles=f"https://api.vworld.kr/req/wmts/1.0.0/{VWORLD_API_KEY}/Satellite/{{z}}/{{y}}/{{x}}.jpeg",
        attr='VWorld Satellite',
        name='위성사진',
        overlay=True,
        control=True
    ).add_to(m)
    folium.Marker([lat, lon], popup=address).add_to(m)
    folium.LayerControl().add_to(m)
    return m

def main() -> None:
    lon, lat = geocode_address(ADDRESS)
    pnu_code = generate_pnu("44200", "10600", 820)
    print(f"PNU 코드: {pnu_code}")
    _ = fetch_land_info(pnu_code)
    m = build_map(lat, lon, ADDRESS)
    m.save("land_info_map.html")
    print("지도 파일이 land_info_map.html로 저장되었습니다.")

if __name__ == "__main__":
    main()
