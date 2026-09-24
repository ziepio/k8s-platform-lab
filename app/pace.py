from dataclasses import dataclass


class PaceError(ValueError):


@dataclass(frozen=True)
class Result:
    pace_seconds_per_km: float
    speed_kmh: float

    def pace_label(self) -> str:
        minutes, seconds = divmod(round(self.pace_seconds_per_km), 60)
        return f"{minutes}:{seconds:02d} /km"


def parse_duration(text: str) -> int:
    parts = text.strip().split(":")
    if len(parts) not in (2, 3):
        raise PaceError("Use MM:SS or HH:MM:SS")
    try:
        numbers = [int(p) for p in parts]
    except ValueError:
        raise PaceError("Duration must contain numbers only") from None
    if any(n < 0 for n in numbers):
        raise PaceError("Duration cannot be negative")
    if len(parts) == 2:
        minutes, seconds = numbers
        hours = 0
    else:
        hours, minutes, seconds = numbers
    if minutes > 59 or seconds > 59:
        raise PaceError("Minutes and seconds must be below 60")
    total = hours * 3600 + minutes * 60 + seconds
    if total == 0:
        raise PaceError("Duration must be greater than zero")
    return total


def calculate(distance_km: float, duration: str) -> Result:
    if distance_km <= 0:
        raise PaceError("Distance must be greater than zero")
    seconds = parse_duration(duration)
    pace = seconds / distance_km
    speed = distance_km / (seconds / 3600)
    return Result(pace_seconds_per_km=pace, speed_kmh=speed)
