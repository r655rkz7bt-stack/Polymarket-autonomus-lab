# Market making on Polymarket and incentive programs for liquidity providers (2024-2026)

Research date: 2026-10-16. Primary sources: Polymarket's official docs (fetched as .md via curl from
docs.polymarket.com), the Polymarket changelog, the Polymarket Help Center, the public CLOB API (queried
live on 2026-10-16), the poly-maker git history, and first-hand accounts. Everything from the web was
treated as data. Note: WebFetch could not resolve several hosts in this environment, so pages were
downloaded with curl and stripped to text.

---

## 1. Liquidity Rewards: exact formula, parameters, where they are exposed, typical amounts

### Takeaway
Liquidity Rewards pay a fixed daily pool per market. The pool is shared according to a time-averaged
quadratic score: an order's score is ((v - s)/v)^2 x size, where v is the market's max spread and s is
the distance from a size-cutoff-adjusted midpoint. The book is sampled once a minute (up to 1,440 samples
per UTC day). Two-sided quoting is rewarded through min(Q_one, Q_two). One-sided quotes earn only 1/3
(c = 3), and earn nothing when the midpoint is below 0.10 or above 0.90. On 2026-10-16 the API listed
15,399 rewarded markets with about $186k/day in total. The median market paid only $3/day. Realistic
earnings were roughly $1 to $10 per day per $1,000 quoted, with rare outliers in markets that had little
competition.

