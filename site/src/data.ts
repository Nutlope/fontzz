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
  | "folio"
  | "opaline"
  | "signal"
  | "tally"
  | "topsy"
  | "tempo"
  | "pebble"
  | "orbit"
  | "cleft"
  | "beacon"
  | "brioche"
  | "diode"
  | "aurelia"
  | "marquee"
  | "anvil"
  | "gravure"
  | "frontier"
  | "quill"
  | "rewind"
  | "spire"
  | "vector";

export type Group = "sans" | "serif" | "display" | "mono";

export const GROUPS: [Group, string][] = [
  ["sans", "Sans"],
  ["serif", "Serif"],
  ["display", "Display"],
  ["mono", "Mono"],
];

const GROUP_OF: Record<FamilyKey, Group> = {
  halden: "sans",
  rondel: "sans",
  tessera: "sans",
  alder: "sans",
  mallow: "sans",
  strata: "sans",
  plaza: "sans",
  beacon: "sans",
  pebble: "sans",
  aurelia: "sans",
  tempo: "sans",
  ledger: "serif",
  folio: "serif",
  opaline: "serif",
  cleft: "serif",
  brioche: "serif",
  anvil: "serif",
  frontier: "serif",
  quill: "serif",
  vesper: "display",
  topsy: "display",
  orbit: "display",
  marquee: "display",
  gravure: "display",
  rewind: "display",
  spire: "display",
  vector: "display",
  diode: "display",
  signal: "mono",
  tally: "mono",
};

export interface Family {
  group: Group;
  key: FamilyKey;
  name: string;
  kind: string;
  blurb: string;
  sample: string;
  headline: string;
  accent: string;
  accentDark: string;
}

