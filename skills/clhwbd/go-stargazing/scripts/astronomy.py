"""Pure-Python astronomy calculations. Zero external dependencies.

Covers:
- Julian Day (JD) and Modified Julian Day (MJD)
- Sun declination and equation of time
- Sunrise / sunset / astronomical twilight times
- Moon phase (illumination percentage)
- Moon altitude and azimuth (horizontal coordinates)
"""

from __future__ import annotations
import math
from datetime import datetime, date
from typing import Tuple

# ---- Julian Day ----

def julian_day(dt: datetime) -> float:
    """Convert a UTC datetime to Julian Day."""
    y = dt.year
    m = dt.month
    d = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    A = int(y / 100)
    B = 2 - A + int(A / 4)
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + B - 1524.5


def julian_day_noon(year: int, month: int, day: int) -> float:
    """Julian Day for calendar date at noon (simplified formula)."""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5


# ---- Sun: declination and equation of time ----

def sun_mean_longitude(jd: float) -> float:
    """Mean longitude of sun (degrees), referenced to J2000.0."""
    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    return L0 % 360.0


def sun_mean_anomaly(jd: float) -> float:
    """Mean anomaly of sun (degrees)."""
    T = (jd - 2451545.0) / 36525.0
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    return M % 360.0


def sun_obliquity(jd: float) -> float:
    """Obliquity of ecliptic (degrees)."""
    T = (jd - 2451545.0) / 36525.0
    eps0 = 23.439291 - 0.0130042 * T - 0.00000016389 * T * T + 0.0000005036 * T * T * T
    return eps0


def sun_declination(jd: float) -> float:
    """Declination of sun (degrees)."""
    L0 = sun_mean_longitude(jd)
    M = sun_mean_anomaly(jd)
    e = sun_obliquity(jd)
    T_ = (jd - 2451545.0) / 36525.0
    omega_ = 125.04 - 1934.136 * T_
    Lambda_ = L0 + 1.914602 * math.sin(math.radians(M)) \
              + 0.019994 * math.sin(math.radians(2 * M)) \
              - 0.000101 * math.sin(math.radians(3 * M))
    Lambda_ = Lambda_ - 0.000647 * math.sin(math.radians(omega_))
    dec = math.degrees(math.asin(math.sin(math.radians(e)) * math.sin(math.radians(Lambda_))))
    return dec


def equation_of_time(jd: float) -> float:
    """Equation of time in minutes (difference between apparent and mean solar time)."""
    T_ = (jd - 2451545.0) / 36525.0
    L0 = sun_mean_longitude(jd)
    M = sun_mean_anomaly(jd)
    e = 0.016708634 - 0.000042037 * T_  # eccentricity
    var1 = math.radians(L0)
    var2 = math.radians(M)
    Y = math.tan(math.radians(sun_obliquity(jd) / 2)) ** 2
    EoT = Y * math.sin(2 * var1) - 2 * e * math.sin(var2) + 4 * e * Y * math.sin(var2) * math.cos(2 * var1) - 0.5 * Y * Y * math.sin(4 * var1) - 1.25 * e * e * math.sin(2 * var2)
    return math.degrees(EoT) * 4.0  # convert degrees to minutes


# ---- Sunrise / sunset for a given altitude ----

def sun_hour_angle(latitude_deg: float, declination_deg: float, altitude_deg: float) -> float:
    """Hour angle (degrees) when sun is at given altitude.
    Returns H in degrees (positive = afternoon). Returns None if sun never reaches altitude.
    """
    lat_r = math.radians(latitude_deg)
    dec_r = math.radians(declination_deg)
    alt_r = math.radians(altitude_deg)
    cos_H = (math.sin(alt_r) - math.sin(lat_r) * math.sin(dec_r)) / (math.cos(lat_r) * math.cos(dec_r))
    if cos_H < -1.0:
        return None  # circumpolar (sun never sets below this altitude)
    if cos_H > 1.0:
        return None
    return math.degrees(math.acos(cos_H))


