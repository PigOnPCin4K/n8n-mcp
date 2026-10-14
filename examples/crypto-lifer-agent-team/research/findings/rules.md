# Crypto Lifer (Sam): Rules Mining Findings

**Method.** I read all 1,104 rule windows in `packs/rules.tsv`. About 55% were noise, e.g. "I never got a ticket", sponsor reads, song lyrics, and course ads. I pulled full-transcript context for about 30 key statements and ran per-year greps over all 743 transcripts.

- **Count format.** "x/n" means x of the n sampled videos that year contain the term. Sample sizes: 2019=20, 2020=56, 2021=92, 2022=120, 2023=119, 2024=127, 2025=118, 2026=91. Transcript length varies, so videos-with-hit is more reliable than raw mention counts.
- **Caption fixes.** "Stokes" = Stochastic RSI. "50 minute" usually = 15-minute. "200 May / 2 a / T May" = 200 MA. "vvp/VRVP" = visible-range volume profile. "risk ward" = risk/reward.

---

## 1. Risk-management rules

**1.1 Risk 1% of the portfolio per trade (the core rule from 2020 to 2023, then it disappears).**
- **Frequency.** "One percent / 1 percent": 16/56 (2020), 49/92 (2021), 33/120 (2022), 21/119 (2023), 1/127 (2024), 0 in 2025–26.
- [20210110 qHT8FwTkCuM 0:45:55] "only use 1% of your portfolio per trade… if I had a $15,000 portfolio I would only risk 150 bucks… the stop loss is 6% so I would take 150 I divide it by 0696". This gives the explicit sizing formula: position = $risk ÷ stop%.
- [20230801 2RSAxCNBk8U] "I use one percent of my portfolio same risk management as spot nothing changes just because there's leverage involved".
- Last explicit mention: [20250210 IRf4YsUe-M8] "I'm risking way less than… 1% of portfolio".
- **2024–26: replaced by fixed-dollar risk per trade.**
  - [20260603 FGSg47VbTuM] "There's my stop-loss. If I get lost, I'll lose 560"
- **Plus a "risk from the day's profits" rule.** [20260223 o0ltCbS84U4 0:32:25] "I risk a small percent. If I made five grand that day, three grand that day, I risk 500 bucks… if I would have lost, I still would have been up 1,400".

**1.2 Always use a stop-loss (stated in every era).**
- **Frequency.** "Stop loss" appears in 36/56 (2020), 69/92 (2021), 104/127 (2024), 70/91 (2026).
- [20260518 GO2KZSuP_jA] "Without a stop-loss, there is no plan because there's no risk management."
- **Stated exception (2021–22).** No stop is acceptable if the whole position is the risk budget.
  - [20210517 tTSiHezyBtM 0:32:24] "you're either going to use a stop loss or you risk less than one percent of your portfolio per trade"
  - [20220314 0EOYRJXR_-8] "I could put a thousand dollars in this no stop loss… the trade becomes the stop loss"

**1.3 Where the stop goes. The method changed over time; it always sits just beyond structure.**
- **2020–21: under the pattern or trendline.** [20200921 MsOCSegEzoI] "your stop-loss is always hiding these trend lines"
- **2021 futures: a moving-average ladder trailing stop.** [20210226 WgSr3Sfz6XU 1:56:46] "my stop loss now is the 21-day moving average… above the 50 my stop loss now gets brought up to the 50-day"
- **2022: one or two swing lows below entry.** [20221027 EKEQ7YqHCBg 0:43:14] "I always keep my stop loss one two support lows below the entry"
- **2024+: the other side of the 200 SMA.** [20240212 WAV_xs6RxSs 0:12:28] "once I get above a 200 SMA I buy then I put a stop loss below the 200 SMA… my stop and my buy are very close together"

**1.4 Move the stop to break-even once in profit (grew over time).**
- **Frequency.** Break-even stop phrases: 6 videos (2020), 2 (2021), 14 (2023), 44 (2024), 35 (2025), 29 (2026).
- [20250807 kKKYygXoy5E] "I move my stop loss into break even at every trade once I'm up."

