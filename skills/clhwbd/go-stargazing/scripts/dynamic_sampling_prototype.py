#!/usr/bin/env python3
"""Dynamic sampling prototype for go-stargazing.

Current prototype capabilities:
- generate sampling points inside simple region bounding boxes
- optional polygon-based point filtering (GeoJSON file or JSON string)
- stage-1 coarse filter on cloud_cover (mock or real Open-Meteo)
- stage-2 lightweight scoring on humidity / visibility / wind + moon factor
- dedupe near-border points across provinces
- cluster nearby high-score points into more natural regional results
- basic query budget + bounded concurrency
"""

from __future__ import annotations

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import hashlib
import json
import math
import ssl
import subprocess
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:
    from scripts.astronomy import (
        julian_day,
        moon_phase,
        moon_altitude,
        moon_interference_score,
        sunset_sunrise_times,
        nightly_observation_window,
    )
except ImportError:
    from astronomy import (
        julian_day,
        moon_phase,
        moon_altitude,
        moon_interference_score,
        sunset_sunrise_times,
        nightly_observation_window,
    )

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
# Open-Meteo hourly forecast window (days from today)
OPEN_METEO_HOURLY_WINDOW_DAYS = 16
DEFAULT_PROVINCE_BOUNDARIES = Path(__file__).resolve().parent.parent / "data" / "china-provinces-full.geojson"
DEFAULT_PREFECTURE_BOUNDARIES = Path(__file__).resolve().parent.parent / "data" / "china-prefecture-level.geojson"

# Canonical built-in national scan preset used when the user asks a national question
# and no explicit boxes are provided. Keep this broad enough to cover west/north key regions
# without pretending a partial subset is "the whole country".
NATIONAL_SCOPE_BOXES = [
    {"province": "新疆", "min_lat": 34.3, "max_lat": 49.1, "min_lng": 73.8, "max_lng": 96.2},
    {"province": "西藏", "min_lat": 26.5, "max_lat": 36.5, "min_lng": 73.4, "max_lng": 99.1},
    {"province": "青海", "min_lat": 31.6, "max_lat": 39.2, "min_lng": 89.4, "max_lng": 103.1},
    {"province": "甘肃", "min_lat": 32.6, "max_lat": 42.8, "min_lng": 92.2, "max_lng": 108.7},
    {"province": "内蒙古", "min_lat": 37.4, "max_lat": 53.5, "min_lng": 97.2, "max_lng": 126.1},
    {"province": "宁夏", "min_lat": 35.2, "max_lat": 39.4, "min_lng": 104.2, "max_lng": 107.7},
    {"province": "山西", "min_lat": 34.6, "max_lat": 40.8, "min_lng": 110.2, "max_lng": 114.6},
    {"province": "河北", "min_lat": 36.0, "max_lat": 42.6, "min_lng": 113.5, "max_lng": 119.9},
]

Coordinate = Tuple[float, float]  # (lng, lat)
PolygonRing = List[Coordinate]
MultiPolygon = List[List[PolygonRing]]


@dataclass
class BoundingBox:
    name: str
    province: str
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


@dataclass
class SamplePoint:
    id: str
    province: str
    scope_name: str
    lat: float
    lng: float
    weather_model: Optional[str] = None
    cloud_cover: Optional[float] = None
    humidity: Optional[float] = None
    visibility_m: Optional[float] = None
    wind_speed: Optional[float] = None
    moon_factor: Optional[float] = None
    elevation_m: Optional[float] = None
    # Nightly aggregation (computed over astronomical twilight window)
    night_avg_cloud: Optional[float] = None
    night_worst_cloud: Optional[float] = None
    night_avg_humidity: Optional[float] = None
    night_avg_visibility: Optional[float] = None
    night_avg_wind: Optional[float] = None
    moon_interference: Optional[float] = None  # 0=强干扰, 100=无干扰
    usable_hours: Optional[float] = None
    longest_usable_streak_hours: Optional[float] = None
    best_window_start: Optional[str] = None
    best_window_end: Optional[str] = None
    best_window_segment: Optional[str] = None
    cloud_stddev: Optional[float] = None
    cloud_stability: Optional[str] = None
    worst_cloud_segment: Optional[str] = None
    stage1_status: str = "pending"
    merged_into: Optional[str] = None
    weather_source: Optional[str] = None
    final_score: Optional[float] = None
    score_breakdown: Optional[dict] = None


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def deterministic_pct(seed_text: str) -> float:
    h = hashlib.md5(seed_text.encode()).hexdigest()
    return float(int(h[:8], 16) % 101)


def deterministic_value(seed_text: str, lower: float, upper: float) -> float:
    h = hashlib.md5(seed_text.encode()).hexdigest()
    ratio = (int(h[:8], 16) % 10000) / 10000.0
    return lower + (upper - lower) * ratio


def safe_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def parse_boxes(payload: str) -> List[BoundingBox]:
    data = json.loads(payload)
    return [BoundingBox(name=row.get("name") or row["province"], province=row["province"], min_lat=float(row["min_lat"]), max_lat=float(row["max_lat"]), min_lng=float(row["min_lng"]), max_lng=float(row["max_lng"])) for row in data]


def load_scope_preset(name: str) -> List[BoundingBox]:
    if name == "national":
        return [
            BoundingBox(name=row.get("name") or row["province"], province=row["province"], min_lat=float(row["min_lat"]), max_lat=float(row["max_lat"]), min_lng=float(row["min_lng"]), max_lng=float(row["max_lng"]))
            for row in NATIONAL_SCOPE_BOXES
        ]
    raise ValueError(f"Unknown scope preset: {name}")


def parse_target_datetime(value: Optional[str]) -> datetime:
    if value:
        return datetime.fromisoformat(value)
    return datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def moon_factor(target_dt: datetime, mode: str) -> float:
    day = target_dt.day
    cycle = ((day - 1) % 29) / 29.0
    illum = 1.0 - abs(cycle - 0.5) * 2
    return round((illum if mode == "moon" else 1 - illum) * 100, 2)


def point_in_ring(lng: float, lat: float, ring: PolygonRing) -> bool:
    inside = False
    n = len(ring)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        intersects = ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


def point_in_polygon(lng: float, lat: float, polygon: List[PolygonRing]) -> bool:
    if not polygon:
        return False
    if not point_in_ring(lng, lat, polygon[0]):
        return False
    for hole in polygon[1:]:
        if point_in_ring(lng, lat, hole):
            return False
    return True


def point_in_multipolygon(lng: float, lat: float, mp: MultiPolygon) -> bool:
    return any(point_in_polygon(lng, lat, poly) for poly in mp)


def normalize_geometry(geometry: dict) -> Optional[MultiPolygon]:
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if gtype == "Polygon":
        return [coords]
    if gtype == "MultiPolygon":
        return coords
    return None  # skip unsupported geometry types


def normalize_region_name(name: str) -> str:
    text = str(name).strip()
    for suffix in ["特别行政区", "壮族自治区", "回族自治区", "维吾尔自治区", "自治州", "地区", "盟", "自治区", "省", "市"]:
        if text.endswith(suffix):
            text = text[: -len(suffix)]
            break
    return text.strip()


def feature_name(feature: dict) -> Optional[str]:
    props = feature.get("properties", {}) or {}
    for key in ["name", "NAME", "province", "admin", "region"]:
        if props.get(key):
            return str(props[key])
    return None


def load_polygons(polygons_json: Optional[str], polygons_file: Optional[str]) -> Tuple[Dict[str, MultiPolygon], Dict[str, MultiPolygon]]:
    """Load two-level boundaries: (province_polygons, prefecture_polygons).
    Auto-loads bundled defaults if no explicit path given.
    """
    province_polygons: Dict[str, MultiPolygon] = {}
    prefecture_polygons: Dict[str, MultiPolygon] = {}

    def _load_single(path: str, polygons_dict: Dict[str, MultiPolygon]) -> None:
        try:
            raw = Path(path).read_text()
        except Exception:
            return
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("type") == "FeatureCollection":
            for feat in data.get("features", []):
                name = feature_name(feat)
                if not name:
                    continue
                geom = normalize_geometry(feat.get("geometry", {}))
                if geom is None:
                    continue
                polygons_dict[name] = geom
                polygons_dict[normalize_region_name(name)] = geom
        elif isinstance(data, dict) and data.get("type") == "Feature":
            name = feature_name(data) or "default"
            geom = normalize_geometry(data.get("geometry", {}))
            if geom:
                polygons_dict[name] = geom
                polygons_dict[normalize_region_name(name)] = geom
        elif isinstance(data, dict) and "geometry" not in data:
            for key, geom in data.items():
                if isinstance(geom, dict) and geom.get("type") in {"Polygon", "MultiPolygon"}:
                    mg = normalize_geometry(geom)
                    if mg:
                        polygons_dict[key] = mg
                        polygons_dict[normalize_region_name(key)] = mg

    # Province level: explicit file > explicit json > bundled default
    if polygons_file:
        _load_single(polygons_file, province_polygons)
    elif polygons_json:
        try:
            data = json.loads(polygons_json)
            tmp: Dict[str, MultiPolygon] = {}
            # inline load into tmp then merge
            def _inline_load(jdata, tgt):
                if isinstance(jdata, dict) and jdata.get("type") == "FeatureCollection":
                    for feat in jdata.get("features", []):
                        name = feature_name(feat)
                        if not name:
                            continue
                        geom = normalize_geometry(feat.get("geometry", {}))
                        if geom is None:
                            continue
                        tgt[name] = geom
                        tgt[normalize_region_name(name)] = geom
            _inline_load(data, province_polygons)
        except Exception:
            pass
    elif DEFAULT_PROVINCE_BOUNDARIES.exists():
        _load_single(str(DEFAULT_PROVINCE_BOUNDARIES), province_polygons)

    # Prefecture level: bundled default (no external file / json support yet)
    if DEFAULT_PREFECTURE_BOUNDARIES.exists():
        _load_single(str(DEFAULT_PREFECTURE_BOUNDARIES), prefecture_polygons)

    return province_polygons, prefecture_polygons


def _fetch_ali_geo_via_curl(adcode: str) -> Optional[dict]:
    """Fetch county/banner-level GeoJSON for a given province adcode via curl (SSL workaround)."""
    url = f"https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json"
    try:
        out = subprocess.check_output(
            ["curl", "-Lks", "--http1.1", "--retry", "2", "--retry-delay", "1", url],
            text=True, timeout=30,
        )
        return json.loads(out)
    except Exception:
        return None


def load_county_polygons(province_adcodes: List[str]) -> Dict[str, MultiPolygon]:
    """Load county/banner polygons for the given province adcode list.
    Falls back gracefully if a fetch fails.
    """
    county_polygons: Dict[str, MultiPolygon] = {}
    for adcode in province_adcodes:
        data = _fetch_ali_geo_via_curl(adcode)
        if not data:
            continue
        for feat in data.get("features", []):
            name = feature_name(feat)
            if not name:
                continue
            geom = normalize_geometry(feat.get("geometry", {}))
            if geom is None:
                continue
            county_polygons[name] = geom
            county_polygons[normalize_region_name(name)] = geom
    return county_polygons


def filter_points_by_polygon(
    points: List[SamplePoint],
    province_polygons: Dict[str, MultiPolygon],
    prefecture_polygons: Dict[str, MultiPolygon],
) -> List[SamplePoint]:
    if not province_polygons and not prefecture_polygons:
        return points
    kept: List[SamplePoint] = []
    for p in points:
        geom = None
        # 1. Try prefecture-level first (more specific)
        if prefecture_polygons:
            geom = (
                prefecture_polygons.get(p.scope_name)
                or prefecture_polygons.get(normalize_region_name(p.scope_name))
            )
        # 2. Fall back to province-level
        if geom is None and province_polygons:
            geom = (
                province_polygons.get(p.province)
                or province_polygons.get(normalize_region_name(p.province))
                or province_polygons.get(p.scope_name)
                or province_polygons.get(normalize_region_name(p.scope_name))
                or province_polygons.get("default")
            )
        if geom is None:
            # No polygon matched this point; keep it instead of over-filtering.
            kept.append(p)
            continue
        if point_in_multipolygon(p.lng, p.lat, geom):
            kept.append(p)
    return kept