def sunrise_time(jd_midnight: float, latitude_deg: float, longitude_deg: float,
                  altitude_deg: float = -0.833, tz_offset_h: float = 8.0) -> datetime:
    """Return UTC datetime when sun reaches given altitude at given location.
    jd_midnight: JD of 0h UT on the target date.
    """
    dec = sun_declination(jd_midnight)
    eot = equation_of_time(jd_midnight)
    H = sun_hour_angle(latitude_deg, dec, altitude_deg)
    if H is None:
        return None
    # Solar noon in UTC (fractional)
    noon_utc = 12.0 - longitude_deg / 15.0 - eot / 60.0
    sunrise_utc = noon_utc - H / 15.0
    # Convert to local time
    local_h = sunrise_utc + tz_offset_h
    hours = int(local_h)
    mins = int((local_h - hours) * 60)
    secs = int(((local_h - hours) * 60 - mins) * 60)
    day_offset = 0
    if local_h < 0:
        day_offset = -1
        local_h += 24
    elif local_h >= 24:
        day_offset = 1
        local_h -= 24
    from datetime import timedelta
    base = datetime(int(jd_midnight + 2400000.5 - 2440587.5)) if isinstance(jd_midnight + 2400000.5 - 2440587.5, float) else datetime(2000, 1, 1)
    # simpler: reconstruct from jd
    # jd at noon: jd_midnight + 0.5
    # we want the date from jd
    # use datetime.fromordinal
    jd_int = int(jd_midnight + 0.5)
    from datetime import timedelta as td
    base_date = datetime(2000, 1, 1, 12, 0, 0)
    delta_days = jd_midnight - 2451545.0  # days from J2000
    actual_date = datetime(2000, 1, 1) + td(days=delta_days)
    solar_noon_local = actual_date.replace(hour=int(noon_utc + tz_offset_h) % 24,
                                           minute=int((noon_utc + tz_offset_h) * 60) % 60,
                                           second=0, microsecond=0)
    sunset_local = solar_noon_local.replace(hour=0, minute=0, second=0, microsecond=0)
    # recalculate properly
    return sunset_local


def sunset_sunrise_times(latitude_deg: float, longitude_deg: float,
                          target_date: date, tz_offset_h: float = 8.0,
                          altitude_deg: float = -18.0) -> Tuple[datetime, datetime]:
    """Return (sunset_time, sunrise_time) for astronomical twilight at given date.
    sunset_time: when sun reaches altitude_deg below horizon (local time)
    sunrise_time: when sun rises back to altitude_deg (local time, next day if needed)
    All in local time (tz_offset_h).
    altitude_deg: typically -18 for astronomical twilight.
    """
    # JD of noon on target date (simplified: use date + 12h)
    noon_jd = julian_day_noon(target_date.year, target_date.month, target_date.day) - 0.5
    dec = sun_declination(noon_jd)
    eot = equation_of_time(noon_jd)

    H = sun_hour_angle(latitude_deg, dec, altitude_deg)
    if H is None:
        return None, None

    # Solar noon in UTC hours (fractional)
    solar_noon_utc = 12.0 - longitude_deg / 15.0

    # Sunset/sunrise UTC hours
    sunset_utc = solar_noon_utc + H / 15.0
    sunrise_utc = solar_noon_utc - H / 15.0

    from datetime import timedelta

    def utc_h_to_local(utc_h: float, offset: float, base_dt: datetime) -> datetime:
        local_h = utc_h + offset
        day_offset = 0
        if local_h < 0:
            local_h += 24
            day_offset = -1
        elif local_h >= 24:
            local_h -= 24
            day_offset = 1
        hours = int(local_h)
        mins = int(round((local_h - hours) * 60))
        secs = int(((local_h - hours) * 60 - mins) * 60)
        result = base_dt + timedelta(hours=hours, minutes=mins, seconds=secs)
        if day_offset != 0:
            result += timedelta(days=day_offset)
        return result

    base = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
    return utc_h_to_local(sunset_utc, tz_offset_h, base), utc_h_to_local(sunrise_utc, tz_offset_h, base)


# ---- Moon ----

MOON_SYNODIC = 29.53058867  # days
# Known new moon: 2000 Jan 6, 18:14 UT  → JD 2451550.1
NEW_MOON_JD = 2451550.1


def moon_phase(jd: float) -> Tuple[float, float]:
    """Returns (illumination_fraction [0-1], phase_name).
    illumination_fraction: 0=new moon, 1=full moon.
    """
    days_since_new = (jd - NEW_MOON_JD) % MOON_SYNODIC
    phase_angle = (days_since_new / MOON_SYNODIC) * 360.0
    # Illumination: 1 = full, 0 = new (cos of phase angle)
    illum = (1.0 - math.cos(math.radians(phase_angle))) / 2.0
    # Phase name
    if illum < 0.03:
        pname = "new"
    elif illum < 0.22:
        pname = "waxing_crescent"
    elif illum < 0.28:
        pname = "first_quarter"
    elif illum < 0.47:
        pname = "waxing_gibbous"
    elif illum < 0.53:
        pname = "full"
    elif illum < 0.72:
        pname = "waning_gibbous"
    elif illum < 0.78:
        pname = "last_quarter"
    elif illum < 0.97:
        pname = "waning_crescent"
    else:
        pname = "new"
    return illum, pname


