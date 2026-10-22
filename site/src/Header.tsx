import { useEffect, useRef, useState } from "react";
import { ALL_ZIP, COUNT_WORD, Family, agentPromptAll } from "./data";
import { Theme } from "./App";
import AgentButton from "./AgentButton";

const cap = (s: string) => s[0].toUpperCase() + s.slice(1);

const KEYS: [string, string][] = [
  ["/", "Preview your text"],
  ["Arrows", "Move between families"],
  ["← →", "Weight, inside a family"],
  ["Esc", "Back"],
];

function Info() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const close = (e: PointerEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("pointerdown", close);
    window.addEventListener("keydown", esc);
    return () => {
      window.removeEventListener("pointerdown", close);
      window.removeEventListener("keydown", esc);
    };
  }, [open]);
  return (
    <div className="info" ref={ref}>
      <button
        className={"icon-btn" + (open ? " on" : "")}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label="About and shortcuts"
        title="About and shortcuts"
      >
        <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">
          <circle cx="10" cy="10" r="7" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <path d="M10 9v4.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          <circle cx="10" cy="6.4" r="1" fill="currentColor" />
        </svg>
      </button>
      {open && (
        <div className="info-pop" role="dialog" aria-label="About fontzz">
          <p className="info-lead">Drawn in code. Free for any project under the OFL.</p>
          <dl className="info-keys">
            {KEYS.map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{v}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}

interface Props {
  family: Family;
  home: boolean;
  theme: Theme;
  onTheme: () => void;
  onHome: () => void;
  preview: string;
  onPreview: (t: string) => void;
  notify: (msg: string) => void;
}

export default function Header({ family, home, theme, onTheme, onHome, preview, onPreview, notify }: Props) {
  return (
    <header className="header">
      <button className="wordmark" onClick={onHome} aria-label="fontzz, back to all families">
        <span className="wordmark-text" style={{ fontFamily: `"${family.name}"` }}>
          fontzz
        </span>
        <span className="wordmark-dot" style={{ background: "var(--accent-" + family.key + ")" }} />
      </button>
      {home ? (
        <p className="tagline">{cap(COUNT_WORD)} original type families. Every weight from 100 to 900. Free under the Open Font License.</p>
      ) : (
        <span />
      )}
      <div className="header-actions">
        <label className="tester">
          <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
            <path d="M3 3.5h10M8 3.5v9" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <input
            value={preview}
            onChange={(e) => onPreview(e.target.value)}
            placeholder={home ? `Type to preview all ${COUNT_WORD}` : "Type to preview"}
            maxLength={48}
            spellCheck={false}
            aria-label="Preview your own text"
          />
          {preview && (
            <button className="tester-clear" onClick={() => onPreview("")} aria-label="Clear preview text">
              <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
                <path d="M4 4l8 8m0-8l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          )}
        </label>
        <Info />
        <button
          className="icon-btn"
          onClick={onTheme}
          aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
          title={theme === "dark" ? "Light theme" : "Dark theme"}
        >
          <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">
            <circle cx="10" cy="10" r="6.25" fill="none" stroke="currentColor" strokeWidth="1.5" />
            <path d="M10 3.75a6.25 6.25 0 0 1 0 12.5z" fill="currentColor" />
          </svg>
        </button>
        {home && (
          <div className="get">
            <AgentButton className="get-agent" prompt={agentPromptAll} file={ALL_ZIP} notify={notify} />
            <a
              className="get-dl"
              href={`/downloads/${ALL_ZIP}`}
              download
              aria-label={`Download all ${COUNT_WORD} families`}
              title={`Download all ${COUNT_WORD} families (4 MB zip)`}
            >
              <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
                <path d="M8 2.5v7.5M4.75 7 8 10.25 11.25 7M3 13h10" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </a>
          </div>
        )}
      </div>
    </header>
  );
}