def generate_grid_points(box: BoundingBox, target_count: int) -> List[SamplePoint]:
    if target_count <= 0:
        return []
    lat_span = max(box.max_lat - box.min_lat, 0.1)
    lng_span = max(box.max_lng - box.min_lng, 0.1)
    ratio = max(0.2, min(5.0, lng_span / lat_span))
    rows = max(1, round(math.sqrt(target_count / ratio)))
    cols = max(1, math.ceil(target_count / rows))
    lat_step = lat_span / rows
    lng_step = lng_span / cols

    points: List[SamplePoint] = []
    idx = 1
    for r in range(rows):
        for c in range(cols):
            if len(points) >= target_count:
                break
            lat = box.min_lat + (r + 0.5) * lat_step
            lng = box.min_lng + (c + 0.5) * lng_step
            points.append(SamplePoint(id=f"{box.province}-{idx}", province=box.province, scope_name=box.name, lat=round(lat, 5), lng=round(lng, 5)))
            idx += 1
    return points


def classify_cloud(point: SamplePoint, mode: str) -> str:
    # Prefer nightly average cloud for coarse filtering; fall back to snapshot cloud_cover.
    c = point.night_avg_cloud if point.night_avg_cloud is not None else point.cloud_cover
    if c is None:
        return "drop"
    if mode == "moon":
        return "pass" if c <= 50 else "edge" if c <= 65 else "drop"
    return "pass" if c <= 35 else "edge" if c <= 50 else "drop"


def coarse_filter(points: Iterable[SamplePoint], mode: str) -> List[SamplePoint]:
    out: List[SamplePoint] = []
    for p in points:
        p.stage1_status = classify_cloud(p, mode)
        if p.stage1_status in {"pass", "edge"}:
            out.append(p)
    return out


def score_cloud(c: Optional[float]) -> float:
    return 0.0 if c is None else max(0.0, min(100.0, 100.0 - c * 1.6))


def score_humidity(h: Optional[float]) -> float:
    if h is None:
        return 0.0
    if h <= 40:
        return 100.0
    if h >= 95:
        return 0.0
    return max(0.0, 100.0 - (h - 40) / 55.0 * 100.0)


def score_visibility(v_m: Optional[float]) -> float:
    if v_m is None:
        return 0.0
    return max(0.0, min(100.0, (v_m / 1000.0) / 24.0 * 100.0))


def score_wind(w: Optional[float]) -> float:
    if w is None:
        return 0.0
    if w <= 2:
        return 100.0
    if w >= 12:
        return 0.0
    return max(0.0, 100.0 - (w - 2) / 10.0 * 100.0)


def is_usable_observation_hour(cloud: Optional[float], wind_kmh: Optional[float], moon_interference: Optional[float]) -> bool:
    """Heuristic for whether an hour is actually worth shooting.
    Designed for stargazing / milky-way style use.
    """
    if cloud is None:
        return False
    if cloud > 20:
        return False
    if wind_kmh is not None and wind_kmh > 28:
        return False
    if moon_interference is not None and moon_interference < 55:
        return False
    return True


def longest_true_streak(flags: List[bool]) -> int:
    best = cur = 0
    for x in flags:
        if x:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def sample_stddev(values: List[float]) -> Optional[float]:
    if not values:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))


def classify_cloud_stability(stddev: Optional[float]) -> Optional[str]:
    if stddev is None:
        return None
    if stddev <= 10:
        return "stable"
    if stddev <= 20:
        return "mixed"
    return "volatile"


def segment_name(rel_hour: int) -> str:
    if rel_hour <= 22:
        return "前半夜"
    if rel_hour <= 26:
        return "中夜"
    return "后半夜"


def best_true_window(times: List[str], flags: List[bool], rel_hours: List[int]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    best_start = best_end = None
    best_len = cur_start = None
    cur_len = 0
    for i, ok in enumerate(flags):
        if ok:
            if cur_start is None:
                cur_start = i
                cur_len = 1
            else:
                cur_len += 1
            if best_len is None or cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
                best_end = i
        else:
            cur_start = None
            cur_len = 0
    if best_start is None or best_end is None:
        return None, None, None

    # Use relative night hours instead of raw ISO timestamps, to avoid timezone/date rendering drift.
    start_hour = rel_hours[best_start] % 24
    end_hour = (rel_hours[best_end] + 1) % 24
    start_ts = f"{start_hour:02d}:00"
    end_ts = f"{end_hour:02d}:00"
    return start_ts, end_ts, segment_name(rel_hours[best_start])


def normalize_night_window(window: Optional[Tuple[int, int]]) -> Tuple[int, int]:
    """Normalize astronomy-derived window into a sane observation-night band.

    Expected semantic window is target evening through next morning, i.e. within [18, 30].
    Some astronomy calculations may return reversed or daytime-looking windows like (8, 17).
    In those cases, fall back to the agreed fixed observation band 18:00-06:00.
    """
    default_window = (18, 30)
    if window is None:
        return default_window
    start_h, end_h = window
    if end_h < start_h:
        end_h += 24
    if start_h < 16 or start_h > 23:
        return default_window
    if end_h <= start_h or end_h > 36:
        return default_window
    start_h = max(18, start_h)
    end_h = min(30, end_h)
    if end_h <= start_h:
        return default_window
    return start_h, end_h


def derive_night_window(latitude_deg: float, longitude_deg: float, target_date) -> Tuple[int, int]:
    """Derive a safer observation-night window from twilight datetimes.

    We use sunset_sunrise_times() directly and repair obviously reversed results
    before collapsing them into relative hours on the target night.
    """
    default_window = (18, 30)
    sunset_dt, sunrise_dt = sunset_sunrise_times(latitude_deg, longitude_deg, target_date, tz_offset_h=8.0, altitude_deg=-18.0)
    if sunset_dt is None or sunrise_dt is None:
        return default_window

    start_dt, end_dt = sunset_dt, sunrise_dt
    if start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt
    if end_dt.date() <= start_dt.date():
        end_dt = end_dt + timedelta(days=1)

    start_h = (start_dt.date() - target_date).days * 24 + start_dt.hour
    end_h = (end_dt.date() - target_date).days * 24 + end_dt.hour
    return normalize_night_window((start_h, end_h))


def compute_final_score(point: SamplePoint, mode: str) -> None:
    """Score a point using nightly aggregated weather when available.
    Uses nightly avg cloud / worst cloud, falling back to single-hour values.
    Moon interference is incorporated as moonlight_score [0-100].
    """
    # Prefer nightly aggregation; fall back to single-hour snapshot
    cloud_for_scoring = point.night_avg_cloud if point.night_avg_cloud is not None else point.cloud_cover
    humidity_for_scoring = point.night_avg_humidity if point.night_avg_humidity is not None else point.humidity
    vis_for_scoring = point.night_avg_visibility if point.night_avg_visibility is not None else point.visibility_m
    wind_for_scoring = point.night_avg_wind if point.night_avg_wind is not None else point.wind_speed

    cloud = score_cloud(cloud_for_scoring)
    humidity = score_humidity(humidity_for_scoring)
    visibility = score_visibility(vis_for_scoring)
    wind = score_wind(wind_for_scoring)

    # Moon: use moonlight interference score if computed, else fallback
    if point.moon_interference is not None:
        # moon_interference: 0=strong interference, 100=no interference
        # Convert to moonlight_score [0-100] where 100=best
        moonlight_score = point.moon_interference
    else:
        moonlight_score = point.moon_factor or 0.0

    # moonlight_score: 0 = bright moon above horizon, 100 = no moonlight
    # For stargazing: less moonlight = better → moonlight_helps = (100 - moonlight_score)
    # For moon-viewing: moonlight helps scenic quality → moonlight_helps = moonlight_score
    if mode == "moon":
        weights = {"moon": 35, "cloud": 25, "visibility": 20, "humidity": 15, "wind": 5}
        moonlight_helps = moonlight_score
        total = moonlight_helps * 0.35 + cloud * 0.25 + visibility * 0.20 + humidity * 0.15 + wind * 0.05
    else:
        weights = {"cloud": 40, "humidity": 20, "visibility": 20, "moon": 15, "wind": 5}
        moonlight_helps = 100 - moonlight_score  # less moonlight = better for stargazing
        total = cloud * 0.40 + humidity * 0.20 + visibility * 0.20 + moonlight_helps * 0.15 + wind * 0.05

    # Hard gates: avoid promoting places that only look good on averages.
    if point.night_worst_cloud is not None and point.night_worst_cloud > 80:
        total = min(total, 69.9)
    if point.longest_usable_streak_hours is not None and point.longest_usable_streak_hours < 3:
        total = min(total, 64.9)

    point.final_score = round(total, 2)
    point.score_breakdown = {
        "weights": weights,
        "cloud_score": round(cloud, 2),
        "humidity_score": round(humidity, 2),
        "visibility_score": round(visibility, 2),
        "moonlight_score": round(moonlight_score, 2),
        "wind_score": round(wind, 2),
        "night_avg_cloud": round(point.night_avg_cloud, 1) if point.night_avg_cloud is not None else None,
        "night_worst_cloud": round(point.night_worst_cloud, 1) if point.night_worst_cloud is not None else None,
        "night_avg_humidity": round(point.night_avg_humidity, 1) if point.night_avg_humidity is not None else None,
        "night_avg_visibility": round(point.night_avg_visibility, 0) if point.night_avg_visibility is not None else None,
        "night_avg_wind": round(point.night_avg_wind, 1) if point.night_avg_wind is not None else None,
        "moon_interference": round(point.moon_interference, 1) if point.moon_interference is not None else None,
        "usable_hours": point.usable_hours,
        "longest_usable_streak_hours": point.longest_usable_streak_hours,
    }


def _extract_first_json_object(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty weather payload")
    start = text.find("{")
    if start < 0:
        raise ValueError("No JSON object found in weather payload")
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i+1])
    raise ValueError("Incomplete JSON object in weather payload")


def _fetch_json_via_curl(url: str, insecure: bool = False) -> dict:
    cmd = ["curl", "-fsSL", "--http1.1", "--retry", "3", "--retry-delay", "1"]
    if insecure:
        cmd.insert(1, "-k")
    cmd.append(url)
    out = subprocess.check_output(cmd, text=True, timeout=60)
    return _extract_first_json_object(out)


def fetch_openmeteo_payload(point: SamplePoint, target_dt: datetime, timezone: str, model: Optional[str] = None) -> dict:
    # Query target date + next date, so the night window can include next-morning hours.
    end_date = (target_dt.date() + timedelta(days=1)).isoformat()
    params = {
        "latitude": point.lat,
        "longitude": point.lng,
        "hourly": "cloud_cover,relative_humidity_2m,visibility,wind_speed_10m",
        "timezone": timezone,
        "start_date": target_dt.date().isoformat(),
        "end_date": end_date,
    }
    if model and model != "best_match":
        params["models"] = model
    url = OPEN_METEO_FORECAST_URL + "?" + urllib.parse.urlencode(params)

    # Prefer curl on this host: in practice it has been more reliable than urllib for Open-Meteo TLS.
    try:
        return _fetch_json_via_curl(url, insecure=False)
    except Exception:
        pass
    try:
        return _fetch_json_via_curl(url, insecure=True)
    except Exception:
        pass
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return _extract_first_json_object(resp.read().decode("utf-8"))
    except Exception:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(url, timeout=30, context=ctx) as resp:
            return _extract_first_json_object(resp.read().decode("utf-8"))


def hourly_index(payload: dict, target_dt: datetime) -> int:
    times = payload.get("hourly", {}).get("time", [])
    if not times:
        raise RuntimeError("No hourly timeline")
    target_key = target_dt.replace(minute=0, second=0, microsecond=0).isoformat(timespec="minutes")
    try:
        return times.index(target_key)
    except ValueError:
        parsed = [datetime.fromisoformat(t) for t in times]
        target_hour = target_dt.replace(minute=0, second=0, microsecond=0)
        return min(range(len(parsed)), key=lambda i: abs((parsed[i] - target_hour).total_seconds()))


