from __future__ import annotations

import re


PNU_PATTERN = re.compile(r"^\d{19}$")
LOT_NUMBER_PATTERN = re.compile(r"(?:산\s*)?(?P<main>\d{1,4})(?:-(?P<sub>\d{1,4}))?\s*(?:번지)?\s*$")


class PNUError(ValueError):
    """Raised when a PNU or its source parts are invalid."""


def generate_pnu(
    legal_dong_code: str,
    main_num: int | str,
    sub_num: int | str = 0,
    *,
    mountain: bool = False,
) -> str:
    """Generate a 19-digit PNU from manual legal-dong and lot-number parts.

    PNU format: legal-dong code(10) + land type(1) + main lot(4) + sub lot(4).
    This module intentionally stays in manual mode. Deriving legal-dong codes from
    free-form addresses should be backed by an authoritative API or code table.
    """
    legal_dong_code = _digits(legal_dong_code, "legal_dong_code")
    if len(legal_dong_code) != 10:
        raise PNUError("legal_dong_code must be exactly 10 digits")

    main = _format_lot_number(main_num, "main_num")
    sub = _format_lot_number(sub_num, "sub_num")
    land_type = "2" if mountain else "1"
    return f"{legal_dong_code}{land_type}{main}{sub}"


def generate_pnu_from_region_codes(
    sgg_code: str,
    bjd_code: str,
    main_num: int | str,
    sub_num: int | str = 0,
    *,
    mountain: bool = False,
) -> str:
    """Generate a PNU from split region codes in manual mode."""
    sgg_code = _digits(sgg_code, "sgg_code")
    bjd_code = _digits(bjd_code, "bjd_code")
    if len(sgg_code) != 5:
        raise PNUError("sgg_code must be exactly 5 digits")
    if len(bjd_code) != 5:
        raise PNUError("bjd_code must be exactly 5 digits")
    return generate_pnu(f"{sgg_code}{bjd_code}", main_num, sub_num, mountain=mountain)


def validate_pnu(pnu: str) -> str:
    pnu = _digits(pnu, "pnu")
    if not PNU_PATTERN.match(pnu):
        raise PNUError("pnu must be exactly 19 digits")
    return pnu


def parse_lot_number(address: str) -> tuple[int, int, bool]:
    """Extract the final parcel lot number from a Korean parcel-style address."""
    text = address.strip()
    match = LOT_NUMBER_PATTERN.search(text)
    if not match:
        raise PNUError("could not parse lot number from address; pass --main-number explicitly")
    mountain = text[max(0, match.start() - 3) : match.start()].strip().endswith("산")
    main = int(match.group("main"))
    sub = int(match.group("sub") or 0)
    return main, sub, mountain


def _format_lot_number(value: int | str, name: str) -> str:
    text = _digits(str(value), name)
    if len(text) > 4:
        raise PNUError(f"{name} must be 1 to 4 digits")
    number = int(text)
    if number < 0:
        raise PNUError(f"{name} must be non-negative")
    return f"{number:04d}"


def _digits(value: str, name: str) -> str:
    text = str(value).strip()
    if not text.isdigit():
        raise PNUError(f"{name} must contain digits only")
    return text
