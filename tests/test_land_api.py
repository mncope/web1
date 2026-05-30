import pytest

from land_system.land_api import LandAPIError, NoLandDataError, parse_land_response


PNU = "4420037031108200000"


def test_parse_public_land_api_response() -> None:
    payload = {
        "response": {
            "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE."},
            "body": {
                "items": {
                    "item": {
                        "pnu": PNU,
                        "ldCodeNm": "충청남도 아산시 영인면 성내리",
                        "lndcgrCodeNm": "전",
                        "lndpclAr": "1234.5",
                        "ladUseSittnNm": "농경지",
                        "tpgrphHgCodeNm": "평지",
                        "tpgrphFrmCodeNm": "사다리",
                        "roadSideCodeNm": "세로",
                        "stdrYear": "2024",
                    }
                }
            },
        }
    }

    result = parse_land_response(payload, requested_pnu=PNU)

    assert result.pnu == PNU
    assert result.address_name == "충청남도 아산시 영인면 성내리"
    assert result.land_category == "전"
    assert result.area_square_meters == 1234.5
    assert result.land_use == "농경지"


def test_parse_public_land_api_error_status() -> None:
    payload = {"response": {"header": {"resultCode": "30", "resultMsg": "SERVICE KEY IS NOT REGISTERED"}}}

    with pytest.raises(LandAPIError):
        parse_land_response(payload, requested_pnu=PNU)


def test_parse_public_land_api_no_data() -> None:
    payload = {"response": {"header": {"resultCode": "00"}, "body": {"items": {}}}}

    with pytest.raises(NoLandDataError):
        parse_land_response(payload, requested_pnu=PNU)