def hydrate_mock_weather(points: List[SamplePoint], target_dt: datetime, mode: str) -> None:
    """Mock weather: single-hour values + nightly aggregates."""
    for p in points:
        base = f"{p.province}:{p.lat:.4f}:{p.lng:.4f}:{target_dt.date().isoformat()}"
        # Simulate a night window of target evening → next morning (18:00-06:00)
        night_hours = 13
        night_cloud_vals = [deterministic_value(f"{base}:cloud:h{h}", 0, 60) for h in range(night_hours)]
        night_hum_vals = [deterministic_value(f"{base}:humidity:h{h}", 20, 80) for h in range(night_hours)]
        night_vis_vals = [deterministic_value(f"{base}:vis:h{h}", 15000, 25000) for h in range(night_hours)]
        night_wind_vals = [deterministic_value(f"{base}:wind:h{h}", 0.5, 10) for h in range(night_hours)]

        # Single-hour: use hour matching target_dt (approx 23:00, i.e. 18:00 + 5h)
        snapshot_idx = min(5, night_hours - 1)
        p.cloud_cover = night_cloud_vals[snapshot_idx]
        p.humidity = night_hum_vals[snapshot_idx]
        p.visibility_m = night_vis_vals[snapshot_idx]
        p.wind_speed = night_wind_vals[snapshot_idx]

        # Nightly aggregates
        p.night_avg_cloud = round(sum(night_cloud_vals) / len(night_cloud_vals), 1)
        p.night_worst_cloud = max(night_cloud_vals)
        p.night_avg_humidity = round(sum(night_hum_vals) / len(night_hum_vals), 1)
        p.night_avg_visibility = round(sum(night_vis_vals) / len(night_vis_vals), 0)
        p.night_avg_wind = round(sum(night_wind_vals) / len(night_wind_vals), 1)
        p.elevation_m = deterministic_value(base + ":elevation", 1500, 4200)

        # Moon interference (mock: based on moon phase)
        illum, _ = moon_phase(julian_day(target_dt))
        mock_moon_alt = deterministic_value(base + ":moon_alt", -30, 60)
        p.moon_interference = moon_interference_score(illum, mock_moon_alt)
        mock_usable = [is_usable_observation_hour(c, w, p.moon_interference) for c, w in zip(night_cloud_vals, night_wind_vals)]
        p.usable_hours = float(sum(1 for x in mock_usable if x))
        p.longest_usable_streak_hours = float(longest_true_streak(mock_usable))
        mock_times = [(target_dt.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(hours=h)).isoformat(timespec="minutes") for h in range(night_hours)]
        mock_rel_hours = [18 + h for h in range(night_hours)]
        p.best_window_start, p.best_window_end, p.best_window_segment = best_true_window(mock_times, mock_usable, mock_rel_hours)
        p.cloud_stddev = round(sample_stddev(night_cloud_vals) or 0.0, 1)
        p.cloud_stability = classify_cloud_stability(p.cloud_stddev)
        worst_idx = max(range(len(night_cloud_vals)), key=lambda i: night_cloud_vals[i])
        p.worst_cloud_segment = segment_name(mock_rel_hours[worst_idx])
        p.moon_factor = moon_factor(target_dt, mode)
        p.weather_source = "mock"


def fetch_point_weather(point: SamplePoint, target_dt: datetime, timezone: str, mode: str, model: Optional[str] = None) -> SamplePoint:
    """Fetch weather for a point, compute single-hour snapshot + nightly aggregation."""
    payload = fetch_openmeteo_payload(point, target_dt, timezone, model=model)
    point.weather_model = model or "best_match"
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])

    # Single-hour snapshot (closest to target time)
    idx = hourly_index(payload, target_dt)
    point.cloud_cover = safe_float(hourly.get("cloud_cover", [None])[idx]) if hourly.get("cloud_cover") else None
    point.humidity = safe_float(hourly.get("relative_humidity_2m", [None])[idx]) if hourly.get("relative_humidity_2m") else None
    point.visibility_m = safe_float(hourly.get("visibility", [None])[idx]) if hourly.get("visibility") else None
    point.wind_speed = safe_float(hourly.get("wind_speed_10m", [None])[idx]) if hourly.get("wind_speed_10m") else None
    point.elevation_m = safe_float(payload.get("elevation"))

    # ---- Nightly aggregation over astronomical twilight window ----
    window = derive_night_window(point.lat, point.lng, target_dt.date())
    if window is not None:
        start_h, end_h = window
        # Collect hourly indices within the night window
        night_cloud, night_hum, night_vis, night_wind = [], [], [], []
        night_moon_scores = []
        usable_flags = []
        night_times = []
        night_rel_hours = []
        # Build list of (hour_index, hour_local) from times
        for i, t_str in enumerate(times):
            # Open-Meteo returns times already in the specified timezone (Asia/Shanghai)
            t = datetime.fromisoformat(t_str)
            # Convert the timestamp into a relative hour index for the target night:
            # target date 18:00 => 18, next day 02:00 => 26, etc.
            day_delta = (t.date() - target_dt.date()).days
            if day_delta not in (0, 1):
                continue
            rel_hour = day_delta * 24 + t.hour
            if not (start_h <= rel_hour <= end_h):
                continue
            cc = hourly.get("cloud_cover", [None])[i] if hourly.get("cloud_cover") else None
            rh = hourly.get("relative_humidity_2m", [None])[i] if hourly.get("relative_humidity_2m") else None
            vis = hourly.get("visibility", [None])[i] if hourly.get("visibility") else None
            ws = hourly.get("wind_speed_10m", [None])[i] if hourly.get("wind_speed_10m") else None
            night_times.append(t.isoformat(timespec="minutes"))
            night_rel_hours.append(rel_hour)
            if cc is not None:
                night_cloud.append(cc)
            if rh is not None:
                night_hum.append(rh)
            if vis is not None:
                night_vis.append(vis)
            if ws is not None:
                night_wind.append(ws)
            # Moon interference at this hour
            jd = julian_day(t)
            illum, _ = moon_phase(jd)
            moon_alt = moon_altitude(jd, point.lat, point.lng)
            interf = moon_interference_score(illum, moon_alt)
            night_moon_scores.append(interf)
            usable_flags.append(is_usable_observation_hour(cc, ws, interf))

        if night_cloud:
            point.night_avg_cloud = sum(night_cloud) / len(night_cloud)
            point.night_worst_cloud = max(night_cloud)
            point.night_avg_humidity = sum(night_hum) / len(night_hum) if night_hum else None
            point.night_avg_visibility = sum(night_vis) / len(night_vis) if night_vis else None
            point.night_avg_wind = sum(night_wind) / len(night_wind) if night_wind else None
            point.moon_interference = sum(night_moon_scores) / len(night_moon_scores) if night_moon_scores else 100.0
            point.usable_hours = float(sum(1 for x in usable_flags if x))
            point.longest_usable_streak_hours = float(longest_true_streak(usable_flags))
            point.best_window_start, point.best_window_end, point.best_window_segment = best_true_window(night_times, usable_flags, night_rel_hours)
            point.cloud_stddev = round(sample_stddev(night_cloud) or 0.0, 1)
            point.cloud_stability = classify_cloud_stability(point.cloud_stddev)
            worst_idx = max(range(len(night_cloud)), key=lambda i: night_cloud[i])
            point.worst_cloud_segment = segment_name(night_rel_hours[worst_idx])
        else:
            # No night hours found → use single-hour values as fallback
            point.night_avg_cloud = point.cloud_cover
            point.night_worst_cloud = point.cloud_cover
            point.night_avg_humidity = point.humidity
            point.night_avg_visibility = point.visibility_m
            point.night_avg_wind = point.wind_speed
            point.moon_interference = 50.0  # uncertain
            point.usable_hours = 0.0
            point.longest_usable_streak_hours = 0.0
            point.best_window_start = None
            point.best_window_end = None
            point.best_window_segment = None
            point.cloud_stddev = None
            point.cloud_stability = None
            point.worst_cloud_segment = None

    point.moon_factor = moon_factor(target_dt, mode)
    point.weather_source = "openmeteo-http"
    return point


def hydrate_real_weather(points: List[SamplePoint], target_dt: datetime, timezone: str, mode: str, max_workers: int, model: Optional[str] = None) -> None:
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {ex.submit(fetch_point_weather, p, target_dt, timezone, mode, model): p for p in points}
        for fut in as_completed(future_map):
            original = future_map[fut]
            try:
                updated = fut.result()
            except Exception:
                # One fetch failure must not abort the entire nationwide scan.
                original.weather_model = model or "best_match"
                original.weather_source = "fetch_error"
                original.cloud_cover = None
                original.humidity = None
                original.visibility_m = None
                original.wind_speed = None
                original.night_avg_cloud = None
                original.night_worst_cloud = None
                original.night_avg_humidity = None
                original.night_avg_visibility = None
                original.night_avg_wind = None
                original.moon_interference = None
                original.usable_hours = 0.0
                original.longest_usable_streak_hours = 0.0
                original.best_window_start = None
                original.best_window_end = None
                original.best_window_segment = None
                original.cloud_stddev = None
                original.cloud_stability = None
                original.worst_cloud_segment = None
                continue
            # Copy back all resolved weather fields, including nightly aggregates.
            original.weather_model = updated.weather_model
            original.cloud_cover = updated.cloud_cover
            original.humidity = updated.humidity
            original.visibility_m = updated.visibility_m
            original.wind_speed = updated.wind_speed
            original.elevation_m = updated.elevation_m
            original.night_avg_cloud = updated.night_avg_cloud
            original.night_worst_cloud = updated.night_worst_cloud
            original.night_avg_humidity = updated.night_avg_humidity
            original.night_avg_visibility = updated.night_avg_visibility
            original.night_avg_wind = updated.night_avg_wind
            original.moon_interference = updated.moon_interference
            original.usable_hours = updated.usable_hours
            original.longest_usable_streak_hours = updated.longest_usable_streak_hours
            original.best_window_start = updated.best_window_start
            original.best_window_end = updated.best_window_end
            original.best_window_segment = updated.best_window_segment
            original.cloud_stddev = updated.cloud_stddev
            original.cloud_stability = updated.cloud_stability
            original.worst_cloud_segment = updated.worst_cloud_segment
            original.moon_factor = updated.moon_factor
            original.weather_source = updated.weather_source


def hydrate_weather(points: List[SamplePoint], real_weather: bool, target_dt: datetime, timezone: str, mode: str, max_workers: int, model: Optional[str] = None) -> None:
    if real_weather:
        hydrate_real_weather(points, target_dt, timezone, mode, max_workers=max_workers, model=model)
    else:
        hydrate_mock_weather(points, target_dt, mode)


def select_stage2_budget(points: List[SamplePoint], max_stage2_points: int) -> List[SamplePoint]:
    ordered = sorted(points, key=lambda p: (0 if p.stage1_status == "pass" else 1, p.night_avg_cloud if p.night_avg_cloud is not None else (p.cloud_cover if p.cloud_cover is not None else 999.0), p.id))
    return ordered[:max_stage2_points]


def generate_adaptive_refinement_points(points: List[SamplePoint], boxes: List[BoundingBox], max_parent_points: int = 4) -> List[SamplePoint]:
    """Generate a small local neighborhood around the best coarse-filtered points.
    Purpose: reduce the chance of missing local weather peaks between coarse sample nodes.
    """
    if not points:
        return []
    box_map = {b.province: b for b in boxes}
    selected = sorted(
        points,
        key=lambda p: (p.night_avg_cloud if p.night_avg_cloud is not None else (p.cloud_cover if p.cloud_cover is not None else 999.0), p.id)
    )[:max_parent_points]
    out: List[SamplePoint] = []
    for parent in selected:
        box = box_map.get(parent.province)
        if not box:
            continue
        lat_step = max((box.max_lat - box.min_lat) * 0.08, 0.12)
        lng_step = max((box.max_lng - box.min_lng) * 0.08, 0.12)
        candidates = [
            (parent.lat + lat_step, parent.lng),
            (parent.lat - lat_step, parent.lng),
            (parent.lat, parent.lng + lng_step),
            (parent.lat, parent.lng - lng_step),
        ]
        for lat, lng in candidates:
            lat = min(max(lat, box.min_lat), box.max_lat)
            lng = min(max(lng, box.min_lng), box.max_lng)
            if abs(lat - parent.lat) < 1e-6 and abs(lng - parent.lng) < 1e-6:
                continue
            out.append(SamplePoint(id=f"{parent.province}:{lat:.4f}:{lng:.4f}", province=parent.province, scope_name=parent.scope_name, lat=lat, lng=lng))
    return out


def dedupe_cross_province(points: List[SamplePoint], distance_km: float = 60.0, score_gap: float = 8.0) -> List[SamplePoint]:
    kept: List[SamplePoint] = []
    for point in sorted(points, key=lambda p: (p.cloud_cover if p.cloud_cover is not None else 999.0, p.id)):
        duplicate_of: Optional[SamplePoint] = None
        for existing in kept:
            if existing.province == point.province:
                continue
            if haversine_km(point.lat, point.lng, existing.lat, existing.lng) > distance_km:
                continue
            c1 = point.cloud_cover if point.cloud_cover is not None else 100.0
            c2 = existing.cloud_cover if existing.cloud_cover is not None else 100.0
            f1 = point.final_score if point.final_score is not None else 0.0
            f2 = existing.final_score if existing.final_score is not None else 0.0
            if abs(c1 - c2) <= score_gap and abs(f1 - f2) <= 12.0:
                duplicate_of = existing
                break
        if duplicate_of is not None:
            point.merged_into = duplicate_of.id
            continue
        kept.append(point)
    return kept


