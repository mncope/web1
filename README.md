# web1

## Land Information Mapping

This project generates an HTML map for a Korean parcel address. It uses VWorld for geocoding and, in real API mode, the public NSDI land characteristics API for parcel-level land information.

## Required API Keys

Create a `.env` file from `.env.example` and set:

- `VWORLD_API_KEY`: required for geocoding and VWorld satellite tiles.
- `LAND_API_KEY`: required for real land API mode.
- `LEGAL_DONG_CODE`: optional 10-digit legal-dong code used for manual PNU generation.

Do not commit real API keys.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your API keys.

## Example Command

Demo mode geocodes the address and writes a map without calling the land API:

```bash
python -m land_system.cli "충청남도 아산시 영인면 성내리 820" --output land_info_map.html --demo
```

Real API mode also calls the public land characteristics API. PNU generation is currently manual: provide `LEGAL_DONG_CODE` in `.env` or pass `--legal-dong-code`.

```bash
python -m land_system.cli "충청남도 아산시 영인면 성내리 820" --output land_info_map.html --legal-dong-code 4420037031
```

## Expected Output

The command writes `land_info_map.html`, centered on the parcel coordinates, with a marker popup. In real API mode, the popup includes normalized land fields such as PNU, land category, area, and land use when the public API returns them.

## Demo Mode vs Real API Mode

- Demo mode (`--demo`) calls VWorld geocoding only and is useful for checking setup and map generation.
- Real API mode calls both VWorld and the public land API. It requires `LAND_API_KEY` and a reliable legal-dong code for PNU generation.

## Known Limitations

- PNU generation is manual. The app does not yet derive legal-dong codes from arbitrary addresses.
- Public API response fields can vary by endpoint/version; the parser normalizes common land-characteristics fields and keeps the raw record for inspection.
- Tests mock API responses and do not call live services.

## Next Roadmap

- Add authoritative legal-dong-code lookup.
- Add richer land API field coverage and UI formatting.
- Add optional live smoke tests gated by environment variables.
- Package the CLI as an installable console script.
