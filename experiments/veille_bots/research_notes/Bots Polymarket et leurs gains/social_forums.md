# What Polymarket bot builders and traders say on social media and forums (2024-2026)

Scope: first-hand practitioner accounts on Reddit (r/Polymarket, r/algotrading, r/algobetting, r/Kalshi), Hacker News, X/Twitter (indirectly), YouTube, and blogs that practitioners link from forums. GitHub READMEs and academic papers are covered in sibling notes (`open_source_bots.md`, `profitability_evidence.md`, `latency_strategies.md`, `market_making_rewards.md`, `arbitrage_models.md`), so they are only mentioned here when a forum post points to them.

Method and caveats:
- Reddit's own site and JSON endpoints returned HTTP 403 or a login wall from this sandbox. Reddit posts and comments were read from the public Arctic Shift archive API (`arctic-shift.photon-reddit.com/api/...`); links below point to the original reddit.com permalinks. Many 2026 posts were "[removed]" by moderators or spam filters, so only titles survive for those.
- Hacker News was read through the official Algolia API (`hn.algolia.com/api/v1/items/<id>`).
- X/Twitter could not be read directly (xcancel returned 451, nitter returned an empty shell). X content appears only where it is quoted on HN or Reddit or in articles.
- Several practitioner blogs linked from forums (kacho.io, uruguabot.com, *.substack.com, news.polymarket.com) did not resolve (DNS failure) from this sandbox. Their content is known only through the authors' own forum posts.
- **Everything below is a claim by the poster** unless it is marked as verifiable (a public wallet or profile was given). Even a wallet link only lets you check the account. It does not prove that a bot made those trades, or that the posted strategy description is accurate.
- Today's date is 2026-10-16. All dates are the posting dates (UTC).

---

## 1. What bots do practitioners say they run, and what results do they claim, by strategy?

### Takeaway
The detailed, checkable accounts (public wallet plus a full P&L breakdown) show small, short-lived profits that decayed or reversed within a few months. Examples: ~$5k net from a cross-venue esports arb that was switched off; +4.2% on combo market making, then all of it and "several thousand dollars more" lost; $58k on the World Cup from a human-in-the-loop sports trader who calls it partly luck. The spectacular claims (99.3% win rate, $1.4K into $965K, $1 into $3.3M) are third-party "I found a wallet" posts or articles, and forum commenters rejected them.

### Cited Findings