def region_direction(box: BoundingBox, lat: float, lng: float) -> str:
    lat_mid = (box.min_lat + box.max_lat) / 2
    lng_mid = (box.min_lng + box.max_lng) / 2
    vertical = "北部" if lat >= lat_mid else "南部"
    horizontal = "东部" if lng >= lng_mid else "西部"
    lat_bias = abs(lat - lat_mid) / max((box.max_lat - box.min_lat) / 2, 0.1)
    lng_bias = abs(lng - lng_mid) / max((box.max_lng - box.min_lng) / 2, 0.1)
    if lat_bias > 0.25 and lng_bias > 0.25:
        mapping = {("北部", "西部"): "西北部", ("北部", "东部"): "东北部", ("南部", "西部"): "西南部", ("南部", "东部"): "东南部"}
        return mapping[(vertical, horizontal)]
    return horizontal if lng_bias >= lat_bias else vertical


HUMAN_REGION_ALIASES = {
    "海西蒙古族藏族": "海西",
    "伊犁哈萨克": "伊犁",
    "阿坝藏族羌族": "阿坝",
    "甘孜藏族": "甘孜",
    "凉山彝族": "凉山",
    "博尔塔拉蒙古": "博州",
    "克孜勒苏柯尔克孜": "克州",
}

FORCE_PREFECTURE_CONTEXT_PROVINCES = {"新疆", "西藏", "青海", "内蒙古"}


def add_province_context(label: str, provinces: List[str]) -> str:
    """Make labels immediately readable by always prefixing province-level context
    for single-province regions, unless already present. Also shorten a few overly long
    autonomous-prefecture names into more natural user-facing forms.
    """
    if not label:
        return label
    for src, dst in HUMAN_REGION_ALIASES.items():
        label = label.replace(src, dst)
    if len(provinces) != 1:
        return label
    prov = provinces[0]
    if label.startswith(prov):
        return label
    return f"{prov}{label}"


def cluster_points(points: List[SamplePoint], cluster_km: float) -> List[List[SamplePoint]]:
    clusters: List[List[SamplePoint]] = []
    for p in sorted(points, key=lambda x: (-(x.final_score or -1), x.id)):
        placed = False
        for cluster in clusters:
            if any(haversine_km(p.lat, p.lng, q.lat, q.lng) <= cluster_km for q in cluster):
                cluster.append(p)
                placed = True
                break
        if not placed:
            clusters.append([p])
    return clusters


def dominant_province(cluster: List[SamplePoint]) -> str:
    counts: Dict[str, int] = {}
    scores: Dict[str, float] = {}
    for p in cluster:
        counts[p.province] = counts.get(p.province, 0) + 1
        scores[p.province] = scores.get(p.province, 0.0) + (p.final_score or 0.0)
    return sorted(counts.keys(), key=lambda k: (counts[k], scores[k]), reverse=True)[0]


def cluster_centroid(cluster: List[SamplePoint]) -> Tuple[float, float]:
    lat = sum(p.lat for p in cluster) / len(cluster)
    lng = sum(p.lng for p in cluster) / len(cluster)
    return lat, lng


# ---------------------------------------------------------------------------
# Geographic reference table: (name, lat, lng, radius_deg, terrain_tag)
# radius_deg ≈ ~50km natural threshold for "nearby" check
# terrain_tag drives the label suffix
# ---------------------------------------------------------------------------
GEOGRAPHIC_FEATURES = [
    # (name, lat, lng, radius_deg, terrain_tag)
    # ---- 甘肃 / 青海 交界北部 ----
    ("阿尔金山", 39.2, 94.0, 1.2, "阿尔金山区域"),
    ("祁连山", 38.5, 99.5, 1.5, "祁连山区"),
    ("河西走廊", 40.5, 95.5, 1.8, "河西走廊"),
    ("敦煌", 40.1, 94.7, 0.8, "敦煌周边"),
    ("马鬃山", 41.5, 96.5, 1.0, "马鬃山区域"),
    ("安西", 40.5, 95.8, 0.8, "安西盆地"),
    # ---- 青海 ----
    ("柴达木盆地", 37.2, 95.5, 2.0, "柴达木盆地"),
    ("可可西里", 35.3, 93.0, 1.5, "可可西里边缘"),
    ("昆仑山", 35.8, 94.5, 1.5, "昆仑山区域"),
    ("巴颜喀拉山", 33.5, 97.0, 1.5, "巴颜喀拉山区域"),
    ("阿尼玛卿山", 34.5, 99.5, 1.2, "阿尼玛卿山区"),
    ("青海湖", 36.9, 100.4, 0.8, "青海湖周边"),
    ("茶卡盐湖", 36.7, 99.1, 0.5, "茶卡盐湖周边"),
    ("德令哈", 37.4, 97.4, 0.6, "德令哈周边"),
    ("格尔木", 36.4, 94.9, 0.6, "格尔木周边"),
    ("西宁", 36.6, 101.8, 0.6, "西宁周边"),
    ("玉树", 33.0, 97.0, 0.8, "玉树周边"),
    # ---- 甘肃 ----
    ("张掖", 38.9, 100.5, 0.6, "张掖周边"),
    ("酒泉", 39.7, 98.5, 0.6, "酒泉周边"),
    ("武威", 37.9, 102.6, 0.6, "武威周边"),
    ("白银", 36.5, 104.2, 0.6, "白银周边"),
    ("定西", 35.6, 104.6, 0.6, "定西周边"),
    # ---- 西藏 ----
    ("纳木错", 30.7, 88.6, 0.8, "纳木错周边"),
    ("羊卓雍错", 29.2, 90.6, 0.6, "羊卓雍错周边"),
    ("珠峰", 28.0, 86.9, 1.0, "珠峰区域"),
    ("阿里地区", 32.5, 80.0, 2.5, "阿里高原"),
    ("那曲", 31.5, 92.0, 0.8, "那曲周边"),
    # ---- 四川 ----
    ("康定", 30.0, 101.9, 0.6, "康定周边"),
    ("稻城亚丁", 28.9, 100.3, 0.6, "稻城亚丁周边"),
    ("若尔盖", 33.6, 102.9, 0.8, "若尔盖周边"),
    # ---- 新疆 ----
    ("喀纳斯", 49.0, 87.0, 0.6, "喀纳斯周边"),
    ("赛里木湖", 44.5, 81.0, 0.6, "赛里木湖周边"),
    ("巴音布鲁克", 43.0, 84.2, 0.8, "巴音布鲁克周边"),
    ("天山", 42.0, 86.0, 2.0, "天山区域"),
    ("塔克拉玛干", 38.5, 82.5, 2.5, "塔克拉玛干沙漠边缘"),
    ("库尔勒", 41.7, 86.1, 0.6, "库尔勒周边"),
    # ---- 内蒙古 ----
    ("额济纳旗", 41.9, 101.1, 0.8, "额济纳旗周边"),
    ("巴丹吉林沙漠", 39.5, 105.0, 1.5, "巴丹吉林沙漠边缘"),
    ("乌兰察布", 41.0, 113.0, 0.8, "乌兰察布周边"),
    ("阿尔山", 47.2, 119.9, 0.6, "阿尔山周边"),
]


def find_nearby_feature(lat: float, lng: float) -> Optional[Tuple[str, str, float]]:
    """Return (feature_name, terrain_tag, distance_km) for the nearest geographic feature within range."""
    best_dist = float("inf")
    best = None
    for name, feat_lat, feat_lng, radius, tag in GEOGRAPHIC_FEATURES:
        d = haversine_km(lat, lng, feat_lat, feat_lng)
        if d < best_dist:
            best_dist = d
            best = (name, tag, d)
    if best_dist > 130.0:  # > ~130km → too far for useful human naming hint
        return None
    return best


def terrain_altitude_tag(cluster: List[SamplePoint]) -> str:
    """Derive terrain/altitude tag from cluster point elevations."""
    elevs = [p.elevation_m for p in cluster if p.elevation_m is not None]
    if not elevs:
        return ""
    avg = sum(elevs) / len(elevs)
    if avg >= 4000:
        return "超高海拔地带"
    if avg >= 3500:
        return "高海拔地带"
    if avg >= 3000:
        return "中高海拔地带"
    if avg >= 2500:
        return "山地区域"
    if avg >= 1500:
        return "低山丘陵地带"
    return ""


def is_admin_like_name(name: str) -> bool:
    return any(name.endswith(s) for s in ["市", "盟", "地区", "自治州", "旗", "县", "区"])


def find_containing_admin_name(
    lat: float,
    lng: float,
    prefecture_polygons: Dict[str, MultiPolygon],
    county_polygons: Optional[Dict[str, MultiPolygon]] = None,
) -> Optional[str]:
    """Lightweight reverse naming layer.
    Checks county/banner polygons first (most specific), then prefecture-level.
    For equal administrative level, prefer shorter (less redundant) names.
    """
    ADMIN_LEVEL_PRIORITY = {"县": 0, "旗": 0, "区": 0, "市": 1, "盟": 2, "地区": 2, "自治州": 2}

    def name_key(n: str) -> tuple:
        """Sort key: county-level first, then by string length."""
        suffix = next((s for s in ADMIN_LEVEL_PRIORITY if n.endswith(s)), "")
        level = ADMIN_LEVEL_PRIORITY.get(suffix, 3)
        return (level, len(n), n)

    # County/banner level first: most specific administrative naming.
    if county_polygons:
        seen = set()
        candidates = []
        for name, geom in county_polygons.items():
            if name in seen or not is_admin_like_name(name):
                continue
            seen.add(name)
            try:
                if point_in_multipolygon(lng, lat, geom):
                    candidates.append(name)
            except Exception:
                continue
        if candidates:
            candidates.sort(key=name_key)
            return candidates[0]

    # Prefecture/league-level fallback when county/banner match is unavailable.
    seen = set()
    candidates = []
    for name, geom in prefecture_polygons.items():
        if name in seen:
            continue
        seen.add(name)
        if not is_admin_like_name(name):
            continue
        try:
            if point_in_multipolygon(lng, lat, geom):
                candidates.append(name)
        except Exception:
            continue
    if not candidates:
        return None
    candidates.sort(key=name_key)
    return candidates[0]


def humanize_prefecture_name(name: str) -> str:
    raw = str(name or "").strip()
    if not raw:
        return raw
    if raw.endswith("自治州"):
        base = raw[:-3]
        for src, dst in HUMAN_REGION_ALIASES.items():
            base = base.replace(src, dst)
        return f"{base}州"
    if raw.endswith("地区") or raw.endswith("盟") or raw.endswith("市"):
        return raw
    return raw


def build_admin_context_label(province: str, county_or_city: str, direction: str, prefecture_polygons: Optional[Dict[str, MultiPolygon]], lat: float, lng: float) -> str:
    county_or_city = normalize_region_name(county_or_city)
    if province in FORCE_PREFECTURE_CONTEXT_PROVINCES and prefecture_polygons:
        prefecture = find_containing_admin_name(lat, lng, prefecture_polygons, county_polygons=None)
        if prefecture:
            prefecture_human = humanize_prefecture_name(prefecture)
            pref_norm = normalize_region_name(prefecture_human)
            # Avoid awkward repeats like "青海海西州海西..."
            if pref_norm and (county_or_city == pref_norm or county_or_city.startswith(pref_norm)):
                return f"{province}{prefecture_human}{direction}"
            if prefecture_human and pref_norm not in county_or_city:
                return f"{province}{prefecture_human}{county_or_city}{direction}"
    return f"{province}{county_or_city}{direction}"