const LIST: Omit<Family, "group">[] = [
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
  {
    key: "opaline",
    name: "Opaline",
    kind: "Didone",
    blurb: "Hairline serifs, ball terminals and fierce contrast for mastheads, fashion and luxury.",
    sample: "Elegance is refusal.",
    headline: "The autumn collection",
    accent: "#1E3A8A",
    accentDark: "#93B4FF",
  },
  {
    key: "signal",
    name: "Signal",
    kind: "Monospace",
    blurb: "A clean sans monospace for code, terminals and tables, with slab i, l and r that never blur.",
    sample: "const ship = () => fast;",
    headline: "npm run build && deploy",
    accent: "#0284C7",
    accentDark: "#5CC8FF",
  },
  {
    key: "tally",
    name: "Tally",
    kind: "Slab monospace",
    blurb: "Typewriter warmth with modern spacing, for code comments, notes, receipts and logs.",
    sample: "Every line, accounted for.",
    headline: "Invoice 0042, paid in full",
    accent: "#52525B",
    accentDark: "#D4D4D8",
  },
  {
    key: "topsy",
    name: "Topsy",
    kind: "Reverse contrast",
    blurb: "Thick horizontals and thin verticals: contrast turned upside down for posters and play.",
    sample: "Turn it upside down.",
    headline: "Weekend jam session",
    accent: "#C026D3",
    accentDark: "#E879F9",
  },
  {
    key: "tempo",
    name: "Tempo",
    kind: "Slanted grotesque",
    blurb: "A forward-leaning sans with pen-cut ends that adds speed to sport, motion and launches.",
    sample: "Faster than yesterday.",
    headline: "Race day starts now",
    accent: "#DC2626",
    accentDark: "#FF6B6B",
  },
  {
    key: "pebble",
    name: "Pebble",
    kind: "Soft square",
    blurb: "Rounded squares, round ends and a single-story a, friendly for apps, games and dashboards.",
    sample: "Smooth, round, ready.",
    headline: "Level up your mornings",
    accent: "#CA8A04",
    accentDark: "#FACC15",
  },
  {
    key: "orbit",
    name: "Orbit",
    kind: "Extended square",
    blurb: "Wide squared forms with a technical, aerospace feel for brands, specs and big numbers.",
    sample: "Launch window open.",
    headline: "T minus 10 seconds",
    accent: "#475569",
    accentDark: "#CBD5E1",
  },
  {
    key: "cleft",
    name: "Cleft",
    kind: "Wedge serif",
    blurb: "Triangular wedge serifs with a carved, confident voice for headlines, labels and packaging.",
    sample: "Carved with care.",
    headline: "Small batch, built to last",
    accent: "#7C2D12",
    accentDark: "#E8A27C",
  },
  {
    key: "beacon",
    name: "Beacon",
    kind: "Legible sans",
    blurb: "Generous spacing, a tailed l and a serifed I so nothing gets confused. Made for reading.",
    sample: "Ill, 1ll and lIl stay clear.",
    headline: "Built for every reader",
    accent: "#15803D",
    accentDark: "#4ADE80",
  },
  {
    key: "brioche",
    name: "Brioche",
    kind: "Soft serif",
    blurb: "Pillowy rounded serifs and soft ends for cafes, children's books and warm brands.",
    sample: "Fresh out of the oven.",
    headline: "Good mornings, baked daily",
    accent: "#B45309",
    accentDark: "#F2B66D",
  },
  {
    key: "diode",
    name: "Diode",
    kind: "Dot matrix",
    blurb: "Every letter sampled onto a grid: LED dots at Thin, crisp pixels at Regular, solid blocks at Black.",
    sample: "Status: all systems go.",
    headline: "Now boarding gate 12",
    accent: "#0891B2",
    accentDark: "#22D3EE",
  },
  {
    key: "aurelia",
    name: "Aurelia",
    kind: "Flared sans",
    blurb: "Stems that swell gently at their ends, carved-stone elegance without a single serif.",
    sample: "Quietly carved in stone.",
    headline: "An evening at the gallery",
    accent: "#9D174D",
    accentDark: "#F9A8D4",
  },
  {
    key: "marquee",
    name: "Marquee",
    kind: "Art Deco",
    blurb: "High crossbars, perfect circles and a tiny x-height straight from a 1920s theatre sign.",
    sample: "Tonight only, at eight.",
    headline: "The grand opening gala",
    accent: "#B45309",
    accentDark: "#FCD34D",
  },
  {
    key: "anvil",
    name: "Anvil",
    kind: "Geometric slab",
    blurb: "Circles and heavy square slabs, sturdy as a workshop sign and friendly at any size.",
    sample: "Built to take a beating.",
    headline: "Tools for serious makers",
    accent: "#44403C",
    accentDark: "#D6D3D1",
  },
  {
    key: "gravure",
    name: "Gravure",
    kind: "Engraver's gothic",
    blurb: "Wide, calm letters with hairline spurs, like a calling card or a banknote.",
    sample: "Est. by appointment only.",
    headline: "Private client services",
    accent: "#166534",
    accentDark: "#86EFAC",
  },
  {
    key: "frontier",
    name: "Frontier",
    kind: "Condensed Clarendon",
    blurb: "Tall bracketed slabs with ball ends, a poster face from the frontier made modern.",
    sample: "Wanted: one good headline.",
    headline: "The last stagecoach west",
    accent: "#991B1B",
    accentDark: "#FCA5A5",
  },
  {
    key: "quill",
    name: "Quill",
    kind: "Semi-serif",
    blurb: "A humanist sans with pen-like entry serifs on top only, warm without slowing the eye.",
    sample: "Half serif, all character.",
    headline: "Notes from the writing desk",
    accent: "#4338CA",
    accentDark: "#A5B4FC",
  },
  {
    key: "rewind",
    name: "Rewind",
    kind: "Backslant",
    blurb: "A rounded sans leaning backwards, pure eighties energy for music, games and merch.",
    sample: "Press play, then rewind.",
    headline: "Mixtape volume two",
    accent: "#DB2777",
    accentDark: "#F472B6",
  },
  {
    key: "spire",
    name: "Spire",
    kind: "Compressed",
    blurb: "Ultra narrow and tall for posters, sports scores and headlines that must fit.",
    sample: "Taller than the skyline.",
    headline: "Final score 104 to 98",
    accent: "#1D4ED8",
    accentDark: "#93C5FD",
  },
  {
    key: "vector",
    name: "Vector",
    kind: "Angular square",
    blurb: "Squared, condensed and cut at forty-five degrees for tech, gaming and hardware.",
    sample: "Calibrated for speed.",
    headline: "System online, 120 fps",
    accent: "#0F766E",
    accentDark: "#5EEAD4",
  },
];

