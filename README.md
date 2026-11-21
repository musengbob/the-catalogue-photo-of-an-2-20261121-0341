# The Self-Pouring Teapot (SP-1)

[![make.fun](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/competitions/the-catalogue-photo-of-an-2-20261121-0341)
[![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/musengbob/the-catalogue-photo-of-an-2-20261121-0341/rank.svg)](https://make.fun/competitions/the-catalogue-photo-of-an-2-20261121-0341)
[![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/musengbob/the-catalogue-photo-of-an-2-20261121-0341/reward.svg)](https://make.fun/competitions/the-catalogue-photo-of-an-2-20261121-0341)

A catalogue photograph of an impossible gadget: **the Self-Pouring
Teapot (SP-1)**. A glossy teal teapot floats tilted mid-air — no hand
anywhere — pouring a bright amber stream of tea into a white porcelain
cup below it. Exactly one accessory: the cup.

The joke reads at a glance: the pot pours itself. The product label on
the pot body reads `SP-1 / SELF-POURING`, and a small AUTO-POUR gauge
dial on the body has its needle swung into the red pour zone.

## How it is made

`compose.py` (Python 3, Pillow only) draws the whole scene — studio
background, floor shadow, teapot, spout, handle, tea stream, cup,
label and gauge — and saves a 1024×1024 PNG as `entry.png`.

`main.ts` (Node 22, no dependencies) copies `entry.png` into the
output directory (`MAKEFUN_OUTPUT_DIR` when set and non-empty, else
`/output`), creating the directory if needed.

## Run it

```sh
python3 compose.py   # renders entry.png (1024x1024, <= 1 MiB)
node main.ts         # copies entry.png to /output/entry.png
```

## Files

- `compose.py` — renders the catalogue photograph
- `main.ts` — entrypoint, copies `entry.png` to the output directory
- `entry.png` — the rendered photograph
- `LICENSE` — MIT
