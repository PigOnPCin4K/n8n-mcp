#!/usr/bin/env python3
"""Lookahead-free backtest of the "Crypto Lifer" mechanical rules on BTCUSDT.

Data: Binance public monthly 15m kline archives (data.binance.vision), resampled
to higher timeframes. Results are reported in R multiples (1R = initial risk),
net of 0.07% per side (0.05% fee + 0.02% slippage).

Rules
  S1  200 SMA close cross, stop beyond min(SMA200, 10-bar low) - 0.1 ATR, 3R target
  S2  "The Model": trend (close>SMA200, SMA21>SMA200) + low touches SMA21, 3R target
  S3  S2 with stop moved to break-even once +1R is reached
  S4  S2 with 50% off at 2R, then BE stop, rest exits on stretch or 6R
Filters (applied to S1/S2)
  F1  daily close vs daily SMA200       F1b weekly close vs weekly SMA200
  F2  next-higher TF close vs its SMA200 F3  StochRSI %K<30 in last 3 bars and K>D
  F4  calendar: no entries Sat, Sun, Mon<18:00 ET, Fri>=12:00 ET

Lookahead protections
  * signals are computed on closed bars; entry is at the next bar's open
  * a higher-TF bar is only visible once its close time <= the decision time
  * if stop and target are touched in the same bar, the stop is assumed first

Usage
  python -I backtest.py                          # full matrix -> results.json
  python -I backtest.py --tf 1h --strategy S2 --filter F1 --show-trades 5
  python -I backtest.py --check                  # sanity checks only
"""
from __future__ import annotations

import argparse
import io
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data"
START = pd.Timestamp("2019-01-01", tz="UTC")       # first allowed signal bar
COST_PER_SIDE = 0.0005 + 0.0002                     # fee + slippage, fraction of notional
YEARS = list(range(2019, 2027))
MIN_SAMPLE = 100

TF_RULES = {"15m": "15min", "1h": "1h", "4h": "4h", "1D": "1D", "3D": "3D", "1W": "W-MON"}
TF_DELTA = {"15m": pd.Timedelta("15min"), "1h": pd.Timedelta("1h"), "4h": pd.Timedelta("4h"),
            "1D": pd.Timedelta("1D"), "3D": pd.Timedelta("3D"), "1W": pd.Timedelta("7D")}
NEXT_TF = {"15m": "1h", "1h": "4h", "4h": "1D"}
EXEC_TFS = ["15m", "1h", "4h"]


# ----------------------------------------------------------------------------- data

def load_15m(data_dir: Path) -> pd.DataFrame:
    frames = []
    for zp in sorted(data_dir.glob("BTCUSDT-15m-*.zip")):
        with zipfile.ZipFile(zp) as zf:
            raw = zf.read(zf.namelist()[0]).decode()
        df = pd.read_csv(io.StringIO(raw), header=None, usecols=range(6),
                         names=["open_time", "open", "high", "low", "close", "volume"])
        df = df[pd.to_numeric(df["open_time"], errors="coerce").notna()]   # drop header rows
        frames.append(df.astype("float64"))
    df = pd.concat(frames, ignore_index=True)
    ts = df["open_time"].astype("int64")
    # Binance switched to microsecond timestamps in 2025; normalise to ms.
    ts = np.where(ts > 10**14, ts // 1000, ts)
    df.index = pd.to_datetime(ts, unit="ms", utc=True)
    df = df.drop(columns="open_time")
    df = df[~df.index.duplicated(keep="first")].sort_index()
    df.index.name = "open_time"
    return df


def resample(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    if tf == "15m":
        return df.copy()
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    out = df.resample(TF_RULES[tf], closed="left", label="left").agg(agg)
    return out.dropna(subset=["open"])


# ----------------------------------------------------------------------------- indicators

def rma(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]
    for n in (21, 50, 200):
        df[f"sma{n}"] = c.rolling(n).mean()
    delta = c.diff()
    rs = rma(delta.clip(lower=0), 14) / rma(-delta.clip(upper=0), 14)
    df["rsi"] = 100 - 100 / (1 + rs)
    lo, hi = df["rsi"].rolling(14).min(), df["rsi"].rolling(14).max()
    stoch = 100 * (df["rsi"] - lo) / (hi - lo).replace(0, np.nan)
    df["k"] = stoch.rolling(3).mean()
    df["d"] = df["k"].rolling(3).mean()
    prev_close = c.shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev_close).abs(),
                    (df["low"] - prev_close).abs()], axis=1).max(axis=1)
    df["atr"] = rma(tr, 14)
    return df


