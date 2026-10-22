import { useEffect, useRef } from "react";
import { FAMILIES, Family, FamilyKey, GLYPH_COUNT, agentPrompt, zipName } from "./data";
import AgentButton from "./AgentButton";
import { Mode, Theme } from "./App";
import WeightRamp from "./WeightRamp";
import TypeView from "./views/TypeView";
import TextView from "./views/TextView";
import InterfaceView from "./views/InterfaceView";
import GlyphsView from "./views/GlyphsView";

interface Props {
  family: Family;
  weight: number;
  mode: Mode;
  text: string | null;
  theme: Theme;
  onWeight: (w: number) => void;
  onMode: (m: Mode) => void;
  onText: (t: string | null) => void;
  onSelect: (k: FamilyKey) => void;
  onBack: () => void;
  notify: (msg: string) => void;
}

const MODES: [Mode, string][] = [
  ["type", "Type"],
  ["text", "Text"],
  ["interface", "Interface"],
  ["glyphs", "Glyphs"],
];

export default function Detail(p: Props) {
  const f = p.family;
  const stripRef = useRef<HTMLDivElement>(null);

  // keep the active family visible in the strip on narrow screens
  useEffect(() => {
    const el = stripRef.current?.querySelector<HTMLElement>(".strip-item.on");
    el?.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
  }, [f.key]);

  return (
    <div className="detail" style={{ "--accent": `var(--accent-${f.key})` } as React.CSSProperties}>
      <nav className="strip" aria-label="Families">
        <button className="strip-back" onClick={p.onBack} title="All families (Esc)">
          <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
            <path d="M13 8H3m4-4L3 8l4 4" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          All
        </button>
        <div
          className="strip-list"
          ref={stripRef}
          role="tablist"
          aria-label="Choose a family"
          onWheel={(e) => {
            // vertical wheels scroll the strip sideways
            if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) e.currentTarget.scrollLeft += e.deltaY;
          }}
        >
          {FAMILIES.map((g) => (
            <button
              key={g.key}
              role="tab"
              aria-selected={g.key === f.key}
              className={"strip-item" + (g.key === f.key ? " on" : "")}
              style={{ fontFamily: `"${g.name}"`, "--accent": `var(--accent-${g.key})` } as React.CSSProperties}
              onClick={() => p.onSelect(g.key)}
              title={g.kind}
            >
              {g.name}
            </button>
          ))}
        </div>
      </nav>

      <div className="stage-head">
        <div className="stage-title">
          <h1 className="stage-name" style={{ fontFamily: `"${f.name}"`, fontWeight: p.weight }}>
            {f.name}
          </h1>
          <p className="stage-meta">
            <span>{f.kind}</span>
            <i />
            <span>{GLYPH_COUNT} glyphs</span>
            <i />
            <span>Variable, 100 to 900</span>
            <i />
            <span>OFL 1.1</span>
          </p>
        </div>
        <div className="actions">
          <AgentButton className="ghost-btn" prompt={() => agentPrompt(f)} file={zipName(f)} notify={p.notify} />
          <a className="solid-btn" href={`/downloads/${f.name}.zip`} download>
            <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
              <path d="M8 2.5v7.5M4.75 7 8 10.25 11.25 7M3 13h10" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Download
          </a>
        </div>
      </div>

      <div className="view" key={p.mode}>
        {p.mode === "type" && <TypeView family={f} weight={p.weight} text={p.text} onText={p.onText} />}
        {p.mode === "text" && <TextView family={f} weight={p.weight} />}
        {p.mode === "interface" && <InterfaceView family={f} weight={p.weight} />}
        {p.mode === "glyphs" && <GlyphsView family={f} weight={p.weight} theme={p.theme} />}
      </div>

      <div className="toolbar">
        <WeightRamp family={f} weight={p.weight} onWeight={p.onWeight} />
        <div className="tabs" role="tablist" aria-label="View">
          {MODES.map(([m, label]) => (
            <button
              key={m}
              role="tab"
              aria-selected={p.mode === m}
              className={"tab" + (p.mode === m ? " on" : "")}
              onClick={() => p.onMode(m)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