**Cross-venue / sportsbook-vs-Polymarket arbitrage (esports) — verifiable wallet**
- u/File-Environmental (blog kacho.io, Polymarket handle @b00k13) ran a bot from January to late March 2026. It de-vigged sharp sportsbook odds into a fair price and posted passive limit orders on Polymarket esports markets at a ≥7% edge. Claimed reconciled P&L: arbitrage +$8,293, directional (unhedged leftover legs) −$3,184, cancelled matches −$134, **net +$4,973**. That came from 3,858 fills on ~$96k volume with a 47.5% win rate. — [Reddit r/algotrading, 2026-06-09](https://www.reddit.com/r/algotrading/comments/1u17e2v/)
- The same author says the edge decayed: monthly win rate went 50.2% → 48.3% → 43.4% "as competition turned up and fees got introduced". Profit was +$2,506 in February and +$390 in March, "so I switched it off." He blames the directional losses on "adverse selection from faster market makers picking off my stale quotes, a sign-flip bug that had me on the wrong team for a while, a devig method (Shin's) that ran hot on favourites." — [Reddit r/algotrading, 2026-06-09](https://www.reddit.com/r/algotrading/comments/1u17e2v/)
- On HN he adds that limit orders in these thin, wide-spread markets took "~25 minutes" on average to fill ("bid at best_bid + 1c and wait"). He also says "Every arb is a directional bet that eventually got arbed." The team-swap bug happened because the bot did not match the team order between the bookmaker and Polymarket ("Coded almost entirely with AI"). — [HN, 2026-06-09](https://news.ycombinator.com/item?id=48461522)
- When he open-sourced the retired Python version (polymm), he wrote that "the scrapers that kept my odds fresh aren't in it — that plus speed was the edge… It's a working foundation, not a money printer." He now runs a Rust rewrite. — [HN Show HN, 2026-07-21](https://news.ycombinator.com/item?id=48994970); [Reddit r/algotrading, 2026-07-21](https://www.reddit.com/r/algotrading/comments/1v2oyv1/)
- An HN commenter (jbowz) said that at ~$5k realised "the dollar number says very little either way". The informative statistics are fill count and average edge per fill. — [HN, 2026-07-21](https://news.ycombinator.com/item?id=48994970)

**Kalshi ↔ Polymarket "risk-free" arbitrage**
- Two heavily upvoted r/algotrading posts (281 and 431 points) promoted open-source Kalshi/Polymarket arb bots. One of them is built on the posters' own SDK (pmxt / Synpath). The backtest claimed for TX-15 was "4 trades, 4 wins, +$321.50" on ~$980 of capital. — [Reddit 2026-01-16](https://www.reddit.com/r/algotrading/comments/1qebxud/); [Reddit 2026-09-29](https://www.reddit.com/r/algotrading/comments/1wt6hzg/)
- Pushback in the comments, from a builder who records Kalshi and Polymarket books (~9 GB/day):
  - Of 19,692 candidate pairs, **91.5% had different settlement rules**. Examples: BTC daily settles on the Binance 1-minute close on Polymarket but on the BRTI 60-second average at 5 PM ET on Kalshi; NYC weather uses different stations.
  - 7.1% of resolved sports baskets did not pay $1.
  - In a live two-book snapshot of 60 pairs, zero cleared 2¢ net. Median depth on the thinner side was about $20.
  - Only 1.18% of 847 BTC 15-minute windows ever split enough to lock, and those paid −0.1¢ to +1.1¢.
  - A "Kalshi as signal, Polymarket as trade" forward paper run lost −10.2¢ ± 5.3¢ per contract (−$79.77 over 70 trades, 50% fill rate).
  - The commenter openly pasted this as Claude output generated from his research notes, so treat it as his claimed data. — [Reddit comment, 2026-09-29](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcuttlk/); [follow-up](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcwomti/)
- Another commenter (u/Sifrisk) ran the same idea in demo mode for weeks. Opportunities lasted long enough that latency did not matter, but the edge was "~0.5% generally after fees, not 3%", total liquidity was limited, and he stopped before going live because "both platforms became illegal to use in my country." — [Reddit comment, 2026-09-29](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcsqwca/)

**Market making / liquidity rewards**
- u/ahunnidhandles said his market-making bot was making "3-8% per month" and that the CLOB v2 upgrade "gave it all back and then some." — [Reddit r/algotrading, 2026-05-02](https://www.reddit.com/r/algotrading/comments/1t1tg30/)
- In the same thread, a commenter said v2 changed partial-fill cancellation and matching sequence. They also said the effective per-fill cost on small orders "crept up roughly 0.4-0.8%" because of relayer/settlement cost not shown in the published fee. Another commenter: "infrastructure changes are a real source of strategy mortality that doesn't show up in backtests." — [Reddit comment](https://www.reddit.com/r/algotrading/comments/1t1tg30/_/ojng8pf/); [Reddit comment](https://www.reddit.com/r/algotrading/comments/1t1tg30/_/ojsqw4p/)
- Combo/parlay RFQ market making (u/IcyResult2203):
  - Started in early July 2026, shortly after Polymarket launched combos. Claimed **+4.2% ROI (~$1,600 on ~$38K committed, ~1,100 filled RFQs) in under a month**, helped by the World Cup and a Polymarket long-shot combo promotion.
  - Then, from late July over about six weeks, "lost all of my profit plus several thousand dollars more" with the same strategy.
  - Suspected manipulation: asks placed far below the best ask to distort his depth-walk pricing, then RFQs on combos using those legs. He also saw "a huge burst of small RFQs for the exact same combo from one — or a cluster — of requestors."
  - A commenter: "the 0.3% cushion is nothing when your fair price itself is getting manipulated by 2-3%." — [Reddit r/algobetting, 2026-10-10](https://www.reddit.com/r/algobetting/comments/1x2q5ob/)
- A removed r/Polymarket post title reads: "Built a Polymarket market-making bot which printed for 2 weeks then stopped filling orders and I lost track of $800 in unredeemed…". Only the title survives. — [Reddit, 2026-06-24](https://www.reddit.com/r/Polymarket/comments/1ue4y0d/)
- defiance_cr (the poly-maker author) said in a Polymarket newsletter interview that his liquidity-reward bot made about $700-800/day at its peak before he shut it down and open-sourced it. This was seen only via a search summary because news.polymarket.com did not resolve here. — [The Oracle / Polymarket newsletter](https://news.polymarket.com/p/automated-market-making-on-polymarket); [X post linking it](https://x.com/polymarketinfo/status/1927753253795545131)

**15-minute / 5-minute crypto up-or-down bots**
- u/Ill-Fly-2027 runs maker orders in the 0.50-0.60 band on BTC/ETH 15-minute markets. Only 65% of orders fill, with a 55% win rate. The 35% that do not fill would have won 80% of the time. He still claims a profit thanks to zero maker fees and "a few dollars in daily market maker rewards". A commenter called this textbook adverse selection: "The fills are selected against you." — [Reddit r/algotrading, 2026-09-11](https://www.reddit.com/r/algotrading/comments/1wdkmjj/); [comment](https://www.reddit.com/r/algotrading/comments/1wdkmjj/_/p96m6mo/)
- u/Orphis_ built a paper-only 5-minute bot with an "execution realism" ladder. The baseline "initially looked mildly profitable under naive assumptions, but progressively died as execution realism increased". The "edge dies with ~0.01 additional slippage". Median quote freshness was ~1.5 s, but the p95 was ~67 s. The real bottleneck was collection latency and quote freshness, not model inference (~100 ms). — [Reddit r/algotrading, 2026-05-28](https://www.reddit.com/r/algotrading/comments/1tpu2nz/)
- A self-described non-coder's live BTC bot: 63.6% win rate, 49W/28L, **+$20.24 net**, max drawdown $41.92, running on AWS. — [Reddit r/Polymarket, 2026-05-28](https://www.reddit.com/r/Polymarket/comments/1tpxkct/)
- On r/Kalshi, the same market type looks the same:
  - A seller's bot claims 265 live trades, 250 won, +$49.89 after fees. The author points out that it buys favourites at 90-95¢, so it "needs ~92.6% wins just to break even. It's at 94.3%. One loss (−$14.23) wiped out about ten wins." He sells a version at $19.99/month. — [Reddit r/Kalshi, 2026-10-10](https://www.reddit.com/r/Kalshi/comments/1x2nrrp/)
  - A thread asking "Has anyone been able to make a successful trading bot" (49 comments) is mostly negative ("After fees, it's a 49/49 flip"; "15m crypto was one of the hardest markets… prone to manipulation and last-second flips").
  - One commenter (u/meeni131) claims "$200-1000 per day per exchange", fully automated on Kalshi and Polymarket, with no losing day in ~90 days. Another replied that only "super liquid, super high turnover, market making or stat arb" strategies could do that. — [Reddit r/Kalshi, 2026-09-29](https://www.reddit.com/r/Kalshi/comments/1wt0s5v/)
- Taker latency complaints: "25ms maker orders but 300ms+ taker orders. News says they removed the 500ms delay but it seems like it's 250-300ms now." — [Reddit r/algotrading, 2026-04-04](https://www.reddit.com/r/algotrading/comments/1sbwxbv/). Other latency threads cite ~268 ms round trip from AWS Dublin ([2026-03-26](https://www.reddit.com/r/algotrading/comments/1s4iena/)) and 117 ms tick-to-RTT ([2026-09-16](https://www.reddit.com/r/algotrading/comments/1wi9xk8/)).
- A removed r/algotrading post title: "I tested the viral 'buy the favourite in the last 2 minutes' Polymarket BTC bot on 7,120 markets. Pre-registered, official settlem…". The body is unavailable. — [Reddit, 2026-09-17](https://www.reddit.com/r/algotrading/comments/1wiwbk2/)

**Copy trading**
- Walk-forward test by OrcaLayer (an analytics vendor, disclosed):
  - Copied wallets' first buys (≥$20, price 0.30-0.85), adding +1¢ slippage and the taker fee.
  - Top-10 wallets went from +$2.72 to +$3.78 per $10 in the selection window to −$2.23 to +$0.16 the following month. Spearman correlation between periods was −0.01, +0.15, +0.08, −0.03.
  - Copying every wallet lost $0.31-0.63 per $10 in every test month. At +3¢ slippage everything was negative.
  - MLB alone: 161,094 copies, total −$83,012.60. NFL, college football, LoL and Valorant looked "the same or worse".
  - Warning: wallet labels such as "smart money" and win rate are computed on full history and leak survivorship into backtests. — [Reddit r/algotrading, 2026-10-11](https://www.reddit.com/r/algotrading/comments/1x38s11/); [data repo](https://github.com/orcalayer/polymarket-copy-trading-whales-backtest)
- A tennis-wallet study across 948 matches found that copying profitable wallets when they pile onto the same favourite had **negative ROI**. It claims ~19% backtest ROI only when sharp-graded wallets oppose historically losing wallets. The author promotes a free tool. — [Reddit r/algobetting, 2026-07-21](https://www.reddit.com/r/algobetting/comments/1v22xy2/)

**Weather bots**
- "Found a Polymarket bot making $209/day from weather markets": 17,332 predictions over 120 days, buying YES at 2.1-45¢ and NO at 35-97¢. Third-party observation; a wallet link was given in a comment. — [Reddit r/Polymarket, 2026-08-30](https://www.reddit.com/r/Polymarket/comments/1w2mx0d/)
- A follow-up post titled "I ran the numbers on that 'bot making $209/day'… the real edge is smaller (and more interesting) than it looks" was removed. — [Reddit, 2026-08-30](https://www.reddit.com/r/Polymarket/comments/1w2sinj/)
- A Kalshi weather trader on r/algotrading doubted the viral X weather posts: "I trade weather extensively on Kalshi and this would not be a viable strategy at all." — [Reddit comment, 2026-07-05](https://www.reddit.com/r/algotrading/comments/1uo4cin/_/ovp7h30/)
- A Kalshi weather bot builder lost money because the API exposed thresholds ("below 65.5") while the UI showed range buckets. — [Reddit r/Kalshi, 2026-04-16](https://www.reddit.com/r/Kalshi/comments/1sn15bt/)
- A search summary of a Medium analysis says a viral weather wallet's ~$88K profit was anchored by a single ~$30K Paris win. It also says the closed-positions API returns only the latest 2,000 trades, so full histories cannot be checked. Secondary source. — [Medium](https://medium.com/mountain-movers/inside-the-data-behind-polymarkets-viral-88k-weather-prediction-trading-strategy-and-results-2e65a8389f37)

**LLM / AI forecasting bots**
- The "Oracle Markets" experiment (u/No_Syrup_4068) paper-trades several LLM agents with €10,000 each. They enter when the model probability differs from the Polymarket price by ≥15 points and exit the next day. Claimed returns: +8.6% for the leader after ~1,000 trades in May, then MiniMax-M3 +14.9% and Nemotron-3-nano +13.3% in July.
  - The author concedes there are "no fees, spreads, slippage or taxes".
  - A large share of the gains came from one shared trade: Ukraine ceasefire bought at 28¢, resolved at 100¢, worth ~€620-674 per agent. — [Reddit 2026-03-13](https://www.reddit.com/r/algotrading/comments/1rsj22d/); [2026-04-02](https://www.reddit.com/r/algotrading/comments/1sactqj/); [2026-05-06](https://www.reddit.com/r/algotrading/comments/1t5g16p/); [2026-07-16](https://www.reddit.com/r/algotrading/comments/1uy5328/)
- Critiques from commenters:
  - Most gains came in the last 7-10 days of a 60-day window. Top trades were 1-3¢ markets (Khamenei, Oscars) where "a 1¢ bid/ask spread on a 3¢ market is 33%". — [comment](https://www.reddit.com/r/algotrading/comments/1rsj22d/_/oa8nfgy/)
  - "You're basically selecting for the most inefficient, lowest liquidity markets where paper fills are the most unrealistic." — [comment](https://www.reddit.com/r/algotrading/comments/1rsj22d/_/oag7h9p/)
  - "I did this and got murdered on unmatched trades." — [comment](https://www.reddit.com/r/algotrading/comments/1rsj22d/_/oab3byl/)
- The same researcher later reported that 391,850 news articles across 54 markets had a next-day movement correlation of **r = −0.002**: "more news ≠ more new information." — [Reddit r/algotrading, 2026-09-30](https://www.reddit.com/r/algotrading/comments/1wujh7m/)
- HN: an article claiming a "Claude AI powered trading bot turns $1 into $3.3M on Polymarket" drew the top reply "Extraordinary claims require extraordinary evidence. I don't believe it." — [HN, 2026-04-05](https://news.ycombinator.com/item?id=47650581)

**"Nothing Ever Happens" (always buy No on non-sports markets)**
- The top HN Polymarket-bot story (471 points, 276 comments) is a meme bot by Sterling Crispin. His X post said "73.4% of all Polymarkets resolve as No". The bot has a 0.65 price ceiling.
  - The author on HN: "The bot has zero risk management… it is essentially a meme." A commenter quoted his X post as admitting no returns.
  - Commenters noted the 73% base rate is irrelevant unless No is priced below it. They also noted that Polymarket charges taker fees outside geopolitics. — [HN, 2026-04-13](https://news.ycombinator.com/item?id=47753472); [author comment](https://news.ycombinator.com/item?id=47755232)
- A commenter backtested this kind of strategy at "like 100% APR", then "realized it was cheating by knowing when things are going to resolve", and found that "1 loss sets you back 10-20 wins". — [HN, 2026-04-13](https://news.ycombinator.com/item?id=47754918)
- On backtesting: "data situation is bad, at least for market making - you need to scrape the orderbook yourself… it's hard to know whether other bids at the same price are ahead of you or behind you in the queue." — [HN, 2026-04-13](https://news.ycombinator.com/item?id=47754764)

**Sports (human plus tooling) — verifiable wallet**
- u/Gurubusters, a retired sports trader who says he now debunks fake gurus on YouTube, claims **~$58k on the 2026 World Cup** and gives his wallet `0x128b4b9c…febee9`.
  - Method: an old in-play model plus discretion, and hotkey API execution vibe-coded with Codex onto a VB.net app.
  - Maker-only orders avoided ~$3,400 in fees and earned ~$850 in maker rebates.
  - "Impatience tax": he parked idle capital on 99.9¢ bids while traders exited before UMA resolution.
  - He admits "<100" matches, "I got lucky", ~$57k on-platform from a $250k bankroll, and $1k-$25k Kelly-sized stakes. — [Reddit r/algobetting, 2026-07-29](https://www.reddit.com/r/algobetting/comments/1v9t7od/); [video](https://www.youtube.com/watch?v=px91PvLv81c)

### Inferences
- The few accounts with wallet transparency agree on a pattern. Real profits were in the low thousands of dollars, came from a structural edge (fresher external odds, maker rebates, liquidity rewards, a new product with naive flow), and lasted weeks to a few months before competition, fees or platform changes eroded them.
- "Locked" arbitrage in thin books is mostly a passive-fill race. The unhedged residual is where money is lost, and it is driven by adverse selection on stale quotes.
- Copy trading of top wallets shows no persistence out-of-sample in the one public walk-forward test, at least in sports.

### Gaps
- Full blog post-mortems (kacho.io adverse-selection post; uruguabot.com "We lost $270 building a Polymarket trading bot", [HN 2026-08-13](https://news.ycombinator.com/item?id=49285009)) could not be fetched because of DNS failure, so their details are missing.
- Many r/Polymarket and r/algotrading bot posts from 2026 were removed, so only titles survive. Examples: "Polymarket bot Failed" ([2026-09-21](https://www.reddit.com/r/Polymarket/comments/1wmqpoj/)); "Found a Polymarket bot making $120/day from liquidity rewards" ([2026-09-07](https://www.reddit.com/r/Polymarket/comments/1wa0uh4/)); "I built a Polymarket LP farming bot. The hardest part wasn't execution — it was finding markets worth farming" ([2026-08-31](https://www.reddit.com/r/Polymarket/comments/1w3g2p6/)).
- No public, wallet-backed, multi-month record of a profitable 15-minute crypto taker bot by its own operator was found on these forums.

---

## 2. What fraction report profit vs loss, and what are the typical complaints?

### Takeaway
No forum gives a real census. Qualitatively, most detailed builder posts report losses, break-even, or profits that decayed. Self-declared winners are either small-sample, not yet live, selling something, or (rarely) wallet-backed and modest. Recurring complaints, roughly in order of frequency:
1. Adverse selection and stale quotes.
2. The 2026 taker fees.
3. Thin books and execution (unmatched legs, slippage).
4. Faster competitors and latency.
5. Platform changes (CLOB v2, fee changes), "ghost fills", and resolution or settlement problems.

### Cited Findings
- **No consensus base rate; mostly negative builders.** The r/Kalshi OP who tried 15-minute crypto, weather and sports bots says "everything I try never seems to be consistently profitable… always still seems like a 50/50 chance." That thread has one big-profit claimant against many sceptics. — [Reddit r/Kalshi, 2026-09-29](https://www.reddit.com/r/Kalshi/comments/1wt0s5v/)
- **Paper lab of 90 strategies (vendor).** About 90 strategies over ten days, 4,200 settled bets, against Kalshi's live book with real fees:
  - Buying 89-95¢ "sure things" in thin entertainment markets: −36¢/contract.
  - Favourites in the final hour: priced at 87%, won 80% over 139 bets.
  - 15-minute crypto momentum: −3.35¢/contract over 781 bets.
  - Coin-flip control: −0.4¢ (fees only).
  - "Nothing won once the sample got big. Everything looked great at 16 bets."
  - The author sells this tool. — [Reddit r/Kalshi, 2026-10-01](https://www.reddit.com/r/Kalshi/comments/1wuy85l/)
- **Adverse selection** is the most cited mechanism. One commenter explains: "your resting quote is a free option you wrote to the market… when real info arrives… the informed side lifts your stale quote before you can pull it." — [Reddit comment, 2026-07-22](https://www.reddit.com/r/algotrading/comments/1v2oyv1/_/oz18gw1/). See also the 65%-filled/55%-win vs 80%-win-unfilled example in [r/algotrading 2026-09-11](https://www.reddit.com/r/algotrading/comments/1wdkmjj/), and the HN story "Adverse selection eating away my Polymarket bot's arbitrage profits" ([HN, 2026-06-30](https://news.ycombinator.com/item?id=48734200)).
- **Fees (2026).**
  - "Crypto fees now 7%!? … made crypto 7% at the outlines and 3.5% at 50¢. Arbitrage is dead." — [Reddit r/Polymarket, 2026-05-18](https://www.reddit.com/r/Polymarket/comments/1tgrx6l/)
  - Replies: "Bots who used to play for small spreads are dead". "my bot was still running the old fee structure and losing money and I didn't understand why." Another commenter called it "a decrease from the 7.2% that it was before clobv2". — [comments](https://www.reddit.com/r/Polymarket/comments/1tgrx6l/)
  - Note that the "7%" figure conflicts with other posts, which quote peak fees of ~1.8% of position at 50¢ for crypto. The disagreement probably comes from expressing the fee as a percentage of cost rather than of notional. See `market_making_rewards.md` and `latency_strategies.md` for the authoritative fee formula.
  - A $0.79 fee shown on a $1 order on a low-priced Wellington temperature market. — [Reddit, 2026-03-31](https://www.reddit.com/r/Polymarket/comments/1s8jtkl/)
  - "Did polymarket just double taker fees overnight?" — [Reddit, 2026-04-01](https://www.reddit.com/r/Polymarket/comments/1s95s2j/)
  - "gross edge was ~2.5%, but after the taker fee and the typical bid-ask spread, I'm net negative." — [Reddit, 2026-08-28](https://www.reddit.com/r/Polymarket/comments/1w0cnmo/)
  - A user-compiled breakdown claims ~$43M of lifetime fees, mostly from a small fraction of heavy traders. Unverified. — [Reddit, 2026-05-21](https://www.reddit.com/r/Polymarket/comments/1tjqjcp/)
  - A YouTube video titled "Understanding Polymarket's New Fees: Why HFT Bots Are Dying — and How to Earn the Rebates" (content not reviewed). — [YouTube](https://www.youtube.com/watch?v=7HXoCMMXr-8)
- **Thin books.** "when you try to put more than a few dollars down, the 20 cent bet you thought you were getting averages out to be 80 cents… These books are too thin to be worth using at any scale." — [Reddit comment, 2026-05-02](https://www.reddit.com/r/algotrading/comments/1t1tg30/_/ojk7dd3/)
- **Unpaired legs in "both sides" arbitrage.** "one side fills instantly but the other side has like 5k liquidity vs 30k on the first. You basically need a naked position tracker… Otherwise you end up accumulating directional risk thinking youre arbing." — [HN, 2026-03-23](https://news.ycombinator.com/item?id=47416315)
- **Ghost fills / incrementNonce exploit.** On BTC 5-minute markets, bad actors reportedly call `incrementNonce()` on the CTF Exchange to invalidate losing orders after the CLOB matches them, so the bot thinks it filled. A free detector was released.
  - Comments: "So this is how all the 'look at all this money this bot made in 5 days' bots work". "WebSocket on PolyMarket has gone haywire, we are getting ghost orders." — [Reddit r/algotrading, 2026-02-22](https://www.reddit.com/r/algotrading/comments/1rb6qay/)
- **Settlement / resolution issues.**
  - A user complained a resolution "bot completely skipped" an O/U 10.5 corners market while 9.5 and 11.5 resolved. — [Reddit r/Polymarket, 2026-09-09](https://www.reddit.com/r/Polymarket/comments/1wbexc3/)
  - An HN commenter wants Polymarket to "address the UMA oracle gang". — [HN, 2026-09-20](https://news.ycombinator.com/item?id=49773181)
  - In the cross-venue arb critique, the UMA dispute risk is "the big one" for locked arbitrage. — [Reddit comment](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcwomti/)
  - On Kalshi: "My bot traded the wrong contract for a week… KXCS2GAME is the whole match, not the game" (title only). — [Reddit r/Kalshi, 2026-08-22](https://www.reddit.com/r/Kalshi/comments/1vvj0q4/). Kalshi also moved crypto to a different matching engine, which produced "market not found" errors for bots. — [Reddit r/Kalshi, 2026-08-25](https://www.reddit.com/r/Kalshi/comments/1vy26z9/)
- **Withdrawal and legality anxiety.** "did anyone manage to get money out of Polymarket?" — [Reddit comment, 2026-08-18](https://www.reddit.com/r/Polymarket/comments/1vqtxrh/). A builder stopped before going live because the platforms "became illegal to use in my country". — [Reddit comment](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcsqwca/)
- **Optimistic counter-voice.** "I was pleasantly surprised to discover how many $100 notes being left on the ground." — [Reddit comment, 2026-09-30](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcwowuo/)
- **"Win rate" misread.** Several posts headline 92-99% win rates ([r/Polymarket 2026-07-17](https://www.reddit.com/r/Polymarket/comments/1uyl7w6/); [2026-08-17](https://www.reddit.com/r/Polymarket/comments/1vqtxrh/)). Commenters respond that win rate on high-priced favourites is meaningless and that profit per contract after fees and the worst single day matter more. Kalshi's breakeven example: 92.6% needed at 90-95¢ prices. — [r/Kalshi 2026-10-10](https://www.reddit.com/r/Kalshi/comments/1x2nrrp/); [r/Kalshi 2026-10-15](https://www.reddit.com/r/Kalshi/comments/1x6cc40/)

### Inferences
- A rough reading of the threads collected: among builders who post detailed numbers, clear sustained profit is the minority, probably below a quarter. Most report losses, flat results after costs, or a profit that later reversed. This is an impression from about 40 threads, not a measurement, and it is biased in both directions: winners hide, and vendors overstate.
- Fees mostly kill taker strategies on mid-priced short-term crypto and high-probability "sure thing" sniping. Maker-only operation (rebates, rewards) is the common adaptation, and it is precisely the position most exposed to adverse selection.

### Gaps
- No forum survey or poll of bot profitability was found.
- Polymarket's official response to the incrementNonce "ghost fill" issue was not found in forum threads.

---

## 3. Paper trading vs live: what gaps do practitioners report?

### Takeaway
Practitioners consistently report that edges seen in backtests or paper runs shrink or disappear under realistic execution. The causes they cite: queue position, partial or one-sided fills, slippage of about 1¢, stale quotes, fees, and survivorship in wallet selection. The common advice is to log the order book at decision time, compare fill price with signal price, and validate unfilled orders.

### Cited Findings
- The "edge dies with ~0.01 additional slippage". The baseline "progressively died as execution realism increased". p95 quote staleness was ~67 s. — [Reddit r/algotrading, 2026-05-28](https://www.reddit.com/r/algotrading/comments/1tpu2nz/)
- "The 80% on the unfilled ones is the tell… The fills are selected against you. Worth checking: for those 35%, what would you have had to pay to actually get in?" — [Reddit comment, 2026-09-11](https://www.reddit.com/r/algotrading/comments/1wdkmjj/_/p96m6mo/)
- "when you go live… log actual fill prices vs the price at signal time. that spread between signal price and fill price is your real execution cost." Also: "a €250 position… moves the price against you just by entering, which doesn't show up in paper fills at all." — [Reddit comment, 2026-03-13](https://www.reddit.com/r/algotrading/comments/1rsj22d/_/oab1krf/)
- The LLM paper author planned to assume "at least 2% Slippage per Trade, 1% Fees per Trade, and 0.3% taxes per winning trade" before going live. — [Reddit comment](https://www.reddit.com/r/algotrading/comments/1rsj22d/_/oa7817j/)
- Copy-trading backtest: "it looked great in-sample every single time". Wallet-level labels leak the future. — [Reddit r/algotrading, 2026-10-11](https://www.reddit.com/r/algotrading/comments/1x38s11/)
- Kalshi paper lab: "Everything looked great at 16 bets"; nothing won at large sample. — [Reddit r/Kalshi, 2026-10-01](https://www.reddit.com/r/Kalshi/comments/1wuy85l/)
- Backtest look-ahead: the "Nothing Ever Happens"-style backtest showed ~100% APR because it knew resolution times. — [HN, 2026-04-13](https://news.ycombinator.com/item?id=47754918)
- The arb critique says historical "gaps" were mostly stale last-trade prints, because Polymarket's price history is trades, not the order book: "A 38c 'gap' was one odd print in a market that traded four times in its whole life." — [Reddit comment, 2026-09-29](https://www.reddit.com/r/algotrading/comments/1wt6hzg/_/pcuttlk/)
- Platform changes break backtests: "you can only sample the version of the market that exists." — [Reddit comment, 2026-05-04](https://www.reddit.com/r/algotrading/comments/1t1tg30/_/ojsqw4p/)
- Free order-book datasets released by practitioners for realistic backtests:
  - PMXT order books. — [Reddit r/algotrading, 2026-02-24, 556 pts](https://www.reddit.com/r/algotrading/comments/1rdhw2n/)
  - Second-by-second top-of-book for ~89k 5-minute crypto markets, March to May 2026, CC0. — [Reddit, 2026-06-17](https://www.reddit.com/r/algotrading/comments/1u8fsg7/)

### Inferences
- For an honest simulator, the forum consensus implies three modelling choices:
  1. Resting orders fill only when the price trades through them, with queue uncertainty. Assuming a fill whenever price touches the level overstates results.
  2. Unfilled signals must be tracked, because they are the winners you missed.
  3. Results must be stress-tested at +1¢ and +3¢ of slippage and against the current fee schedule.

### Gaps
- No practitioner published a side-by-side paper-vs-live P&L for the same Polymarket bot over the same period. The Oracle Markets LLM project said it would go live with small real money but no live results were found.

---

## 4. What do X/Twitter, YouTube and hype channels say, and how credible are they?

### Takeaway
X and short-video platforms are dominated by promotional "this bot turned $X into $Y" content, course and bot sellers, and, per the WSJ, paid creators staging fake wins. Forum users treat this content as mostly grift. Credible X content found was limited to builders who openly disclaim returns (e.g. Sterling Crispin's meme bot) and interviews with known builders (defiance_cr).

### Cited Findings
- r/algotrading thread "Polymarket bot posts?": "hundreds of likely fake posts about Polymarket algos and accounts to copy trade".
  - Top replies: "Much more likely to be someone trying to scam people for courses/bots" (106 points).
  - "'I found an edge so big I'm ghosting the internet… you have 3 days to buy my course…' he says via the internet."
  - "Those who can't, sell shitty courses and broken bots that quote random things at random prices."
  - Another commenter singled out "that moon dev guy". — [Reddit, 2026-07-05](https://www.reddit.com/r/algotrading/comments/1uo4cin/)
- WSJ investigation (around 2026-06-20, via secondary coverage): Polymarket paid mostly college-age creators about $2,000-3,000/month to film staged trades and wins on dummy copies of its site. The WSJ reviewed 1,105 videos from 10 creators. Figures for fake winnings differ between outlets ($900K vs $1.9M). — [The Block](https://www.theblock.co/post/405471/polymarket-paid-creators-to-stage-fake-winning-bets-on-dummy-sites-wsj); [TechSpot](https://www.techspot.com/news/112856-polymarket-paid-influencers-fake-winning-bets-built-dummy.html). A Reddit commenter linked the WSJ story as evidence that "Polymarket also pays people to make posts like this". — [Reddit comment](https://www.reddit.com/r/algotrading/comments/1uo4cin/_/ovpss61/)
- On r/Polymarket, the "99.3% win rate, $1.4K → $965,388" bot post drew: "I'm starting to think these are posts by polymarket themselves. Just absolute slop making it look easy to make money trying to drive volume". Another reply: "Win rate on 32,614 trades is doing less work than it looks like… a few hundred reads of the same feed, each one fired dozens of times." — [Reddit, 2026-08-17](https://www.reddit.com/r/Polymarket/comments/1vqtxrh/)
- Similar hype titles: "🚨INSANE: Polymarket bot makes $386,000 in ONE YEAR" ([2026-05-07](https://www.reddit.com/r/Polymarket/comments/1t6cyxh/)); "'I will build an AI weather trading bot and earn $5000 a week on polymarket'" (mocking, [2026-07-10](https://www.reddit.com/r/Polymarket/comments/1usry3e/)). A commenter on the arb post linked a Finbold article claiming a bot turned "$313 into $438,000 in a month". — [Reddit comment](https://www.reddit.com/r/algotrading/comments/1qebxud/_/nzzd6e2/)
- r/algobetting post title: "Stop reading articles about 'how Polymarket bots work.' If those authors knew, they'd be running bots, not writing Medium posts." — [Reddit, 2026-02-26](https://www.reddit.com/r/algobetting/comments/1rex02n/)
- HN: "There are folks on X running vibe-coded Polymarket arbitrage bots playing with hundreds of thousands of dollars. Some people have pretty wild risk tolerances!" — [HN, 2026-01-07](https://news.ycombinator.com/item?id=46528358)
- Gatekeeping reaction to open-sourcing: "When you have an edge… keep it to yourself", and "I have a strong suspicion you're not in the quant industry". — [Reddit comments, 2026-01-16](https://www.reddit.com/r/algotrading/comments/1qebxud/)

### Inferences
- Viral X and short-video P&L claims about Polymarket bots should be treated as marketing until there is a wallet link and a reconciled P&L. Even then, a wallet showing profit does not establish which strategy produced it.

### Gaps
- X threads by known builders (defiance_cr, 15-minute crypto bot accounts, "gabagool"-style operators, weather whales) could not be read directly because the X mirrors were blocked. Their content here is second-hand.
- YouTube content was not reviewed beyond titles and links given in forum posts.

---

## 5. Scams: bot sellers, Telegram bots, fake copy trading — warning signs

### Takeaway
Forum and security-research reports describe four kinds of risk. GitHub "Polymarket bot" repos have been weaponised to steal private keys (malicious npm dependencies in a hijacked verified organisation). A custodial Telegram trading bot (Polycule) was drained of ~$230k in January 2026. Phishing has cost users millions. And "working bot for sale" posts, paid courses and lookalike bots circulate on Reddit and X.

### Cited Findings
- StepSecurity found that "dev-protocol — a verified GitHub organization with 568 followers belonging to a legitimate Japanese DeFi project — has been hijacked and is now being used to distribute malicious Polymarket trading bots." — [HN, 2026-03-15](https://news.ycombinator.com/item?id=47392215). A search summary says it held 20+ bot variants with inflated stars and hidden npm packages that lift the wallet private key on `npm install`.
- SlowMist reportedly found a Polymarket copy-trading bot on GitHub that read private keys from `.env` and exfiltrated them. — [KuCoin News](https://www.kucoin.com/news/flash/polymarket-copy-trading-bot-project-found-to-contain-malicious-code-stealing-private-keys)
- Polycule (a Polymarket Telegram bot) was hacked for ~$230,000 in user funds in January 2026. Sources disagree on the confirmation date (7 vs 13 January). Users reportedly could not withdraw afterwards, and rivals called it a rug. Commentators blame server-side key custody. — [Phemex](https://phemex.com/news/article/polycule-tg-bot-hacked-230000-in-user-funds-compromised-52040); [Odaily](https://www.odaily.news/en/post/5208756); [Cryptopolitan](https://www.cryptopolitan.com/polycule-polymarket-bot-goes-offline/)
- Phishing: ~$2.94M lost by Polymarket users in a suspected phishing campaign (fake sites, compromised credentials), not via Polymarket's contracts. — [Cryptopolitan](https://www.cryptopolitan.com/polymarket-users-suspected-phishing-attack/)
- On Reddit:
  - "Anyone interested in purchasing a working bot" with an 18-19 day test screenshot ("don't have the funds" to run it). — [r/Polymarket, 2026-08-22](https://www.reddit.com/r/Polymarket/comments/1vv3sn0/)
  - "PolyApex Telegram Bot That Copies Polymarket Insiders Wallets" (promotion). — [r/Kalshi, 2026-08-15](https://www.reddit.com/r/Kalshi/comments/1vox9do/)
  - "Warning! Bot Scams!" (removed). — [r/Kalshi, 2026-08-09](https://www.reddit.com/r/Kalshi/comments/1vk1r1z/)
  - Repeated "[Hiring] Polymarket bot UX feedback" posts. — [r/Polymarket, 2026-07-11](https://www.reddit.com/r/Polymarket/comments/1uthrxc/)
  - Dozens of near-identical "I built a Polymarket bot that alerts you to price swings" spam posts on a single day (2026-04-18) in r/algobetting, most removed. — [example](https://www.reddit.com/r/algobetting/comments/1sowkky/)
  - A Gumroad listing sells a $99 "Polymarket Copy Trading Smart Bot". — [Gumroad](https://mustafaramx.gumroad.com/l/PolymarketCopyTradingSmartBot)
- A retired sports trader says he busts gurus who use fake "Inspect Element" P&L spreadsheets: "Don't trust screenshots." — [Reddit r/algobetting, 2026-07-29](https://www.reddit.com/r/algobetting/comments/1v9t7od/)
- Ghost-fill manipulation (see §2) was cited by commenters as one way "bot made $X in 5 days" screenshots could be produced. — [Reddit, 2026-02-22](https://www.reddit.com/r/algotrading/comments/1rb6qay/)
- Combo market maker: suspected spoofed asks and bursts of automated RFQs from one requestor cluster were used to pick off his pricing. — [Reddit r/algobetting, 2026-10-10](https://www.reddit.com/r/algobetting/comments/1x2q5ob/)

Warning signs compiled from these sources:
1. The product asks for a private key or seed phrase, or keeps keys server-side (custodial Telegram bots).
2. The repo needs `npm install` / `pip install` of obscure dependencies plus a `.env` with `PRIVATE_KEY`.
3. Inflated stars or forks on a newly repurposed organisation.
4. Win-rate-only marketing (90-99%) with no fees or worst-day figures.
5. Screenshots instead of wallet links.
6. "Edge so big… buy my course" urgency.
7. Bots offered for sale by people who "don't have the funds" to run them.
8. Subscription bots ($20-99) sold by their own backtesters.
9. Undisclosed paid promotion, per the WSJ report on Polymarket's own creator campaign.

### Inferences
- For this lab, which by rule never handles keys or real orders, the relevant lesson is defensive. Downloaded "Polymarket bot" code is a malware vector and should never be executed. Social P&L claims are not evidence.

### Gaps
- No first-hand Reddit victim account of a Telegram copy-trading key theft was retrievable. The r/Kalshi "Warning! Bot Scams!" post was removed.
- Whether Polycule users were compensated was not established.
