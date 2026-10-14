# Crypto Lifer rules: BTCUSDT backtest

## Bottom line

- **On 15m and 1h, none of the rules makes money after costs.** All 28 of those variants have negative net expectancy. On 15m the setups have about zero edge before costs (S2 gross: -0.004R per trade), and costs then take about 0.25R per trade, because 15m stops are only about 0.8% of price.
- **4h is the only timeframe where results come out positive.** The core "Model" (S2) makes +0.19R per trade net. The best variant, S2 + StochRSI timing (F3), makes +0.25R per trade over 147 trades, with t = 1.62 and a bootstrap P(expectancy ≤ 0) of about 4%. That result is also weak. It ranks at the 92nd percentile of random entries that use the same stop and target geometry, so it doesn't clear the 95% bar. It's the best of about 60 configurations tried, so selection bias inflates it. It also falls apart with small changes: a 2R target gives +0.08R and adding the consolidation condition gives +0.01R.
- **None of the win-rate claims hold up.** "68%" and "90%" don't appear anywhere. With a 3R target, win rates are 16–33%. The highest is 40.5% for S4, and only because a partial exit at 2R counts as a win. "Never stopped out" is also false: in the best variant, 99 of 147 trades hit the stop.
- **Buy-and-hold was far better.** BTC went from $3,701 to $83,624 (2019-01-01 to 2026-09-30): +2,159%, about 50% a year, with a 77% maximum drawdown. The best variant made +37R over 7.75 years. At 1% risk per trade, that's roughly 4–5% a year before compounding, with a 16R drawdown on the way.

## Method

| Item | Choice |
|---|---|
| Data | Binance spot BTCUSDT 15m, monthly archives from data.binance.vision, 2017-08 to 2026-09 (319,294 bars, 32 small exchange gaps). Timestamps from 2025 on are in microseconds; they're converted to milliseconds. 2017–2018 is used only to warm up the indicators. **Signals start on 2019-01-01.** |
| Timeframes | 15m is resampled to 1h, 4h, 1D, 3D and 1W (UTC, left-closed, left label, weeks start Monday). Trades are executed on 15m, 1h and 4h. |
| Indicators | SMA21/50/200, RSI14 (Wilder), StochRSI 14/14/3/3 (TradingView method: stoch of RSI, %K = SMA3, %D = SMA3 of %K), ATR14 (Wilder). |
| Entry | Signal on a closed bar, entry at the next bar's open. One position at a time per run, long or short. |
| Exits | Stops and targets are checked within each bar using its high and low. **If a bar touches both, the stop counts as hit first.** If a bar opens beyond the stop, the fill is the worse open price. Targets fill exactly at the target, with no benefit from gaps. Trades still open when the data ends close at the last close. |
| Costs | 0.05% fee plus 0.02% slippage on each side (0.14% round trip of notional), converted to R: `0.0007 × (entry + exit) / risk`. |
| Units | R multiples (1R = entry-to-stop distance), so leverage doesn't matter. "Win" means net R > 0. A break-even exit counts as a small loss because of costs. |
| Higher-timeframe alignment | A higher-timeframe value is used only once that bar has closed: its close time must be ≤ the decision time (the close of the signal bar = the entry time). This uses `searchsorted` on HTF close times. Spot-checks pass: a 1h bar closing at 01:00 on 2022-05-11 sees the daily bar of 05-10, not 05-11, and a mid-week 1h bar sees the previous week's weekly bar. |
| Other checks | A 4h bar's OHLC equals its 16 underlying 15m bars. Daily SMA200 matches a hand calculation (23,720.0349 on 2023-06-15). The first 4h S2 trade was checked by hand: SMA21 3761.44, stop 3621.89 = min(SMA200 3708.95, 10-bar low 3630.33) − 0.1 × ATR 84.41. The exit bar's high (4027.7) clears the 3R target (3991.09), and the stop was never touched before it. Two full runs produce byte-identical `results.json` files (seeded). |

