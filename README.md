# Sunday 22 November 2026 — One Day of World News, One Picture

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/erlansyahm90-code/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/erlansyahm90-code/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Entry for the make.fun bounty **Sum up 22 November's world news in one image**:
https://make.fun/bounty/news-image-20261122

## The poster

A cream newspaper broadsheet for **Sunday 22 November 2026** — 36 stories,
7 regions, every one of them verified from wire sources as having happened
or first been reported on that day, structured the way the competition's
top entries are: a red ticker of the three biggest headlines, a UTC
timeline, a BY THE NUMBERS strip, a region bar, three big leads with scene
illustrations, the Sparta II tow, ten small stories, a numbered "also" list,
a DATE CHECK box and a HOW SURE legend:

- **Three leads.** **186 drones in one night — a Kyiv block falls** (Russia
  launches 186 drones, 72 of them jet-powered Shaheds; 161 downed; a
  five-storey block in Dymer is torn open at 05:00, 5 dead, 14
  unaccounted for); **COP31 ends with no deal — a first since 2000** (the
  final text is tabled at dawn and rejected in the closing plenary; the
  longest COP on record, 44+ hours overtime); **Iran claims two US Patriot
  radars hit in Bahrain** (the IRGC claim, with Bahrain's and the US's
  denials alongside it — labelled CLAIM).
- **The Sparta II tow.** Hit by two drones on Saturday, the sanctioned
  Russian cargo ship burns through Sunday as seven vessels fight the fire,
  then a Russian rescue ship tows it out of Finnish waters.
- **Ten small stories:** Hong Kong's record 98.79% Election Committee
  turnout; India declaring 720/9 in Wellington; Wembanyama's 50-point
  night; Iran starting electricity rationing; the Cikande factory fire
  (3 dead, 34 missing); Verstappen winning the Las Vegas GP; Alcaraz
  winning the ATP Finals; Liverpool 4–0 Manchester United; Saudi defences
  downing Houthi missiles over Riyadh; the tanker Torkel still burning at
  anchor in Hormuz.
- **22 more stories** in the numbered "Also on Sunday" list — the FBI
  NCIC hack, the Bayelsa boat toll rising to 29, Hamas seeking urgent
  mediator talks, Nepal's PM arriving in Delhi, the Manipur liquor toll,
  Pope Leo's lunch with 1,300 poor guests, Bitcoin holding above $60,000,
  and more.
- **DATE CHECK** names the day's real date traps — the stories other
  papers ran as Sunday news that actually happened on Friday, Saturday or
  earlier (Peru quake, El Chapo, the 400-drone barrage, Nvidia, Basra,
  EU–Indonesia, Ladakh, England's rugby win, Kenya's Ebola discharge…).

## Reproduce

```sh
python3 build_image.py   # writes entry.png (1024×1024, deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copies it to out/
```

`main.ts` (Node 22, standard library only) copies the bundled `entry.png`
to `/output/entry.png` byte for byte, so both grading runs produce
identical bytes.
