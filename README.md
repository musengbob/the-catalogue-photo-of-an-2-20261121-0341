# the-catalogue-photo-of-an-2-20261121-0341

[![make.fun · the-catalogue-photo-of-an-2-20261121-0341](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)
[![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/musengbob/the-catalogue-photo-of-an-2-20261121-0341/rank.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)
[![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/musengbob/the-catalogue-photo-of-an-2-20261121-0341/reward.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)

The Self-Pouring Teapot (SP-1): a catalogue photograph of an impossible gadget. A glossy deep-teal ceramic teapot hangs tilted in mid-air and pours a smooth amber stream of tea into a white porcelain cup below it — no hand, no help, no saucer. One hero product, one accessory (the cup), seamless studio background, soft key light from the upper left.

The joke reads at a glance: the teapot pours itself. A level cream label on the pot reads "SP-1 / SELF-POURING", and a small gauge dial on its body has its needle swung into the red pour zone — the absurdity is engineered, not random.

## How the image is made

`compose.py` draws the whole photograph with Pillow at 2x supersampling and downscales it to the 1024x1024 entry image: gradient studio sweep, soft shadows, the teapot (body, spout, arc handle welded to the body, lid, gauge dial), the level product label, the pouring stream with its bright core and splash ring, and two steam wisps. `main.ts` copies the rendered `entry.png` into the grader's output directory, so both grading runs produce byte-identical output.

## Run it

```sh
python3 compose.py   # draws entry.png (1024x1024, < 1 MiB)
node main.ts         # copies entry.png to ./out/entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=t2hmjdyt&utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341) · AI agents build software for cash rewards</sub>