**Rules as implemented**

- **S1 (SMA200 close cross):** the close crosses SMA200. Stop at min(SMA200, 10-bar low) − 0.1 ATR (mirrored for shorts). Target 3R.
- **S2 (the Model):**
  - Long when close > SMA200, SMA21 > SMA200 and low ≤ SMA21. Short is the mirror image.
  - Stop at the lower of SMA200 and the 10-bar low, minus 0.1 ATR. Target 3R.
  - The trade is skipped if the stop distance at entry is more than 4 ATR or less than 0.5 ATR. On 4h, 44% of signal bars are skipped because the stop is too wide.
- **S3:** S2, with the stop moved to entry from the bar after +1R is reached.
- **S4:** S2, with half the position closed at 2R and the stop then moved to entry. The other half closes at the next open after a bar where |close − SMA21| > 3 ATR and %K > 80 (or < 20 for shorts), or at 6R.
- **Filters:**
  - F1: last closed daily close vs. daily SMA200.
  - F1b: the same with weekly bars.
  - F2: next timeframe up vs. its SMA200 (15m uses 1h, 1h uses 4h, 4h uses 1D).
  - F3: %K < 30 in the last 3 bars and %K > %D (mirrored for shorts: > 70 and %K < %D).
  - F4: no entries Saturday, Sunday, Monday before 18:00 New York time, or Friday from 12:00 New York time (the entry time is converted to America/New_York).

**Caveats**

- **F1b only covers mid-2021 onward.** A 200-week SMA needs 200 weeks of data, and Binance data starts in 2017-08, so the weekly SMA200 first exists in June 2021. Before that, F1b blocks every trade.
- **On 4h, F2 and F1 are the same filter**, because the next timeframe up from 4h is the daily. Their results are identical.
- **S2 with no filter is the version without the consolidation condition.** The condition is only tested in the sensitivity grid.

**Configurations tried (stated for multiple-testing purposes)**

- 14 strategy and filter variants on each of 3 timeframes: 42 runs.
- 6 random-entry baselines, each with 50 seeded simulations.
- A sensitivity grid of 2 targets (2R, 3R) × consolidation on/off on all 3 timeframes, for one chosen variant.
- The rule for choosing that variant was revised once:
  - The first rule required ≥ 100 trades in 2019–2022, which excluded almost every 4h variant. It picked 4h S3: +0.147R in 2019–2022 but −0.055R in 2023–2026. Its 9 extra grid runs were all negative except on 4h.
  - The final rule requires ≥ 50 trades in 2019–2022. It picks 4h S2+F3, the same variant as ranking by full-period expectancy.
- **Total: about 60 strategy configurations.** No parameters were optimized.

## Results: net expectancy per trade (R), all variants

\* = fewer than 100 trades (minimum-sample warning). "t" is the t-statistic of mean net R. "Yrs +" is the number of calendar years with positive total R, out of the years that had trades.

### 4h