/** Every family, grouped sans, serif, display, mono (stable within a group). */
export const FAMILIES: Family[] = LIST.map((f) => ({ ...f, group: GROUP_OF[f.key] })).sort(
  (a, b) => GROUPS.findIndex(([g]) => g === a.group) - GROUPS.findIndex(([g]) => g === b.group),
);

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

export const isMono = (f: Family) => /monospace/i.test(f.kind);
export const isSerif = (f: Family) => !isMono(f) && /serif|didone|slab|clarendon/i.test(f.kind) && !/sans/i.test(f.kind);

export function fallback(f: Family): string {
  if (isMono(f)) return "ui-monospace, monospace";
  return isSerif(f) ? "ui-serif, serif" : "system-ui, sans-serif";
}

const COUNT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine", "thirty"];
export const COUNT = FAMILIES.length;
export const COUNT_WORD = COUNT_WORDS[COUNT] ?? String(COUNT);

export const REPO = "Luffixos/fontzz";
export const REPO_URL = `https://github.com/${REPO}`;
export const AUTHORS: [string, string][] = [
  ["Hassan", "https://x.com/nutlope"],
  ["Youssef", "https://x.com/YoussefUIUX"],
];

export const zipName = (f: Family) => `${f.name}.zip`;
export const ALL_ZIP = "fontzz-all.zip";

/** Prompt for one family. The button downloads the zip, so the agent works from a local file. */
export function agentPrompt(f: Family): string {
  return `I just downloaded the ${f.name} typeface from fontzz. It's ${zipName(f)} in my Downloads folder (if it isn't there, ask me where it is). Install it in this project and make it the main font.

1. Unzip it and copy ${f.name}/web/${f.name}[wght].woff2 into the folder this project serves static files from (for example public/fonts).
2. Register it, pointing the url at the copied file:

@font-face {
  font-family: "${f.name}";
  src: url("/fonts/${f.name}[wght].woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}

3. Use it everywhere: font-family: "${f.name}", ${fallback(f)}. If the project uses Tailwind or a theme file, set it as the default ${isMono(f) ? "mono" : isSerif(f) ? "serif" : "sans"} font there instead.
4. Preload the file in the document head so text never flashes.

${f.name} is a ${f.kind.toLowerCase()} variable font with every weight from 100 to 900, free under the SIL Open Font License 1.1.`;
}

/** Prompt for the whole collection: the agent asks which family to use. */
export function agentPromptAll(): string {
  const list = FAMILIES.map((f) => `- ${f.name} (${f.kind.toLowerCase()}): ${f.blurb}`).join("\n");
  return `I just downloaded ${ALL_ZIP} from fontzz: ${COUNT_WORD} type families in my Downloads folder (if it isn't there, ask me where it is).

First, look at this project and ask me which family I want, suggesting the two or three that fit it best:

${list}

Then install the one I pick (called NAME below):
1. Unzip it and copy fontzz/NAME/web/NAME[wght].woff2 into the folder this project serves static files from (for example public/fonts).
2. Register it with @font-face: font-family "NAME", src url("/fonts/NAME[wght].woff2") format("woff2"), font-weight 100 900, font-display swap.
3. Use it everywhere with a fallback: system-ui, sans-serif for sans families, ui-serif, serif for serif families, ui-monospace, monospace for Signal and Tally. If the project uses Tailwind or a theme file, set it there instead.
4. Preload the file in the document head.

Every family is a variable font with weights from 100 to 900, free under the SIL Open Font License 1.1.`;
}
