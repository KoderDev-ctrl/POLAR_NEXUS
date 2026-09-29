"""POLAR NEXUS v2.1 core (numpy/stdlib only). Trained artifacts are read, never written.
Operational hazard = P4 + P_kin24 + P6 (time-dependent). M5/M8 = advisory only (structurally barred from routing)."""
from __future__ import annotations
import hashlib, json, math, os, shutil, stat
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
import numpy as np

# =============== errors / status ===============
class ArtifactMismatch(RuntimeError): ...
class InsufficientData(RuntimeError): ...
class ForbiddenHazardInput(RuntimeError): ...
OK, DEGRADED, REPLAY, INSUFFICIENT = "OPERATIONAL_OK", "DEGRADED", "REPLAY_NOT_OPERATIONAL", "INSUFFICIENT_DATA"

# =============== 15. immutability ===============
def sha256_file(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(chunk): h.update(b)
    return h.hexdigest()

def build_manifest(root, files):
    return {rel: sha256_file(os.path.join(root, rel)) for rel in files}

def verify_manifest(manifest, root):
    """Fail closed BEFORE any pickle/joblib/keras load (those execute code)."""
    for rel, want in manifest.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p): raise ArtifactMismatch(f"missing {rel}")
        if sha256_file(p) != want: raise ArtifactMismatch(f"hash mismatch {rel}")
    return True

