import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry point: the catalogue photo is rendered by compose.py and shipped
// as entry.png next to this file. This program only places that image into
// the grader's output directory, so every grading run emits byte-identical
// output. It refuses to run if the rendered image is missing, rather than
// silently producing an empty entry.
const repoRoot = dirname(fileURLToPath(import.meta.url));
const sourceImage = join(repoRoot, "entry.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(repoRoot, "out");

if (!existsSync(sourceImage)) {
  throw new Error(
    `entry.png not found in ${repoRoot} -- run "python3 compose.py" first`,
  );
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourceImage, join(outputDir, "entry.png"));