**1.5 Aim for at least 3:1 risk/reward and accept a low win rate.**
- [20220921 lG6eh5bbn6c] "I make sure I trade three to ones"
- [20240126 RVkCpAe9ilg] "always risking one for three every single time"
- [20250418 4uywZJQIFSE 0:34:15] "I only need to win three out of 10 of them the way I do my risk management"
- R:R phrasing appears in about 60–75% of videos every year from 2020 on.

**1.6 Leverage: there is no stable maximum.**
- **2021.** [20210615 a45ZJTQr9fY 0:26:08] "if you use it like a thousand to five thousand dollars no more than 10x leverage if you're using 100 bucks you can use 34x"
- **2022.** [20220825 2IGnFeyVixg 0:50:52] "i'm not a huge leverage trader i use no more than three"
- **Later live trades are much higher:** "37x" [20240422 Jo1HGMjXFxA], "62x leverage" [20251013 Ch1Y3FtYWl0].
- **The consistent principle is that leverage serves the stop.**
  - [20230125 HY0eaj2A9qo] "I'm super strict about risk management whatever my Leverage is strategic to be able to use a good stop loss"
  - Keep the stop above the liquidation price [20240505 X2buq161e6I].
  - [20250920 3xphdcESOAU 0:12:15] "I've never increased my leverage as I go into profit… if more money comes in, I usually lower the leverage".

**1.7 Account structure.**
- **Separate leverage account; skim profits, never refill.**
  - [20240110 ow68gkeznVE 1:07:54] "I'm a big spot Trader spot swing Trader and I keep a smaller leverage account… I turn about five grand into [seven] Grand and then I take the two grand"
- **Dry powder and core Bitcoin.**
  - [20201015 uX-4xDDMd9k] "keep at least fifty percent to thirty percent of my portfolio [in] tether unless you're in a full bull market"
  - [20220527 wID-xqRx6Os] "I keep sixty percent of my portfolio into bitcoin at all times"
- **Micro-caps.** 1% down to "point zero zero one percent" of the portfolio [20210824 ODhvYnkuhvA].

## 2. Entry rules / "my strategy"

His strategy went through three eras. The constant layer underneath is top-down timeframe alignment:
- [20201026 QjuBvlo0O6M] "i won't even go into the dance if the four hour doesn't look good"
- [20230910 ldFoqB4VZvQ] "if the daily has an uptrend but the weekly doesn't I always take the bigger time frame"

**Era A, 2020–21: pattern bottom plus divergence/MACD and a 9-point checklist.**
- [20201201 IxW-5gdrJPs 0:21:03] "I play bullish patterns I buy at the bottom of the pattern… I use moving averages I have a checklist… combined with divergences"
- [20201112 FBjIxKKuj5w 0:42:55] "you draw a pennant you go to the bottom of the pattern you look at the macd you get in when the blue line is curving and about to cross"
- [20201121 5nzKwKXDv5Y] "I always enter on bullish Divergence"

**Era B, 2021–23: touch of the 21 MA plus low stochastics plus a flag; enter when moving averages are tight.**
- [20220213 QhHP3CyY62w] "if you touch the 21 and you're low on the Stokes you should take a move"
- [20210927 1XqGXzRNlFI] "when the moving averages get super tight that's when I begin to enter"
- [20231009 8DygVdQ8KO8 0:54:20] "my system is based off What's called the Twisted Sister… you'll either come down to the 21 or the 21 will come meet price"

**Era C, 2023–26: the 200/21 system, increasingly on the 1-minute to 1-hour charts.**
- **Frequency.** 200-MA phrases: 14/56 (2020) → 78/119 (2023) → 110/127 (2024) → 78/91 (2026). Raw mentions went from 46 to 1,578 at the 2024 peak. "1-minute" mentions went from 185 (2021) to 1,112 (2024).
- [20240305 7SRBXhkWR7Y] "my strategy when you lose the 200… that's time to short when you gain it it's time to Long"
- [20241122 RJpex7kLykg 0:18:29] "I can only get in when price touches the 21 these are my rules… so I fine tune my rules… I have to get in when we are above the 200 and touching the 21"
- [20250526 96q4uzrvHps 1:16:02] "whenever the stoastics are low and the 21 is close and we're in a flag, 90% of the time we get a pump. It's my strategy… I back tested it"
- [20260706 fguIg-1-BzM] Wait for "the 21 to cross the 200".