def cluster_label(cluster: List[SamplePoint], boxes: List[BoundingBox], prefecture_polygons: Optional[Dict[str, MultiPolygon]] = None, county_polygons: Optional[Dict[str, MultiPolygon]] = None) -> str:
    provinces = sorted({p.province for p in cluster})
    box_map = {b.province: b for b in boxes}
    lat, lng = cluster_centroid(cluster)
    feature = find_nearby_feature(lat, lng)
    altitude_tag = terrain_altitude_tag(cluster)

    # Prefer county/banner-level naming; add nearby geographic hint when useful.
    if len(provinces) == 1 and prefecture_polygons:
        prov = provinces[0]
        admin_name = find_containing_admin_name(lat, lng, prefecture_polygons, county_polygons=county_polygons)
        if admin_name:
            direction = region_direction(box_map[prov], lat, lng)
            base = build_admin_context_label(prov, admin_name, direction, prefecture_polygons, lat, lng)
            if feature:
                feat_name, terrain_tag, feature_distance = feature
                norm_admin = normalize_region_name(admin_name)
                norm_feat = normalize_region_name(feat_name)
                if norm_feat and norm_feat not in norm_admin and feature_distance <= 130:
                    return f"{base}，靠{feat_name}方向"
            return base

    # Try geographic feature name second
    if feature:
        feat_name, terrain_tag, feature_distance = feature
        if len(provinces) == 1:
            prov = provinces[0]
            parts = [prov, terrain_tag]
            if altitude_tag and altitude_tag not in terrain_tag:
                parts.append(altitude_tag)
            return "".join(parts)
        else:
            parts = [terrain_tag]
            if altitude_tag and altitude_tag not in terrain_tag:
                parts.append(altitude_tag)
            return "".join(parts)

    # Fallback to province + direction
    if len(provinces) == 1:
        prov = provinces[0]
        direction = region_direction(box_map[prov], lat, lng)
        suffix = f"{altitude_tag}·{direction}" if altitude_tag else direction
        return f"{prov}{suffix}"
    main_prov = dominant_province(cluster)
    top_two = provinces[:2]
    direction = region_direction(box_map[main_prov], lat, lng)
    suffix = f"{altitude_tag}·{direction}" if altitude_tag else direction
    return f"{'-'.join(top_two)}交界{suffix}"


def summarize_cluster(cluster: List[SamplePoint], boxes: List[BoundingBox], prefecture_polygons: Optional[Dict[str, MultiPolygon]] = None, county_polygons: Optional[Dict[str, MultiPolygon]] = None) -> dict:
    provinces = sorted({p.province for p in cluster})
    label = cluster_label(cluster, boxes, prefecture_polygons=prefecture_polygons, county_polygons=county_polygons)
    label = add_province_context(label, provinces)
    lat, lng = cluster_centroid(cluster)
    best = sorted(cluster, key=lambda p: (-(p.final_score or -1), p.night_avg_cloud if p.night_avg_cloud is not None else 999.0))[0]
    elevs = [p.elevation_m for p in cluster if p.elevation_m is not None]
    # Aggregate nightly weather across cluster members
    nc = [p.night_avg_cloud for p in cluster if p.night_avg_cloud is not None]
    nw = [p.night_worst_cloud for p in cluster if p.night_worst_cloud is not None]
    nh = [p.night_avg_humidity for p in cluster if p.night_avg_humidity is not None]
    nv = [p.night_avg_visibility for p in cluster if p.night_avg_visibility is not None]
    nwi = [p.night_avg_wind for p in cluster if p.night_avg_wind is not None]
    mi = [p.moon_interference for p in cluster if p.moon_interference is not None]
    uh = [p.usable_hours for p in cluster if p.usable_hours is not None]
    ls = [p.longest_usable_streak_hours for p in cluster if p.longest_usable_streak_hours is not None]
    cs = [p.cloud_stddev for p in cluster if p.cloud_stddev is not None]
    moon_scores = [p.moon_factor or 0.0 for p in cluster]
    summary = {
        "label": label,
        "provinces": provinces,
        "cluster_size": len(cluster),
        "lat": round(lat, 5),
        "lng": round(lng, 5),
        "best_point_id": best.id,
        "final_score": round(sum((p.final_score or 0.0) for p in cluster) / len(cluster), 2),
        "best_score": best.final_score,
        # Nightly aggregated weather
        "night_avg_cloud": round(sum(nc) / len(nc), 1) if nc else None,
        "night_worst_cloud": round(max(nw), 1) if nw else None,
        "night_avg_humidity": round(sum(nh) / len(nh), 1) if nh else None,
        "night_avg_visibility_m": round(sum(nv) / len(nv), 0) if nv else None,
        "night_avg_wind_kmh": round(sum(nwi) / len(nwi), 1) if nwi else None,
        "moon_interference": round(sum(mi) / len(mi), 1) if mi else None,
        "usable_hours": round(sum(uh) / len(uh), 1) if uh else None,
        "longest_usable_streak_hours": round(sum(ls) / len(ls), 1) if ls else None,
        "best_window_start": best.best_window_start,
        "best_window_end": best.best_window_end,
        "best_window_segment": best.best_window_segment,
        "cloud_stddev": round(sum(cs) / len(cs), 1) if cs else None,
        "cloud_stability": classify_cloud_stability(round(sum(cs) / len(cs), 1)) if cs else None,
        "worst_cloud_segment": best.worst_cloud_segment,
        "avg_moonlight_score": round(sum(moon_scores) / len(moon_scores), 1),
        "avg_cloud_cover": round(sum((p.cloud_cover or 0.0) for p in cluster) / len(cluster), 2),
        "avg_elevation_m": round(sum(elevs) / len(elevs), 0) if elevs else None,
        "members": [p.id for p in sorted(cluster, key=lambda x: x.id)],
    }
    summary["qualification"] = region_qualification(summary)
    summary["decision_rank_score"] = region_decision_rank_score(summary)
    summary["human_view"] = build_region_human_view(summary)
    return summary


