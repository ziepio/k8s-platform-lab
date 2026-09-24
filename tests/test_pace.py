import pytest
from app.pace import PaceError, calculate, parse_duration

def test_parses_minutes_and_seconds():
    assert parse_duration("5:30") == 330

def test_parses_hours():
    assert parse_duration("1:30:00") == 5400

@pytest.mark.parametrize("bad", ["", "abc", "90:00:00:00", "5:75", "0:00", "-5:00"])
def test_rejects_nonsense(bad):
    with pytest.raises(PaceError):
        parse_duration(bad)

def test_half_marathon_in_two_hours():
    result = calculate(21.0975, "2:00:00")
    assert result.pace_label() == "5:41 /km"
    assert round(result.speed_kmh, 2) == 10.55

def test_rejects_zero_distance():
    with pytest.raises(PaceError):
        calculate(0, "30:00")
