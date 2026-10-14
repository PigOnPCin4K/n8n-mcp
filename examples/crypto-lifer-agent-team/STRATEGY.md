# Crypto Lifer Strategy: Distilled and Tested

This is a systematic version of the Bitcoin trading method Crypto Lifer (Sam) teaches on his daily "Bitcoin Live Trading" streams, built from 743 transcripts (10.1M words, Sep 2019 to Oct 2026) and checked against seven years of BTCUSDT data.

**Short version.** His stated rules are consistent and sensible: trade with the 200 SMA, enter on pullbacks to the 21 SMA instead of chasing candles, always have a stop, require 3:1. Tested mechanically, only one of his setups showed a positive result after costs: the **4h "Model"** (about +0.19R per trade, ~31% win rate). Everything on 15m and 1h, where he does most of his live trading, lost money after fees. Holding BTC over the same period returned far more than any variant. The plan below uses the rules that held up, sized small, with a long-term spot holding as the main position.

Sources for every claim: [`research/findings/`](research/findings/) (cited as `[videoId @ h:mm:ss]`) and [`backtest/RESULTS.md`](backtest/RESULTS.md).

---

## 1. How his method changed over seven years

| Period | Core setup | Main tools | Source |
|---|---|---|---|
| 2019-2021 | Buy the bottom of bullish patterns (flag, wedge, cup and handle) in the last 25% of the pattern; 12-item checklist | MACD "buy in the pink", RSI divergence (second low), stochastics on 4h/daily, 144 WMA "Trend Watch" | [era1](research/findings/era1.md) |
| 2021-2022 | Price at the bottom of a pattern with Stoch RSI oversold on both 15m and 1h; retests over breakouts | Stoch RSI alignment across timeframes, 21 MA as mean-reversion anchor | [era2](research/findings/era2.md) |
| 2022-2024 | Break-and-retest; "21 MA touch inside a flag with low stochastics"; 4h close vs 200 SMA as bias | Volume profile / POC, Bookmap, 200 SMA ladder | [era3](research/findings/era3.md), [era4](research/findings/era4.md) |
| 2024-2025 | 200 SMA close cross on 1m-1h ("my go-to signal"); "one indicator tells all" = 1h 200 SMA | SMA 21/50/100/200, 200 SMMA, VRVP | [era5](research/findings/era5.md), [era6](research/findings/era6.md) |
| 2025-2026 | **"The Model"**: above the 200, 21 above the 200, price drifts sideways until the 21 touches it; mirror for shorts | SMA 21/200, Stoch RSI, daily/3-day candle-body reversals, weekly 200 as regime | [era7](research/findings/era7.md), [era8](research/findings/era8.md) |

Mentions per 100k words ([term_trends.md](research/term_trends.md)) show the same shift: MACD fell from 57 (2020) to 2 (2026), wedge/triangle from 121 to 46, while "200 MA" rose from 1 (2019) to 80-88 (2023-2025). Stochastics peaked in 2022. His stated "risk 1% per trade" rule appears in 49 of 92 sampled 2021 videos and is effectively gone after 2023, replaced by fixed dollar amounts at 20-60x leverage ([rules](research/findings/rules.md)).

## 2. The strategy

### 2.1 Setup: the 4h Model

| Element | Rule | His words | Backtest |
|---|---|---|---|
| Timeframe | 4h candles, closed bars only | Same setup quoted on 1m to 4h [era8] | 15m: -0.26R, 1h: -0.09R, **4h: +0.19R** per trade |
| Trend | Close above the 4h SMA200 **and** SMA21 above SMA200 (short: both below) | "It's when the 21 is inside of consolidation above a 200" [jOpL_rx5Whk @ 0:12:35] | Core of the only positive result |
| Trigger | The candle's low touches the SMA21 (short: high touches it) | "when this 21 touches price action" [-Dd8mFij6dM @ 0:10:36] | |
| Timing | Stoch RSI (14,14,3,3) %K below 30 within the last 3 candles and %K above %D (short: above 70 and turning down) | "Stochastics RSI will change your life" [lgy3R3KgcmU @ 0:22:29] | +0.19R to +0.25R, 7 of 8 years positive, but chosen from ~60 variants: treat as an upper bound |
| Stop | Below the lower of SMA200 and the 10-candle low, minus 0.1 ATR (short: mirror) | "stop below a wick below the 200 MA" [-Dd8mFij6dM @ 1:14:32] | Skip if the stop is wider than 4 ATR or tighter than 0.5 ATR |
| Target | Fixed 3R | "a two to one is not my favorite trade" [tz1tLKeGVs0 @ 1:18:02] | 2R target dropped expectancy to +0.08R |
| Management | Leave the stop where it is until stop or target | He moves to break-even "fast" [era8 §3] | Break-even at +1R **lowered** expectancy on every timeframe (4h: +0.19R to +0.02R) |
| Optional exit | Take half off when price is more than 3 ATR from the SMA21 with stochastics at an extreme | "far from the 21… this is where I should clip it" [5UN-IzeeO3E @ 1:05:34] | Same expectancy, smaller drawdown (13.4R vs 17.6R) |

Expect about 18 trades a year, a 30% win rate, losing streaks of up to 15, and drawdowns of 15-18R. At 0.5% risk per trade that is a 7-9% equity drawdown; at his 1% it doubles.

### 2.2 Filters

