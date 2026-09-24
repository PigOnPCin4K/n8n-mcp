# Fabio Valentini Order-Flow Scalping: Simple Plan

Source video: [Trading LIVE with a World TOP Ranked Scalper (EXTREME Accuracy)](https://youtu.be/tvERE-Beu2U)
Guest: Fabio Valentini, Nasdaq futures (NQ) scalper, top-3 Robbins World Cup futures division.

> Note: the video could not be streamed from the build environment. This plan is built from
> published summaries of this video and Fabio's documented method (links at bottom).
> Numbers marked **(default)** are starting values chosen for automation, not quotes from the video.
> This is education, not financial advice. Paper trade first.

---

## 1. The whole method in one sentence

Figure out if the market is **balanced or out of balance**, go to a **key volume level**,
and only pull the trigger when **aggressive buyers/sellers show up in your direction**.

He calls it **Direction → Location → Aggression**. If any one is missing, you stay flat.

## 2. Tools you need (and where to get them)

| What | Where to check it | Cost |
|------|-------------------|------|
| **CVD (Cumulative Volume Delta)** | TradingView → open [NQ chart](https://www.tradingview.com/chart/?symbol=CME_MINI%3ANQ1%21) → **Indicators** → search "Cumulative Volume Delta" → add the built-in one. Docs: [TradingView CVD help page](https://www.tradingview.com/support/solutions/43000725058-cumulative-volume-delta/) | Free chart; real-time CME data is a paid add-on (free data is delayed) |
| Volume Profile (POC, VAH, VAL, LVNs) | TradingView → Indicators → "Session Volume Profile" or "Visible Range Volume Profile" | Free/plan-dependent |
| VWAP | TradingView → Indicators → "VWAP" | Free |
| Big trades ("bubbles") | TradingView community script [Big Trader (Fabio Style)](https://www.tradingview.com/script/eQT3ExZ2/) | Free |
| Footprint chart | TradingView "Volume Footprint" (paid plans) or [DeepCharts](https://deepcharts.com) — the platform Fabio helped build | Paid |

**What CVD is:** a running total of (market buy volume − market sell volume).
CVD rising = buyers are hitting the offer (aggressive buying). CVD falling = sellers are hitting the bid.

**How to read it (the only 3 things that matter):**
1. **Agreement** – price up and CVD up = real buying. Trade with it.
2. **Divergence** – price makes a new high but CVD makes a lower high = buyers are running out. Watch for a failed breakout.
3. **Absorption** – CVD surges one way but price doesn't move = someone big is absorbing with limit orders. Expect a turn.

## 3. Daily routine

**Before the open (10 min)**
1. Mark yesterday's **POC, VAH, VAL** (Value Area High/Low) from the session volume profile.
2. Mark overnight high/low and VWAP.
3. Decide the **market state**:
   - Price inside yesterday's value area and rotating → **Balance** → use the Mean Reversion model, or don't trade.
   - Price accepted outside value (holding outside, not snapping back) → **Imbalance** → use the Trend model.

**Session to trade**
- **Trend model:** New York session (9:30–11:30 ET). Avoid the London open for trend trades (too many fake breakouts).
- **Mean Reversion model:** London session or slow/compressed (summer) days.

## 4. The two setups

### Setup A — Trend model (market out of balance)
1. **Direction:** price has broken out of balance and CVD agrees with the move.
2. **Location:** on the impulse leg, find the **LVN** (Low Volume Node — the thin spot on the profile). Wait for price to pull back into it.
3. **Aggression:** at the LVN, wait for big trades / footprint imbalance **in the trend direction** (e.g. a ~30+ contract print on NQ). No aggression = no trade.
4. **Stop:** just beyond the aggressive print / LVN, plus 1–2 ticks.
5. **Target:** the previous balance **POC**. Take the full position off there.
6. **Manage:** if CVD keeps pushing strongly your way, move stop to break-even early.

### Setup B — Mean reversion model (failed breakout)
1. **Direction:** price pokes outside the value area but **fails** — closes back inside. CVD shows divergence or aggression dying (buyers hitting but price not moving).
2. **Location:** pullback to the edge of value (VAH/VAL) or an LVN just inside it.
3. **Aggression:** big trades in the reversal direction.
4. **Stop:** beyond the failed breakout's extreme, plus 1–2 ticks.
5. **Target:** the **POC** of the balance area.

## 5. Risk rules (non-negotiable)

- Risk **0.25%** of the account per trade to start the day.
- Only increase size using **profits made earlier that day** (never base capital).
- Minimum **2:1** reward-to-risk. If the POC target is too close to give 2R, skip it.
- **Stop trading after 3 losses** in a day.
- Expect ~50% win rate. The edge comes from winners being bigger than losers.

## 6. One-page checklist (print this)

- [ ] Market state: Balance or Imbalance?
- [ ] Which model fits? (Trend / Mean Reversion / none)
- [ ] Is price at my level (LVN, VAH/VAL)?
- [ ] Is CVD agreeing (trend) or diverging (reversion)?
- [ ] Did aggressive orders show up in my direction at the level?
- [ ] Stop placed beyond the print + 1–2 ticks?
- [ ] Target = POC, and is it ≥ 2R?
- [ ] Losses today < 3?

## 7. Automation

The machine-readable version of these rules is in [`fabio-rules.yaml`](./fabio-rules.yaml).
Recommended build order:

1. **Data:** tick-level NQ/MNQ trades with aggressor side (e.g. Databento, Rithmic, or CQG feed). Candle-only data cannot compute true CVD or big trades.
2. **Deterministic feature engine** (code, not AI): volume profile, POC/VAH/VAL, LVNs, CVD, big-trade detector, market-state classifier.
3. **Rules engine:** evaluates `fabio-rules.yaml` and emits signals.
4. **AI model as reviewer, not trigger:** give it the chart snapshot + features and ask it to veto/approve and write the journal entry. Keeps behavior testable.
5. **Alerting:** send signals to phone/Discord (an n8n webhook workflow works well here).
6. **Backtest → paper trade 30+ days → micro contracts (MNQ)** before any real size.

## Sources

- [Trading LIVE with a World TOP Ranked Scalper (YouTube)](https://www.youtube.com/watch?v=tvERE-Beu2U)
- [Auction Market Theory + LVN Playbook by Fabio (TradeZella)](https://www.tradezella.com/strategies/auction-market-strategy)
- [Fabio Valentino's Nasdaq Futures Playbook: Two Live Models (iu.com.au)](https://iu.com.au/fabio-valentinos-nasdaq-futures-playbook-two-live-models-for-reading-order-flow-volume-nodes/)
- [Fabio Valentini Scalping Strategy: Settings & Rules (PickMyTrade)](https://blog.pickmytrade.trade/fabio-valentini-pro-scalper-nasdaq-scalping-strategy/)
- [World-Cup Scalper Strategy: Fabio Valentini's Order-Flow Edge (forex.in.rs)](https://www.forex.in.rs/footprint-vwap-compounding/)
- [Chart Fanatics: Auction Market Theory Strategy by Fabio](https://www.chartfanatics.com/strategies/auction-market-strategy)
- [TradingView: Cumulative Volume Delta](https://www.tradingview.com/support/solutions/43000725058-cumulative-volume-delta/)
