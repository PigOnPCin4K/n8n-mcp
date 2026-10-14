# Crypto Lifer Agent Team

A Bitcoin trading strategy distilled from Crypto Lifer's (Sam's) daily live streams, tested on seven years of data, and run by a team of AI agents as an n8n workflow that paper-trades it.

| | |
|---|---|
| Source material | 743 stream and video transcripts, 10.1M words, Sep 2019 to Oct 2026 ([sources.tsv](research/sources.tsv)) |
| Research | 8 era analysts, a rules miner, a method deep-reader and a quant, each writing cited findings ([AGENT_TEAM.md](AGENT_TEAM.md#1-research-team-how-the-strategy-was-built)) |
| Strategy | [STRATEGY.md](STRATEGY.md): his method by era, the rules that held up, risk, what was dropped |
| Backtest | [backtest/RESULTS.md](backtest/RESULTS.md): BTCUSDT 2019-2026, lookahead-free, net of costs |
| Agent team | [crypto-lifer-agent-team.workflow.json](crypto-lifer-agent-team.workflow.json): Signal Engine, Chart Analyst, Skeptic, Desk Lead, Risk Gate, paper ledger |

## Findings

1. **His method moved from chart patterns to moving averages.** In 2019-2021 he bought pattern bottoms with a MACD/RSI checklist. Since 2023 he uses the 21/200 SMA "Model": price above the 200 SMA, the 21 SMA above the 200, enter when the 21 touches price, stop under the 200, at least 3:1.
2. **Most of what he trades live does not survive costs.** On 15m and 1h every variant tested lost money after 0.14% round-trip costs. His "go-to" 200 SMA cross had no edge on any timeframe.
3. **The 4h Model is the one positive result**, and it is small: +0.19R per trade (+0.25R with Stoch RSI timing, the best of ~60 variants), ~31% win rate, losing streaks of up to 15.
4. **Moving the stop to break-even quickly made results worse on every timeframe.** His calendar and higher-timeframe filters did not consistently help: they lowered the 4h Model's results and helped some of the losing variants.
5. **His win-rate claims ("68%", "90%") are not supported**, and his dated price predictions missed more often than they hit. Short-horizon measured-move targets did better.
6. **Holding BTC beat every trading variant** over 2019-2026 by a wide margin, which matches what he does himself with a separate long-term BTC stack.

## Running the agent team

1. In n8n: **Workflows -> Import from file** -> `crypto-lifer-agent-team.workflow.json`.
2. Add an **Anthropic** credential to the three model nodes and a **Telegram** credential to the two Telegram nodes; set `telegramChatId` in **Strategy Config**.
3. Activate. Every 15 minutes it checks BTCUSDT; when a new 4h Model signal appears the three agents review it, the Risk Gate sizes it, and you get a Telegram alert for the paper trade, its exit, and the running score of agent desk vs plain rules.

Design, roles and cost: [AGENT_TEAM.md](AGENT_TEAM.md). No exchange keys are used and no orders are sent.

## Reproducing the research

```bash
pip install yt-dlp curl_cffi pandas numpy

# 1. Transcripts (sequential, with backoff; YouTube rate-limits caption downloads per IP)
python tools/fetch_transcripts.py --out corpus
# 2. Term trends, high-signal passages, rule statements, and 8 era packs for the analyst agents
python tools/build_corpus.py --corpus corpus
# 3. Backtest
cd backtest && python download_data.py && python -I backtest.py
```

Only 743 of the channel's ~3,900 videos are covered so far (every year is represented). Running step 1 from a normal connection and re-running the analysts on the new packs would extend the coverage.

## Files

```
STRATEGY.md                              the strategy
AGENT_TEAM.md                            research team and trading team design
crypto-lifer-agent-team.workflow.json    n8n workflow (22 nodes)
backtest/                                backtest.py, download_data.py, RESULTS.md, results.json
research/findings/era1..8.md             per-era analysis with [videoId @ h:mm:ss] citations
research/findings/rules.md               rulebook mined across all transcripts
research/findings/methods.md             what his "strategy revealed" streams actually teach
research/term_trends.md                  indicator and topic mentions per year
research/sources.tsv                     every video analysed
tools/                                   transcript download and corpus building
```

This is research into a public educator's methods, not affiliated with or endorsed by him, and not financial advice.