def freeze_copy(src, dst, expected_sha):
    """Byte-for-byte copy into models/IMMUTABLE, verified, mode 0444. Source is only read."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    if sha256_file(dst) != expected_sha:
        os.remove(dst); raise ArtifactMismatch(f"copy corrupted {src}")
    os.chmod(dst, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return dst

# =============== config: versioned + hashed (11) ===============
@dataclass(frozen=True)
class HazardCfg:
    version: str; sha256: str; mode_default: str; p: dict; provenance: dict
    @staticmethod
    def load(path):
        raw = json.load(open(path))
        canon = json.dumps({"version": raw["version"], "params": raw["params"]}, sort_keys=True, separators=(",", ":"))
        return HazardCfg(raw["version"], hashlib.sha256(canon.encode()).hexdigest(), raw.get("mode_default", "operational"),
                         dict(raw["params"]), dict(raw.get("provenance", {})))
    def __getattr__(self, k):
        try: return self.__dict__["p"][k]
        except KeyError: raise AttributeError(k)
    def stamp(self): return {"hazard_config_version": self.version, "hazard_config_sha256": self.sha256}

# =============== EPSG:3031 ===============
_A, _E2 = 6378137.0, 0.00669437999014
_E = math.sqrt(_E2); _LTS = math.radians(71.0)
def _t(p): return math.tan(math.pi / 4 - p / 2) / ((1 - _E * math.sin(p)) / (1 + _E * math.sin(p))) ** (_E / 2)
def _m(p): return math.cos(p) / math.sqrt(1 - _E2 * math.sin(p) ** 2)
_K = _A * _m(_LTS) / _t(_LTS)
def to_xy(lat, lon):
    phi, lam = math.radians(-lat), math.radians(lon); rho = _K * _t(phi)
    return rho * math.sin(lam), rho * math.cos(lam)
def to_latlon(x, y):
    rho = math.hypot(x, y)
    if rho == 0: return -90.0, 0.0
    ts = rho / _K; phi = math.pi / 2 - 2 * math.atan(ts)
    for _ in range(8): phi = math.pi / 2 - 2 * math.atan(ts * ((1 - _E * math.sin(phi)) / (1 + _E * math.sin(phi))) ** (_E / 2))
    return -math.degrees(phi), math.degrees(math.atan2(x, y))
def grid_scale(lat):
    phi = math.radians(-lat); return _K * _t(phi) / (_A * _m(phi)) if abs(lat) < 90 else 1.0

# =============== 7. exact temporal semantics on every point ===============
@dataclass(frozen=True)
class Point:
    role: str            # P4 | P_kin24 | P6 | M5_ADV | M8_ADV
    kind: str            # observed | derived | predicted | advisory
    source: str          # dataset_4 | persistence_baseline | model_6 | model_5 | model_8
    artifact_version: str
    role_in_hazard: str  # operational | baseline | advisory
    x_m: float; y_m: float; lat: float; lon: float
    base_time: datetime  # instant of the last observation the point is derived from
    valid_at: datetime   # instant this position refers to
    horizon_h: float     # (valid_at - base_time) in hours; validated
    computed_at: datetime
    quality: dict = field(default_factory=dict)
    limitations: tuple = ()
    def __post_init__(self):
        for n in ("base_time", "valid_at", "computed_at"):
            if getattr(self, n).tzinfo is None: raise ValueError(f"{n} must be tz-aware UTC")
        if abs((self.valid_at - self.base_time).total_seconds() / 3600 - self.horizon_h) > 1e-6:
            raise ValueError("horizon_h inconsistent with base_time/valid_at")
        if self.kind == "observed" and self.horizon_h != 0: raise ValueError("observation must have horizon 0")
        if self.kind in ("predicted", "derived", "advisory") and self.horizon_h <= 0: raise ValueError("forecast needs horizon>0")
        if self.role_in_hazard == "advisory" and self.kind != "advisory": raise ValueError("advisory role requires kind=advisory")
    def to_dict(self):
        d = asdict(self)
        for n in ("base_time", "valid_at", "computed_at"): d[n] = getattr(self, n).isoformat()
        return d

def mk_point(role, kind, source, ver, rih, x, y, base, horizon_h, now, quality=None, limitations=()):
    lat, lon = to_latlon(x, y)
    return Point(role, kind, source, ver, rih, float(x), float(y), lat, lon, base, base + timedelta(hours=horizon_h),
                 float(horizon_h), now, quality or {}, tuple(limitations))

# =============== 4/13. Dataset-4 freshness + live-ingest gates ===============
def check_ingest(watermark, now, cfg, mode):
    """Operational mode requires a live ingest. Replay is allowed only when labelled REPLAY."""
    lag_h = (now - watermark).total_seconds() / 3600
    if mode == "operational" and lag_h > cfg.ingest_max_lag_h:
        raise InsufficientData(f"INGEST_NOT_LIVE: store watermark {lag_h:.0f} h old (> {cfg.ingest_max_lag_h} h)")
    return lag_h

def d4_clean_track(df, iceberg_id, now, cfg, min_quality=0):
    raw_df = df[df.iceberg_id == iceberg_id]
    if raw_df.empty: raise InsufficientData(f"unknown iceberg {iceberg_id}")
    g = raw_df.sort_values("datetime_utc")
    g = g[g.source_quality >= min_quality]
    if g.empty: raise InsufficientData(f"no valid fixes for {iceberg_id}")
    xy = np.array([to_xy(a, b) for a, b in zip(g.latitude.to_numpy(), g.longitude.to_numpy())])
    
    t_sec = (g.datetime_utc - g.datetime_utc.iloc[0]).dt.total_seconds().to_numpy()
    start = 0
    for i in range(len(g)-1):
        dt_d = max((t_sec[i+1] - t_sec[i]) / 86400, 1e-6)
        if np.hypot(*(xy[i+1] - xy[i])) / 1000 / dt_d <= cfg.d4_max_step_km:
            start = i
            break
    idx = [start]
    for i in range(start + 1, len(g)):
        dt_d = max((t_sec[i] - t_sec[idx[-1]]) / 86400, 1e-6)
        if np.hypot(*(xy[i] - xy[idx[-1]])) / 1000 / dt_d <= cfg.d4_max_step_km: idx.append(i)
        
    g, xy = g.iloc[idx], xy[idx]
    last = g.datetime_utc.iloc[-1].to_pydatetime()
    age_h = (now - last).total_seconds() / 3600
    if age_h > cfg.d4_max_age_h: raise InsufficientData(f"P4_STALE: last valid fix {age_h:.0f} h old (> {cfg.d4_max_age_h} h)")
    if age_h < -1e-6: raise InsufficientData("P4 timestamp in the future")
    if len(g) < cfg.d4_min_fixes: raise InsufficientData(f"need >={cfg.d4_min_fixes} valid fixes")
    t = (g.datetime_utc - g.datetime_utc.iloc[-1]).dt.total_seconds().to_numpy() / 3600.0
    q_dist = {int(k): int(v) for k, v in raw_df.source_quality.value_counts().to_dict().items()}
    return dict(t_h=t, x=xy[:, 0], y=xy[:, 1], base_time=last, age_h=age_h, 
                n_raw=len(raw_df), n_clean=len(g), q_dist=q_dist)

def kinematic_velocity(t_h, x, y, n=3):
    dt = np.diff(t_h[-(n + 1):]); vx = np.diff(x[-(n + 1):]) / dt; vy = np.diff(y[-(n + 1):]) / dt
    return float(np.median(vx)), float(np.median(vy))     # m/h

# =============== 9/10. persistence = baseline; M6 validation limits exposed ===============
def load_m6_limitations(metadata_path):
    m = json.load(open(metadata_path))
    return {
        "median_error_km": m["median_error_km"], "p90_error_km": m["p90_error_km"], "max_error_km": m["max_error_km"],
        "persistence_median_error_km": m["persistence_median_error_km"],
        "improvement_over_persistence_pct": m["improvement_over_persistence_pct"],
        "beats_persistence": m["improvement_over_persistence_pct"] > 0,
        "caveats": [
            f"Does not beat persistence: median {m['median_error_km']:.3f} km vs {m['persistence_median_error_km']:.3f} km ({m['improvement_over_persistence_pct']:.1f}%).",
            f"Tail error up to {m['max_error_km']:.1f} km (P90 {m['p90_error_km']:.2f} km).",
            "Validated on linearly interpolated hourly series (smooth by construction); skill on raw irregular observations is unmeasured.",
            "Per-iceberg walk-forward split: same icebergs in train/val/test; no unseen-iceberg holdout.",
        ]}

def kin_baseline_limitation(cfg):
    return (f"Persistence baseline, not truth: measured D4 24 h P90 error {cfg.r24_km} km for moving icebergs.",)

# =============== 5. Model 5 adapter (km in / m out) + advisory (2) ===============
M5_FEATURES = ["x_t","y_t","prev_dx","prev_dy","prev_speed","area_t","perimeter_t","long_axis_t","short_axis_t",
               "mass_t","aspect_t","area_log_t","mass_log_t","perimeter_log_t","major_log_t","minor_log_t","prev_direction"]
def m5_predict(pipeline, feats, x_m, y_m):
    """pipeline = pickle.load(V6_1_final_model.pkl)['model']  (StandardScaler+Ridge).
    feature_scaler.pkl is never loaded/applied (6). x_t,y_t km; dx,dy m."""
    f = dict(feats); f["x_t"], f["y_t"] = x_m / 1000.0, y_m / 1000.0
    row = np.array([[f[k] for k in M5_FEATURES]], float)
    if not np.isfinite(row).all(): raise ValueError("M5 features incomplete - refuse, do not impute")
    dx, dy = pipeline.predict(row)[0]
    return x_m + dx, y_m + dy, (float(dx), float(dy))

M5_HORIZON_H = 365 * 24.0
def m5_advisory(pipeline, feats, x_m, y_m, base_time, now, ver="V6.1"):
    """Long-horizon (annual transition) advisory. role_in_hazard='advisory' => cannot enter routing."""
    xn, yn, (dx, dy) = m5_predict(pipeline, feats, x_m, y_m)
    return mk_point("M5_ADV", "advisory", "model_5", ver, "advisory", xn, yn, base_time, M5_HORIZON_H, now,
                    {"disp_m": math.hypot(dx, dy), "nominal_horizon": "annual transition"},
                    ("Annual-transition model (train 2020->22, test 22->23); horizon is nominal ~365 d.",
                     "Ridge does not beat persistence on its own test set (mean 0.02717 vs 0.02678 km).",
                     "Not used in the operational 24 h hazard."))

# =============== 3. Model 8 adapter = advisory only ===============
M8_BLEND = (0.8, 0.2)
def m8_blend(xgb, et, w=M8_BLEND): return w[0] * np.asarray(xgb) + w[1] * np.asarray(et)
def m8_advisory(models, feat_names, feats, x_m, y_m, base_time, now, max_imputed_frac, ver="CRYOX_V9"):
    """models: dict(xgb_e,xgb_n,et_e,et_n,imputer) with .predict/.transform. Packaged imputer is part of the contract,
    but heavy imputation is refused and reported. Output magnitudes are km (as in CRYOX_V9_test_predictions.csv).
    PARITY UNVERIFIED: test features are not in the package, so raw predict() -> final_* needs a golden test on your dataset."""
    row = np.array([[feats.get(k, np.nan) for k in feat_names]], float)
    frac = float(np.isnan(row).mean())
    if frac > max_imputed_frac: raise ValueError(f"M8 imputed fraction {frac:.2f} > {max_imputed_frac}")
    X = models["imputer"].transform(row)
    e = float(m8_blend(models["xgb_e"].predict(X)[0], models["et_e"].predict(X)[0]))
    n = float(m8_blend(models["xgb_n"].predict(X)[0], models["et_n"].predict(X)[0]))
    return mk_point("M8_ADV", "advisory", "model_8", ver, "advisory", x_m + e * 1000, y_m + n * 1000, base_time, 365 * 24.0, now,
                    {"east_km": e, "north_km": n, "imputed_fraction": frac, "parity": "UNVERIFIED"},
                    ("Next-observation model, horizon 90-365 d (val/test all 365 d).",
                     "Test mean error 0.753 km vs zero-motion 0.743 km: no skill over 'not moving'.",
                     "Not used in routing or the operational hazard."))

# =============== 6/8/12. Hazard: time-dependent, configurable, metrics ===============
def _ang(a, b):
    na, nb = np.hypot(*a), np.hypot(*b)
    if na < 1e-9 or nb < 1e-9: return None
    return float(np.degrees(np.arccos(np.clip(a @ b / (na * nb), -1, 1))))

class Hazard:
    def __init__(self, p4, pk24, p6, cfg: HazardCfg):
        self.cfg = cfg; self.H = cfg.horizon_h
        self.p4 = np.array([p4.x_m, p4.y_m]); self.pk = np.array([pk24.x_m, pk24.y_m])
        self.p6 = None if p6 is None else np.array([p6.x_m, p6.y_m])
        self.base_time = p4.base_time; self.k = grid_scale(p4.lat)
        self.vk = (self.pk - self.p4) / self.H
        self.v6 = self.vk if self.p6 is None else (self.p6 - self.p4) / self.H
        self.points = (p4, pk24) + (() if p6 is None else (p6,))
    def centres(self, h): return self.p4 + self.vk * h, self.p4 + self.v6 * h
    def radius_km(self, h):
        c = self.cfg; h = max(h, 0.0)
        r = c.r0_km + (c.r24_km - c.r0_km) * min(h, self.H) / self.H
        if h > self.H: r += c.v90_km_day * (h - self.H) / 24.0
        return r
    def radius_grid_m(self, h): return self.radius_km(h) * 1000.0 * self.k
    def unbounded(self, h): return self.radius_km(h) > self.cfg.max_radius_km
    def clearance_m(self, xy, h):
        a, b = self.centres(h); ab = b - a; L2 = float(ab @ ab); xy = np.asarray(xy, float)
        s = 0.0 if L2 == 0 else min(1.0, max(0.0, float((xy - a) @ ab) / L2))
        return float(np.hypot(*(xy - (a + s * ab)))) - self.radius_grid_m(h)      # grid m (>= true m / k)
    def field(self, hours):
        """HazardField: one entry per requested t (hours since base_time) for RouteX16 / Supabase."""
        out = []
        for h in hours:
            a, b = self.centres(h)
            out.append(dict(h=h, valid_at=(self.base_time + timedelta(hours=h)).isoformat(),
                            c_kin=to_latlon(*a), c_m6=to_latlon(*b), radius_km=self.radius_km(h), unbounded=self.unbounded(h)))
        return out
    def metrics(self):
        k = self.k; d = lambda v: float(np.hypot(*v)) / 1000 / k
        if self.p6 is None: return dict(triangle_available=False, triangle_area_km2=0.0, disagreement_km=None)
        v1, v2 = self.pk - self.p4, self.p6 - self.p4
        area = 0.5 * abs(float(v1[0]*v2[1] - v1[1]*v2[0])) / 1e6 / k**2
        edges = [d(self.pk - self.p4), d(self.p6 - self.p4), d(self.p6 - self.pk)]
        v_k, v_6 = self.pk - self.p4, self.p6 - self.p4
        return dict(triangle_available=True, triangle_area_km2=area, disagreement_km=edges[2],
                    disagreement_ratio=edges[2] / self.cfg.r24_km, kin_disp_km=edges[0], m6_disp_km=edges[1],
                    heading_diff_deg=_ang(v_k, v_6), speed_ratio_m6_over_kin=(edges[1] / edges[0] if edges[0] > 1e-9 else None),
                    compactness=area / max(max(edges) ** 2, 1e-12))
    def envelope(self):
        """Triangle(P4, P_kin24, P6) buffered by r24. Swept envelope over [t_obs, t_obs+24h], never a same-instant region."""
        m = self.metrics(); r = self.radius_km(self.H)
        pts = [self.p4, self.pk] + ([] if self.p6 is None else [self.p6])
        span = max(np.ptp([p[0] for p in pts]), np.ptp([p[1] for p in pts]), 1.0)
        if self.p6 is not None:
            v1, v2 = self.pk - self.p4, self.p6 - self.p4
            area_g = 0.5 * abs(float(v1[0]*v2[1] - v1[1]*v2[0]))
        else:
            area_g = 0.0
        kind = "buffered_triangle" if (self.p6 is not None and area_g / span**2 >= self.cfg.collinear_tol) else "buffered_linestring"
        return dict(kind=kind, vertices=[dict(role=p.role, lat=p.lat, lon=p.lon, valid_at=p.valid_at.isoformat(), horizon_h=p.horizon_h) for p in self.points],
                    buffer_km=r, unbounded=self.unbounded(self.H), metrics=m,
                    temporal=dict(semantics="swept_envelope_not_same_instant", start=self.base_time.isoformat(),
                                  end=(self.base_time + timedelta(hours=self.H)).isoformat()))
    def risk_level(self, min_clearance_grid_m):
        c = self.cfg; m = self.metrics(); r = self.radius_grid_m(self.H)
        ratio = m.get("disagreement_ratio") or 0.0
        if min_clearance_grid_m < 0 or ratio >= c.disagreement_high_ratio: return "HIGH"
        if min_clearance_grid_m < c.clearance_medium_factor * r or ratio >= c.disagreement_medium_ratio: return "MEDIUM"
        return "LOW"

@dataclass(frozen=True)
class RouteHazardInput:
    hazard: Hazard; cfg_stamp: dict; base_time: datetime; degraded: bool

def build_route_hazard(points, cfg):
    """The ONLY constructor RouteX16 may receive. Advisory points (M5/M8) are rejected structurally."""
    by = {p.role: p for p in points}
    bad = [p.role for p in points if p.role_in_hazard == "advisory" or p.source in ("model_5", "model_8")]
    if bad: raise ForbiddenHazardInput(f"advisory points barred from routing: {bad}")
    if "P4" not in by or "P_kin24" not in by: raise InsufficientData("P4 and P_kin24 required")
    if len({p.base_time for p in points}) != 1: raise ForbiddenHazardInput("points must share base_time")
    return RouteHazardInput(Hazard(by["P4"], by["P_kin24"], by.get("P6"), cfg), cfg.stamp(), by["P4"].base_time, "P6" not in by)

def cpa_tcpa(route_xyh, hz: Hazard, dt_h=0.05):
    """route_xyh: [[x,y,h_since_base_time],...]; every waypoint compared with the hazard AT ITS OWN TIME."""
    R = np.asarray(route_xyh, float); best_c, best_h, best_sep = math.inf, None, math.inf
    for i in range(len(R) - 1):
        n = max(1, int((R[i + 1, 2] - R[i, 2]) / dt_h))
        for s in np.linspace(0, 1, n + 1):
            p = R[i, :2] + s * (R[i + 1, :2] - R[i, :2]); h = R[i, 2] + s * (R[i + 1, 2] - R[i, 2])
            c = hz.clearance_m(p, h); a, b = hz.centres(h)
            best_sep = min(best_sep, float(min(np.hypot(*(p - a)), np.hypot(*(p - b)))))
            if c < best_c: best_c, best_h = c, h
    return dict(min_clearance_grid_m=best_c, tcpa_h=best_h, cpa_grid_m=best_sep)