def _humanize_iso_time(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    if isinstance(value, str) and len(value) == 5 and value[2] == ":":
        return value
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%H:%M")
    except Exception:
        return None


def _window_phrase(region: dict) -> Optional[str]:
    start = _humanize_iso_time(region.get("best_window_start"))
    end = _humanize_iso_time(region.get("best_window_end"))
    segment = region.get("best_window_segment")

    def _looks_like_night(hhmm: str) -> bool:
        try:
            hh = int(hhmm.split(":", 1)[0])
        except Exception:
            return False
        return hh >= 18 or hh <= 6

    if start and end and _looks_like_night(start) and _looks_like_night(end):
        return f"更适合守候的时段大致在 {start}-{end}"
    if segment:
        return f"相对更好的时段偏{segment}"
    return None


def _confidence_phrase(confidence: Optional[str]) -> Optional[str]:
    if confidence == "high":
        return "短期预报可信度较高"
    if confidence == "medium":
        return "属于中期预报，建议出发前再复查一次"
    if confidence == "low":
        return "属于中远期预报，当前更适合作趋势参考"
    return None


def _hours_phrase(hours: Optional[float]) -> Optional[str]:
    if hours is None:
        return None
    if hours <= 0.2:
        return "几乎没有成型的可拍窗口"
    if hours < 1.0:
        return "不到 1 小时"
    if abs(hours - round(hours)) < 1e-6:
        return f"约 {int(round(hours))} 小时"
    return f"约 {hours:.1f} 小时"


def _stability_phrase(value: Optional[str]) -> Optional[str]:
    if value == "stable":
        return "云量比较稳"
    if value == "mixed":
        return "云量有些波动"
    if value == "volatile":
        return "云量波动较大"
    return None


def _qualification_phrase(value: Optional[str]) -> Optional[str]:
    if value == "recommended":
        return "可作为优先候选"
    if value == "backup":
        return "可作为备选"
    if value == "observe_only":
        return "更适合先观察，不建议直接拍板"
    return None


def _evidence_phrase(evidence_type: Optional[str], model_coverage: Optional[int]) -> Optional[str]:
    if evidence_type in {"dual_model", "multi_model"}:
        return f"有 {model_coverage or 2} 个模型提供支持"
    if evidence_type == "single_model":
        return "目前只有 1 个模型给出较明显支持"
    return None


def _judgement_phrase(judgement: Optional[str], dispute_type: Optional[str] = None) -> Optional[str]:
    if judgement == "共识推荐":
        return "多模型结论一致，适合优先关注"
    if judgement == "备选":
        return "可以留在候选名单里"
    if judgement == "单模型亮点":
        return "只有单个模型明显看好，适合保守看待"
    if judgement == "争议区":
        if dispute_type == "强分歧区":
            return "模型分歧较大，风险偏高"
        if dispute_type == "单模型乐观区":
            return "只有部分模型乐观，不能直接当首选"
        if dispute_type == "窗口不稳区":
            return "虽然有可拍时段，但窗口不够稳"
        return "模型之间还有争议"
    if judgement == "不建议":
        return "当前不建议优先考虑"
    return None


def build_region_human_view(region: dict) -> dict:
    usable_hours = region.get("usable_hours")
    streak = region.get("longest_usable_streak_hours")
    worst_cloud = region.get("night_worst_cloud")
    avg_cloud = region.get("night_avg_cloud")
    wind = region.get("night_avg_wind_kmh") or region.get("night_avg_wind")
    moon = region.get("moon_interference")
    stability = region.get("cloud_stability")
    qualification = region.get("qualification")
    evidence_type = region.get("evidence_type")
    model_coverage = region.get("model_coverage")
    judgement = region.get("judgement")
    dispute_type = region.get("dispute_type")

    highlights = []
    if usable_hours is not None:
        highlights.append(f"可拍窗口 { _hours_phrase(usable_hours) }")
    if streak is not None:
        highlights.append(f"最长连续可拍窗口 { _hours_phrase(streak) }")
    if avg_cloud is not None:
        highlights.append(f"整晚平均云量约 {avg_cloud:.1f}%")
    if worst_cloud is not None:
        highlights.append(f"最差时段云量约 {worst_cloud:.0f}%")

    risks = []
    stability_text = _stability_phrase(stability)
    if stability_text:
        risks.append(stability_text)
    if wind is not None:
        risks.append(f"夜间平均风速约 {wind:.1f} km/h")
    if moon is not None:
        risks.append(f"月光影响约 {moon:.1f}/100")

    readable = {
        "推荐级别": _qualification_phrase(qualification),
        "联合判断": _judgement_phrase(judgement, dispute_type),
        "模型支持": _evidence_phrase(evidence_type, model_coverage),
        "可拍窗口": _hours_phrase(usable_hours),
        "最长连续窗口": _hours_phrase(streak),
        "平均云量": f"约 {avg_cloud:.1f}%" if avg_cloud is not None else None,
        "最差时段云量": f"约 {worst_cloud:.0f}%" if worst_cloud is not None else None,
        "云量走势": stability_text,
        "夜间平均风速": f"约 {wind:.1f} km/h" if wind is not None else None,
        "月光影响": f"约 {moon:.1f}/100" if moon is not None else None,
        "亮点摘要": [x for x in highlights if x],
        "风险摘要": [x for x in risks if x],
    }
    return readable


def region_qualification(region: dict) -> str:
    streak = region.get("longest_usable_streak_hours") or 0
    usable = region.get("usable_hours") or 0
    worst_cloud = region.get("night_worst_cloud")
    stability = region.get("cloud_stability")
    if streak >= 5 and usable >= 5 and (worst_cloud is None or worst_cloud <= 60) and stability != "volatile":
        return "recommended"
    if streak >= 3 and usable >= 3:
        return "backup"
    return "observe_only"


def region_decision_rank_score(region: dict) -> float:
    score = float(region.get("final_score") or 0.0)
    qual = region.get("qualification") or region_qualification(region)
    if qual == "recommended":
        score += 8.0
    elif qual == "backup":
        score += 1.5
    else:
        score -= 10.0
    stability = region.get("cloud_stability")
    if stability == "stable":
        score += 2.0
    elif stability == "volatile":
        score -= 6.0
    worst_cloud = region.get("night_worst_cloud")
    if worst_cloud is not None and worst_cloud > 80:
        score -= 8.0
    return round(score, 2)


def build_region_brief_advice(region: dict, confidence: Optional[str] = None) -> str:
    label = region.get("display_label") or region.get("label", "该区域")
    usable_hours = region.get("usable_hours")
    streak = region.get("longest_usable_streak_hours")
    worst_cloud = region.get("night_worst_cloud")
    score = region.get("final_score") or 0.0
    cloud_stability = region.get("cloud_stability")

    tail = []
    window_phrase = _window_phrase(region)
    conf_phrase = _confidence_phrase(confidence)
    if window_phrase:
        tail.append(window_phrase)
    if cloud_stability == "stable":
        tail.append("云量波动较小")
    elif cloud_stability == "volatile":
        tail.append("云量波动较大")
    if conf_phrase:
        tail.append(conf_phrase)
    suffix = f"（{'，'.join(tail)}）" if tail else ""

    if usable_hours is not None and streak is not None:
        if streak >= 5 and usable_hours >= 5 and (worst_cloud is None or worst_cloud <= 60):
            return f"{label} 值得优先关注；这晚可用时段比较完整，可以放进第一候选{suffix}。"
        if streak >= 3 and usable_hours >= 3:
            return f"{label} 可以先留在备选名单里；有一段还不错的可拍时间，但出发前最好再复查一次{suffix}。"
        return f"{label} 现在不适合太早拍板；能拍的时间偏短，更适合先观察{suffix}。"

    if score >= 75:
        return f"{label} 值得优先关注；这晚整体条件比较能打，可以放进第一候选{suffix}。"
    if score >= 60:
        return f"{label} 可以先留在备选名单里；临近出发前最好再复查一次{suffix}。"
    return f"{label} 这轮不建议优先考虑{suffix}。"



def aggregate_labels(points: List[SamplePoint], boxes: List[BoundingBox], top_n: int, cluster_km: float, prefecture_polygons: Optional[Dict[str, MultiPolygon]] = None, county_polygons: Optional[Dict[str, MultiPolygon]] = None, confidence: Optional[str] = None) -> List[dict]:
    if not points:
        return []
    clusters = cluster_points(points, cluster_km=cluster_km)
    summaries = [summarize_cluster(c, boxes, prefecture_polygons=prefecture_polygons, county_polygons=county_polygons) for c in clusters]
    summaries.sort(key=lambda x: (-x["decision_rank_score"], -x["final_score"], x["avg_cloud_cover"], x["label"]))
    summaries = summaries[:top_n]
    for region in summaries:
        region["brief_advice"] = build_region_brief_advice(region, confidence=confidence)
    return summaries


DIRECTION_SUFFIXES = ["东北部", "西北部", "东南部", "西南部", "东部", "西部", "南部", "北部", "中部"]


def extract_direction_suffix(label: Optional[str]) -> Optional[str]:
    base = str(label or "").split("，", 1)[0].strip()
    for suffix in DIRECTION_SUFFIXES:
        if base.endswith(suffix):
            return suffix
    return None


def build_anchor_label(label: Optional[str]) -> Optional[str]:
    if not label:
        return label
    base = str(label).split("，", 1)[0].strip()
    for suffix in DIRECTION_SUFFIXES:
        if base.endswith(suffix):
            return f"{base[:-len(suffix)]}一带"
    return base


def should_use_anchor_label(scope_meta: dict) -> bool:
    scope_mode = scope_meta.get("scope_mode")
    coverage = scope_meta.get("scope_coverage") or {}
    envelope = coverage.get("envelope") or {}
    area = abs((envelope.get("max_lat", 0) - envelope.get("min_lat", 0)) * (envelope.get("max_lng", 0) - envelope.get("min_lng", 0)))
    if scope_mode == "national":
        return True
    if coverage.get("province_count", 0) >= 2:
        return True
    if area >= 20.0:
        return True
    return False


def apply_label_presentation(labels: List[dict], scope_meta: dict) -> List[dict]:
    use_anchor = should_use_anchor_label(scope_meta)
    for region in labels:
        refined_label = region.get("label")
        anchor_label = build_anchor_label(refined_label)
        direction = extract_direction_suffix(refined_label)
        region["refined_label"] = refined_label
        region["anchor_label"] = anchor_label
        region["display_label"] = anchor_label if (use_anchor and anchor_label) else refined_label
        if use_anchor and anchor_label and refined_label and anchor_label != refined_label:
            region["refinement_note"] = f"这一轮先把范围锁在 {anchor_label} 这片区域；如果继续往下细看，更优落点可能会收敛到 {refined_label}。"
        elif (not use_anchor) and anchor_label and refined_label and anchor_label != refined_label and direction:
            region["refinement_note"] = f"继续细看后，这片区域里更好的落点偏向{direction[:-1]}，大致落在 {refined_label}。"
    return labels


def dedupe_display_labels(labels: List[dict]) -> List[dict]:
    deduped: Dict[str, dict] = {}
    for region in labels:
        key = region.get("display_label") or region.get("label")
        prev = deduped.get(key)
        if not prev:
            deduped[key] = region
            continue
        prev_score = prev.get("decision_rank_score", prev.get("final_score", 0.0)) or 0.0
        curr_score = region.get("decision_rank_score", region.get("final_score", 0.0)) or 0.0
        if curr_score > prev_score:
            deduped[key] = region
    return list(deduped.values())


def summarize_fetch_health(points: List[SamplePoint]) -> dict:
    total = len(points)
    failed = sum(1 for p in points if p.weather_source == "fetch_error")
    success = total - failed
    ratio = (failed / total) if total else 0.0
    status = "ok"
    user_note = None
    if ratio >= 0.35:
        status = "degraded"
        user_note = "本轮天气数据抓取缺失偏多，结果更适合先看趋势，建议稍后再复查一次。"
    elif ratio > 0:
        status = "partial"
        user_note = "本轮有少量点位数据抓取失败，但整体结论仍可参考。"
    return {
        "status": status,
        "total_points": total,
        "successful_points": success,
        "failed_points": failed,
        "failed_ratio": round(ratio, 3),
        "user_note": user_note,
    }


def build_scope_meta(boxes: List[BoundingBox]) -> dict:
    provinces = sorted({b.province for b in boxes})
    coverage_boxes = [
        {
            "name": b.name,
            "province": b.province,
            "min_lat": b.min_lat,
            "max_lat": b.max_lat,
            "min_lng": b.min_lng,
            "max_lng": b.max_lng,
        }
        for b in boxes
    ]
    min_lat = min(b.min_lat for b in boxes)
    max_lat = max(b.max_lat for b in boxes)
    min_lng = min(b.min_lng for b in boxes)
    max_lng = max(b.max_lng for b in boxes)

    if len(boxes) == 1:
        area = abs((boxes[0].max_lat - boxes[0].min_lat) * (boxes[0].max_lng - boxes[0].min_lng))
        scope_mode = "point_check" if area <= 2.0 else "regional"
    elif len(provinces) >= 3:
        scope_mode = "national"
    else:
        scope_mode = "regional"

    guardrail = {"ok": True, "warnings": []}
    if scope_mode == "national":
        # Simple anti-omission guardrail: national scans should cover broad west-to-east and north-to-south extents,
        # otherwise they are likely partial national subsets masquerading as nationwide results.
        if min_lng > 90:
            guardrail["warnings"].append("national_scope_missing_far_west")
        if max_lng < 115:
            guardrail["warnings"].append("national_scope_missing_far_east_or_northeast")
        if max_lat < 43:
            guardrail["warnings"].append("national_scope_missing_northern_band")
        if min_lat > 28:
            guardrail["warnings"].append("national_scope_missing_southwestern_band")
        if len(provinces) < 5:
            guardrail["warnings"].append("national_scope_province_count_too_small")
        guardrail["ok"] = len(guardrail["warnings"]) == 0

    if scope_mode == "national" and not guardrail["ok"]:
        scope_reduction_reason = "partial_national_subset"
    else:
        scope_reduction_reason = "none"

    return {
        "scope_mode": scope_mode,
        "scope_coverage": {
            "province_count": len(provinces),
            "provinces": provinces,
            "box_count": len(boxes),
            "boxes": coverage_boxes,
            "envelope": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lng": min_lng,
                "max_lng": max_lng,
            },
        },
        "scope_reduction_reason": scope_reduction_reason,
        "scope_guardrail": guardrail,
    }


def build_decision_summary(labels: List[dict], confidence: Optional[str] = None, joint: Optional[dict] = None, third_model_recheck: Optional[dict] = None) -> dict:
    primary = labels[0] if labels else None
    backups = labels[1:3] if len(labels) > 1 else []

    # Prefer joint judgement as the final decision anchor when available.
    joint_regions = (joint or {}).get("consensus_regions", []) if joint else []
    if joint_regions:
        joint_primary = joint_regions[0]
        primary_region = joint_primary.get("display_label") or joint_primary.get("label")
        primary_advice = joint_primary.get("joint_brief_advice")
        backup_regions = [(x.get("display_label") or x.get("label")) for x in joint_regions[1:3]]
        refinement_note = joint_primary.get("refinement_note")
    else:
        primary_region = (primary.get("display_label") or primary.get("label")) if primary else None
        primary_advice = primary.get("brief_advice") if primary else None
        backup_regions = [(x.get("display_label") or x.get("label")) for x in backups]
        refinement_note = primary.get("refinement_note") if primary else None

    summary = {
        "primary_region": primary_region,
        "primary_advice": primary_advice,
        "backup_regions": backup_regions,
        "confidence_note": _confidence_phrase(confidence),
        "risk_note": None,
        "third_model_note": None,
        "joint_note": None,
        "refinement_note": refinement_note,
        "one_line": None,
        "final_reply_draft": None,
        "reply_drafts": {},
    }
    if primary:
        if primary.get("cloud_stability") == "volatile":
            summary["risk_note"] = "云量波动偏大，稳定性一般"
        elif primary.get("longest_usable_streak_hours") is not None and primary.get("longest_usable_streak_hours") < 3:
            summary["risk_note"] = "连续可拍窗口偏短"
    if joint and joint.get("top_joint_advice"):
        summary["joint_note"] = joint.get("top_joint_advice")
    if third_model_recheck and third_model_recheck.get("enabled"):
        if third_model_recheck.get("triggered"):
            summary["third_model_note"] = f"已触发 {third_model_recheck.get('requested_model')} 复核"
        else:
            summary["third_model_note"] = f"未触发 {third_model_recheck.get('requested_model')} 复核"

    primary_region = summary.get("primary_region")
    primary_advice = summary.get("primary_advice")
    confidence_note = summary.get("confidence_note")
    risk_note = summary.get("risk_note")
    joint_note = summary.get("joint_note")
    third_note = summary.get("third_model_note")
    refinement_note = summary.get("refinement_note")
    backup_regions = summary.get("backup_regions") or []

    if primary_region and primary_advice:
        summary["one_line"] = f"当前优先关注 {primary_region}。"

    reply_lines = []
    if primary_advice:
        reply_lines.append(f"结论：{primary_advice}")
    elif primary_region:
        reply_lines.append(f"结论：当前优先关注 {primary_region}。")

    if backup_regions:
        reply_lines.append(f"备选：{ '、'.join(backup_regions) }")
    if joint_note:
        reply_lines.append(f"联合判断：{joint_note}")
    if risk_note:
        reply_lines.append(f"风险：{risk_note}")
    if refinement_note:
        reply_lines.append(f"细化说明：{refinement_note}")
    if confidence_note:
        reply_lines.append(f"置信度：{confidence_note}")
    if third_note:
        reply_lines.append(f"复核：{third_note}")

    if reply_lines:
        summary["final_reply_draft"] = "\n".join(reply_lines)

    concise_parts = []
    if primary_region:
        concise_parts.append(f"优先关注 {primary_region}")
    if risk_note:
        concise_parts.append(f"风险：{risk_note}")
    if refinement_note:
        concise_parts.append(refinement_note)
    if confidence_note:
        concise_parts.append(confidence_note)
    if concise_parts:
        concise = "；".join(part.rstrip('。') for part in concise_parts if part)
        summary["reply_drafts"]["concise"] = concise + "。"

    standard_parts = []
    if primary_advice:
        standard_parts.append(f"结论：{primary_advice}")
    if joint_note:
        standard_parts.append(f"联合判断：{joint_note}")
    if refinement_note:
        standard_parts.append(f"细化说明：{refinement_note}")
    if confidence_note:
        standard_parts.append(f"置信度：{confidence_note}")
    if standard_parts:
        summary["reply_drafts"]["standard"] = "\n".join(standard_parts)

    if summary.get("final_reply_draft"):
        summary["reply_drafts"]["detailed"] = summary["final_reply_draft"]
    return summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Dynamic sampling prototype for go-stargazing")
    p.add_argument("--mode", choices=["stargazing", "moon"], default="stargazing")
    p.add_argument("--target-count", type=int, default=8, help="Target samples per box")
    p.add_argument("--dedupe-km", type=float, default=60.0, help="Cross-province dedupe distance")
    p.add_argument("--cluster-km", type=float, default=120.0, help="Cluster radius for natural regional labels")
    p.add_argument("--cloud-gap", type=float, default=8.0, help="Max cloud-cover gap for dedupe merge")
    p.add_argument("--real-weather", action="store_true", help="Fetch real weather from Open-Meteo instead of mock values")
    p.add_argument("--target-datetime", help="ISO datetime like 2026-03-27T20:00:00")
    p.add_argument("--timezone", default="Asia/Shanghai", help="Timezone for Open-Meteo hourly response")
    p.add_argument("--boxes-json", help="JSON array of bounding boxes")
    p.add_argument("--scope-preset", choices=["national"], help="Use a built-in canonical scope preset when no explicit boxes are supplied")
    p.add_argument("--polygons-json", help="GeoJSON/JSON string for polygon filtering")
    p.add_argument("--polygons-file", help="Path to GeoJSON/JSON file for polygon filtering")
    p.add_argument("--max-workers", type=int, default=6, help="Max concurrent weather fetches")
    p.add_argument("--max-stage2-points", type=int, default=12, help="Budget cap for stage2 scoring points")
    p.add_argument("--top-n", type=int, default=3, help="Max number of output regions")
    p.add_argument("--model", choices=["best_match", "gfs_global", "gfs_seamless", "icon_global", "ecmwf_ifs"], default="best_match", help="Weather model route to use. best_match = Open-Meteo default")
    p.add_argument("--compare-models", nargs="+", choices=["gfs_global", "gfs_seamless", "icon_global", "ecmwf_ifs"], help="Run the full query once per listed model and return a comparison payload")
    p.add_argument("--auto-third-model", choices=["icon_global"], help="If initial dual-model result is disputed / single-model-heavy, auto-run a third model for recheck")
    p.add_argument("--strict-national-scope", action="store_true", help="When scope_mode resolves to national, fail fast if coverage looks like a partial national subset")
    p.add_argument("--pretty", action="store_true")
    return p