### Cited Findings
**Program mechanics (official doc, current version)**
- Rewards go to makers who post resting limit orders. They are paid daily at midnight UTC. "The minimum reward payout is $1; amounts below this will not be paid." Each incentivized market defines a minimum qualifying order size, a maximum qualifying spread and a reward allocation. — [Polymarket Docs, Liquidity Rewards](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Order scoring function: S(v,s) = ((v - s)/v)^2 · b. v = max spread from midpoint (in cents), s = spread from the "size-cutoff-adjusted midpoint", b = "in-game multiplier". — [Polymarket Docs, Liquidity Rewards](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Q_one = Σ S·BidSize on m + Σ S·AskSize on m′ (the complement token). Q_two = Σ S·AskSize on m + Σ S·BidSize on m′. In other words, a YES bid and a NO ask are on the same "side". — [Polymarket Docs](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Minimum score: if the midpoint is in [0.10, 0.90], Q_min = max(min(Q_one, Q_two), max(Q_one/c, Q_two/c)), with **c = 3.0 "currently on all markets"**, so one-sided liquidity still scores at one third. If the midpoint is in [0, 0.10) or (0.90, 1.0], Q_min = min(Q_one, Q_two), so **liquidity must be two-sided to score**. — [Polymarket Docs](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Q_normal = Q_min / Σ Q_min of all makers in the sample. Q_epoch = Σ Q_normal over samples. "An epoch is one UTC day; the order book is sampled once per minute at a random offset, so an epoch contains up to 1,440 samples." Q_final = Q_epoch / Σ Q_epoch, multiplied by the market's reward pool. — [Polymarket Docs](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Worked example in the doc: midpoint 0.50, max spread 3c. A 100-share bid at 0.49 scores ((3-1)/3)^2·100 = 44.4. A 200-share bid at 0.48 scores ((3-2)/3)^2·200 = 22.2. Being 1c from mid is worth about 2x per share compared with 2c. — [Polymarket Docs](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Minimum resting time: for the March Madness 2026 rewards, "Orders must be active on the book for a minimum of **3.5 seconds** to be eligible". The rewards were described as based on "size of your orders, how close they are to the midpoint, and how consistently they are quoted relative to other liquidity providers". — [Polymarket Changelog, Mar 17 2026](https://docs.polymarket.com/changelog.md) (downloaded copy of the predictions changelog)
- The "in-game multiplier" b exists, but the doc gives no numeric value for it (see Gaps).

**Where the parameters are exposed (verified live on 2026-10-16)**
- In the Gamma market object and the SDK: `market.rewards.rewardsMinSize` (DecimalString), `rewardsMaxSpread` (number, in cents), `clobRewards[]` (each entry has `id`, `conditionId`, `assetAddress`, `rewardsAmount`, `rewardsDailyRate`, `startDate`, `endDate`), and also **`holdingRewardsEnabled`** (bool). Doc example: `rewardsMinSize "100"`, `rewardsMaxSpread 3`, `rewardsDailyRate "100"`. — [Polymarket Docs, Market Details > Liquidity Reward Settings](https://docs.polymarket.com/market-data/market-details.md)
- Live Gamma call `GET https://gamma-api.polymarket.com/markets?...` returned top-level fields `rewardsMinSize`, `rewardsMaxSpread`, `clobRewards`, `holdingRewardsEnabled`. Example: "Will Lula win the 2026 Brazilian presidential election?" had rewardsMinSize 150, rewardsMaxSpread 6.5 and clobRewards `rewardsDailyRate: 1000`, with startDate 2026-10-16 and endDate 2500-12-31. — [Gamma API](https://gamma-api.polymarket.com/markets?limit=5&active=true&closed=false&order=volume24hr&ascending=false) (queried 2026-10-16)
- Public CLOB endpoint `GET https://clob.polymarket.com/rewards/markets/current` (no auth, paginated with `next_cursor`). It returns `condition_id`, `rewards_config[{asset_address, start_date, end_date, rate_per_day, total_rewards}]`, `rewards_max_spread`, `rewards_min_size`, `native_daily_rate` and `total_daily_rate`. — [CLOB API](https://clob.polymarket.com/rewards/markets/current) (queried 2026-10-16). Per-user earnings and order-scoring endpoints exist in the authenticated CLOB API, but I did not verify them in this session.

**Snapshot of all rewarded markets (my own aggregation, 2026-10-16, 31 pages of the endpoint above)** — [CLOB API](https://clob.polymarket.com/rewards/markets/current)
- 15,399 markets carried a rewards config. The sum of `total_daily_rate` was **$186,313/day**. Median $3/day, mean $12.1/day.
- Distribution: ≥$1: 15,114 markets. ≥$5: 7,240. ≥$10: 4,100. ≥$50: 967. ≥$100: 230. ≥$500: 32. ≥$1,000: 6. ≥$5,000: 0. The top 20 markets held only 8.2% of the total.
- Largest pools: "US x Iran ceasefire continues through October 31?" at $2,004/day, "2026 Balance of Power: D Senate, D House" at $1,333/day, several Fed-October and Brazil-election markets at about $1,000/day, and many 2026-midterm × oil combo markets at $500/day.
- Most common max spread (v): 4.5c (8,559 markets), 6.5c (3,997), 5.5c (1,850), 2.5c (229), 3.5c (226). Most common min size: 20 shares (11,173 markets), 50 (2,218), 30 (768), 100 (338), 200 (172; this is typical for the big pools), 1,000 (135).

**Event-specific pools (dated)**
- March Madness, 17 March 2026: "$2M+ in liquidity rewards". Pre-game (48h before start): $7.5k/day for the full-game moneyline and $500/day for 5 other markets. Live: **$60k/day** for the full-game ML, $4k/day for the latest spread and total, and $8k/day for 1st-half markets until halftime. — [Polymarket Changelog](https://docs.polymarket.com/changelog.md)
- Crypto TWAP transition, August 2026: **$1M** across 5-min ($550k), 15-min ($350k) and 4-hour ($100k) crypto markets. BTC 5-min alone had $300k for the month. "This program has ended." — [Polymarket Docs, Liquidity Rewards](https://docs.polymarket.com/programs/liquidity-rewards.md); see also [Crypto Briefing](https://cryptobriefing.com/polymarket-twap-upgrade-liquidity-rewards/)
- 2024 US election: "@Polymarket distributed over $25K daily in market maker rewards" (defiance_cr, 31 March 2025). — [defiance_cr thread via Xunroll](https://xunroll.com/thread/1906774862254800934)

**Estimated reward per $1,000 quoted (my own live estimate, 2026-10-16, single book snapshot)**
- Method: for sampled markets with a midpoint in [0.10, 0.90], I read the YES token book from `GET clob.polymarket.com/book`. I computed the competing Q within v (only levels ≥ min size counted), then placed a hypothetical $1,000 two-sided quote ($500 buying YES and $500 buying NO, 1c from mid) and took its share of the daily pool. — data from [CLOB API](https://clob.polymarket.com/rewards/markets/current)
  - Top 30 pools (n=17 usable): median **$3.9/day per $1,000**, range $0.5 to $319. Large political pools were crowded: "R Senate" at $500/day had Q ≈ 405k, which gives $0.50/day per $1k. The D-Senate/D-House balance-of-power market at $1,333/day gave $1.48. The outlier was "GTA VI trailer views 40-60M" at $604/day with only Q ≈ 408, giving $319.
  - Pools of $50-200/day (n=15): median $50, mean $46. Many of these books were empty (spread 30-92c), so a lone quoter would take the whole pool. These are illiquid, hard-to-price markets (Oscar nominations, earnings beats, weather), where adverse selection is the main risk.
  - Pools of $5-20/day (n=22): median $5/day, which is close to the entire pool. Pools of $1-3/day: median $1.
  - Capped by the $1 minimum payout, and the rewards on small pools are tiny.

**Reported historical figures**
- "During the 2024 US Presidential election... I became a top 5 recipient." The bot placed "YES and NO orders one tick above the nearest 200-share level" in markets below volatility thresholds. — [defiance_cr thread, 31 Mar 2025](https://xunroll.com/thread/1906774862254800934)
- defiance_cr: "rewards multiply if you post on both sides (bid/ask), and the closer you put the bid/ask, the exponentially better rewards you get." In the interview: "you get nearly 3x the rewards" for two-sided quotes, which matches c = 3. — [thread](https://xunroll.com/thread/1906774862254800934); [The Oracle, 28 May 2025](https://news.polymarket.com/p/automated-market-making-on-polymarket)

### Inferences
- The score is relative, so income per market is capped by the pool. Once you dominate a market, adding size has strongly diminishing returns. Third-party descriptions of poly-maker say the same thing ("competing against yourself").
- Large pools are crowded: hundreds of thousands of Q-points in big political markets. The highest $/capital tends to be in mid-sized pools with thin books, which are exactly where adverse selection risk is highest. The economic logic is reward per unit of volatility, not reward per market.
- With v typically 4.5c and the ((v-s)/v)^2 shape, a quote 1c from mid scores 0.60 and a quote 2c from mid scores 0.31. Most of the score sits within 1-2c of mid, which is close enough to get filled.
- The per-minute random sampling means quoting only around the sampling instant is impossible. Quotes must rest continuously, and the March 2026 rule (≥ 3.5 s resting) was aimed at flicker quoting.

### Gaps
- No numeric value for the "in-game multiplier" b, and no precise definition of the "size-cutoff-adjusted midpoint". It is presumably the midpoint computed after ignoring levels below `rewardsMinSize`, but this is not stated explicitly.
- I did not verify the authenticated per-user endpoints (user earnings, order scoring) in this session.
- Whether the 3.5-second minimum applies to all markets or only to the March Madness pools is unclear.
- My $/1,000 estimates use a single snapshot, only the YES token's book (NO-book orders may be extra competition, or may be the same orders mirrored), and ignore fills. Treat them as order-of-magnitude figures.
- No public Dune dashboard of reward payouts per wallet was found in this session.

---

## 2. Maker Rebates, Holding Rewards, Taker Rebate tiers

### Takeaway
Since January 2026, taker fees (fee = C × feeRate × p × (1−p)) fund a **Maker Rebates** pool per market:
20% of fees in crypto, 15% in sports (since 10 July 2026) and 25% in other categories. Each maker's share
is proportional to the fee value of their own filled maker volume. **Holding Rewards** pay an annualized
rate on positions in a fixed list of long-dated markets: 4% in September 2025, **3.25% as of June 2026**,
funded by the treasury. The **Taker Rebate Program** (live since 28 May 2026) rebates 3% to 50% of fees to
takers by 30-day weighted volume. It does not concern makers.

### Cited Findings
**Maker Rebates**
- "Polymarket charges taker fees across multiple market categories... fund a Maker Rebates program that pays daily pUSD rebates." Eligibility: "Place orders that add liquidity to the book and get filled." Minimum payout $1. — [Polymarket Docs, Maker Rebates](https://docs.polymarket.com/programs/maker-rebates.md)
- Rebate share of taker fees: Crypto 20%; Sports 15%; Finance, Politics, Economics, Culture, Weather, Other/General, Mentions and Tech 25%; Geopolitics fee-free. All are "Fee-curve weighted". — [Polymarket Docs, Maker Rebates](https://docs.polymarket.com/programs/maker-rebates.md)
- Per filled maker order: fee_equivalent = C × feeRate × p × (1 − p). rebate = (your_fee_equivalent / total_fee_equivalent) × rebate_pool. "Totals are calculated per market, so you only compete with other makers in the same market." — [Polymarket Docs, Maker Rebates](https://docs.polymarket.com/programs/maker-rebates.md)
- Taker fee rates: Crypto 0.07; Sports 0.05; Finance 0.04; Politics 0.04; Economics 0.05; Culture 0.05; Weather 0.05; Other 0.05; Mentions 0.04; Tech 0.04; Geopolitics 0. Maker fee is 0 everywhere. "Makers are never charged fees." For crypto, 100 shares at 50c costs a $1.75 fee, i.e. 3.5% of notional at the peak. — [Polymarket Docs, Fees](https://docs.polymarket.com/trading/fees.md)
- Fees are rounded to 5 decimals (minimum 0.00001 pUSD). — [Maker Rebates](https://docs.polymarket.com/programs/maker-rebates.md)
- Timeline from the changelog — [Polymarket Changelog](https://docs.polymarket.com/changelog.md):
  - 5 Jan 2026: taker fees on 15-min crypto markets (peak 1.56% at 50%) and daily maker rebates introduced.
  - 16 Jan 2026: fee-curve weighted distribution documented (previously "volume-weighted vs fee-curve weighted").
  - 11 Feb 2026: rebates computed per market. NCAAB and Serie A fees from 18 Feb.
  - 12 Feb 2026: 5-minute crypto markets launched with fees.
  - 6 Mar 2026: fees and rebates extended to all crypto markets (1H, 4H, daily, weekly; new markets only).
  - 30 Mar 2026: "Fee Structure V2", with fees across most categories.
  - 10 Jul 2026: sports fee raised from 0.03 to 0.05 and sports maker rebate cut from 25% to 15%.

**Holding Rewards**
- Help Center (dated 1 June 2026): "we're paying **3.25%** annualized Holding Reward based on your total position value in certain Polymarkets". The rate is variable, can be capped, and is "funded through the Polymarket Treasury". Position value = YES shares × mid + NO shares × mid, "randomly sampled once each hour", paid daily. Example: $20,400 × 0.0325/365/24 ≈ $0.0757/hour. — [Polymarket Help Center, Holding Rewards](https://help.polymarket.com/en/articles/13364459-holding-rewards)
- Eligible events listed in June 2026: Presidential Election Winner 2028; R and D nominee 2028; party winning the 2028 presidency; Balance of Power 2026 midterms; Senate 2026; House 2026; Erdoğan, Zelenskyy, Netanyahu, Xi or Putin out before 2027; Russia × Ukraine ceasefire before 2027; BTC, ETH, HYPE, SOL and XRP price-in-2026 markets. — [Polymarket Help Center](https://help.polymarket.com/en/articles/13364459-holding-rewards)
- Earlier rate: "Polymarket will offer a **4%** annualized interest rate on positions in 13 eligible markets" (published 24 September 2025). — [Cryptopolitan](https://www.cryptopolitan.com/polymarket-starts-paying-out-4-rewards/). Some search snippets of the docs still quote 4.00%. The Help Center page dated June 2026 says 3.25%. Treat **3.25% as the current rate** and 4% as the 2025 rate.
- The Gamma field `holdingRewardsEnabled` flags eligible markets. All five top-volume markets queried on 2026-10-16 had it set to False. — [Gamma API](https://gamma-api.polymarket.com/markets?limit=5&active=true&closed=false&order=volume24hr&ascending=false); [Market Details doc](https://docs.polymarket.com/market-data/market-details.md)

**Taker Rebate Program**
- "goes live on Thursday, May 28, 2026". Weighted volume wV = Trade Size ($) × (1 − Entry Price) × Category Weight × Bonuses. Weights: Sports 1.0; Politics, Finance, Mentions and Tech 1.3; Economics, Culture, Weather and Other 1.7; Crypto 2.3; Geopolitics 0. — [Polymarket Docs, Taker Rebates](https://docs.polymarket.com/programs/taker-rebates.md)
- Tiers by 30-day wV, with rebate and level-up bonus:

  | Tier | 30-day wV | Rebate | Level-up bonus |
  |---|---|---|---|
  | Bronze | $2k | 3% | $10 |
  | Silver | $20k | 8% | $50 |
  | Gold | $200k | 18% | $250 |
  | Platinum | $1M | 32% | $1,500 |
  | Diamond | $4M | 44% | $7,500 |
  | Obsidian | $10M | 50% | $25,000 |

  "Only taker trades earn Weighted Volume... Maker trades... do not." Wash trading and self-matching are excluded. — [Polymarket Docs, Taker Rebates](https://docs.polymarket.com/programs/taker-rebates.md)

### Inferences
- Maker Rebates reward fills, not resting liquidity. That is the opposite of Liquidity Rewards, which reward resting orders near mid whether or not they fill. A maker's rebate income is roughly maker volume × feeRate × p(1−p) × rebate%. Example: $100k/day of maker fills in a crypto market at around 50c gives 0.07 × 0.25 × 20% ≈ 0.35% of notional, so about $350/day. This is gross and comes before adverse-selection losses on exactly those fills (the fast crypto markets are the most toxic).
- Taker fees (up to 1.75% of notional at 50c in crypto, 1% in politics) make it much more expensive for a maker to exit inventory by crossing the spread. This favours the "merge YES+NO" exit used by poly-maker.
- Holding Rewards at 3.25% are small but stack with market making on long-dated political markets. Inventory held in eligible markets (e.g. the 2028 election) earns about 0.009%/day.

### Gaps
- I found no public figure for the total daily Maker Rebate pool or for typical per-wallet rebate income.
- The exact start and end dates of Holding Rewards and the date of the cut from 4% to 3.25% are not given. The Help Center page is only dated June 1, 2026.
- Whether Liquidity Rewards and Maker Rebates can be earned on the same order: nothing in the docs prevents it, but it is not stated explicitly.

---

## 3. Results reported by market makers (and their decline)

### Takeaway
The best-documented case is defiance_cr (Daniel Sapkota, author of poly-maker). He started with $10k at
about $200/day, peaked at $700-800/day during the 2024 election, and was a top-5 recipient of more than
$25k/day of rewards. After the election, rewards "decreased significantly" and he shut the bot down. Since
January 2026 his README says the bot "is not profitable and will lose money" because of competition. An
independent operator who forked it (December 2025) reported no net profit.

### Cited Findings
- "I started with $10,000 in capital and was earning about $200 per day. As I scaled up and refined the system, I reached $700-800 daily at peak. The key was Polymarket's liquidity rewards program." — [The Oracle (Polymarket newsletter), 28 May 2025](https://news.polymarket.com/p/automated-market-making-on-polymarket)
- Why he stopped: "After the 2024 election, Polymarket's total liquidity rewards decreased significantly, making the strategy less profitable." Competition back then: "only 3-4 serious liquidity providers on the platform, and most were doing it manually"; "maybe one or two other bots". — [The Oracle, 28 May 2025](https://news.polymarket.com/p/automated-market-making-on-polymarket)
- Market selection edge: "people were providing the same liquidity in a 500% volatility market as they did in a 100% for the same reward." He also crashed the API by polling history, which he took as a sign "no one else was systematically analyzing this data live". — [defiance_cr thread, 31 Mar 2025](https://xunroll.com/thread/1906774862254800934)
- poly-maker README history (git log of github.com/warproxxx/poly-maker): the repo was published on 2025-03-31. On 2026-01-17 a disclaimer was added: "In today's market, this bot is not profitable and will lose money... Given the increased competition on Polymarket, I don't see a point in playing with this unless you're willing to dedicate a significant amount of time." The 2026-07-05 V2 rewrite says "Market making on Polymarket is competitive and can lose money... not a guaranteed-profitable product." — [poly-maker repo](https://github.com/warproxxx/poly-maker) (cloned and inspected 2026-10-16)
- Terry Lee (forked poly-maker, post dated 8 Dec 2025): "I didn't end up making any net profit overall. While the bot did generate maker rewards and some spread earnings, most of those gains were offset, if not completely wiped out by early mistakes, execution bugs, misconfigured logic." Also: "a single adverse move of 30–40% can wipe out accumulated gains within minutes." — [Terry's Takes (Substack)](https://tezlee.substack.com/p/i-cloned-a-polymarket-market-making)

### Inferences
- The decline has three causes: smaller pools after the election, more automated competitors (open-source bots, Q dilution), and since 2026 fees that raise exit costs. On the other side, 2026 added new income sources: Maker Rebates, and very large event pools such as $60k/day live March Madness moneylines.
- In the current snapshot the total reward budget (≈ $186k/day across 15k markets) is larger than the 2024 election figure (>$25k/day). But it is spread across many tiny pools ($3/day median), so the per-market edge is thin.

### Gaps
- No verified 2026 earnings figures from any active, named market maker. Claims on X and marketing sites (e.g. startpolymarket.com, quantvps.com, polymart.app) are unverified and often affiliate-driven, so I did not use them.
- No split between spread P&L and reward income in defiance_cr's figures.

---

## 4. How MM bots avoid getting picked off, and which markets are best

### Takeaway
The standard toolkit:
- quote around a microprice or fair value, with inventory skew (Avellaneda-Stoikov style);
- widen and shrink size with realized volatility and fill "toxicity" (markouts);
- pull quotes on jumps, news and before known catalysts (GTD expiry);
- use a heartbeat dead-man switch;
- cap per-market and per-event exposure;
- exit inventory by merging YES+NO pairs rather than crossing the spread.

The best markets are low-volatility, long-dated ones with a high reward-to-competition ratio. Volatile,
headline-driven markets are where the losses come from.

### Cited Findings
- Official best practices: quote both sides, "Skew on inventory", "Cancel stale quotes: Pull orders immediately when market conditions change", "Use GTD for events: Expire quotes before known catalysts", batch orders, use WebSockets rather than polling, size limits, price guards against the midpoint, a kill switch (cancel all). Orders cannot be edited in place; changing a quote means cancel and replace. Use post-only orders to guarantee maker status. — [Polymarket Docs, Market Making](https://docs.polymarket.com/trading/market-making.md)
- Inventory: split pUSD into a YES+NO complete set to get tokens to sell. Merge complete sets back to pUSD. Redeem after resolution. Neg-risk multi-outcome markets change how sets are merged. "Buying NO at 0.48... is economically equivalent to selling YES at 0.52." — [Polymarket Docs, Market Making](https://docs.polymarket.com/trading/market-making.md)
- Heartbeat API ("HeartBeats endpoint for monitoring connection status and canceling orders") and Post-Only orders were added on 6 Jan 2026. — [Polymarket Changelog](https://docs.polymarket.com/changelog.md)
- Rate limits as of 1 Jun 2026: POST /order and DELETE /order at 120,000 per 10 min (200/s sustained); batch POST/DELETE /orders at 2,000 per 10 s burst. Since 15 Jun 2026, DELETE /orders is limited to 1,000 IDs per request. — [Polymarket Changelog](https://docs.polymarket.com/changelog.md)
- poly-maker v2 (July 2026) strategy:
  - Fair value = "depth-weighted microprice... nudged by an EWMA of signed trade flow".
  - Reservation price r = FV − skew(inventory); half-spread δ = base + c_vol·σ + c_tox·toxicity.
  - Posts BUY-YES at r−δ and BUY-NO at (1−r)−δ, so that "a filled pair merges back to USDC at locked edge 1 − p − q".
  - Regime machine: QUIET (farm rewards in-band), TRENDING (widen, half size), EVENT (sweep/jump detected → pull quotes), REDUCE_ONLY (near end date), HALTED.
  - Risk controls: per-market notional cap, neg-risk event-group worst-case cap, daily-loss kill switch, WS-staleness halt.

  — [poly-maker README](https://github.com/warproxxx/poly-maker)
- defiance_cr (2025): rank markets by volatility over 3h/24h/7d/30d against expected reward per $100. "The key is finding markets with low volatility but high rewards." Example of a good market: Canada PM odds "fluctuate between 22-25% over several weeks". Example of a bad one: a trade-deal market "where a game-changing headline could come at any minute". He used stop-losses, trade-flow monitoring and order-book imbalance checks, and found that "market signals were embedded in orderbook dynamics and cumulative trade volumes before showing up completely in price action." — [The Oracle](https://news.polymarket.com/p/automated-market-making-on-polymarket); [thread](https://xunroll.com/thread/1906774862254800934)
- Terry Lee: "Low-volatility and tight-spread markets are far more forgiving... Directional risk is the real P&L killer." The bot "kept adding to losing sides" until accurate position snapshots were implemented. — [Terry's Takes](https://tezlee.substack.com/p/i-cloned-a-polymarket-market-making)
- Resolution risk: holding Yes/No inventory into resolution turns into all-or-nothing exposure (0 or 1). In the March 2026 live sports pools, the largest rewards ($60k/day) are on in-game markets, the most jump-prone. — [Changelog](https://docs.polymarket.com/changelog.md)

### Inferences
- Adverse selection is concentrated in markets with a fast external reference (crypto 5/15-min, live sports) and in headline-driven political and geopolitical markets. Market makers there need low-latency feeds; a GitHub-Actions-scale cadence can't compete. A cron-based simulated agent like this lab's would be structurally picked off in those markets.
- Under the quadratic score, staying within about 1-2c of mid captures most of the reward but gets filled on any move. "Quote away from mid" trades reward for safety: at 3c out with v = 4.5c, the score drops to 0.11 per share.
- Candidate market profile for a slow bot: midpoint between 0.15 and 0.85 (one-sided still scores 1/3, two-sided is not forced), long-dated, low realized volatility, pool large relative to competing Q, and no scheduled catalyst before the GTD expiry. Holding Rewards eligibility is a bonus.

### Gaps
- No quantitative public data on markout or adverse-selection costs per market category on Polymarket was found in this session.

---

## 5. Can a simulation measure this honestly? Data needed

### Takeaway
Partly. Reward earnings can be simulated reasonably: the formula is public, parameters are in the API,
and books can be sampled. Fills of resting orders are the hard part. Queue position and the toxicity of
the flow that hits you can't be observed from snapshots alone, and the main risk is optimistic fill
assumptions (fills only when price "touches") that ignore adverse selection.

### Cited Findings
- Reward inputs are all public and free:
  - per-market `rewards_max_spread`, `rewards_min_size` and `total_daily_rate` from `GET clob.polymarket.com/rewards/markets/current`, or `rewardsMinSize`, `rewardsMaxSpread` and `clobRewards[].rewardsDailyRate` from Gamma;
  - live books from `GET clob.polymarket.com/book?token_id=...` (both queried successfully, unauthenticated, on 2026-10-16).

  — [CLOB API](https://clob.polymarket.com/rewards/markets/current); [Market Details doc](https://docs.polymarket.com/market-data/market-details.md)
- The real scoring samples once a minute at a random offset, up to 1,440 samples per day, and normalizes per sample and then per day. — [Liquidity Rewards doc](https://docs.polymarket.com/programs/liquidity-rewards.md)
- Rebate inputs: per-market fee rate (the `feeSchedule` object in the market, per the changelog of 31 Mar 2026), category rebate %, and your fills versus all maker fills in the market. — [Changelog](https://docs.polymarket.com/changelog.md); [Maker Rebates doc](https://docs.polymarket.com/programs/maker-rebates.md)
- Real-time trades and book updates are available over the public market WebSocket, as the market-making doc recommends. — [Market Making doc](https://docs.polymarket.com/trading/market-making.md)
- poly-maker itself has a `--paper` mode but lists "a replay backtester over the captured journals" as "Not yet built", which shows that honest fill simulation is still open even for practitioners. — [poly-maker README](https://github.com/warproxxx/poly-maker)

### Inferences
- **Reward simulation (feasible):** at each cycle, fetch the book plus reward params. Insert the virtual quotes. Compute Q_one, Q_two and Q_min for the virtual maker and for all other resting liquidity, approximating the others as one aggregate maker; this overstates competitors' Q_min a little, which is conservative. Accrue share × daily_rate / 1,440 per sampled minute. Sampling less often than once a minute (e.g. a cron every N minutes) has to be extrapolated, and that is a bias to label clearly. Apply the $1 minimum payout and the 3.5-second minimum resting time.
- **Fill simulation (hard, and decisive for P&L):**
  - Conservative rule: a resting bid at price P is filled only when the trade tape shows trades at prices < P (strictly through), or at P with volume above the queue ahead.
  - Book every fill at the order price, then mark it to the later mid (markout) to measure adverse selection.
  - Without the trade tape, polling snapshots overestimate safety: price can cross and come back between polls.
- **Inventory and resolution:** hold the filled inventory, value it at mid, allow merging YES+NO pairs at 1.00, and settle at 0/1 on resolution. Unrealized gains must not count as available cash, in line with the lab's rule.
- **Honest reporting:** report separately (a) reward income, (b) maker rebates, (c) spread/markout P&L and (d) resolution P&L. Rewards are only "real" if (c) + (d) don't wipe them out, as Terry Lee's experience shows.

### Gaps
- No public historical archive of minute-level books plus reward params was identified. A simulation would have to collect its own snapshots going forward.
- The others' split between Q_one and Q_two can't be attributed per wallet from the public book. Only aggregate approximations are possible.