**Entry filters.**
- **Don't chase.**
  - [20220310 rC6dgv3qPiY] "i don't chase green candles"
  - [20230714 rpkdq6P4LOA] "I can't chase candles… it's against my rules"
- **Let the trade come to you.** [20240110 ow68gkeznVE] "my system is all about making the trade come to you don't force the trade"
- **Long bias.** [20260515 kNkDDbEiZKg] "I'm the king at finding the bottom. That's why I never short… not never… rarely".

## 3. Exit / profit-taking rules

- **Sell at resistance or the target, a little early.**
  - [20220728 X4SxwT8XOY0 1:44:12] "i take profits at resistance each time i call it a day"
  - [20230902 FpetOY-AAR4 0:27:25] "I never go for the exact target I always just take my profit a little early so… I guarantee the win"
- **Take profit when price stretches from the moving averages; re-enter on the stochastic reset.**
  - [20211001 Mp6Oo7hPZBE 1:41:01] "you always take profit whenever you get away from the 21 day moving average… wait for the pattern to reform and get back in when the stokes are low"
  - [20240320 mtVnQR5X7Og 0:08:00] "you get in when they're tight you start taking profits when the 21 and the 200 get far apart and you get a bearish Divergence"
- **Fast gains get banked.**
  - [20240913 9ZLcIav1M3I] "usually when I make money that fast I take it that's my strategy"
  - The "pay the trader" catchphrase grows from 3 videos (2021) to 23 (2025).
- **Targets are measured moves** (pattern height): 71/92 (2021), 90/120 (2022), 57/91 (2026).
- **No immediate re-entry.** [20250410 dty_RiQ324s 1:11:19] "I usually don't go into a trade after I get out of a trade. It's another one of my rules… I feel like I'm overtrading".
- **Partials and scaling out are rare.** At most 13 videos in any year, e.g. "I sold partials" [20231023 TULKeRt_eTM]. Exits are mostly all-out.

## 4. Indicator rules

- **Stochastic RSI (the main trigger, 2021–25).** Present in 69/92 (2021) → 101/127 (2024) → 55/91 (2026).
  - Buy when stochastics are low or resetting: [20211015 BBgAY0LLF_o] "I love to get in when stochastics are low".
  - Short resistance when they are high: [20221027 EKEQ7YqHCBg] "short resistance when the Stokes are high".
- **Moving averages.** He uses the 21 (always called "21-day", whatever the timeframe), 50, 80/100 and 200 SMA.
  - A golden or death cross (50/200) is confirmation, not a trigger [20210830 cKBP8PSMusQ]. Mentions peak at 64/127 (2024).
- **MACD and divergence fade.**
  - MACD appears in 39/56 videos (2020) but 14/91 (2026). [20230913 JA5Ku1tN-ag] "so many times the macd will give you a false signal I don't stress the macd".
  - Divergence was called "my number one rule" in [20230602 iczf8e74jME], but mentions drop sharply after 2023.
- **Volume profile / point of control (POC).** Absent before 2022. Then 53/120 videos (2022), 72/127 (2024), 24/91 (2026).
  - Used with the 200 MA as a regime filter: [20240205 _uLJcKha2Tw] "the second you lose a 200 SMA and a point of control you just have to assume… put in a short with a stop".
- **Bookmap and liquidity.** From 2022: 52/120 videos, then 88/127 (2024). It is also a channel sponsor with an affiliate link.
  - Explicitly secondary: [20241105 QCoFI_gJGac 0:45:50] "I do not follow bookmap blindly… if my strategy which tells me above the 200 is telling me long and bookmap says liquidity is below I will counter trade bookmap".
  - "Liquidation" is mostly a warning ("don't get liquidated") or a reference to liquidation levels; I found no liquidation-level entry rule.
