export type FamilyKey =
  | "halden"
  | "rondel"
  | "tessera"
  | "alder"
  | "mallow"
  | "strata"
  | "plaza"
  | "vesper"
  | "ledger"
  | "folio";

export interface Family {
  key: FamilyKey;
  name: string;
  kind: string;
  blurb: string;
  sample: string;
  headline: string;
  accent: string;
  accentDark: string;
}

export const FAMILIES: Family[] = [
  {
    key: "halden",
    name: "Halden",
    kind: "Neo-grotesque",
    blurb: "A neutral, tightly spaced workhorse for interfaces, dashboards and product copy.",
    sample: "Clarity is a quiet kind of confidence.",
    headline: "Software that explains itself",
    accent: "#E5482B",
    accentDark: "#FF6A4D",
  },
  {
    key: "rondel",
    name: "Rondel",
    kind: "Geometric",
    blurb: "True circles, sharp apexes and a small x-height, with tall ascenders that give it poise.",
    sample: "Round numbers, sharp ideas.",
    headline: "Measured twice, launched once",
    accent: "#2F5BEA",
    accentDark: "#6E8EFF",
  },
  {
    key: "tessera",
    name: "Tessera",
    kind: "Squared grotesque",
    blurb: "Squared curves and a big x-height that feel engineered, technical and unmistakably modern.",
    sample: "Built square, designed to move.",
    headline: "Infrastructure for teams that ship",
    accent: "#16946A",
    accentDark: "#3FCB97",
  },
  {
    key: "alder",
    name: "Alder",
    kind: "Humanist",
    blurb: "Pen-angled cuts, gentle contrast and narrow, open forms that read warmly at any size.",
    sample: "Warm letters for honest words.",
    headline: "Stories worth reading slowly",
    accent: "#B9801A",
    accentDark: "#E2AE4C",
  },
  {
    key: "mallow",
    name: "Mallow",
    kind: "Rounded",
    blurb: "Round ends, a single-story a and a tailed l: friendly and generous without being cute.",
    sample: "Soft edges, clear intentions.",
    headline: "Banking that feels like a hello",
    accent: "#D2427F",
    accentDark: "#FF77AD",
  },
  {
    key: "strata",
    name: "Strata",
    kind: "Condensed grotesque",
    blurb: "Narrow and tall, built for dense dashboards, data tables and headlines that need to fit.",
    sample: "More data, same width.",
    headline: "Every metric at a glance",
    accent: "#0E7C86",
    accentDark: "#34C3CF",
  },
  {
    key: "plaza",
    name: "Plaza",
    kind: "Extended grotesque",
    blurb: "Wide, planted letterforms for brand marks, hero type and anything that should feel big.",
    sample: "Wide open spaces.",
    headline: "Big ideas need room",
    accent: "#5B45E0",
    accentDark: "#9C8CFF",
  },
  {
    key: "vesper",
    name: "Vesper",
    kind: "Contrast sans",
    blurb: "Heavy verticals against fine horizontals: editorial polish without a single serif.",
    sample: "Quiet details, loud clarity.",
    headline: "The details are the design",
    accent: "#8E3B8A",
    accentDark: "#D884D4",
  },
  {
    key: "ledger",
    name: "Ledger",
    kind: "Slab serif",
    blurb: "Sturdy square serifs and an even texture for documentation, reports and product writing.",
    sample: "Facts, firmly set.",
    headline: "Docs people actually finish",
    accent: "#4D7C0F",
    accentDark: "#9BD43B",
  },
  {
    key: "folio",
    name: "Folio",
    kind: "Text serif",
    blurb: "Bracketed serifs and calm contrast for essays, long reads and editorial pages.",
    sample: "Every word, well placed.",
    headline: "Long reads, beautifully set",
    accent: "#9A3412",
    accentDark: "#F59E6B",
  },
];

export const GLYPH_COUNT = 285;

export const WEIGHTS: [number, string][] = [
  [100, "Thin"],
  [200, "ExtraLight"],
  [300, "Light"],
  [400, "Regular"],
  [500, "Medium"],
  [600, "SemiBold"],
  [700, "Bold"],
  [800, "ExtraBold"],
  [900, "Black"],
];

export function weightName(w: number): string {
  const r = Math.min(900, Math.max(100, Math.round(w / 100) * 100));
  return WEIGHTS.find(([v]) => v === r)![1];
}

export const SAMPLES = [
  "Sphinx of black quartz, judge my vow.",
  "Every pixel, on purpose.",
  "Ship faster, sleep better.",
  "Type is what language looks like.",
  "The quick brown fox jumps over the lazy dog.",
  "Hello, world.",
  "Q3 revenue up 18.4% to $2,190,000",
];

export const BASIC =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@?!$%#*()[]{}/\\|.,:;-_+=<>^~'\"`·";

export const EXTENDED =
  "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿĀāĂăĄąĆćČčĎďĐđĒēĖėĘęĚěĞğĪīİıĽľŁłŃńŇňŌōŐőŒœŔŕŘřŚśŞşŠšŤťŪūŮůŰűŸŹźŻżŽž¡¿«»‹›“”‘’„‚…·•°±×÷€£¥¢©®™§←→↑↓";

export const isSerif = (f: Family) => /serif/i.test(f.kind) && !/sans/i.test(f.kind);

export function fallback(f: Family): string {
  return isSerif(f) ? "ui-serif, Georgia, serif" : "system-ui, sans-serif";
}

const origin = () => (typeof window === "undefined" ? "" : window.location.origin);

/** A self-contained prompt an AI coding agent can follow to install one family. */
export function agentPrompt(f: Family): string {
  const o = origin();
  return `Install the ${f.name} typeface in this project and make it the main font.

${f.name} is a ${f.kind.toLowerCase()} variable font with every weight from 100 to 900, free under the SIL Open Font License 1.1.

1. Download ${o}/fonts/${f.key}.woff2 and save it as "${f.name}[wght].woff2" in the folder this project serves static assets from (for example public/fonts).
2. Register it, pointing the url at the saved file:

@font-face {
  font-family: "${f.name}";
  src: url("/fonts/${f.name}[wght].woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}

3. Use it everywhere: font-family: "${f.name}", ${fallback(f)}. If the project uses Tailwind or a theme file, set it as the default ${isSerif(f) ? "serif" : "sans"} font there instead.
4. Preload the file in the document head so text never flashes.

The full family (variable and static TTF files) is at ${o}/downloads/${f.name}.zip`;
}

/** A prompt that lets the agent choose the family that fits the project. */
export function agentPromptAll(): string {
  const o = origin();
  const list = FAMILIES.map((f) => `- ${f.name} (${f.kind.toLowerCase()}): ${f.blurb} File: ${o}/fonts/${f.key}.woff2`).join("\n");
  return `Pick the fontzz typeface that best fits this project, then install it as the main font. If the choice is unclear, ask me first.

All families are variable fonts with every weight from 100 to 900, free under the SIL Open Font License 1.1.

${list}

To install the chosen family (called NAME below):
1. Download its file and save it as "NAME[wght].woff2" in the folder this project serves static assets from (for example public/fonts).
2. Register it with @font-face: font-family "NAME", src url("/fonts/NAME[wght].woff2") format("woff2"), font-weight 100 900, font-display swap.
3. Use it everywhere with a system fallback (system-ui, sans-serif, or ui-serif, Georgia, serif for Ledger and Folio). If the project uses Tailwind or a theme file, set it there instead.
4. Preload the file in the document head.`;
}
