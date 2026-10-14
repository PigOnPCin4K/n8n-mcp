# Agent Team Design

Two teams of agents were involved: a **research team** that turned the streams into a rulebook, and a **trading team** (the n8n workflow) that applies the rulebook to live BTC data on a paper account.

## 1. Research team (how the strategy was built)

| Agent | Input | Output |
|---|---|---|
| Era analysts x8 | ~66k words each of high-signal passages from ~90 streams, one slice of 2019-09 to 2026-10 | [`research/findings/era1..8.md`](research/findings/): setups, exits, risk, indicators, HTF framework, track record, red flags, all cited as `[videoId @ h:mm:ss]` |
| Rules miner | ~1,100 explicit rule statements across all 743 transcripts, plus corpus-wide greps | [`research/findings/rules.md`](research/findings/rules.md): de-duplicated rulebook with confidence levels and how each rule changed by year |
| Method deep-reader | Full transcripts of the streams whose titles promise to explain his method | [`research/findings/methods.md`](research/findings/methods.md): what each "strategy revealed" stream actually teaches, mechanical rules, gaps |
| Quant | 7 years of BTCUSDT 15m candles from the Binance public archive | [`backtest/`](backtest/): lookahead-free test of the core rules, net of costs |

The orchestrator (Claude Code) downloaded and pre-processed the transcripts ([`tools/`](tools/)), assigned the slices, and synthesised [STRATEGY.md](STRATEGY.md) from the findings and the backtest.

## 2. Trading team (the n8n workflow)

File: [`crypto-lifer-agent-team.workflow.json`](crypto-lifer-agent-team.workflow.json). 22 nodes, validated with this repository's workflow validator (0 errors).

```
Every 15 min
  -> Strategy Config            (all tunable parameters)
  -> Signal Engine   [code]     candles 15m..1w, SMA 21/50/200, Stoch RSI, RSI, ATR,
                                regime, 200-SMA ladder, calendar, candidate setups
  -> Paper Ledger    [code]     manage the open paper trade, daily loss limit, loss streak,
                                de-duplicate signals, shadow book of every raw signal
       |-> Trade Updates? -> Format -> Telegram   (closes, break-even, take-profit warnings)
       '-> Review Needed?
             -> Chart Analyst  [LLM]  scores each candidate against the playbook
             -> Skeptic        [LLM]  argues against the preferred candidate
             -> Desk Lead      [LLM]  final call: enter one candidate or skip
             -> Risk Gate      [code] hard rules, sizing, veto
             -> Approved? -> Open Paper Trade -> Telegram alert
```

### Division of labour

The split is deliberate: **anything that can be computed is computed, and the language models only judge.**

| Role | Kind | Responsibility | Cannot |
|---|---|---|---|
| Signal Engine | Deterministic | Detect the setups from STRATEGY.md on closed candles (default: 4h Model with Stoch RSI timing); compute entry, stop and targets; apply the optional regime / higher-timeframe / calendar filters | - |
| Paper Ledger | Deterministic | Check open trades against each new 15m bar (stop counted first when both are hit in one bar), track equity, daily losses and loss streak; review each signal once; keep a shadow book that takes every signal mechanically | - |
| Chart Analyst | LLM | Rate each candidate 1-5 for playbook fit with specific evidence from the snapshot | Invent prices or levels |
| Skeptic | LLM | Look for his documented failure modes: long bias, fighting the higher timeframe, chop at the 200, chasing stretched moves, conflicting timeframes, thin sessions, event days | Approve without checking |
| Desk Lead | LLM | Enter only if Analyst >= 4 and Skeptic did not reject; pick a target label from the candidate | Set size, entry or stop |
| Risk Gate | Deterministic | Re-derive levels from the engine, enforce >= 3R, risk 0.5% of equity (divided by 3 after 8 straight losses), cap leverage at 5x, stop after 2 losing trades a day | Be overridden by any agent |

This mirrors the gap the research found between what he says and what he does: his stated rules (3:1, stop always set, wait for the retest) are sound; many losses come from overriding them on stream. The deterministic parts hold the stated rules; the Skeptic exists to catch the overrides.

### Does the agent team add anything?

Unknown until it has run for a while, so the workflow measures it. Every fresh signal also goes into a **shadow book** that takes it mechanically (fixed 3R target, same stop, same costs). Trade-update messages report both lines, e.g. `Agent desk: 6 trades, +2.1R | Plain rules: 11 trades, +1.4R`. If after a few dozen signals the desk does not beat the plain rules, switch the agents off and trade the rules, or keep them only for the written thesis. The backtest baseline for the plain rules is about +0.19R to +0.25R per trade on 4h.

### Cost and frequency

The agents only run when the Signal Engine finds a new eligible signal and no paper trade is open. With the default 4h setup that is roughly 20-40 reviews a year (the backtest took ~19 trades a year with one position at a time), not every 15 minutes. Each review is three model calls.

### Setup

1. Import the JSON into n8n (Workflows -> Import from file).
2. Create an **Anthropic** credential and select it on the three model nodes (`Analyst Model`, `Skeptic Model`, `Desk Lead Model`). The model is set to `claude-sonnet-5-5`; change it in each model node if needed.
3. Create a **Telegram** bot credential, select it on both Telegram nodes, and put your chat id in `Strategy Config -> telegramChatId`. To use Slack, email or a Data Table instead, swap the two Telegram nodes.
4. Review `Strategy Config` (risk, timeframes, enabled setups, filters, FOMC/CPI dates). The defaults follow the backtest; the comments say what each switch did there.
5. Activate the workflow. The paper ledger lives in workflow static data, which n8n only persists for active (production) executions, not manual test runs.

Market data comes from `data-api.binance.vision`, Binance's public market-data host, because `api.binance.com` returns HTTP 451 in some regions. No API key is needed and no orders are ever sent.

### Extending it

- **More confluence for the Analyst**: give the agents tools (e.g. an HTTP tool for funding rates or open interest, or a Data Table of past paper trades so the Skeptic can see recent results per setup).
- **Real execution**: deliberately not included. If you go there, put it after the Risk Gate, keep the gate deterministic, and run the paper version long enough to compare its results with the backtest first.