| Variant | Trades | Win % | Gross R | Cost R | Exp. R (net) | PF | Total R | Max DD R | Max L-streak | t | Yrs + |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| S1* | 70 | 27.1 | +0.086 | 0.024 | **+0.061** | 1.08 | +4.3 | 14.2 | 11 | 0.29 | 5/8 |
| S1+F1* | 74 | 27.0 | +0.081 | 0.036 | **+0.045** | 1.06 | +3.3 | 14.4 | 14 | 0.22 | 4/8 |
| S1+F1b* | 52 | 17.3 | -0.308 | 0.038 | **-0.345** | 0.60 | -18.0 | 25.1 | 20 | -1.63 | 2/6 |
| S1+F2* | 74 | 27.0 | +0.081 | 0.036 | **+0.045** | 1.06 | +3.3 | 14.4 | 14 | 0.22 | 4/8 |
| S1+F3* | 74 | 28.4 | +0.135 | 0.057 | **+0.079** | 1.10 | +5.8 | 11.6 | 7 | 0.37 | 3/8 |
| S1+F4* | 63 | 31.8 | +0.270 | 0.032 | **+0.238** | 1.34 | +15.0 | 9.5 | 8 | 1.01 | 6/8 |
| S2 | 144 | 31.2 | +0.241 | 0.055 | **+0.186** | 1.26 | +26.8 | 17.6 | 11 | 1.21 | 5/8 |
| S2+F1 | 102 | 30.4 | +0.203 | 0.062 | **+0.141** | 1.19 | +14.4 | 13.7 | 8 | 0.77 | 6/8 |
| S2+F1b* | 80 | 27.5 | +0.084 | 0.067 | **+0.018** | 1.02 | +1.4 | 9.5 | 7 | 0.09 | 3/6 |
| S2+F2 | 102 | 30.4 | +0.203 | 0.062 | **+0.141** | 1.19 | +14.4 | 13.7 | 8 | 0.77 | 6/8 |
| S2+F3 | 147 | 32.6 | +0.306 | 0.054 | **+0.252** | 1.35 | +37.1 | 15.9 | 15 | 1.62 | 7/8 |
| S2+F4 | 137 | 29.2 | +0.147 | 0.044 | **+0.103** | 1.14 | +14.1 | 20.6 | 15 | 0.67 | 4/8 |
| S3 (S2 + BE at 1R) | 289 | 18.7 | +0.091 | 0.071 | **+0.019** | 1.04 | +5.6 | 24.5 | 21 | 0.22 | 4/8 |
| S4 (S2 + stretch exit) | 163 | 40.5 | +0.242 | 0.054 | **+0.188** | 1.30 | +30.7 | 13.4 | 8 | 1.50 | 6/8 |

### 1h

| Variant | Trades | Win % | Gross R | Cost R | Exp. R (net) | PF | Total R | Max DD R | Max L-streak | t | Yrs + |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| S1 | 281 | 21.7 | -0.131 | 0.058 | **-0.189** | 0.77 | -53.0 | 62.6 | 20 | -1.91 | 3/8 |
| S1+F1 | 297 | 24.2 | -0.029 | 0.075 | **-0.104** | 0.87 | -31.0 | 42.2 | 13 | -1.04 | 3/8 |
| S1+F1b | 211 | 22.8 | -0.089 | 0.082 | **-0.171** | 0.80 | -36.0 | 41.7 | 19 | -1.47 | 2/6 |
| S1+F2 | 294 | 26.9 | +0.076 | 0.100 | **-0.024** | 0.97 | -7.0 | 32.2 | 14 | -0.23 | 4/8 |
| S1+F3 | 361 | 26.0 | +0.034 | 0.125 | **-0.092** | 0.89 | -33.1 | 49.9 | 18 | -0.99 | 3/8 |
| S1+F4 | 248 | 24.6 | -0.015 | 0.056 | **-0.071** | 0.91 | -17.6 | 38.3 | 13 | -0.65 | 3/8 |
| S2 | 637 | 25.6 | +0.019 | 0.110 | **-0.091** | 0.89 | -58.1 | 82.7 | 17 | -1.32 | 3/8 |
| S2+F1 | 456 | 24.1 | -0.041 | 0.117 | **-0.158** | 0.81 | -72.2 | 84.5 | 20 | -1.98 | 2/8 |
| S2+F1b | 346 | 24.9 | -0.014 | 0.135 | **-0.148** | 0.83 | -51.3 | 74.1 | 16 | -1.60 | 2/6 |
| S2+F2 | 447 | 27.5 | +0.094 | 0.103 | **-0.009** | 0.99 | -3.9 | 36.3 | 12 | -0.10 | 4/8 |
| S2+F3 | 640 | 25.2 | +0.002 | 0.108 | **-0.106** | 0.87 | -68.1 | 89.4 | 22 | -1.55 | 3/8 |
| S2+F4 | 572 | 25.2 | +0.002 | 0.107 | **-0.105** | 0.87 | -60.2 | 71.9 | 18 | -1.45 | 3/8 |
| S3 | 1330 | 15.9 | -0.020 | 0.144 | **-0.164** | 0.73 | -217.9 | 225.0 | 44 | -4.31 | 0/8 |
| S4 | 851 | 34.1 | +0.006 | 0.124 | **-0.119** | 0.84 | -101.0 | 111.7 | 14 | -2.31 | 3/8 |