def align_htf(ltf: pd.DataFrame, ltf_tf: str, htf: pd.DataFrame, htf_tf: str,
              cols: list[str]) -> pd.DataFrame:
    """Values of the last FULLY CLOSED htf bar as of each ltf bar's close (decision time)."""
    decision = (ltf.index + TF_DELTA[ltf_tf]).asi8
    htf_close = (htf.index + TF_DELTA[htf_tf]).asi8
    idx = np.searchsorted(htf_close, decision, side="right") - 1
    out = pd.DataFrame(index=ltf.index)
    for col in cols:
        vals = htf[col].to_numpy()
        out[col] = np.where(idx >= 0, vals[np.clip(idx, 0, None)], np.nan)
    out["_htf_idx"] = idx
    return out


# ----------------------------------------------------------------------------- signals

@dataclass
class Spec:
    strategy: str              # S1..S4, or RAND
    filters: tuple = ()        # subset of F1, F1b, F2, F3, F4
    target_r: float = 3.0
    consolidation: bool = False

    @property
    def name(self) -> str:
        parts = [self.strategy] + list(self.filters)
        if self.consolidation:
            parts.append("cons")
        if self.target_r != 3.0 and self.strategy != "S4":
            parts.append(f"T{self.target_r:g}R")
        return "+".join(parts)


