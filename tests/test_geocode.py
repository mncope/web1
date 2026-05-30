from land_system.geocode import Coordinate, parse_geocode_response


def test_parse_vworld_geocode_response() -> None:
    payload = {
        "response": {
            "status": "OK",
            "result": {"point": {"x": "126.95471242", "y": "36.856220258"}},
        }
    }

    assert parse_geocode_response(payload) == Coordinate(lon=126.95471242, lat=36.856220258)