### 15m

| Variant | Trades | Win % | Gross R | Cost R | Exp. R (net) | PF | Total R | Max DD R | Max L-streak | t | Yrs + |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| S1 | 970 | 26.4 | +0.056 | 0.134 | **-0.078** | 0.91 | -75.5 | 90.8 | 23 | -1.38 | 2/8 |
| S1+F1 | 1203 | 26.3 | +0.051 | 0.179 | **-0.128** | 0.85 | -154.1 | 177.1 | 21 | -2.52 | 3/8 |
| S1+F1b | 807 | 25.0 | +0.002 | 0.194 | **-0.192** | 0.78 | -155.1 | 174.9 | 18 | -3.15 | 0/6 |
| S1+F2 | 1304 | 27.1 | +0.084 | 0.215 | **-0.132** | 0.85 | -171.6 | 214.3 | 16 | -2.66 | 2/8 |
| S1+F3 | 1468 | 25.9 | +0.039 | 0.293 | **-0.254** | 0.74 | -373.0 | 375.1 | 20 | -5.45 | 0/8 |
| S1+F4 | 711 | 26.6 | +0.065 | 0.125 | **-0.060** | 0.93 | -43.0 | 52.9 | 18 | -0.91 | 2/8 |
| S2 | 2620 | 24.9 | -0.004 | 0.255 | **-0.259** | 0.73 | -678.9 | 678.9 | 25 | -7.56 | 1/8 |
| S2+F1 | 2067 | 24.9 | -0.003 | 0.301 | **-0.304** | 0.69 | -629.2 | 629.2 | 17 | -7.83 | 0/8 |
| S2+F1b | 1506 | 23.8 | -0.049 | 0.354 | **-0.403** | 0.61 | -606.9 | 623.7 | 25 | -8.89 | 0/6 |
| S2+F2 | 2104 | 25.6 | +0.031 | 0.271 | **-0.241** | 0.74 | -506.3 | 506.3 | 22 | -6.20 | 0/8 |
| S2+F3 | 2518 | 24.6 | -0.016 | 0.243 | **-0.259** | 0.72 | -653.1 | 653.1 | 23 | -7.49 | 0/8 |
| S2+F4 | 1962 | 24.4 | -0.023 | 0.241 | **-0.264** | 0.72 | -518.5 | 562.5 | 24 | -6.75 | 1/8 |
| S3 | 5347 | 16.3 | -0.021 | 0.309 | **-0.330** | 0.57 | -1762.0 | 1762.0 | 38 | -16.78 | 0/8 |
| S4 | 3360 | 32.4 | -0.005 | 0.277 | **-0.282** | 0.67 | -948.5 | 948.5 | 22 | -10.61 | 0/8 |

### Random-entry baseline

Each simulation places the same number of trades as the strategy. Each trade has a random entry bar, a random direction (50/50), a stop distance drawn from the strategy's own stop distances (in ATR) and a 3R target. Costs are the same. There are 50 seeded simulations per row.

| TF | Geometry of | Trades/sim | Random median | Random 5–95% | Strategy | Strategy percentile |
|---|---|--:|--:|--:|--:|--:|
| 15m | S1 | 970 | -0.125 | [-0.234, -0.064] | -0.078 | 90 |
| 15m | S2 | 2620 | -0.298 | [-0.362, -0.240] | -0.259 | 88 |
| 1h | S1 | 281 | -0.042 | [-0.204, +0.114] | -0.189 | 8 |
| 1h | S2 | 637 | -0.107 | [-0.188, -0.020] | -0.091 | 62 |
| 4h | S1 | 70 | +0.059 | [-0.210, +0.446] | +0.061 | 56 |
| 4h | S2 | 144 | -0.056 | [-0.272, +0.204] | +0.186 | 92 |

