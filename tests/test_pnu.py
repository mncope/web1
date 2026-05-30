import pytest

from land_system.pnu import PNUError, generate_pnu, generate_pnu_from_region_codes, parse_lot_number, validate_pnu


def test_generate_pnu_from_legal_dong_code() -> None:
    assert generate_pnu("4420037031", 820) == "4420037031108200000"


def test_generate_pnu_from_split_region_codes() -> None:
    assert generate_pnu_from_region_codes("44200", "37031", 820, 7) == "4420037031108200007"


def test_generate_pnu_mountain_flag() -> None:
    assert generate_pnu("4420037031", 8, 2, mountain=True) == "4420037031200080002"


def test_validate_pnu_rejects_invalid_length() -> None:
    with pytest.raises(PNUError):
        validate_pnu("442003703108200000")


def test_parse_lot_number_from_address() -> None:
    assert parse_lot_number("충청남도 아산시 영인면 성내리 820-3") == (820, 3, False)