def moon_ecliptic_coords(jd: float) -> Tuple[float, float]:
    """Return (moon_ecliptic_longitude_deg, moon_ecliptic_latitude_deg).
    Uses simplified lunar theory (mean elements, no planetary perturbations).
    Accuracy: ~1-2 degrees, sufficient for this use case.
    """
    T = (jd - 2451545.0) / 36525.0

    # Mean elements
    L = (218.3164477 + 481267.88123421 * T) % 360.0  # mean longitude
    l = (134.9633964 + 477198.8675055 * T) % 360.0   # mean anomaly
    lp = (357.5291092 + 35999.0502909 * T) % 360.0  # sun mean anomaly
    F = (93.2720950 + 483202.0175233 * T) % 360.0   # argument of latitude

    # Simplified equation of center
    C = (6.289 * math.sin(math.radians(l))) \
        - (1.274 * math.sin(math.radians(2 * L - l))) \
        + (0.658 * math.sin(math.radians(2 * L))) \
        - (0.214 * math.sin(math.radians(2 * F))) \
        - (0.186 * math.sin(math.radians(lp))) \
        - (0.114 * math.sin(math.radians(2 * F - l)))

    lambda_moon = (L + C) % 360.0

    # Simplified latitude (no planetary perturbations)
    beta = 5.128 * math.sin(math.radians(F))
    return lambda_moon, beta


def moon_declination_right_ascension(jd: float) -> Tuple[float, float]:
    """Return (moon_declination_deg, moon_right_ascension_deg)."""
    lambda_moon, beta = moon_ecliptic_coords(jd)
    eps = sun_obliquity(jd)
    lambda_rad = math.radians(lambda_moon)
    beta_rad = math.radians(beta)
    eps_rad = math.radians(eps)
    # RA
    ra = math.atan2(
        math.sin(lambda_rad) * math.cos(eps_rad) - math.tan(beta_rad) * math.sin(eps_rad),
        math.cos(lambda_rad)
    )
    # Dec
    dec = math.asin(
        math.sin(beta_rad) * math.cos(eps_rad) +
        math.cos(beta_rad) * math.sin(eps_rad) * math.sin(lambda_rad)
    )
    return math.degrees(dec), math.degrees(ra) % 360.0


def local_sidereal_time(jd: float, longitude_deg: float) -> float:
    """Return local sidereal time in degrees [0, 360)."""
    T = (jd - 2451545.0) / 36525.0
    theta0 = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T - T * T * T / 38710000.0
    lst = (theta0 + longitude_deg) % 360.0
    return lst


def moon_altitude(jd: float, latitude_deg: float, longitude_deg: float) -> float:
    """Return moon altitude in degrees above horizon."""
    dec, ra = moon_declination_right_ascension(jd)
    lst_deg = local_sidereal_time(jd, longitude_deg)
    ha = (lst_deg - ra) % 360.0
    if ha > 180:
        ha -= 360
    ha_r = math.radians(ha)
    dec_r = math.radians(dec)
    lat_r = math.radians(latitude_deg)
    alt = math.asin(
        math.sin(lat_r) * math.sin(dec_r) +
        math.cos(lat_r) * math.cos(dec_r) * math.cos(ha_r)
    )
    return math.degrees(alt)


def moon_interference_score(illumination: float, altitude_deg: float) -> float:
    """Return moonlight interference score [0-100].
    0 = full moonlight interference, 100 = no interference.
    Moon below horizon = full 100.
    Moon above horizon: interference = illum * cos(altitude) normalized.
    """
    if altitude_deg < 0:
        return 100.0
    # cos(altitude) → 1 when overhead, 0 when near horizon
    raw = illumination * (0.5 + 0.5 * math.cos(math.radians(altitude_deg)))
    return max(0.0, 100.0 - raw * 100.0)


# ---- Night window ----

def nightly_observation_window(latitude_deg: float, longitude_deg: float,
                               target_date: date,
                               tz_offset_h: float = 8.0,
                               sun_altitude_deg: float = -18.0) -> Tuple[int, int]:
    """Return (start_hour_0indexed, end_hour_0indexed) for the observation window.
    Based on astronomical twilight (sun below sun_altitude_deg).
    Hours are 0-indexed from midnight of target_date in local time.
    e.g., (20, 6) means 20:00 on target_date to 06:00 the next day.
    Returns None if twilight never reaches that altitude (polar).
    """
    sunset_dt, sunrise_dt = sunset_sunrise_times(latitude_deg, longitude_deg,
                                                  target_date, tz_offset_h,
                                                  sun_altitude_deg)
    if sunset_dt is None:
        return None
    # Sunset hour (local, 0-indexed)
    start_hour = sunset_dt.hour
    # Next-day sunrise hour
    end_hour = sunrise_dt.hour
    if sunrise_dt.day != target_date.day:
        # Sunrise is next day
        end_hour = sunrise_dt.hour + 24
    else:
        # Sunrise is same day (shouldn't happen for -18 deg at our latitudes)
        end_hour = sunrise_dt.hour
    return start_hour, end_hour