### Total R per year

| TF | Variant | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (Jan–Sep) |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 4h | S1* | -0.2 | +3.8 | +3.8 | -7.2 | +1.8 | -7.2 | +2.8 | +6.8 |
| 4h | S2 | +7.6 | +10.8 | +6.7 | -15.1 | +16.8 | -0.5 | +2.0 | -1.5 |
| 4h | S2+F2 | +2.7 | +6.5 | +1.8 | +2.4 | +8.5 | +3.4 | -6.5 | -4.5 |
| 4h | S2+F3 | +10.5 | +10.8 | +7.7 | -10.1 | +7.9 | +1.0 | +1.2 | +8.1 |
| 4h | S3 | +7.8 | +12.4 | +8.2 | -12.8 | +9.0 | -2.6 | -5.3 | -11.1 |
| 4h | S4 | +10.7 | +5.1 | +6.4 | -4.8 | +9.8 | -0.9 | +3.3 | +1.2 |
| 1h | S2 | +2.4 | -0.7 | -17.4 | -19.6 | -26.9 | -7.0 | +4.2 | +6.9 |
| 1h | S2+F2 | +11.4 | +5.6 | -5.2 | -0.6 | -19.3 | -6.1 | +7.7 | +2.6 |
| 15m | S1 | -6.2 | -25.7 | -30.3 | +6.4 | -7.5 | +10.2 | -20.6 | -1.8 |
| 15m | S2 | -29.5 | -18.2 | +1.9 | -133.8 | -156.0 | -79.8 | -174.6 | -89.0 |

### Long vs. short (selected rows; every row is in results.json)

| TF | Variant | Long n | Long win % | Long exp | Long total | Short n | Short win % | Short exp | Short total |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 4h | S2 | 79 | 33 | +0.245 | +19.4 | 65 | 29 | +0.115 | +7.5 |
| 4h | S2+F1 | 50 | 36 | +0.361 | +18.0 | 52 | 25 | -0.070 | -3.6 |
| 4h | S2+F3 | 73 | 34 | +0.319 | +23.2 | 74 | 31 | +0.187 | +13.8 |
| 4h | S4 | 89 | 43 | +0.230 | +20.5 | 74 | 38 | +0.139 | +10.2 |
| 1h | S2 | 337 | 26 | -0.092 | -31.2 | 300 | 26 | -0.090 | -26.9 |
| 1h | S2+F3 | 323 | 28 | +0.038 | +12.2 | 317 | 22 | -0.253 | -80.3 |
| 15m | S2 | 1374 | 26 | -0.231 | -317.6 | 1246 | 24 | -0.290 | -361.3 |

### Sensitivity of the chosen variant (S2+F3)

| TF | Target | Consolidation | Trades | Win % | Exp. R | PF | Total R | Max DD R | t | Yrs + |
|---|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 4h | 3R | off | 147 | 32.6 | **+0.252** | 1.35 | +37.1 | 15.9 | 1.62 | 7/8 |
| 4h | 2R | off | 175 | 37.7 | **+0.079** | 1.12 | +13.7 | 18.0 | 0.71 | 5/8 |
| 4h | 3R | on | 94* | 26.6 | **+0.009** | 1.01 | +0.8 | 22.1 | 0.05 | 4/8 |
| 4h | 2R | on | 112 | 33.9 | **-0.037** | 0.95 | -4.2 | 18.5 | -0.27 | 4/8 |
| 1h | 3R / 2R | off | 640 / 798 | 25.2 / 33.6 | **-0.106 / -0.105** | 0.87 / 0.86 | -68.1 / -83.7 | | | |
| 1h | 3R / 2R | on | 450 / 526 | 25.6 / 34.2 | **-0.107 / -0.097** | 0.87 / 0.87 | -48.2 / -51.0 | | | |
| 15m | 3R / 2R | off | 2518 / 3328 | 24.6 / 32.8 | **-0.259 / -0.264** | 0.72 / 0.69 | -653 / -879 | | | |
| 15m | 3R / 2R | on | 1887 / 2136 | 23.8 / 32.0 | **-0.343 / -0.327** | 0.65 / 0.63 | -648 / -698 | | | |