def build_frame(raw15: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Execution-TF bars with indicators and aligned higher-TF context."""
    df = add_indicators(resample(raw15, tf))
    daily = add_indicators(resample(raw15, "1D"))
    weekly = add_indicators(resample(raw15, "1W"))
    nxt = add_indicators(resample(raw15, NEXT_TF[tf]))
    for prefix, htf, htf_tf in (("d_", daily, "1D"), ("w_", weekly, "1W"), ("n_", nxt, NEXT_TF[tf])):
        a = align_htf(df, tf, htf, htf_tf, ["close", "sma200"])
        df[prefix + "close"], df[prefix + "sma200"] = a["close"], a["sma200"]
    entry_et = (df.index + TF_DELTA[tf]).tz_convert("America/New_York")
    dow, hour = entry_et.dayofweek, entry_et.hour
    blocked = (dow >= 5) | ((dow == 0) & (hour < 18)) | ((dow == 4) & (hour >= 12))
    df["cal_ok"] = ~np.asarray(blocked)
    return df


def signals(df: pd.DataFrame, spec: Spec):
    """Return long/short boolean signal arrays and their stop prices (all at bar close)."""
    c, h, l, atr = df["close"], df["high"], df["low"], df["atr"]
    s21, s200 = df["sma21"], df["sma200"]
    ll10, hh10 = l.rolling(10).min(), h.rolling(10).max()

    if spec.strategy == "S1":
        long_sig = (c > s200) & (c.shift() < s200.shift())
        short_sig = (c < s200) & (c.shift() > s200.shift())
    else:  # S2/S3/S4 share The Model entry
        long_sig = (c > s200) & (s21 > s200) & (l <= s21)
        short_sig = (c < s200) & (s21 < s200) & (h >= s21)
        if spec.consolidation:
            rng = h.shift().rolling(10).max() - l.shift().rolling(10).min()
            tight = rng < 2.5 * atr
            long_sig &= tight
            short_sig &= tight
    long_stop = np.minimum(s200, ll10) - 0.1 * atr
    short_stop = np.maximum(s200, hh10) + 0.1 * atr

    for f in spec.filters:
        if f == "F1":
            long_sig &= df["d_close"] > df["d_sma200"]
            short_sig &= df["d_close"] < df["d_sma200"]
        elif f == "F1b":
            long_sig &= df["w_close"] > df["w_sma200"]
            short_sig &= df["w_close"] < df["w_sma200"]
        elif f == "F2":
            long_sig &= df["n_close"] > df["n_sma200"]
            short_sig &= df["n_close"] < df["n_sma200"]
        elif f == "F3":
            k, d = df["k"], df["d"]
            long_sig &= (k.rolling(3).min() < 30) & (k > d)
            short_sig &= (k.rolling(3).max() > 70) & (k < d)
        elif f == "F4":
            long_sig &= df["cal_ok"]
            short_sig &= df["cal_ok"]
        else:
            raise ValueError(f"unknown filter {f}")

    live = df.index >= START
    return ((long_sig & live).to_numpy(), (short_sig & live).to_numpy(),
            long_stop.to_numpy(), short_stop.to_numpy())


# ----------------------------------------------------------------------------- execution

@dataclass
class Bars:
    t: np.ndarray
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    atr: np.ndarray
    stretch_long: np.ndarray
    stretch_short: np.ndarray

    @classmethod
    def from_frame(cls, df: pd.DataFrame) -> "Bars":
        ext = (df["close"] - df["sma21"]).abs() > 3 * df["atr"]
        return cls(df.index.to_numpy(), *(df[x].to_numpy() for x in ("open", "high", "low", "close", "atr")),
                   (ext & (df["k"] > 80)).to_numpy(), (ext & (df["k"] < 20)).to_numpy())


def first_hit(b: Bars, start: int, side: int, stop: float, target: float, extra=None):
    """First bar >= start where stop/target is touched (stop wins ties) or extra[] is true.
    Returns (bar index, kind) with kind in {'stop', 'target', 'extra', 'eod'}."""
    n, j, step = len(b.o), start, 64
    while j < n:
        e = min(n, j + step)
        if side > 0:
            s, t = b.l[j:e] <= stop, b.h[j:e] >= target
        else:
            s, t = b.h[j:e] >= stop, b.l[j:e] <= target
        hit = s | t if extra is None else s | t | extra[j:e]
        if hit.any():
            k = int(np.argmax(hit))
            return j + k, "stop" if s[k] else "target" if t[k] else "extra"
        j, step = e, step * 2
    return n - 1, "eod"


def stop_fill(b: Bars, j: int, side: int, stop: float) -> float:
    # A bar that opens through the stop fills at the (worse) open.
    return min(stop, b.o[j]) if side > 0 else max(stop, b.o[j])


def manage(b: Bars, i: int, side: int, entry: float, stop: float, spec: Spec):
    """Simulate one trade entered at open of bar i. Returns (legs, exit_bar, flat_bar, reason)
    where legs is a list of (fraction, exit_price)."""
    risk = abs(entry - stop)
    px = lambda r: entry + side * r * risk  # noqa: E731
    n = len(b.o)

    if spec.strategy in ("S1", "S2", "RAND"):
        j, kind = first_hit(b, i, side, stop, px(spec.target_r))
        if kind == "stop":
            return [(1.0, stop_fill(b, j, side, stop))], j, j, "stop"
        if kind == "target":
            return [(1.0, px(spec.target_r))], j, j, "target"
        return [(1.0, b.c[j])], j, j, "eod"

    trigger = 1.0 if spec.strategy == "S3" else 2.0
    j, kind = first_hit(b, i, side, stop, px(trigger))
    if kind == "stop":
        return [(1.0, stop_fill(b, j, side, stop))], j, j, "stop"
    if kind == "eod":
        return [(1.0, b.c[j])], j, j, "eod"

    if spec.strategy == "S3":
        # +1R reached in bar j; BE applies from the next bar (original stop was not hit in j).
        final = px(spec.target_r)
        hit_final = (b.h[j] >= final) if side > 0 else (b.l[j] <= final)
        if hit_final:
            return [(1.0, final)], j, j, "target"
        if j + 1 >= n:
            return [(1.0, b.c[j])], j, j, "eod"
        k, kind = first_hit(b, j + 1, side, entry, final)
        if kind == "stop":
            return [(1.0, stop_fill(b, k, side, entry))], k, k, "breakeven"
        if kind == "target":
            return [(1.0, final)], k, k, "target"
        return [(1.0, b.c[k])], k, k, "eod"

    # S4: half off at 2R in bar j, then BE stop / 6R / stretch exit at next open.
    legs = [(0.5, px(2.0))]
    six = px(6.0)
    if (b.h[j] >= six) if side > 0 else (b.l[j] <= six):
        return legs + [(0.5, six)], j, j, "6R"
    stretch = b.stretch_long if side > 0 else b.stretch_short
    if stretch[j] and j + 1 < n:
        return legs + [(0.5, b.o[j + 1])], j + 1, j + 1, "stretch"
    if j + 1 >= n:
        return legs + [(0.5, b.c[j])], j, j, "eod"
    k, kind = first_hit(b, j + 1, side, entry, six, extra=stretch)
    if kind == "stop":
        return legs + [(0.5, stop_fill(b, k, side, entry))], k, k, "breakeven"
    if kind == "target":
        return legs + [(0.5, six)], k, k, "6R"
    if kind == "extra" and k + 1 < n:
        return legs + [(0.5, b.o[k + 1])], k + 1, k + 1, "stretch"
    return legs + [(0.5, b.c[k])], k, k, "eod"


def trade_record(b: Bars, sig_bar: int, side: int, entry: float, stop: float, legs, exit_bar, reason):
    risk = abs(entry - stop)
    gross = sum(f * side * (p - entry) / risk for f, p in legs)
    cost = COST_PER_SIDE * (entry + sum(f * p for f, p in legs)) / risk
    return {"signal_time": str(pd.Timestamp(b.t[sig_bar])), "entry_time": str(pd.Timestamp(b.t[sig_bar + 1])),
            "exit_time": str(pd.Timestamp(b.t[exit_bar])), "side": "long" if side > 0 else "short",
            "entry": round(float(entry), 2), "stop": round(float(stop), 2),
            "risk_atr": round(float(risk / b.atr[sig_bar]), 3), "reason": reason,
            "gross_r": float(gross), "cost_r": float(cost), "net_r": float(gross - cost)}


def run_strategy(df: pd.DataFrame, b: Bars, spec: Spec) -> list[dict]:
    long_sig, short_sig, long_stop, short_stop = signals(df, spec)
    cand = np.flatnonzero(long_sig ^ short_sig)
    trades, free, n = [], 0, len(b.o)
    use_atr_bounds = spec.strategy in ("S2", "S3", "S4")
    for i in cand:
        if i < free or i + 1 >= n:
            continue
        side = 1 if long_sig[i] else -1
        stop = long_stop[i] if side > 0 else short_stop[i]
        entry = b.o[i + 1]
        risk = side * (entry - stop)
        if not np.isfinite(risk) or risk <= 0:
            continue
        if use_atr_bounds and not (0.5 * b.atr[i] <= risk <= 4 * b.atr[i]):
            continue
        legs, exit_bar, flat_bar, reason = manage(b, i + 1, side, entry, stop, spec)
        trades.append(trade_record(b, i, side, entry, stop, legs, exit_bar, reason))
        free = flat_bar
    return trades


def run_random(df: pd.DataFrame, b: Bars, ref_trades: list[dict], target_r: float,
               n_sims: int, seed: int) -> list[float]:
    """Expectancy of random entries matching the reference trade count and stop geometry."""
    if not ref_trades:
        return []
    rng = np.random.default_rng(seed)
    risk_atr = np.array([t["risk_atr"] for t in ref_trades])
    live = np.flatnonzero((df.index >= START) & np.isfinite(b.atr))[:-1]
    spec = Spec("RAND", target_r=target_r)
    exps = []
    for _ in range(n_sims):
        bars = rng.choice(live, size=len(ref_trades), replace=True)
        sides = rng.choice([-1, 1], size=len(bars))
        k = rng.choice(risk_atr, size=len(bars), replace=True)
        rs = []
        for i, side, m in zip(bars, sides, k):
            entry = b.o[i + 1]
            stop = entry - side * m * b.atr[i]
            legs, exit_bar, _, reason = manage(b, i + 1, side, entry, stop, spec)
            rs.append(trade_record(b, i, side, entry, stop, legs, exit_bar, reason)["net_r"])
        exps.append(float(np.mean(rs)))
    return exps


# ----------------------------------------------------------------------------- metrics

def metrics(trades: list[dict]) -> dict:
    r = np.array([t["net_r"] for t in trades], dtype=float)
    n = len(r)
    if n == 0:
        return {"trades": 0}
    gross = np.array([t["gross_r"] for t in trades])
    cum = np.cumsum(r)
    dd = np.max(np.maximum.accumulate(np.concatenate([[0.0], cum]))[1:] - cum)
    streak = best = 0
    for x in r:
        streak = streak + 1 if x < 0 else 0
        best = max(best, streak)
    pos, neg = r[r > 0].sum(), -r[r < 0].sum()
    years = pd.to_datetime([t["entry_time"] for t in trades]).year
    per_year = {str(y): round(float(r[years == y].sum()), 2) for y in YEARS}
    sd = r.std(ddof=1) if n > 1 else np.nan
    out = {
        "trades": n, "win_rate": round(float((r > 0).mean()), 4),
        "avg_gross_r": round(float(gross.mean()), 4), "avg_cost_r": round(float((gross - r).mean()), 4),
        "expectancy_r": round(float(r.mean()), 4),
        "profit_factor": round(float(pos / neg), 3) if neg > 0 else None,
        "total_r": round(float(r.sum()), 2), "max_dd_r": round(float(dd), 2),
        "longest_losing_streak": best,
        "t_stat": round(float(r.mean() / (sd / np.sqrt(n))), 2) if n > 1 and sd > 0 else None,
        "years_positive": int(sum(v > 0 for y, v in per_year.items() if (years == int(y)).any())),
        "years_traded": int(len(set(years))),
        "per_year_r": per_year, "low_sample": n < MIN_SAMPLE,
    }
    for side in ("long", "short"):
        rs = np.array([t["net_r"] for t in trades if t["side"] == side])
        out[side] = {"trades": len(rs), "win_rate": round(float((rs > 0).mean()), 4) if len(rs) else None,
                     "expectancy_r": round(float(rs.mean()), 4) if len(rs) else None,
                     "total_r": round(float(rs.sum()), 2)}
    return out


def buy_and_hold(raw15: pd.DataFrame) -> dict:
    d = resample(raw15[raw15.index >= START], "1D")["close"]
    first = float(raw15[raw15.index >= START]["open"].iloc[0])
    eq = d / first
    years = (d.index[-1] - d.index[0]).days / 365.25
    return {"start": str(d.index[0].date()), "end": str(d.index[-1].date()),
            "start_price": round(first, 2), "end_price": round(float(d.iloc[-1]), 2),
            "total_return_pct": round(float(eq.iloc[-1] - 1) * 100, 1),
            "cagr_pct": round(float(eq.iloc[-1] ** (1 / years) - 1) * 100, 1),
            "max_drawdown_pct": round(float((1 - eq / eq.cummax()).max()) * 100, 1)}


# ----------------------------------------------------------------------------- checks

def sanity_checks(raw15: pd.DataFrame) -> None:
    print("== sanity checks")
    months = raw15.index.tz_convert(None).to_period("M").nunique()
    assert raw15.index.is_monotonic_increasing and raw15.index.is_unique
    assert raw15.index[-1] > pd.Timestamp("2025-02-01", tz="UTC"), "2025+ timestamps not normalised"
    gaps = raw15.index.to_series().diff().gt(pd.Timedelta("15min")).sum()
    print(f"15m bars {len(raw15)}  {raw15.index[0]} .. {raw15.index[-1]}  months={months} gaps={gaps}")

    h4 = resample(raw15, "4h")
    t0 = pd.Timestamp("2024-03-05 08:00", tz="UTC")
    sl = raw15.loc[t0:t0 + pd.Timedelta("4h") - pd.Timedelta("1ns")]
    assert len(sl) == 16 and h4.loc[t0, "high"] == sl["high"].max() and h4.loc[t0, "open"] == sl["open"].iloc[0]
    assert h4.loc[t0, "close"] == sl["close"].iloc[-1] and h4.loc[t0, "low"] == sl["low"].min()
    wk = resample(raw15, "1W")
    assert (wk.index.dayofweek == 0).all(), "weekly bars must open on Monday"
    print("resample OK (4h bar matches its 16 x 15m bars; weekly bars open Monday)")

    d = add_indicators(resample(raw15, "1D"))
    t = pd.Timestamp("2023-06-15", tz="UTC")
    pos = d.index.get_loc(t)
    manual = sum(d["close"].iloc[pos - 199:pos + 1]) / 200
    assert abs(manual - d.loc[t, "sma200"]) < 1e-6
    print(f"daily SMA200 on {t.date()}: manual={manual:.4f} rolling={d.loc[t, 'sma200']:.4f}")

    h1 = add_indicators(resample(raw15, "1h"))
    a = align_htf(h1, "1h", d, "1D", ["close", "sma200"])
    for ts in ["2022-05-10 23:00", "2022-05-11 00:00", "2022-05-11 13:00", "2024-01-01 22:00"]:
        ts = pd.Timestamp(ts, tz="UTC")
        decision = ts + TF_DELTA["1h"]
        k = int(a.loc[ts, "_htf_idx"])
        htf_open = d.index[k]
        assert htf_open + TF_DELTA["1D"] <= decision
        assert k + 1 >= len(d) or d.index[k + 1] + TF_DELTA["1D"] > decision
        print(f"1h bar {ts} (decision {decision}) -> daily bar {htf_open.date()} "
              f"closed {htf_open + TF_DELTA['1D']}; close={a.loc[ts, 'close']:.2f}")
    wa = align_htf(h1, "1h", add_indicators(wk), "1W", ["close"])
    ts = pd.Timestamp("2024-01-10 12:00", tz="UTC")
    wk_open = wk.index[int(wa.loc[ts, "_htf_idx"])]
    assert wk_open == pd.Timestamp("2024-01-01", tz="UTC")
    print(f"1h bar {ts} -> weekly bar opening {wk_open.date()} (the current week is not used)")
    print("all checks passed\n")


# ----------------------------------------------------------------------------- main

def matrix_specs() -> list[Spec]:
    specs = []
    for strat in ("S1", "S2"):
        specs.append(Spec(strat))
        specs += [Spec(strat, (f,)) for f in ("F1", "F1b", "F2", "F3", "F4")]
    specs += [Spec("S3"), Spec("S4")]
    return specs


def summarize_row(tf: str, spec: Spec, m: dict) -> str:
    if not m["trades"]:
        return f"{tf:>4} {spec.name:<14} no trades"
    warn = " (n<100)" if m["low_sample"] else ""
    return (f"{tf:>4} {spec.name:<14} n={m['trades']:>5} win={m['win_rate']:.1%} exp={m['expectancy_r']:+.3f}R "
            f"cost={m['avg_cost_r']:.3f}R PF={m['profit_factor']} tot={m['total_r']:+.1f}R dd={m['max_dd_r']:.1f}R "
            f"t={m['t_stat']} yrs+={m['years_positive']}/{m['years_traded']}{warn}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--tf", choices=EXEC_TFS, help="run a single timeframe")
    ap.add_argument("--strategy", choices=["S1", "S2", "S3", "S4"], help="run a single strategy")
    ap.add_argument("--filter", action="append", default=[], choices=["F1", "F1b", "F2", "F3", "F4"])
    ap.add_argument("--target", type=float, default=3.0)
    ap.add_argument("--consolidation", action="store_true")
    ap.add_argument("--show-trades", type=int, default=0, help="print the first N trades of a single run")
    ap.add_argument("--sims", type=int, default=50, help="random-entry simulations per baseline")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--check", action="store_true", help="run sanity checks and exit")
    ap.add_argument("--out", type=Path, default=HERE / "results.json")
    args = ap.parse_args()

    raw15 = load_15m(args.data_dir)
    if args.check:
        sanity_checks(raw15)
        return

    if args.strategy:  # single run
        spec = Spec(args.strategy, tuple(args.filter), args.target, args.consolidation)
        for tf in [args.tf] if args.tf else EXEC_TFS:
            df = build_frame(raw15, tf)
            trades = run_strategy(df, Bars.from_frame(df), spec)
            print(summarize_row(tf, spec, metrics(trades)))
            for t in trades[:args.show_trades]:
                print("   ", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in t.items()})
        return

    sanity_checks(raw15)
    results = {"meta": {
        "data": f"Binance spot BTCUSDT 15m, {raw15.index[0]} .. {raw15.index[-1]} (signals from {START.date()})",
        "cost_per_side": COST_PER_SIDE, "random_sims": args.sims, "seed": args.seed},
        "buy_and_hold": buy_and_hold(raw15), "runs": [], "random": [], "sensitivity": []}
    tfs = [args.tf] if args.tf else EXEC_TFS
    frames, all_trades = {}, {}
    for tf in tfs:
        df = build_frame(raw15, tf)
        frames[tf] = (df, Bars.from_frame(df))
        for spec in matrix_specs():
            trades = run_strategy(df, frames[tf][1], spec)
            all_trades[(tf, spec.name)] = trades
            m = metrics(trades)
            results["runs"].append({"tf": tf, "variant": spec.name, **m})
            print(summarize_row(tf, spec, m))
        for strat in ("S1", "S2"):
            ref = all_trades[(tf, strat)]
            exps = run_random(df, frames[tf][1], ref, 3.0, args.sims, args.seed)
            strat_exp = metrics(ref)["expectancy_r"]
            rnd = {"tf": tf, "geometry_of": strat, "trades_per_sim": len(ref), "sims": len(exps),
                   "exp_median": round(float(np.median(exps)), 4),
                   "exp_p05": round(float(np.percentile(exps, 5)), 4),
                   "exp_p95": round(float(np.percentile(exps, 95)), 4),
                   "strategy_exp": strat_exp,
                   "strategy_percentile": round(float(np.mean(np.array(exps) < strat_exp)) * 100, 1)}
            results["random"].append(rnd)
            print(f"{tf:>4} RANDOM({strat}) median={rnd['exp_median']:+.3f}R  5-95%=[{rnd['exp_p05']:+.3f}, "
                  f"{rnd['exp_p95']:+.3f}]  strategy={strat_exp:+.3f}R at pct {rnd['strategy_percentile']}")

    # Two selections, both reported: (a) chosen on 2019-2022 only and judged on 2023-2026;
    # (b) best full-period expectancy (in-sample, biased upward) for the sensitivity grid.
    def window_exp(trades, lo, hi):
        r = [t["net_r"] for t in trades if lo <= int(t["entry_time"][:4]) <= hi]
        return (round(float(np.mean(r)), 4) if r else None), len(r)

    halves = {key: (window_exp(tr, 2019, 2022), window_exp(tr, 2023, 2026)) for key, tr in all_trades.items()}
    eligible = [k for k, (first, _) in halves.items() if first[1] >= MIN_SAMPLE // 2]
    is_key = max(eligible, key=lambda k: halves[k][0][0])
    full = [k for k, tr in all_trades.items() if len(tr) >= MIN_SAMPLE]
    best_key = max(full, key=lambda k: metrics(all_trades[k])["expectancy_r"])
    results["selection"] = {
        "in_sample_pick": {"rule": "highest 2019-2022 expectancy with >=50 trades in 2019-2022",
                           "tf": is_key[0], "variant": is_key[1],
                           "exp_2019_2022": halves[is_key][0][0], "n_2019_2022": halves[is_key][0][1],
                           "exp_2023_2026": halves[is_key][1][0], "n_2023_2026": halves[is_key][1][1]},
        "full_period_best": {"rule": "highest full-period expectancy with >=100 trades",
                             "tf": best_key[0], "variant": best_key[1],
                             "exp_2019_2022": halves[best_key][0][0], "n_2019_2022": halves[best_key][0][1],
                             "exp_2023_2026": halves[best_key][1][0], "n_2023_2026": halves[best_key][1][1]}}
    for label, sel in results["selection"].items():
        print(f"\n{label}: {sel['tf']} {sel['variant']}  2019-22 exp={sel['exp_2019_2022']}R "
              f"(n={sel['n_2019_2022']})  2023-26 exp={sel['exp_2023_2026']}R (n={sel['n_2023_2026']})")

    parts = best_key[1].split("+")
    for tf in tfs:
        df, b = frames[tf]
        for target in (2.0, 3.0):
            for cons in (False, True):
                spec = Spec(parts[0], tuple(parts[1:]), target, cons)
                m = metrics(run_strategy(df, b, spec))
                results["sensitivity"].append({"tf": tf, "variant": spec.name, "target_r": target,
                                               "consolidation": cons, **m})
                print("  sens " + summarize_row(tf, spec, m))

    args.out.write_text(json.dumps(results, indent=1))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
