import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
const clips = ["dune.mp4", "batman.mp4", "dragon.mp4"];
const missing = clips.filter(
  (name) => !existsSync(new URL(`../public/clips/${name}`, import.meta.url)),
);
if (missing.length) {
  console.error(
    `Faltan clips oficiales en public/clips/: ${missing.join(", ")}. El montaje final no se exportará con material sustituto.`,
  );
  process.exit(1);
}
const result = spawnSync(
  "npx",
  [
    "--no-install",
    "remotion",
    "render",
    "src/index.ts",
    "HBOFinal",
    "out/Tzubaru-HBO-Max-final.mp4",
    "--browser-executable=/usr/bin/chromium",
    "--gl=swangle",
    "--concurrency=2",
    "--crf=18",
  ],
  { stdio: "inherit" },
);
process.exit(result.status ?? 1);