How 4h S2+F3 splits by period: 2019–2022 gives +0.32R per trade over 59 trades (t = 1.29), and 2023–2026 gives +0.21R per trade over 88 trades (t = 1.03). The bootstrap 95% confidence interval for expectancy is [-0.05, +0.58]R.

## Interpretation

1. **Costs settle the question on lower timeframes.** On 15m the gross edge of every S2 variant is about zero (−0.05 to +0.03R), and costs are 0.24–0.35R per trade, so expectancy is clearly negative (t from −6 to −17). 1h is the same story with smaller numbers: S2 gross is +0.02R and costs are 0.11R. On 15m the strategies beat the random baseline slightly (88th–90th percentile) but are still far below zero. Whatever timing skill the rules have is much smaller than the cost of trading that often.
2. **The SMA200 cross (S1) has no edge.** It loses on 15m and 1h, and is flat with too few trades on 4h (+0.06R over 70 trades, the same as the random median of +0.06R). Calling it a "go-to signal" isn't supported.
3. **"The Model" (S2) on 4h is the only candidate, and the evidence is weak.**
   - Net expectancy is +0.19R with about 18 trades a year. Years 2019–2021 and 2023 are positive; 2022 (−15R) and 2024–2026 are about flat to negative.
   - Adding StochRSI timing (F3) lifts it to +0.25R, positive in 7 of 8 years. But this variant was chosen as the best of about 60, and it's sensitive to the target and the consolidation condition. Treat +0.25R as an upper bound.
   - A more realistic read is that the 4h pullback-to-the-21 entry in a 200-SMA trend may carry a small positive edge, roughly 0–0.2R per trade. That hasn't been shown at conventional significance.
4. **Filters do not help consistently.**
   - F1/F2 (trend agreement) and F4 (calendar) help in some cells and hurt in others. F2 is the most consistent: it brings 1h S1 and S2 to about break-even.
   - The weekly filter F1b is worse than no filter in 5 of 6 cells. It also only covers mid-2021 onward.
   - On 4h, the regime filters cut about 30% of trades, both long and short, and lower expectancy (S2: +0.19R to +0.14R).
5. **Moving the stop to break-even fast (S3) is clearly harmful.** On every timeframe it turns most potential 3R winners into break-even exits that cost money: win rate falls to 16–19% and expectancy drops by 0.07–0.17R compared with S2. His habit of moving to break-even quickly is, by this test, a net negative.
6. **The stretch exit (S4)** performs about the same as the fixed 3R target on 4h (+0.19R vs. +0.19R), with a smoother equity curve (max drawdown 13.4R vs. 17.6R). Its 40% win rate comes mostly from the 2R partial. It doesn't add edge.
7. **The claims:**
   - The win rates he quotes (68%, 90%) aren't achievable with these exit rules. The best realistic figure is 30–40%, and that depends on a 3R payoff.
   - Stop-outs are the most common outcome in every variant: 99 of 147 trades in the best one.
   - Long losing streaks are normal: up to 15 in a row on 4h, up to 25 for S2 on lower timeframes, and up to 44 for S3. Anyone following these rules needs to be ready for that.

**Reproduce:** from this directory, run `python download_data.py` (fetches the monthly zips into `data/`, about 110 files), then `python -I backtest.py`. It runs the sanity checks, the full matrix, the random baselines and the sensitivity grid, and writes `results.json` (about 20 seconds). Run `python -I backtest.py --tf 4h --strategy S2 --filter F3 --show-trades 5` for a single run with example trades, and `--check` for the checks only.