- **Weekly close.** Used for narrative levels (26/118 videos in 2025), not as a rule.
- **Hedging.** No hedging rule. The hits are news and gold commentary. The only allocation advice is gold at "ten to twenty percent of your portfolio" [20200306 _-uK3wc8Gy0].

## 5. Discipline / psychology rules

- **Calendar rules (2022+; one of the most repeated "my rules").**
  - [20220710 gWMSzB_U1X8] "i don't trade sunday night into monday morning"
  - [20240324 Abw3Sz93wD4] "once Saturday night kicks in my rule is not to trade anymore"
  - [20250217 42R8kTYNLaI] "I usually don't trade Mondays until 600 p.m… every time I break my rules I pay for it"
  - [20260102 qnDZauUAcV8 1:17:03] "I just don't trade Fridays… I made trading rules"
  - [20260507 s3dcIE2Y4NU 1:55:06] "if you made good gains throughout the week, leave Thursday alone"
  - Best days: [20240422 Jo1HGMjXFxA] "I'll go way harder on a Tuesday Wednesday".
- **Rule number one is to protect capital.**
  - [20231105 a0HyotG_K5E] "number one rule do not lose money in trading"
  - [20260507 s3dcIE2Y4NU 1:31:50] "go after securing your money more than making money"
  - A separate investing rule: [20241115 SADHA6XaQ_k] "the number one rule for me do not sell your Bitcoin".
- **You know nothing (from Mark Douglas).**
  - [20241224 vyJapukC9jY] "number one rule you may be wrong"
  - Plan for both directions: [20210319 SjRJjpjBiJs] "I always have two projections"; [20220916 aZ1xBGO_bhg] "you always have to have a backdoor plan".
- **Consistency and mechanical repetition.**
  - [20220604 BTJNW4ghv5s] "if you trade the same way every time you will gain an edge"
- **Don't overtrade or force trades.** Overtrading mentions were 0–2 videos per year before 2024, then 21–25 per year.
  - [20260507 s3dcIE2Y4NU] "when you have to be in a trade all the time, someone's controlling you"
- **Progression: spot first, then demo (about 100 trades), then leverage.**
  - [20230817 mDkSTzDi7Es] "I didn't trade Futures till I traded for like years and years… spot until I really got my risk management down"

## 6. Contradictions

1. **"Always use a stop" versus trades without one.**
   - [20200826 ni-1aEwyz6E] "i got liquidated… fell asleep without a stop loss"
   - [20210810 PcNlo8tEuBc] "i'll take a 1200 hit on this one no stop loss"
   - [20250923 enZqKbmdZSo 1:36:15] "I'm still in the ETH trade… It's underwater big time, but I'm going to hold it until I win it."
2. **The 1% rule versus actual size.**
   - The first statement already doubles it: "only risk one percent… but i was only risking two percent" [20200925 4MZU1sDsZso 2:13:02].
   - [20250511 lvLG0I8sFeo 0:33:07] "80 80 70 grand for 270,000… I don't know if I'm ready to… lose 70 grand if price action goes down by just $1,000… I'll dull it down"
   - He stops stating any percentage after 2023.
3. **Leverage.**
   - He said "no more than three [x]" in 2022, but live trades are 30–60x+.
   - [20241122 RJpex7kLykg 0:14:29] "I always say I'm not leverage trading but… I have $100,000 in a leverage [bot]"
   - [20241115 SADHA6XaQ_k] "I never trade all coins… on Leverage and I made a leverage allcoin trade last night".
4. **He breaks his own rules openly.** Admissions ("broke/against my rules") go from none before 2022 to 9 videos (2024) and 6 (2026).
   - [20240517 MOFTAACQk9I] "I always go against my rules but I'm Entertainer too"
   - [20241115 SADHA6XaQ_k] "I front run my signal which I'm never supposed to do"
   - [20241218 gV8u0x7lO6s] "I usually do not trade fed day… and then I traded it anyway"
   - [20260706 fguIg-1-BzM] "I didn't wait for the 21 to cross the 200… I broke my rules"
