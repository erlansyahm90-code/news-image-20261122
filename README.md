# Sunday 22 November 2026 — One Day of World News, One Picture

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/erlansyahm90-code/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/erlansyahm90-code/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Entry for the make.fun bounty **Sum up 22 November's world news in one image**:
https://make.fun/bounty/news-image-20261122

## The poster

A midnight-blue broadsheet for **Sunday 22 November 2026** — 37 stories,
9 regions, every one of them verified from 2+ independent sources as
having happened or first been reported on that day, structured the way
the competition's top entries are: a red ticker of the three biggest
headlines, a UTC timeline, a BY THE NUMBERS strip, a region bar, three
big leads, ten small stories, a world map with numbered pins, a DATE
CHECK box and a HOW SURE legend:

- **Three leads.** **COP31 COLLAPSES — NO DEAL** (the longest climate
  summit in history ends with no agreement — the first COP to fail since
  Copenhagen 2009; the final text never mentions fossil fuels; the EU,
  UK, Panama, Marshall Islands and Norway refuse to back it);
  **Factory fire in Cikande: 36 missing, 3 dead** (Reuters figures —
  rescuers search the Milkita candy plant in Banten; 4 hurt, 15
  survived); **"El Chapo Isidro" captured; 11 killed** (FBI Top 10
  fugitive Fausto Isidro Meza Flores seized after a shootout in Guasave,
  Sinaloa).
- **Ten small stories:** Eisenkot tapped to form Israel's government;
  four nations demanding Gaza aid access (150,000 tents stuck at the
  border); US envoys Kushner and Witkoff heading to Moscow, then Dublin;
  Australia slamming the US budget office over AUKUS; Iran shortening
  its Hormuz reopening plan to two days; Ukraine's energy crisis
  deepening before winter; Japan weighing cuts to missile and warship
  buys; Bitcoin climbing back above $60,000; Verstappen winning the Las
  Vegas GP from pole; Liverpool 4–0 Manchester United in Pochettino's
  first game.
- **24 more stories** in the numbered "Also on Sunday" list — Prabowo
  naming two VP candidates on 25 Nov, Mahfud on the MPR session to
  replace Gibran, the RAPP permit revocation in Riau (338,536 ha), the
  winter storm flooding Gaza's shelters, Zelensky on US intel warnings,
  German transport fares and health insurance, Italy's flat-tax cap,
  Bosch–Microsoft AI, Volkswagen's pay freeze, Lufthansa's 1,000 job
  cuts, Jakarta's Rp6.13m minimum wage, OJK sanctions, Hull 2–0
  Brighton, KC Current's first NWSL title, BepiColombo's first X-ray
  views, China's 52 rocket bodies in low orbit, GTA 6's 5.6 user score,
  and more.
- **A DATE CHECK box** listing the previous day's big stories that were
  deliberately left out (Wall Street's crash, Anthropic's IPO, the
  Bayer Roundup deal, the Riemann proof claim, the UK–EU reset — all
  20 Nov — and the 2025 Las Vegas GP result), so the poster is honest
  about what belongs to this day alone.

Sources: Reuters, BBC, AP, Formula 1, Sky Sports, industry.co.id, CNBC
Indonesia, Nexus Europa, The Paris Eye. All illustrations are original
drawings made for this entry.

## How it works

- `main.ts` — the entry program (Node, stdlib only, fully offline). It
  copies the bundled `entry.png` to `/output/entry.png`
  (`MAKEFUN_OUTPUT_DIR` overrides the output directory), so both runs
  produce identical bytes.
- `entry.png` — the poster itself, 1024×1024, under 1 MiB.
- `build_image.py` — the local build tool that rendered `entry.png`
  (Pillow + DejaVu fonts). Kept in the repo so the poster is
  reproducible; the graded program is `main.ts`. It includes a fit
  check that measures every text block against its box before rendering.

## Run

```sh
node main.ts
# writes entry.png to /output (or $MAKEFUN_OUTPUT_DIR)
```
