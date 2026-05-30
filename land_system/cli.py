from __future__ import annotations

import argparse
from pathlib import Path

from .config import ConfigurationError, load_settings, require_api_key
from .geocode import geocode_address
from .land_api import LandAPIError, fetch_land_info
from .map_builder import save_map
from .pnu import PNUError, generate_pnu, parse_lot_number


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = load_settings()

    try:
        vworld_key = require_api_key(settings.vworld_api_key, "VWORLD_API_KEY")
        coordinate = geocode_address(args.address, vworld_key)
        land_info = None

        if not args.demo:
            legal_dong_code = args.legal_dong_code or settings.default_legal_dong_code
            if not legal_dong_code:
                raise ConfigurationError(
                    "LEGAL_DONG_CODE or --legal-dong-code is required for real land API mode. "
                    "Use --demo to generate a map without land API data."
                )
            main_num, sub_num, parsed_mountain = parse_lot_number(args.address)
            pnu = generate_pnu(
                legal_dong_code,
                args.main_number if args.main_number is not None else main_num,
                args.sub_number if args.sub_number is not None else sub_num,
                mountain=args.mountain or parsed_mountain,
            )
            land_info = fetch_land_info(pnu, require_api_key(settings.land_api_key, "LAND_API_KEY"))

        output = save_map(
            coordinate,
            args.address,
            Path(args.output),
            land_info=land_info,
            vworld_api_key=vworld_key,
        )
    except (ConfigurationError, LandAPIError, PNUError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(f"Saved map to {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a land information map for a Korean parcel address.")
    parser.add_argument("address", help="Parcel address, e.g. '충청남도 아산시 영인면 성내리 820'")
    parser.add_argument("--output", default="land_info_map.html", help="Output HTML file path")
    parser.add_argument("--demo", action="store_true", help="Skip the public land API call and generate a geocoded map only")
    parser.add_argument("--legal-dong-code", help="10-digit legal-dong code used for manual PNU generation")
    parser.add_argument("--main-number", type=int, help="Main lot number override")
    parser.add_argument("--sub-number", type=int, default=None, help="Sub lot number override")
    parser.add_argument("--mountain", action="store_true", help="Set PNU mountain/forest flag")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