| Filter | His rule | Backtest on 4h | Default |
|---|---|---|---|
| Daily close vs daily 200 SMA (regime) | "never short when the daily was above the 200" [era7] | Cut ~30% of trades, expectancy +0.19R to +0.14R (better for longs, worse for shorts) | Off; the agents see it as context |
| Weekly close vs weekly 200 SMA | His bull/bear line in 2026 [OC3-MHqLPuY @ 0:14:17] | Worse than no filter in 5 of 6 tests (only usable from mid-2021) | Off |
| Calendar (no weekends, Monday before 18:00 ET, Friday afternoon) | Stated in most years, often broken | 4h S2: +0.19R to +0.10R | Off |
| FOMC / CPI day | Stays flat into Fed decisions [iWvdsJWuk1I @ 0:55:13] | Not tested | On when dates are entered |

### 2.3 Risk

| Rule | Value | Origin |
|---|---|---|
| Risk per trade | 0.5% of equity | His 2020-2023 rule was 1%; halved because the edge is small and streaks are long |
| Reward:risk | At least 3:1 | Stated in every era |
| Leverage | Whatever the stop requires, capped at 5x; liquidation always beyond the stop | He uses 20-60x; "liquidation must sit beyond the stop" is his one consistent leverage rule |
| Daily stop | Stop for the day after 2 losing trades | His "stop after a loss on a green day" and chop rules |
| Losing streak | After 8 consecutive losses, divide risk by 3 until a winner | "after 8-10 straight losses… I downsized by 3x" [IuzTdLkVo6A @ 1:23:31] |
| One position at a time | Yes | Keeps the paper ledger comparable with the backtest |

### 2.4 Long-term holding (separate from trading)

He keeps a long-term BTC stack apart from his trading account and adds when the **2-week Stoch RSI is below its oversold line** ("Whenever the two-week chart is below the stochastic RSI dotted line, I'm buying more Bitcoin" [jOpL_rx5Whk @ 0:03:33]). Over 2019-2026 buy-and-hold returned about +2,159% (~50% a year, 77% max drawdown), against roughly 4-5% a year for the best trading variant at 1% risk. The evidence points to making the holding the main position and the trading sleeve the small one. The 2-week signal itself was not backtested.

## 3. What was kept and what was dropped

| His rule or habit | Consistency in streams | Verdict |
|---|---|---|
| 21/200 SMA "Model" on 4h | High (2023-2026) | **Kept**: only positive result |
| Stoch RSI timing on two timeframes | High (2021-2026) | **Kept** as timing filter |
| 3:1 minimum, stop beyond structure | High (all years) | **Kept** |
| 200 SMA close cross ("go-to signal", "one indicator") | High (2024-2025) | Dropped: no edge on any timeframe (4h +0.06R = random baseline) |
| Scalping 1m-15m | His main live activity | Dropped: costs exceed the edge (15m gross edge ~0R, costs ~0.25R per trade) |
| Moving the stop to break-even quickly | Rising (2 videos in 2021, 44 in 2024) | Dropped: lowers results everywhere |
| Calendar filters | Medium, often broken | Optional, off by default |
| Pattern odds ("68%", "90%", "95%") | Repeated constantly, never sourced | Ignored. Realistic win rates are 16-40% |
| Bookmap liquidity, POC, VRVP gaps | Medium (2022-2025) | Context only: never stated as a mechanical rule, and he says the MA system overrides them |
| 20-100x leverage, averaging down, no-stop DCA bots | Frequent on stream | Dropped |
| Daily candle-body reversal ("tweezer") | Medium (2025-2026) | Available in the workflow, off by default, not yet backtested |

## 4. Track record seen in the streams

Across eras the analysts found the same pattern ([era5](research/findings/era5.md) §10, [era6](research/findings/era6.md) §10, [era8](research/findings/era8.md) §10):

- **Short-horizon measured-move targets often hit.** Examples: Nov 2024 flag targets 78.6k and 87k; the Mar 2025 bear flag to 78.5k; the Oct 2023 4h target of $33.5k.
- **Dated multi-week predictions often missed.** Examples: "116k by January 20" (2025), "150k by March 31" (2025), "$24-32k at end of 2023". A viewer said on air that none of his predictions had come true [GMVKByVMZr0 @ 1:52:57].
- **His best recent call:** the 2026 cycle bottom from a 2-week RSI bullish divergence near $59-62k, which ran to ~$86.9k.
- **P&L is self-reported and selective.** There is no trade log. Most gains are quoted as leveraged return on margin.

He also sells a paid group ($99/month), courses, and exchange and Bookmap affiliate links, and promotes them throughout the streams.

## 5. Limitations

- **Coverage:** 743 of the channel's ~3,900 videos were analysed. They are a stratified sample spanning every year, taken before YouTube rate-limited caption downloads. [`tools/fetch_transcripts.py`](tools/fetch_transcripts.py) can resume the rest.
- **Transcripts:** auto-captions mangle numbers and names, so the analysts interpreted them in context.
- **Backtest scope:** BTCUSDT spot only, 2019-2026, about 60 configurations tried. Funding costs on perpetuals are not included. The best variant is not statistically significant (t = 1.62, bootstrap P(expectancy <= 0) about 4%, 92nd percentile of random entries).
- **The agent layer is untested.** The workflow's shadow book records every raw signal so that, over time, you can see whether the agents' filtering beats the plain rules.

Nothing here is financial advice. The workflow paper-trades only.
