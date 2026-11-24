// news-image-20261123 entry point (Node 22, standard library only).
//
// The poster is built offline and shipped in this repository as entry.png.
// This program only places a copy at the output path the grader reads.
// It takes no input, makes no network calls, and always writes the same bytes.
//
// Run it outside the grader with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
// The grader runs this program twice and compares the bytes, so the copy
// must be exact: read the shipped poster and write it unchanged.
const ENTRY_FILE = 'entry.png';
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, ENTRY_FILE), readFileSync(join(here, ENTRY_FILE)));
