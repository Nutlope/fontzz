import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FAMILIES, Family, FamilyKey } from "./data";
import IndexBand from "./IndexBand";
import Detail from "./Detail";
import Header from "./Header";

export type Mode = "type" | "text" | "interface" | "glyphs";
export type Theme = "light" | "dark";

// index columns on wide screens; rows are derived so any family count fills the page
const COLS = FAMILIES.length > 10 ? 2 : 1;

const initialWeights = Object.fromEntries(FAMILIES.map((f) => [f.key, 400])) as Record<FamilyKey, number>;

function systemTheme(): Theme {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [active, setActive] = useState<FamilyKey | null>(null);
  const [hovered, setHovered] = useState<FamilyKey | null>(null);
  const [weights, setWeights] = useState(initialWeights);
  const [mode, setMode] = useState<Mode>("type");
  const [text, setText] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [preview, setPreview] = useState("");
  const [fits, setFits] = useState<Record<string, number>>({});
  const firstLoad = useRef(true);
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      const t = localStorage.getItem("fontzz-theme");
      if (t === "light" || t === "dark") return t;
    } catch {
      /* storage unavailable */
    }
    return systemTheme();
  });
  const toastTimer = useRef<number>();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    const t = window.setTimeout(() => (firstLoad.current = false), 1200);
    return () => window.clearTimeout(t);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((t) => {
      const n = t === "dark" ? "light" : "dark";
      try {
        localStorage.setItem("fontzz-theme", n);
      } catch {
        /* storage unavailable */
      }
      return n;
    });
  }, []);

  const notify = useCallback((msg: string) => {
    setToast(msg);
    window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(null), 1600);
  }, []);

  const setWeight = useCallback((key: FamilyKey, w: number) => {
    const v = Math.round(Math.min(900, Math.max(100, w)));
    setWeights((ws) => (ws[key] === v ? ws : { ...ws, [key]: v }));
  }, []);

  const open = useCallback(
    (key: FamilyKey, w?: number) => {
      if (w !== undefined) setWeight(key, w);
      firstLoad.current = false;
      setActive(key);
      window.scrollTo({ top: 0 });
    },
    [setWeight],
  );

  const onFit = useCallback((key: string, px: number) => {
    setFits((f) => (f[key] === px ? f : { ...f, [key]: px }));
  }, []);
  const fit = Math.min(Infinity, ...Object.values(fits));

  // keyboard: arrows step family and weight, Esc goes back
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      if (t.isContentEditable || t.tagName === "INPUT" || t.tagName === "TEXTAREA") {
        if (e.key === "Escape") t.blur();
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const idx = active ? FAMILIES.findIndex((f) => f.key === active) : -1;
      if (e.key === "Escape" && active) {
        setActive(null);
      } else if (active && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
        const n = (idx + (e.key === "ArrowDown" ? 1 : FAMILIES.length - 1)) % FAMILIES.length;
        setActive(FAMILIES[n].key);
        e.preventDefault();
      } else if (active && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
        const cur = weights[active];
        const next = e.shiftKey
          ? cur + (e.key === "ArrowRight" ? 10 : -10)
          : e.key === "ArrowRight"
            ? Math.floor(cur / 100) * 100 + 100
            : Math.ceil(cur / 100) * 100 - 100;
        setWeight(active, next);
        e.preventDefault();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [active, weights, setWeight]);

  const focusFamily: Family = useMemo(
    () => FAMILIES.find((f) => f.key === (active ?? hovered ?? "halden"))!,
    [hovered, active],
  );
  const activeFamily = active ? FAMILIES.find((f) => f.key === active)! : null;
  const trimmed = preview.trim();

  return (
    <div className={"app" + (active ? " is-open" : "")}>
      <Header
        family={focusFamily}
        home={!active}
        notify={notify}
        theme={theme}
        onTheme={toggleTheme}
        onHome={() => setActive(null)}
        preview={preview}
        onPreview={setPreview}
      />
      {activeFamily ? (
        <Detail
          family={activeFamily}
          weight={weights[activeFamily.key]}
          mode={mode}
          text={text ?? (trimmed ? trimmed : null)}
          theme={theme}
          onWeight={(w) => setWeight(activeFamily.key, w)}
          onMode={setMode}
          onText={setText}
          onSelect={(k) => setActive(k)}
          onBack={() => setActive(null)}
          notify={notify}
        />
      ) : (
        <main
          className="bands"
          style={{ "--rows": Math.ceil(FAMILIES.length / COLS) } as React.CSSProperties}
          onPointerLeave={() => setHovered(null)}
        >
          {FAMILIES.map((f, i) => (
            <IndexBand
              key={f.key}
              family={f}
              index={i}
              weight={weights[f.key]}
              preview={trimmed}
              fit={fit}
              intro={firstLoad.current}
              onFit={(px) => onFit(f.key, px)}
              onHover={(h) => setHovered(h ? f.key : null)}
              onOpen={(w) => open(f.key, w)}
            />
          ))}
        </main>
      )}
      <div className={"toast" + (toast ? " show" : "")} role="status" aria-live="polite">
        {toast}
      </div>
    </div>
  );
}
