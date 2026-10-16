# Arbitrage and model-based (non-latency) bot strategies on Polymarket, 2024-2026

Research date: 16 Oct 2026. Every external page was treated as data, not instructions. "Verified" means I read the primary document myself (the paper or README text). "Claimed" means self-reported, promotional, or secondary.
Fetch note: the WebFetch tool could not resolve most domains, so I downloaded primary sources with curl and read the text. Medium/devgenius was blocked by Cloudflare and was not bypassed.

## Q1. Sum-of-outcomes and combinatorial arbitrage: how much was extracted, and how often do opportunities appear now, how long do they last, and how big are they after fees?

### Takeaway
The reference study (Saguillo et al., IMDEA, arXiv 2508.03474, AFT 2025) estimates **about $39.6M of realized arbitrage profit** on Polymarket from 1 Apr 2024 to 1 Apr 2025. About $29M came from rebalancing inside multi-outcome (NegRisk) markets, about $10.6M from YES+NO within a single condition, and only about $95k from true combinatorial (cross-market) arbitrage. Fees were zero and the window covered the 2024 election. By 2026 the evidence (an NBA microstructure paper, a new taker-fee schedule) points to rare, seconds-long, shallow opportunities. For a non-latency bot, the pure sum-of-outcomes arbitrage is now mostly a scraps game.