def check_date_availability(target_dt: datetime) -> Tuple[bool, Optional[datetime]]:
    """Check if Open-Meteo can serve hourly data for the target night.
    We need target date + next date because the night window spans past midnight.
    Returns (is_available, latest_available_date).
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    latest = today + timedelta(days=OPEN_METEO_HOURLY_WINDOW_DAYS)
    required_end = target_dt + timedelta(days=1)
    is_available = required_end <= latest
    return is_available, latest


def _judgement_bucket(score: float) -> str:
    if score >= 75:
        return "strong"
    if score >= 60:
        return "candidate"
    return "reject"


def build_joint_brief_advice(region: dict, confidence: Optional[str] = None) -> str:
    label = region.get("display_label") or region.get("label", "该区域")
    judgement = region.get("judgement")
    spread = region.get("score_spread") or 0.0
    dispute_type = region.get("dispute_type")
    conf_phrase = _confidence_phrase(confidence)
    suffix = f"（{conf_phrase}）" if conf_phrase else ""
    model_phrase = "多模型" if (region.get("model_coverage") or 0) >= 3 else "双模型"
    if judgement == "共识推荐":
        return f"{model_phrase}都比较支持 {label}；这晚可以优先关注{suffix}。"
    if judgement == "单模型亮点":
        return f"{label} 目前主要是单个模型更看好；可以继续盯着看，但别只凭这一轮就拍板{suffix}。"
    if judgement == "备选":
        return f"{label} 可以先留在备选名单里；模型看法还没完全站到一边，出发前最好再复查一次{suffix}。"
    if judgement == "争议区":
        if dispute_type == "强分歧区":
            return f"{label} 这轮分歧比较大（模型差异约 {spread:.1f} 分）；先别急着拍板{suffix}。"
        if dispute_type == "单模型乐观区":
            return f"{label} 更像是部分模型偏乐观；还需要更多复核，先别急着定{suffix}。"
        if dispute_type == "窗口不稳区":
            return f"{label} 虽然不是完全没机会，但整晚不够稳，更适合先观察{suffix}。"
        return f"{label} 这轮模型看法分歧不小（差异约 {spread:.1f} 分）；暂时不建议直接拍板{suffix}。"
    return f"{label} 这轮不建议优先考虑{suffix}。"


def build_joint_judgement(model_results: Dict[str, dict], confidence: Optional[str] = None) -> dict:
    """Merge multiple model outputs into one consensus judgement.
    Heuristic: key by region label, compare scores/clouds across models.
    """
    by_label: Dict[str, dict] = {}
    for model_name, result in model_results.items():
        for region in result.get("region_labels", []):
            label = region.get("display_label") or region["label"]
            entry = by_label.setdefault(label, {
                "label": label,
                "display_label": region.get("display_label") or region.get("label"),
                "anchor_label": region.get("anchor_label"),
                "refined_label": region.get("refined_label") or region.get("label"),
                "refinement_note": region.get("refinement_note"),
                "provinces": region.get("provinces", []),
                "per_model": {},
            })
            entry["per_model"][model_name] = {
                "score": region.get("final_score"),
                "night_avg_cloud": region.get("night_avg_cloud"),
                "night_worst_cloud": region.get("night_worst_cloud"),
                "moon_interference": region.get("moon_interference"),
                "usable_hours": region.get("usable_hours"),
                "longest_usable_streak_hours": region.get("longest_usable_streak_hours"),
                "cloud_stability": region.get("cloud_stability"),
                "qualification": region.get("qualification"),
                "human_view": build_region_human_view({
                    "usable_hours": region.get("usable_hours"),
                    "longest_usable_streak_hours": region.get("longest_usable_streak_hours"),
                    "night_avg_cloud": region.get("night_avg_cloud"),
                    "night_worst_cloud": region.get("night_worst_cloud"),
                    "moon_interference": region.get("moon_interference"),
                    "cloud_stability": region.get("cloud_stability"),
                    "qualification": region.get("qualification"),
                }),
            }

    consensus = []
    for label, entry in by_label.items():
        model_scores = [v["score"] for v in entry["per_model"].values() if v.get("score") is not None]
        model_clouds = [v["night_avg_cloud"] for v in entry["per_model"].values() if v.get("night_avg_cloud") is not None]
        if not model_scores:
            continue
        min_score = min(model_scores)
        max_score = max(model_scores)
        avg_score = round(sum(model_scores) / len(model_scores), 2)
        score_spread = round(max_score - min_score, 2)
        avg_cloud = round(sum(model_clouds) / len(model_clouds), 1) if model_clouds else None

        buckets = [_judgement_bucket(s) for s in model_scores]
        model_coverage = len(entry["per_model"])
        dispute_type = None
        usable_vals = [v.get("usable_hours") for v in entry["per_model"].values() if v.get("usable_hours") is not None]
        stability_flags = [v.get("cloud_stability") for v in entry["per_model"].values() if v.get("cloud_stability")]
        qualifications = [v.get("qualification") for v in entry["per_model"].values() if v.get("qualification")]
        has_volatile = any(x == "volatile" for x in stability_flags)
        has_recommended = any(q == "recommended" for q in qualifications)
        all_recommended = qualifications and all(q == "recommended" for q in qualifications)
        all_backup_or_better = qualifications and all(q in {"recommended", "backup"} for q in qualifications)
        has_observe_only = any(q == "observe_only" for q in qualifications)
        if model_coverage >= 2:
            strong_count = sum(1 for b in buckets if b == "strong")
            candidate_count = sum(1 for b in buckets if b == "candidate")
            reject_count = sum(1 for b in buckets if b == "reject")
            recommended_count = sum(1 for q in qualifications if q == "recommended")
            if all(b == "strong" for b in buckets) and score_spread <= 10 and all_recommended:
                judgement = "共识推荐"
            elif model_coverage >= 3 and strong_count >= 2 and reject_count == 0 and recommended_count >= 2 and score_spread <= 15:
                judgement = "共识推荐"
            elif model_coverage >= 3 and (strong_count + candidate_count) >= 2 and reject_count <= 1 and all_backup_or_better:
                judgement = "备选"
            elif strong_count == 1 and reject_count == 0:
                judgement = "争议区"
                dispute_type = "单模型乐观区"
            elif has_observe_only or ((usable_vals and max(usable_vals) >= 3 and min(usable_vals) < 3) or has_volatile):
                judgement = "争议区"
                dispute_type = "窗口不稳区"
            elif score_spread >= 20 or any(b == "reject" for b in buckets):
                judgement = "争议区"
                dispute_type = "强分歧区"
            elif any(b == "strong" for b in buckets) and all_backup_or_better:
                judgement = "备选"
            elif all_backup_or_better:
                judgement = "备选"
            else:
                judgement = "不建议"
            evidence_type = "dual_model" if model_coverage == 2 else "multi_model"
        else:
            if all(b == "strong" for b in buckets) and has_recommended:
                judgement = "单模型亮点"
            elif any(b == "strong" for b in buckets) and not has_observe_only:
                judgement = "单模型亮点"
            elif any(b == "candidate" for b in buckets) and not has_observe_only:
                judgement = "备选"
            else:
                judgement = "不建议"
            evidence_type = "single_model"

        row = {
            "label": label,
            "display_label": entry.get("display_label") or label,
            "anchor_label": entry.get("anchor_label"),
            "refined_label": entry.get("refined_label") or label,
            "refinement_note": entry.get("refinement_note"),
            "provinces": entry.get("provinces", []),
            "judgement": judgement,
            "dispute_type": dispute_type,
            "evidence_type": evidence_type,
            "model_coverage": model_coverage,
            "avg_score": avg_score,
            "score_spread": score_spread,
            "avg_night_cloud": avg_cloud,
            "per_model": entry["per_model"],
        }
        decision_rank_score = avg_score
        if judgement == "共识推荐":
            decision_rank_score += 10
        elif judgement == "备选":
            decision_rank_score += 2
        elif judgement == "单模型亮点":
            # Fortune explicitly wanted stronger suppression of raw-score spikes that
            # only come from one model.
            decision_rank_score -= 12
        elif judgement == "争议区":
            if dispute_type == "强分歧区":
                decision_rank_score -= 16
            elif dispute_type == "单模型乐观区":
                decision_rank_score -= 12
            elif dispute_type == "窗口不稳区":
                decision_rank_score -= 10
        elif judgement == "不建议":
            decision_rank_score -= 20
        row["decision_rank_score"] = round(decision_rank_score, 2)
        row["human_view"] = build_region_human_view(row)
        row["joint_brief_advice"] = build_joint_brief_advice(row, confidence=confidence)
        consensus.append(row)

    rank = {"共识推荐": 0, "备选": 1, "单模型亮点": 2, "争议区": 3, "不建议": 4}
    consensus.sort(key=lambda x: (rank.get(x["judgement"], 9), -x["decision_rank_score"], -x["avg_score"], x["score_spread"], x["label"]))
    top_joint_advice = consensus[0].get("joint_brief_advice") if consensus else None
    return {
        "summary": {
            "consensus_count": sum(1 for x in consensus if x["judgement"] == "共识推荐"),
            "single_model_count": sum(1 for x in consensus if x["judgement"] == "单模型亮点"),
            "candidate_count": sum(1 for x in consensus if x["judgement"] == "备选"),
            "disputed_count": sum(1 for x in consensus if x["judgement"] == "争议区"),
            "reject_count": sum(1 for x in consensus if x["judgement"] == "不建议"),
        },
        "top_joint_advice": top_joint_advice,
        "consensus_regions": consensus,
    }


def run_pipeline(args, boxes: List[BoundingBox], province_polygons, prefecture_polygons, county_polygons, target_dt: datetime, confidence: str, model: Optional[str] = None) -> dict:
    """Run the full sampling → weather → score → aggregate pipeline once for a given model."""
    started_at = time.perf_counter()
    all_points: List[SamplePoint] = []
    generated_count_before_filter = 0
    for box in boxes:
        pts = generate_grid_points(box, args.target_count)
        generated_count_before_filter += len(pts)
        pts = filter_points_by_polygon(pts, province_polygons, prefecture_polygons)
        all_points.extend(pts)

    hydrate_weather(all_points, real_weather=args.real_weather, target_dt=target_dt, timezone=args.timezone, mode=args.mode, max_workers=args.max_workers, model=model)
    coarse_pass = coarse_filter(all_points, args.mode)

    # Adaptive refinement: add a few local neighbor probes around the best coarse-pass points,
    # then let them compete for the stage-2 budget. This reduces the chance of missing local peaks.
    adaptive_points = generate_adaptive_refinement_points(coarse_pass, boxes)
    if adaptive_points:
        hydrate_weather(adaptive_points, real_weather=args.real_weather, target_dt=target_dt, timezone=args.timezone, mode=args.mode, max_workers=args.max_workers, model=model)
        adaptive_points = coarse_filter(adaptive_points, args.mode)
        coarse_pass = coarse_pass + adaptive_points

    stage2_points = select_stage2_budget(coarse_pass, max_stage2_points=args.max_stage2_points)
    for p in stage2_points:
        compute_final_score(p, args.mode)
    deduped = dedupe_cross_province(stage2_points, distance_km=args.dedupe_km, score_gap=args.cloud_gap)
    labels = aggregate_labels(deduped, boxes, top_n=args.top_n, cluster_km=args.cluster_km, prefecture_polygons=prefecture_polygons, county_polygons=county_polygons, confidence=confidence)

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 1)
    scope_meta = build_scope_meta(boxes)
    labels = apply_label_presentation(labels, scope_meta)
    labels = dedupe_display_labels(labels)
    labels.sort(key=lambda x: (-x["decision_rank_score"], -(x.get("final_score") or 0.0), x.get("display_label") or x["label"]))
    labels = labels[: args.top_n]
    for region in labels:
        region["brief_advice"] = build_region_brief_advice(region, confidence=confidence)
        region["human_view"] = build_region_human_view(region)
    top_region_advice = labels[0].get("brief_advice") if labels else None
    fetch_health = summarize_fetch_health(all_points + adaptive_points)
    decision_summary = build_decision_summary(labels, confidence=confidence)
    if fetch_health.get("user_note"):
        note = fetch_health.get("user_note")
        decision_summary["data_quality_note"] = note
        if decision_summary.get("final_reply_draft"):
            decision_summary["final_reply_draft"] += f"\n数据完整性：{note}"
        decision_summary.setdefault("reply_drafts", {})
        if decision_summary["reply_drafts"].get("concise"):
            decision_summary["reply_drafts"]["concise"] = decision_summary["reply_drafts"]["concise"].rstrip("。") + f"；{note}。"
        if decision_summary["reply_drafts"].get("standard"):
            decision_summary["reply_drafts"]["standard"] += f"\n数据完整性：{note}"
        if decision_summary.get("final_reply_draft"):
            decision_summary["reply_drafts"]["detailed"] = decision_summary["final_reply_draft"]
    return {
        "mode": args.mode,
        "target_datetime": target_dt.isoformat(),
        "weather_model": model or "best_match",
        "forecast_confidence": confidence,
        "scope_mode": scope_meta["scope_mode"],
        "scope_coverage": scope_meta["scope_coverage"],
        "scope_reduction_reason": scope_meta["scope_reduction_reason"],
        "scope_guardrail": scope_meta["scope_guardrail"],
        "fetch_health": fetch_health,
        "decision_summary": decision_summary,
        "top_region_advice": top_region_advice,
        "timing": {
            "elapsed_ms": elapsed_ms,
            "elapsed_seconds": round(elapsed_ms / 1000.0, 2),
        },
        "confidence_note": {
            "high": "3天内：数据可靠，接近实况",
            "medium": "4-7天：预报精度有所下降，建议参考趋势",
            "low": "8-16天：预报不确定性较高，请以当天Windy等本地工具为准",
        }.get(confidence, ""),
        "budget": {"max_workers": args.max_workers, "max_stage2_points": args.max_stage2_points, "top_n": args.top_n},
        "polygon_filtering": {
            "enabled": bool(province_polygons or prefecture_polygons),
            "province_count": len(province_polygons),
            "prefecture_count": len(prefecture_polygons),
            "generated_before_filter": generated_count_before_filter,
            "remaining_after_filter": len(all_points),
        },
        "input_boxes": [asdict(b) for b in boxes],
        "generated_points": [asdict(p) for p in all_points],
        "stage1_survivors": [asdict(p) for p in coarse_pass],
        "stage2_points": [asdict(p) for p in stage2_points],
        "deduped_survivors": [asdict(p) for p in deduped],
        "region_labels": labels,
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.boxes_json:
        boxes = parse_boxes(args.boxes_json)
    elif args.scope_preset:
        boxes = load_scope_preset(args.scope_preset)
    else:
        parser.error("--boxes-json is required unless --scope-preset is provided")
    target_dt = parse_target_datetime(args.target_datetime)

    # Date availability check
    if args.real_weather:
        available, latest_dt = check_date_availability(target_dt)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_ahead = (target_dt.date() - today.date()).days
        confidence = "high" if days_ahead <= 3 else "medium" if days_ahead <= 7 else "low"
        if not available:
            print(json.dumps({
                "error": "date_out_of_range",
                "message": f"Open-Meteo 实时预报最晚只支持查询 {latest_dt.date().isoformat()}（今天起 +{OPEN_METEO_HOURLY_WINDOW_DAYS} 天）。"
                           f"你指定的日期 {target_dt.date().isoformat()} 超出范围。",
                "target_date": target_dt.date().isoformat(),
                "latest_available_date": latest_dt.date().isoformat(),
                "forecast_confidence": confidence,
                "suggestion": f"清明节（4月4日）距今超过 {OPEN_METEO_HOURLY_WINDOW_DAYS} 天，建议在 4 月 1 日之后再查询。",
            }, ensure_ascii=False), file=sys.stderr)
            return
    else:
        confidence = "mock"

    province_polygons, prefecture_polygons = load_polygons(args.polygons_json, args.polygons_file)

    scope_meta = build_scope_meta(boxes)
    if args.strict_national_scope and scope_meta["scope_mode"] == "national" and not scope_meta["scope_guardrail"]["ok"]:
        print(json.dumps({
            "error": "national_scope_guardrail_failed",
            "message": "当前 boxes 更像局部全国子集，不足以代表全国默认扫描。",
            "scope_mode": scope_meta["scope_mode"],
            "scope_coverage": scope_meta["scope_coverage"],
            "scope_reduction_reason": scope_meta["scope_reduction_reason"],
            "scope_guardrail": scope_meta["scope_guardrail"],
            "suggestion": "补全全国范围 boxes，或显式把本次查询改成 regional。",
        }, ensure_ascii=False), file=sys.stderr)
        return

    # Load county/banner polygons for provinces that appear in the current query boxes.
    # Key: prefecture-level adcode (not province-level), so we actually get county/banner data
    PREFECTURE_ADCODES = {
        "内蒙古": ["152900", "150200", "150300", "150500", "150600", "150700", "150800", "150900", "152100", "152200", "152500", "152600", "152900"],
        "青海": ["630100", "632200", "632300", "632500", "632600", "632700", "632800", "632900", "633000"],
        "甘肃": ["620100", "620200", "620300", "620400", "620500", "620600", "620700", "620800", "620900", "621000", "621100", "621200"],
        "新疆": ["650100", "650200", "650400", "652300", "652700", "652800", "652900", "653000", "653100", "653200", "653400", "654000", "654200", "654300", "654400"],
        "西藏": ["540100", "540200", "540300", "540400", "540500", "540600", "542500", "542600"],
        "四川": ["510100", "510300", "510400", "510500", "510600", "510700", "510800", "510900", "511000", "511100", "511300", "511400", "511500", "511600", "511700", "511800", "511900", "512000", "513200", "513300", "513400"],
    }
    box_provinces = sorted({b.province for b in boxes})
    adcodes = []
    for p in box_provinces:
        if p in PREFECTURE_ADCODES:
            adcodes.extend(PREFECTURE_ADCODES[p])
    county_polygons: Dict[str, MultiPolygon] = {}
    if adcodes:
        county_polygons = load_county_polygons(adcodes)

    # Comparison mode: run once per model and return a comparison payload
    if args.compare_models:
        compare_started = time.perf_counter()
        scope_meta = build_scope_meta(boxes)
        comparison = {
            "comparison_target_datetime": target_dt.isoformat(),
            "forecast_confidence": confidence,
            "scope_mode": scope_meta["scope_mode"],
            "scope_coverage": scope_meta["scope_coverage"],
            "scope_reduction_reason": scope_meta["scope_reduction_reason"],
            "scope_guardrail": scope_meta["scope_guardrail"],
            "compare_models": args.compare_models,
            "model_results": {},
            "fetch_health": None,
        }
        for model_name in args.compare_models:
            comparison["model_results"][model_name] = run_pipeline(args, boxes, province_polygons, prefecture_polygons, county_polygons, target_dt, confidence, model=model_name)
        comparison["joint_judgement"] = build_joint_judgement(comparison["model_results"], confidence=confidence)

        # Option 1: only trigger a third model recheck when dual-model result is still disputed / single-model-heavy.
        if args.auto_third_model and args.auto_third_model not in comparison["model_results"]:
            summary = comparison["joint_judgement"].get("summary", {})
            should_rerun = summary.get("disputed_count", 0) > 0 or summary.get("single_model_count", 0) > 0
            comparison["third_model_recheck"] = {
                "enabled": True,
                "requested_model": args.auto_third_model,
                "triggered": should_rerun,
                "reason": "initial_dual_model_disputed_or_single_model_heavy" if should_rerun else "initial_dual_model_already_stable",
            }
            if should_rerun:
                comparison["model_results"][args.auto_third_model] = run_pipeline(
                    args, boxes, province_polygons, prefecture_polygons, county_polygons, target_dt, confidence, model=args.auto_third_model
                )
                comparison["joint_judgement"] = build_joint_judgement(comparison["model_results"], confidence=confidence)
                comparison["compare_models"] = list(comparison["model_results"].keys())

        # Aggregate fetch health across model runs.
        fetch_rows = [v.get("fetch_health") for v in comparison["model_results"].values() if v.get("fetch_health")]
        if fetch_rows:
            total_points = sum(x.get("total_points", 0) for x in fetch_rows)
            failed_points = sum(x.get("failed_points", 0) for x in fetch_rows)
            failed_ratio = (failed_points / total_points) if total_points else 0.0
            comparison["fetch_health"] = {
                "status": "degraded" if failed_ratio >= 0.35 else ("partial" if failed_ratio > 0 else "ok"),
                "total_points": total_points,
                "failed_points": failed_points,
                "failed_ratio": round(failed_ratio, 3),
                "user_note": "本轮有部分模型查询出现抓取缺失，结论可参考，但更建议临近出发前再复查。" if failed_ratio > 0 else None,
            }

        # Decision layer: prefer the first model's ranked labels + joint note
        first_model_key = next(iter(comparison["model_results"].keys())) if comparison["model_results"] else None
        first_labels = comparison["model_results"].get(first_model_key, {}).get("region_labels", []) if first_model_key else []
        if not first_labels:
            first_labels = []
            for row in comparison.get("joint_judgement", {}).get("consensus_regions", [])[:3]:
                first_labels.append({
                    "label": row.get("label"),
                    "display_label": row.get("display_label") or row.get("label"),
                    "brief_advice": row.get("joint_brief_advice"),
                    "cloud_stability": None,
                    "longest_usable_streak_hours": None,
                    "refinement_note": row.get("refinement_note"),
                })
        comparison["decision_summary"] = build_decision_summary(
            first_labels,
            confidence=confidence,
            joint=comparison.get("joint_judgement"),
            third_model_recheck=comparison.get("third_model_recheck"),
        )
        if comparison.get("fetch_health", {}).get("user_note"):
            note = comparison["fetch_health"]["user_note"]
            comparison["decision_summary"]["data_quality_note"] = note
            if comparison["decision_summary"].get("final_reply_draft"):
                comparison["decision_summary"]["final_reply_draft"] += f"\n数据完整性：{note}"
            if comparison["decision_summary"]["reply_drafts"].get("concise"):
                comparison["decision_summary"]["reply_drafts"]["concise"] = comparison["decision_summary"]["reply_drafts"]["concise"].rstrip("。") + f"；{note}。"
            if comparison["decision_summary"]["reply_drafts"].get("standard"):
                comparison["decision_summary"]["reply_drafts"]["standard"] += f"\n数据完整性：{note}"
            if comparison["decision_summary"].get("final_reply_draft"):
                comparison["decision_summary"]["reply_drafts"]["detailed"] = comparison["decision_summary"]["final_reply_draft"]

        total_ms = round((time.perf_counter() - compare_started) * 1000, 1)
        comparison["timing"] = {
            "elapsed_ms": total_ms,
            "elapsed_seconds": round(total_ms / 1000.0, 2),
            "per_model_seconds": {
                k: v.get("timing", {}).get("elapsed_seconds") for k, v in comparison["model_results"].items()
            },
        }
        print(json.dumps(comparison, ensure_ascii=False, indent=2 if args.pretty else None))
        return

    # Single-model run
    payload = run_pipeline(args, boxes, province_polygons, prefecture_polygons, county_polygons, target_dt, confidence, model=args.model)
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
