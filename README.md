# Sunday 22 November 2026 — One Day of World News, One Picture

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/erlansyahm90-code/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/erlansyahm90-code/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Entry for the make.fun bounty **Sum up 22 November's world news in one image**:
https://make.fun/bounty/news-image-20261122

## The poster

A midnight-blue broadsheet for **Sunday 22 November 2026** — 48 stories,
10 regions and beats, every one of them verified from 2+ independent
sources as having happened or first been reported on that day:

- **Lead: COP31 COLLAPSES — NO DEAL.** The longest climate summit in
  history ends with no agreement — the first COP to fail since Copenhagen
  2009. President Kurum: "there is no agreement on this text." The final
  text never mentions fossil fuels; the EU, UK, Panama, Marshall Islands
  and Norway refuse to back it. The lead block also carries two more
  climate/environment stories: the RAPP permit revocation in Riau
  (338,536 ha) and the winter storm flooding Gaza's shelters.
- **Politics & diplomacy (8 stories, illustrated):** Eisenkot tapped to
  form Israel's government, passing over Netanyahu; four nations demanding
  Gaza aid access; US envoys Kushner and Witkoff heading to Moscow, then
  Dublin; FBI Top 10 fugitive "El Chapo Isidro" captured in Sinaloa with
  11 killed; Australia slamming the US budget office over AUKUS; Iran
  shortening its Hormuz reopening plan to two days; Ukraine's energy
  crisis deepening before winter; Japan weighing cuts to missile and
  warship buys.
- **Indonesia & economy (8 stories, illustrated):** the Cikande factory
  fire (36 missing, 3 dead — Reuters figures); Prabowo to name two VP
  candidates on 25 November; Mahfud on the MPR session to replace Gibran;
  Bitcoin climbing back above $60,000 after plunging to $55,300; Jakarta's
  2027 minimum wage hitting Rp6.13m; coal, CPO and ferroalloy exports to
  run via DSI from 2027; 242,482 part-time teachers going full-time;
  Bekasi's 2027 wage Rp6.48m, the highest in Indonesia.
- **Sport (5 stories):** Verstappen winning the Las Vegas GP from pole
  (Norris +0.639, Piastri +1.529); Liverpool 4–0 Manchester United in
  Pochettino's first game; Hull 2–0 Brighton on a McBurnie injury-time
  brace; KC Current winning their first NWSL title 2–1; Spurs cruising
  114–91 past the Pelicans.
- **24 more stories** in the numbered "Also on Sunday" list — German
  transport fares and health insurance, Zelensky on US intel warnings,
  Italy's flat-tax cap, Bosch–Microsoft AI, Volkswagen's pay freeze,
  Lufthansa's 1,000 job cuts, BMKG rain, OJK sanctions, the new rail
  timetable, BepiColombo's first X-ray views, China's 52 rocket bodies
  in low orbit, GTA 6's 5.6 user score, and the BBC's Sunday features.
- **A DATE CHECK footer** listing the previous day's big stories that
  were deliberately left out (Wall Street's crash, Anthropic's IPO, the
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