5. **"Same strategy forever" versus clear evolution.**
   - [20250225 iB5cBbD_1qQ] "I'm not going to change the way I traded"
   - versus [20260310 HPXgon2nKck 0:20:32] "before I started trading the 200 so much… I kind of switched almost all my strategy"
6. **Win-rate claims are inconsistent.**
   - High claims: "18 for 25" [20211103 PC30vJ9sYuw], "80 to 90 of the time" [20220812 iaYrEoXUYOw], "90% of the time" [20250526 96q4uzrvHps].
   - Low claims: "I made this trade 10 times and I lost it seven times" [20210728 xbclKrxjep8], and "win three out of 10" [20250418 4uywZJQIFSE].
7. **"Never/rarely short" versus his own system's short rule** ("lose the 200 → short") and rising use of the word "short" from 2022.
8. **Selective presentation.** The catchphrase "no stop loss got hit in the making of this trade" appears in 13 videos (2021) and 26 (2022). It is marketing, not a rule.
9. **Education disclaimers versus promises.** "I'll never tell you what to buy or sell" [20220120 Qyev0kdM5Zg], yet "if you trade the way I trade you will make so much money" [20240201 RXUENaahPH4].

## 7. Consolidated rulebook

| # | Rule | Confidence |
|---|---|---|
| 1 | Every trade has a predefined stop; know the dollar loss before entry. | High |
| 2 | Risk about 1% of the account per trade (2020–23). Later: small fixed dollar amounts, ideally less than the day's realized profit. | High (stated); Med (later form) |
| 3 | Position size = $risk ÷ stop distance (%). | Med |
| 4 | Require at least 3:1 reward:risk; a 30% win rate is acceptable. | High |
| 5 | Stop just beyond structure: pattern bottom or trendline, 1–2 swing lows below entry, or the other side of the 200 SMA. | High |
| 6 | Move the stop to break-even once in profit. | Med-High (2024–26) |
| 7 | No stop is allowed only if the position itself is the max loss (at most 1%, spot or micro-cap). | Med |
| 8 | Leverage is chosen to fit the stop. Never add leverage into profit. Keep a small separate leverage account; skim profits, never refill. | Med |
| 9 | Top-down: daily/4h must agree; the higher timeframe wins conflicts; time the entry on a lower timeframe. | High |
| 10 | Long when price is above the 200 SMA and pulls back to touch the 21 MA, in a flag, with low Stoch RSI. Mirror for shorts below the 200. | High (2023–26); Low (earlier) |
| 11 | Enter when the moving averages are compressed (21 near the 200); expect expansion. | Med-High |
| 12 | Buy the bottom of bullish patterns (falling wedge, bull flag, cup and handle); target the measured move. | High (2020–23); Med (later) |
| 13 | Confirm with bullish or hidden-bullish divergence (MACD cross in 2020). | Med (declining) |
| 14 | Don't chase green candles; wait for the next flag or retest. | High |
| 15 | Take profit at resistance or the target, slightly early ("pay the trader"). | High |
| 16 | Take profit when price stretches far from the 21, the 21/200 spread is wide, or stochastics are high; re-enter on the reset. | Med-High |
| 17 | Don't re-enter immediately after exiting; avoid overtrading. | Med |
| 18 | Calendar filter: skip Sunday night to Monday daytime, Fridays, Saturday nights and Fed days; Thursday is optional; press on Tuesday/Wednesday. | Med-High (often broken) |
| 19 | POC, Bookmap and liquidity are secondary; the moving-average system overrides them. | Med |
| 20 | Never go all-in. Keep stablecoin dry powder. Keep core BTC as a separate long-term holding ("don't sell your Bitcoin"). | High |
| 21 | High-risk micro-caps get at most 1% (often 0.1%) of the portfolio. | Med (2021) |
| 22 | Assume you know nothing; keep two projections and a backdoor plan. | High |
| 23 | Repeat one setup mechanically; backtest or demo about 100 trades; trade spot before leverage. | Med |
| 24 | Rule number one: protect capital before making money. | Med |
