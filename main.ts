import { copyFile, mkdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

function fail(message: string): never {
  console.error(`main.ts failed: ${message}`);
  process.exit(1);
}

const source = join(BOT_DIR, "POST.json");
const dest = join(OUTPUT_DIR, "POST.json");

let sourceBytes: Buffer;
let outputBytes: Buffer;
try {
  await mkdir(OUTPUT_DIR, { recursive: true });
  await copyFile(source, dest);
  // Read both sides back: the copy call succeeding is not proof the
  // bytes on disk are the ones we meant to publish.
  sourceBytes = await readFile(source);
  outputBytes = await readFile(dest);
} catch (err) {
  fail(
    `could not copy or read back POST.json (${source} -> ${dest}): ` +
      (err instanceof Error ? err.message : String(err)),
  );
}

// ---- Validate the output we actually wrote ----
if (outputBytes.length !== sourceBytes.length) {
  fail(
    `POST.json byte length mismatch: output is ${outputBytes.length} ` +
      `bytes but source is ${sourceBytes.length} bytes`,
  );
}

let parsed: unknown;
try {
  parsed = JSON.parse(outputBytes.toString("utf8"));
} catch {
  fail("POST.json in the output dir is not valid JSON");
}

if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
  fail("POST.json must be a JSON object with a url field");
}

const url = (parsed as Record<string, unknown>).url;
// A bare https://x.com/ prefix is not an entry: the value must be the
// URL of one posted status, https://x.com/<handle>/status/<numeric id>.
const STATUS_URL = /^https:\/\/x\.com\/[^/]+\/status\/\d+$/;
if (typeof url !== "string" || !STATUS_URL.test(url)) {
  fail(
    `POST.json "url" must be an X status URL like ` +
      `https://x.com/<handle>/status/<id>, got: ${JSON.stringify(url)}`,
  );
}

console.log(`main.ts ok: ${dest} (${outputBytes.length} bytes) url=${url}`);
