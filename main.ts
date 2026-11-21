// The Self-Pouring Teapot (SP-1) — entrypoint.
// Copies the pre-rendered catalogue photograph (entry.png, produced by
// compose.py in this same directory) into the output directory so the
// grader finds /output/entry.png. No dependencies, Node 22.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const entryDir = new URL(".", import.meta.url).pathname;
const source = join(entryDir, "entry.png");

const rawOut = process.env.MAKEFUN_OUTPUT_DIR;
const outDir = rawOut && rawOut.trim().length > 0 ? rawOut.trim() : "/output";

if (!existsSync(source)) {
  throw new Error(
    `entry.png is missing next to main.ts (looked in ${entryDir}). ` +
      "Run `python3 compose.py` first to render the catalogue photograph.",
  );
}

// Validate the file before copying: it must be a real PNG, 1024x1024,
// and within the 1 MiB gate, or the entry would fail the gate silently.
const bytes = readFileSync(source);
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error(`entry.png is not a valid PNG (bad signature, ${bytes.length} bytes).`);
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024x1024, got ${width}x${height}.`);
}
if (statSync(source).size > 1048576) {
  throw new Error(`entry.png is over the 1 MiB gate (${statSync(source).size} bytes).`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, join(outDir, "entry.png"));
console.log(`entry.png (${width}x${height}, ${bytes.length} bytes) -> ${join(outDir, "entry.png")}`);