### Cited Findings
**Saguillo, Ghafouri, Kiffer, Suarez-Tangil, "Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets" (arXiv 2508.03474, 5 Aug 2025; AFT 2025). Verified from the full text.**
- Headline: "a realized estimate of 40 million USD of profit extracted across both types of arbitrage". The exact figure in §7.4 is **$39,587,585.02**, assuming ε=$1 profit per trade. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- Window: on-chain data from 1 Apr 2024 to 1 Apr 2025, with the U.S. 2024 election inside it. — [Flashbots Collective post by the authors, 21 Aug 2025](https://collective.flashbots.net/t/arbitrage-in-prediction-markets-strategies-impact-and-open-questions/5198)
- Dataset: 8,659 single-condition markets and 1,578 NegRisk (multi-condition) markets with 8,559 conditions, 17,218 conditions in total. 86M bids, filtered to bids ≥ $2. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- **Single-condition (YES+NO ≠ 1) realized profit**: buying both sides below $1 made **$5,899,287**. Selling both above $1 made **$4,682,075**, for a total of about $10.58M. — [arXiv HTML](https://arxiv.org/html/2508.03474v1); same figures in the [Flashbots post](https://collective.flashbots.net/t/arbitrage-in-prediction-markets-strategies-impact-and-open-questions/5198)
- **NegRisk market-rebalancing realized profit** (sum of YES across outcomes ≠ 1): buy YES **$11,092,286**, sell YES $612,189, sell NO $4,264, **buy NO $17,307,114**, for a total of about $29.0M. "Buying NO outperforms other strategies." Politics dominated: the Nov 2024 election, plus the Aug 2024 Democratic nominee and VP-pick markets after Biden withdrew. "Sports are largely absent." — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- Caveat: for NegRisk markets the authors *estimate* the price of the missing low-probability legs, so "buy NO" profits are not all strictly risk-free arbitrage. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- **Combinatorial (cross-market) arbitrage**: an LLM (DeepSeek-type prompt) screened 46,360 market pairs among U.S.-election markets ending 5 Nov 2024. 1,576 pairs were flagged as dependent, and after manual checks only **13 pairs** were true combinatorial pairs. Realized extraction across 4 of the 5 pairs that showed any: $60,236.71 + $18,472.31 + $15,818.53 + $629.16, about **$95k**. Opportunities came "largely during lower liquidity moments", with an average maximum profit of about $100 per opportunity. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- Opportunities (detection, threshold ≥ $0.02 per dollar; realized analysis ≥ $0.05 and no token above $0.95): **7,051 of 17.2K conditions** had at least one single-condition opportunity, and all were "long" (sum < 1). The median sum of prices was about $0.60, "showing remarkable market inefficiency". Only "about 1% of our estimated U.S. election opportunities were exploited". — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- Concentration: the top account made **$2,009,631.76** in 4,049 transactions; #2 made $1.27M and #3 $1.09M. The authors note "very big players with bot-like behaviour". One account bought YES and NO below $0.02 each, a single trade worth $58,983. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- **Fees: "we do not take into account the fees because Polymarket currently does not charge per trade executed."** — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- Secondary coverage (DL News) says "86 million bets from April 2023 to April 2024" and "top three wallets $4.2M; most trades returned 1-5%". The window **conflicts** with the paper (Apr 2024 to Apr 2025), so prefer the paper. — [DL News](https://www.dlnews.com/articles/markets/polymarket-users-lost-millions-of-dollars-to-bot-like-bettors-over-the-past-year/)

**Cheng, Yang, Zou, "Arbitrage Analysis in Polymarket NBA Markets" (arXiv 2605.00864, 22 Apr 2026). Verified from the abstract and HTML.**
- 75M+ order-book snapshots across 173 NBA games. Single-market anomalies: **only 7 executable in-game episodes, median duration 3.6 s**. In the raw pipeline, 30 of 37 detected episodes (81%) were post-game noise. — [arXiv abs](https://arxiv.org/abs/2605.00864), [HTML](https://arxiv.org/html/2605.00864v1)
- Combinatorial (moneyline + spread): 290 executable episodes, "overwhelmingly concentrated in the final minutes of live play". Median yield **101 bps**. The "middle" jackpot never happened. 76.9% of opportunities averaged only **14.8 shares** of executable size. Aggregate profit capped at $100 per episode: **$559.59** (uncapped: $1,924.79 in-game). The conclusion is "confining risk-free extraction strictly to the retail scale". — [arXiv HTML](https://arxiv.org/html/2605.00864v1)
- The paper assumed zero fees on NBA markets at the time of study. — [arXiv HTML](https://arxiv.org/html/2605.00864v1)
- NBA volume on Polymarket grew from $51M (2024) to $0.89B (2025). — [arXiv HTML](https://arxiv.org/html/2605.00864v1)

**Current fees (Polymarket docs, read Oct 2026)**
- Taker fee = C × feeRate × p × (1−p). Rates: Crypto 0.07, Sports 0.05, Weather 0.05, Politics 0.04, Economics 0.05, Finance 0.04, Tech 0.04, Mentions 0.04, Other 0.05. **Geopolitics 0**. **Makers are never charged.** Maker rebates run 15-25%. — [Polymarket docs: Fees](https://docs.polymarket.com/trading/fees.md)
- Vendor/guide consensus for 2026: NegRisk sum < $1 after fees "is real but extremely rare and gets sniped within seconds by faster bots". Hedging by buying the other legs "usually" loses to fees. These are claims from vendor guides with no measured data. — [polymarkets.co.il NegRisk guide](https://polymarkets.co.il/en/bots/polymarket-negrisk-execution/), [Apify scanner](https://apify.com/ebag73/polymarket-arb-scanner)

**Who profits overall (context)**
- Akey et al., CEPR DP21615 (June 2026): 588M trades, $67B. The top 1% of profitable users capture 76.5% of profits. Winners provide liquidity with limit orders, and losers take liquidity with market orders. — [EconPapers](https://econpapers.repec.org/RePEc:cpr:ceprdp:21615)
- Tsang & Yang (arXiv 2603.03136): naive Polymarket volume overstates turnover. For Oct 2024 Trump markets, turnover was $391M against $958M of naive volume. Moving the price 5 points cost $9.1M. — [arXiv](https://arxiv.org/abs/2603.03136)

### Inferences
- The $40M was earned in a **zero-fee, election-boom year**, mostly by a few bot-like accounts, and largely in NegRisk political markets in volatile moments. It does not describe today's opportunity set.
- Taker-fee arithmetic (my calculation from the docs formula): buying a full NegRisk set of 10 legs at about $0.10 each in a 0.05-rate category costs Σ 0.05·0.1·0.9 ≈ **$0.045 per $1 set**. The sum of asks must therefore be below about $0.955 to break even. A 2-leg YES+NO at about 0.5/0.5 costs about $0.025. So pure taker-taker arbitrage now needs a gross gap of roughly 2.5-4.5¢, versus anything above 0 in 2024. **Geopolitics markets (0 fee) and maker-side (limit order) legs are where fee-free rebalancing is still possible.**
- In the 2024 data, "Buy NO" across NegRisk markets was the biggest bucket. Mechanically this means selling the field when ΣYES > 1. It is also partly a disguised bet against overpriced long-shots, which links to the favourite-longshot bias rather than pure arbitrage.
- For a simulated lab running on a cron (minutes, not ms), sub-10-second single-market gaps are not capturable. The realistic play is **posting limit orders (maker) on cheap legs** of NegRisk sets and waiting for fills. That needs a fill model that is honest about adverse selection.

### Gaps
- No independent 2026 measurement of NegRisk sum-of-YES opportunity frequency or duration across the whole platform was found. Only NBA-specific data (above) and vendor claims.
- Exact current fee-introduction dates per category were not established. The docs page has no date in the fetched copy.
- The paper's realized-profit method (rolling 950-block windows, minimum token position) may over- or under-count. The authors say their estimates "generally undercount" potential profit.

## Q2. Combinatorial/logical arbitrage between related markets (election vs party, date ladders, threshold ladders)

### Takeaway
True logical arbitrage between *different* markets was tiny in the 2024 data: about $95k across 13 verified pairs. It is hard to detect automatically, because LLMs flag many false dependencies. Where it exists today (NBA moneyline/spread), it is short-lived, concentrated late in games and about 15 shares deep. Monotonic ladders (dates and thresholds) are the most mechanical variant, but I found no quantitative 2025-26 study of ladder violations on Polymarket.

### Cited Findings
- Combinatorial definition and difficulty: a naive pairwise check is O(2^(n+m)). The authors used an LLM plus heuristics (timeliness, topic, combinatorial relationship) plus manual validation. Most LLM false positives were "weaker" dependencies, such as a swing state vs the national winner. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- Example pairs with realized arbitrage: the GOP presidential win-margin market and the balance-of-power market (presidency/House/Senate). The largest pair made $60k. Pair 4 (popular-vote winner vs presidency) had **6,630 opportunities**, but each was small (average max profit about $100). — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- The authors flag "weak dependencies" (for example "Team A wins semifinal" vs "Team A wins final") as a temporal window for statistical rather than risk-free trades. — [arXiv HTML](https://arxiv.org/html/2508.03474v1)
- NBA moneyline + spread: 290 episodes, 101 bps median, depth-limited (see Q1). — [arXiv 2605.00864](https://arxiv.org/html/2605.00864v1)
- Gebele & Matthes formalise "subset–superset" arbitrage. When one contract's YES set strictly contains another's, buying YES on the superset and NO on the subset spans the outcome space. — [arXiv 2601.01706](https://arxiv.org/html/2601.01706v1)

### Inferences
- Ladders ("BTC above X by date D" across X; "event by date D1 < D2") impose monotonicity: P(by D1) ≤ P(by D2), and P(above X1) ≥ P(above X2) for X1 < X2. A violation gives a risk-free spread (buy the cheap superset, sell or buy NO on the subset). These checks are cheap to run every cycle on Gamma API data and need no LLM. This is the most lab-friendly logical check. Its frequency in 2026 is unknown and should be measured by the lab itself.
- Most "logical" relations seen in practice are only *approximately* dependent, for example a party vs a candidate when candidates can be replaced. They carry resolution-rule risk and should be treated as relative-value trades, not arbitrage.

### Gaps
- No public 2025-2026 dataset or post quantifying ladder or date-ladder violations on Polymarket was found.

## Q3. Cross-platform arbitrage (Polymarket vs Kalshi, Limitless, Myriad, PredictIt, Betfair, sportsbooks): resolution-rule mismatch and capital lock-up

### Takeaway
The academic evidence (Gebele & Matthes, TUM, Jan 2026) shows **persistent, structural cross-venue gaps of 2-4% on average after execution costs**. About 6% of events are listed on several venues. The gaps persist because positions cannot be netted and capital is locked until resolution, and because "equivalent" markets often resolve on different rules. The 2024 election is the textbook case: Polymarket resolved on media calls, Kalshi on inauguration. Execution-adjusted spreads there averaged about $0.03 and reached $0.07. Against sportsbooks, Polymarket's main sports lines sit within about 0.6 points of Pinnacle's de-vigged price, and vendor-measured Polymarket-vs-book arbitrage had a **median edge of 0.44%**.

### Cited Findings
- Gebele & Matthes, "Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets" (arXiv 2601.01706, 5 Jan 2026). 100,000+ events across 10 venues, 2018-2025. About **6% of events are concurrently listed** on several platforms. Equivalent markets show "persistent execution-aware price deviations of 2–4% on average". — [arXiv HTML](https://arxiv.org/html/2601.01706v1)
- Mechanism: "arbitrage positions cannot be netted across venues and must be held until resolution". Divergences are "structural rather than transient". Many pairs show arbitrage almost all the time, while for others fees (for example Futuur) absorb the nominal gaps entirely. — [arXiv HTML](https://arxiv.org/html/2601.01706v1)
- Annualized yields: a "substantial mass exceeds 200% APY" (opportunities persisting at least 1 h). These yields are driven by short times to resolution rather than large mispricings. A naive strategy (always enter the single highest-yield equivalent pair and hold to resolution) returned **1,218.66% over 800 days across only 15 trades**, after modeled frictions. This is a backtest, with few trades. — [arXiv HTML](https://arxiv.org/html/2601.01706v1)
- 2024 election: Polymarket and Limitless resolve on media network calls, Kalshi and Myriad on inauguration. This creates a strict subset relation (Kalshi ⊂ Polymarket), so YES on Polymarket plus NO on Kalshi covers all outcomes. Execution-adjusted spreads before election night "average approximately $0.03 and reach up to $0.07 for sustained intervals". Annualized returns ranged "from single-digit percentages to several hundred percent" depending on the assumed lock-up. Polymarket had $3.3B in volume, Kalshi over $1B, and both were fee-free on that market. — [arXiv HTML](https://arxiv.org/html/2601.01706v1)
- Ng, Peng, Tao, Zhou (SSRN 5331995): Polymarket led Kalshi in price discovery in 2024, and large discrepancies persisted. Snippet only, not read in full. — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5331995)
- Practitioner claims (not verified): gross gaps of 1-5¢ on flagship markets, often 0.5-1.5¢ net. In one example a 3¢ gap is eaten by about 2.2¢ of fees. Kalshi's taker fee is quadratic in price. "A 7% spread is not an edge if there is a 10% chance the contracts resolve differently." Both venues must be pre-funded. — [pm.wiki](https://pm.wiki/fr/learn/prediction-market-arbitrage-after-fees), [tech-insider](https://tech-insider.org/prediction-markets/prediction-market-arbitrage/), [nexusfi](https://nexusfi.com/a/prediction-markets/arbitrage-prediction-markets)
- Sportsbooks vs Polymarket (OddsPapi, a vendor, 88 fixtures on 13 Oct 2026). Winner-market median margin: Polymarket 1.00%, Kalshi 1.02%, Pinnacle 4.02%, bet365 6.70%. Median de-vigged gap to Pinnacle: Polymarket **0.59 pts**, Kalshi 0.75, bet365 0.83. Depth on the thinner side (median top of book): Polymarket $221 overall and $1,830 on the NFL. — [OddsPapi blog](https://oddspapi.io/blog/polymarket-api-kalshi-api-vs-sportsbooks-the-developers-guide/)
- Polymarket vs sportsbooks arbitrage (OddsPapi, 1 Oct 2026). 2,938 raw pairs reduced to **42 real arbs after screens**. **Median edge 0.44%**, best 1.53%, median Polymarket depth $4,023. Most raw "arbs" were placeholder or stale quotes; a naive scanner flags a "29% arb" against a $1.15 order. — [OddsPapi blog](https://oddspapi.io/blog/polymarket-arbitrage-local-bookmakers/)
- Betfair API: the delayed app key is free, gives delayed best-offer prices (1-180 s, or 1-60 s in older docs) and no traded volume. A live key costs £299 and requires a funded account. The keys are for personal use only. — [Betfair developer docs](https://betfair-developer-docs.atlassian.net/wiki/x/GA8p)

### Inferences
- For this lab: cross-venue "arbitrage" can be **simulated** (Kalshi public market data needs no auth), but it is really a held-to-resolution spread trade with resolution-rule risk. The simulator should require a rule-by-rule equivalence check (source, cutoff time, and the treatment of ties, postponements and cancellations) before calling a spread "risk-free". Capital lock-up matters: a 3% spread locked for 3 months is about 12% a year, before the risk of a resolution mismatch.
- More useful than true arbitrage is using **Kalshi or Pinnacle as a reference price** (see Q4b). The ~0.6-pt agreement with Pinnacle means edges are small, and mostly in thin props and wings, not main lines.
- France/legal: the lab only simulates, which is fine. Kalshi/Betfair data reading is allowed via free public endpoints.

### Gaps
- No public, audited P&L of any real cross-platform arbitrage bot was found.
- Limitless, Myriad and PredictIt spreads specific to 2025-26 were not quantified beyond the TUM paper's aggregate.

## Q4. Model-based bots

### Q4a. Weather (temperature) markets

#### Takeaway
There are many public weather bots (GFS/ECMWF/ICON ensembles via Open-Meteo, METAR/ASOS, Weather Underground resolution). Several trader wallets show large self-reported PnL ($34k to $133k). But the **only careful open-source evaluations show backtest edges that do not survive live trading because of adverse selection on fills**, and show that the market favourite beats a raw ensemble at picking the bin. The edge, if any, sits in underpriced cheap bins (5-30¢) at 1-3 day lead times, with per-station bias calibration.

#### Cited Findings
- Dev.to ranking (posted 16 Jun, year presumably 2026; author anonymous, promotes the "Parity" terminal). Weather-trader wallets with PnL: ColdMath **+$124,896** (6,575 predictions, 81.7% "win rate", claimed to be a bot built on a Claude-based agent framework, buying bins at very low prices); VibeTrader +$132,854 (37.7% win rate, also trades Elon-tweet markets); BeefSlayer +$62,064; HenryTheAtmoPhD +$55,838 (claims to be a retired atmospheric-science professor); HondaCivic +$55,408; russell110320 +$43,936 (global-temperature markets); Maskache2 +$34,106 (33.5% win rate). — [dev.to](https://dev.to/xniiinx/my-top-7-most-profitable-weather-market-traders-on-polymarket-gb7). **Claimed**: wallet stats are cited from Polymarket profiles but not independently audited here, and the list is survivorship-biased.
- A Medium/DevGenius post claims a bot turned $1,000 into $24,000 trading London weather since Apr 2025, and others made $65k across NYC/London/Seoul. I could not read it (Cloudflare block); figures are from the search snippet only. — [DevGenius](https://blog.devgenius.io/found-the-weather-trading-bots-quietly-making-24-000-on-polymarket-and-built-one-myself-for-free-120bd34d6f09)
- **hightempbot (GitHub, wwwlqh). Verified README**: an Open-Meteo 11-model ensemble with per-station EMOS calibration (retrained monthly), Weather Underground observations, and order-book walking. Results: paper trading 9-21 May 2026, 142 bets, 73% win, **+3%** return on stake. Live 21-23 May 2026, 25 bets, +60%, but "one outlier, not an edge": a single tail bet turned $1.96 into $70.50, and the main NO strategy won 18 of 22 and still lost $1.94. Best out-of-sample backtest: 308 bets, 81%, +30%. "**The backtests did not carry over to live trading** … the bets the bot could actually fill were disproportionately the losing ones (adverse selection), whichever forecast model was used." — [GitHub hightempbot](https://github.com/wwwlqh/hightempbot)
- **wxedge (GitHub, README in Thai, updated Sep 2026). Verified README**: free sources include ECMWF EPS, GEFS, ICON EPS, NBM, HRRR, NWS and Open-Meteo; IEM ASOS METAR serves as ground truth. Edge audit on 40 market-days, priced at D-24h: the model's top bin was right 40% of the time and **the market favourite 55%** ("the market is better at picking the bin"). But "value bets" (p_model − price > 5%), 59 trades, hit 37% with **ROI +113% before fees**, with profit concentrated in bins priced 0.05-0.30. The author says the edge is "not predicting better than the market, but buying bins the market underprices". Best lead time is 1-3 days; same-day observations absorb the edge. The sum of YES across bins is usually 0.98-1.01. US markets resolve on the **hourly** values of the WRH/Weather Underground page, whose backend is the Synoptic API (needs an NWS token); IEM METAR is the proxy. A 45-day KLGA calibration found HRRR/GFS had the lowest RMSE, ahead of ECMWF IFS/AIFS, with model-specific biases. — [GitHub wxedge](https://github.com/omersait8000-dotcom/wxedge)
- suislanchez polymarket-kalshi-weather-bot: a 31-member GFS ensemble via Open-Meteo, trading Kalshi KXHIGH and Polymarket when edge > 8%, with Kelly sizing capped at $100 per trade. The README says "simulation tool … does not place real trades". The repo description mentions "Highest profits $1.8k", unverified. — [GitHub](https://github.com/suislanchez/polymarket-kalshi-weather-bot)
- Other repos: slavkokolych-alt (ECMWF+GFS+ICON+GEM, Student-t tails, runs on GitHub Actions); codewithpom; kshitij406; PolyWeather. Their READMEs claim methods but no audited P&L. — [slavkokolych-alt](https://github.com/slavkokolych-alt/polymarket-weather-bot), [codewithpom](https://github.com/codewithpom/polymarket-weather-bot), [kshitij406](https://github.com/kshitij406/polymarket-weather-bot), [PolyWeather](https://github.com/abhiram-k-2223/PolyWeather)
- Commercial weather bots sell for $250 a week, with the seller's own disclaimer of losing weeks. These are marketing pages. — [polylab.sell.app](https://polylab.sell.app/product/polylabs-weather-trading-bot)
- Weather markets now carry a 0.05 taker fee rate (fee = 0.05·p·(1−p) per share). — [Polymarket docs](https://docs.polymarket.com/trading/fees.md)

#### Inferences
- The consistent pattern across the honest sources: **the market is well calibrated on the modal bin, and the money is in cheap tail bins and in calibration per station and lead time**. Taker fees at p = 0.10 are about 4.5% of stake (0.05·0.1·0.9 / 0.1), which eats into small edges. A maker-style (limit-order) approach avoids fees but suffers the adverse selection that hightempbot documented.
- The simulator must model fills honestly: a resting order that fills is more likely when the market moved against you. Without this, weather backtests will be inflated, exactly as hightempbot found.
- Resolution source is critical: rounding to integer units, 2°F bins in the US vs 1°C elsewhere, hourly WU values vs 5-minute METAR.

#### Gaps
- No audited, wallet-verified P&L time series for a forecast-driven weather bot. ColdMath and others are leaderboard snapshots, and their "bot" nature is claimed.

### Q4b. Sports models vs sharp bookmaker odds (Pinnacle/Betfair as truth)

#### Takeaway
I found **no rigorous study** showing that Pinnacle- or Betfair-referenced betting beats Polymarket sports markets over time. The available measurements (vendor snapshots, Oct 2026) show Polymarket main lines agree with Pinnacle to within about 0.6 points and carry a much lower margin (about 1% vs 4%). Gaps exist mostly in thin wings, props and stale quotes. Pinnacle-as-truth is a sound *filter*, but its edge on main lines is small.

#### Cited Findings
- Median de-vigged gap to Pinnacle: Polymarket 0.59 pts. Margins: Polymarket about 1% vs Pinnacle 4.02%. Data: 88 fixtures, 13 Oct 2026. Vendor, not peer-reviewed. — [OddsPapi](https://oddspapi.io/blog/polymarket-api-kalshi-api-vs-sportsbooks-the-developers-guide/)
- Polymarket "prices the main markets tight and the wings wide". NFL quarter handicaps and totals had overrounds of 96-98%, which are placeholder rungs. Real cross-book arbs had a median edge of 0.44%. — [OddsPapi](https://oddspapi.io/blog/polymarket-arbitrage-local-bookmakers/)
- A tutorial on testing whether Polymarket is sharper than Pinnacle (needs closing prices from both, outcomes, at least 100 events) presents no results. A companion post claims 3-8% divergences between Polymarket and sportsbooks, unsupported. — [OddsPapi backtest guide](https://oddspapi.io/blog/?p=2489)
- In the 2024-25 data, "Sports Single markets dominate in exploited [single-condition arbitrage] opportunities, surpassing the election profit", and many more small opportunities (≤ $100 of liquidity) appear in sports. — [arXiv 2508.03474](https://arxiv.org/html/2508.03474v1)
- Adjacent literature (sportsbooks, not Polymarket): Simon (Management Science 2025, 3,681 MLB games) finds mostly reliable lines but some profitable simple strategies; Elaad, Reade & Singleton (2020, 16,000+ football matches) find odds are unbiased on average but individual bookmakers are not efficient. — via [search summary; Berkeley/eScholarship PDFs](https://escholarship.org/content/qt67x6v3qd/qt67x6v3qd.pdf)

#### Inferences
- Use Pinnacle (via The Odds API free tier) or Kalshi as a fair-value anchor. Trade only when Polymarket deviates by more than about 2-3 pts net of the 0.05-rate taker fee (about 1.25% of stake at p = 0.5) **and** the quote has real depth and is fresh. Expect few signals and small edges.
- Polymarket's low margin means a "beat the closing line" test needs Pinnacle closing odds, which The Odds API historical endpoint has only on paid tiers. A free path: snapshot odds in the lab's own cycle to build history.

#### Gaps
- No audited CLV or long-run P&L study of Polymarket sports vs Pinnacle or Betfair.

### Q4c. Election/poll models

#### Takeaway / Gaps
- I found no 2024-2026 source reporting quantified profits from poll-model bots (538/Silver Bulletin-style) on Polymarket. Election-period evidence concerns arbitrage (Q1/Q3), not model-based edge. Price discovery led on Polymarket in 2024 ([SSRN 5331995](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5331995)), which suggests poll models were not ahead of the market. This is an inference.

### Q4d. AI/LLM forecasting bots: do they beat the market?

#### Takeaway
Not yet, reliably. On Prophet Arena (Kalshi events), even GPT-5 failed to break even with a naive bet-the-favoured-side rule: average return 0.943 against a market baseline of 0.899. In the live Prediction Arena trading (Jan-Mar 2026), Cohort 1 models averaged **−22.6% on Kalshi and −1.1% on Polymarket**. On ForecastBench, superforecasters still lead the best LLMs by about 0.017 Brier, with parity extrapolated for about late 2026. LLMs help mostly as calibrated aggregators and when they are "crowd-adjusted" toward market prices.

#### Cited Findings
- **Prophet Arena** (arXiv 2510.17638, ICLR 2026): 1,367 Kalshi events resolved before 11 Oct 2025, 23 LLMs. Brier scores fall in [0.18, 0.22]. GPT-5 (reasoning) had Brier 0.184 vs the market's 0.187. **Average return: GPT-5 0.943, market baseline 0.899**, Grok-4 0.864, Gemini 2.5 Flash 0.883, Llama-4-Scout 0.805. "Even GPT-5, the top-ranked model, fails to reach break-even (Average Return < 1), and most models fall below 0.9." LLMs are better calibrated than the market (ECE). The market "achieves the highest short-term accuracy near event resolution", while some LLMs beat it at longer horizons. — [arXiv HTML v2](https://arxiv.org/html/2510.17638v2)
- **Prediction Arena** (Arcada Labs/Harvard, arXiv 2604.07355, 28 Mar 2026), live trading with $10k per model, 12 Jan to 9 Mar 2026. Cohort 1 averaged **−22.6% on Kalshi and −1.1% on Polymarket**. grok-4-20-checkpoint had a 71.4% settlement win rate on Polymarket. gemini-3.1-pro-preview made +6.02% on Polymarket in 3 days, the best of any model. Drivers: initial prediction accuracy and capitalizing on correct calls. "Research volume shows no correlation with outcomes." — [arXiv HTML](https://arxiv.org/html/2604.07355v1)
- **ForecastBench** (FRI, 29 Jan 2026): superforecasters are #1. xAI Grok 4.20 (Preview) and Cassi's ensemble_2_crowdadj are tied at #2, ahead of GPT-5, o3 and Claude Sonnet 4.5, with a gap of **0.017 Brier**. Claude 3.5 Sonnet scored 0.117 (Oct 2024) and Grok 4.20 0.102 (Oct 2025). The extrapolated superforecaster parity is **Nov 2026** (95% CI Jan 2026 to Nov 2027), with market-question parity around Aug 2026. Cassi's "crowd adjustment" (re-check when the forecast disagrees with the market price) improves its Brier by about 0.01. — [FRI Substack](https://forecastingresearch.substack.com/p/llms-are-closing-the-gap-on-human)
- Earlier ForecastBench (Feb 2025): superforecasters 0.081 vs GPT-4.5 0.101. A later "Brier Index" puts superforecasters at 70.6% vs the best LLM at 67.9%. — [longtermwiki](https://www.longtermwiki.com/knowledge-base/responses/epistemic-tools/tools/forecastbench), [FRI Brier Index](https://forecastingresearch.substack.com/p/introducing-the-brier-index)
- **PolyBench** (arXiv 2604.14199, Apr 2026): 7 LLMs on live Polymarket snapshots from 6-12 Feb 2026 (38,666 markets, CLOB-based execution simulation). Only 2 of 7 were positive: MiMo-V2-Flash +17.6% and Gemini-3-Flash +6.2% (confidence-weighted return). Five lost money. The window is short, one week. — [arXiv abs](https://arxiv.org/abs/2604.14199)
- **LiveTradeBench** (UIUC, arXiv 2511.03628, Nov 2025): 50-day live evaluation of 21 LLMs on U.S. stocks and Polymarket. High LMArena scores do not imply better trading. Per the search snippet, one strong stock model returned below −30% on Polymarket, and the correlation between general ability and Polymarket performance was −0.38 (not verified in the full text). — [arXiv abs](https://arxiv.org/abs/2511.03628)

#### Inferences
- Raw LLM probability against the market price, traded as a taker, is negative-EV on average once fees and spread are included (Prophet Arena's baseline return of 0.899 shows the cost of naive betting). The positive signals are narrow: longer horizons, LLM-as-calibrator, and crowd-adjusted ensembles. Short live windows (3 days, 1 week) are noise.
- For the lab: use an LLM as a *filter or tie-breaker* on long-horizon markets, with forecasts shrunk toward the market price, and measure it with the lab's own resolved-market Brier and return log before giving it capital.

#### Gaps
- No full Prophet Arena results with a betting rule that accounts for fees on Polymarket. No audited, long-running live P&L for an LLM agent trading real Polymarket money.

## Q5. Free data sources each strategy needs

### Takeaway
Every strategy here can be fed with free sources: Polymarket Gamma/CLOB (no auth for reads), Kalshi public market data, The Odds API (500 credits a month), the Betfair delayed key, Open-Meteo (10k calls a day, non-commercial), IEM ASOS/METAR, and the NOAA/NWS APIs.

### Cited Findings
- Polymarket Gamma and CLOB reads need no auth. Kalshi public market reads need no auth. — [OddsPapi API guide](https://oddspapi.io/blog/polymarket-api-kalshi-api-vs-sportsbooks-the-developers-guide/)
- **The Odds API** free "Starter" plan: 500 credits a month, all sports, most bookmakers. Historical odds come only on paid plans ($30 a month for 20K credits). A call costs markets × regions credits. — [the-odds-api.com](https://the-odds-api.com/)
- OddsPapi's free plan offers 250 requests a month and includes Polymarket, Kalshi and Pinnacle in one feed, with a free /historical-odds endpoint (vendor claim). — [OddsPapi](https://oddspapi.io/blog/polymarket-arbitrage-local-bookmakers/)
- **Betfair** delayed key: free, delayed best-offer prices, no volume; live key costs £299. — [Betfair docs](https://betfair-developer-docs.atlassian.net/wiki/x/GA8p)
- **Open-Meteo** free API: non-commercial use only, below 10,000 calls a day, 5,000 an hour and 600 a minute (300k a month), CC-BY 4.0. It includes ensemble APIs (GFS, ECMWF, ICON members). — [Open-Meteo terms](https://open-meteo.com/en/terms), [pricing](https://open-meteo.com/en/pricing)
- **IEM ASOS** (mesonet.agron.iastate.edu) gives hourly METAR for airport stations worldwide and rate-limits with HTTP 429 (about 2 s between calls advised). Weather Underground pages are the resolution reference for US markets. — [wxedge README](https://github.com/omersait8000-dotcom/wxedge)
- Polymarket on-chain history comes via the Polygon public nodes used in the 2024 study (Alchemy). — [arXiv 2508.03474](https://arxiv.org/html/2508.03474v1)

### Inferences
- The lab's non-commercial simulation fits Open-Meteo's free terms. The Odds API's 500 credits a month is about 16 h2h single-region calls a day, so poll Pinnacle only for markets that Polymarket actually lists, and only near kickoff.

### Gaps
- I did not confirm whether the NWS/Synoptic token needed for the exact US resolution feed is free.
