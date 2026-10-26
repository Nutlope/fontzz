import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { FAMILIES, Family, FamilyKey, GROUPS, Group } from "./data";
import Tile from "./Tile";
import Detail from "./Detail";
import Header from "./Header";
import WeightRamp from "./WeightRamp";
import Credit from "./Credit";

export type Mode = "type" | "text" | "interface" | "glyphs";
export type Theme = "light" | "dark";
type Filter = Group | "all";

const initialWeights = Object.fromEntries(FAMILIES.map((f) => [f.key, 400])) as Record<FamilyKey, number>;

function systemTheme(): Theme {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

const keyFromHash = (): FamilyKey | null => {
  const k = window.location.hash.slice(1);
  return FAMILIES.some((f) => f.key === k) ? (k as FamilyKey) : null;
};

/** Columns and rows that give the biggest names for n tiles in a w x h wall. */
function layout(n: number, w: number, h: number) {
  const aspect = 2.1; // names are wide words, so tiles want to be about twice as wide as tall
  let best = { cols: 1, rows: n, size: 0 };
  for (let cols = 1; cols <= n; cols++) {
    const rows = Math.ceil(n / cols);
    const size = Math.min(w / cols / aspect, h / rows);
    if (size > best.size) best = { cols, rows, size };
  }
  return best;
}

export default function App() {
  const [active, setActiveState] = useState<FamilyKey | null>(keyFromHash);
  const [filter, setFilter] = useState<Filter>("all");
  const [globalWeight, setGlobalWeight] = useState(400);
  const [wall, setWall] = useState({ w: 1200, h: 800 });
  const wallRef = useRef<HTMLElement>(null);
  const pushed = useRef(false);
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

  // routing: each family has its own #hash, so links share and Back works
  const activeRef = useRef(active);
  activeRef.current = active;
  const setActive = useCallback((key: FamilyKey | null) => {
    const cur = activeRef.current;
    if (cur === key) return;
    const url = key ? `#${key}` : window.location.pathname + window.location.search;
    if (key && !cur) {
      window.history.pushState(null, "", url);
      pushed.current = true;
    } else if (!key && pushed.current) {
      pushed.current = false;
      window.history.back();
    } else {
      window.history.replaceState(null, "", url);
    }
    activeRef.current = key;
    setActiveState(key);
  }, []);

  useEffect(() => {
    const onPop = () => {
      pushed.current = false;
      setActiveState(keyFromHash());
    };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const open = useCallback(
    (key: FamilyKey, w?: number) => {
      if (w !== undefined) setWeight(key, w);
      firstLoad.current = false;
      setActive(key);
      window.scrollTo({ top: 0 });
    },
    [setWeight, setActive],
  );

  const visible = useMemo(() => FAMILIES.filter((f) => filter === "all" || f.group === filter), [filter]);
  // the detail strip follows the filter, unless the open family is outside it
  const strip = useMemo(
    () => (active && !visible.some((f) => f.key === active) ? FAMILIES : visible),
    [active, visible],
  );
  const counts = useMemo(() => {
    const c: Record<string, number> = { all: FAMILIES.length };
    for (const f of FAMILIES) c[f.group] = (c[f.group] ?? 0) + 1;
    return c;
  }, []);

  const applyGlobal = useCallback((w: number) => {
    const v = Math.round(Math.min(900, Math.max(100, w)));
    setGlobalWeight(v);
    setWeights(Object.fromEntries(FAMILIES.map((f) => [f.key, v])) as Record<FamilyKey, number>);
  }, []);

  // measure the wall so the grid can pick its columns
  useLayoutEffect(() => {
    const el = wallRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => el.clientWidth && setWall({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    if (el.clientWidth) setWall({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, [active, filter]);
  const grid = layout(visible.length, wall.w, wall.h);

  const onFit = useCallback((key: string, px: number) => {
    setFits((f) => (f[key] === px ? f : { ...f, [key]: px }));
  }, []);
  const fit = Math.min(Infinity, ...visible.map((f) => fits[f.key] ?? Infinity));

  // keyboard: arrows step family and weight, Esc goes back
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      if (t.isContentEditable || t.tagName === "INPUT" || t.tagName === "TEXTAREA") {
        if (e.key === "Escape") t.blur();
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === "/") {
        document.querySelector<HTMLInputElement>(".tester input")?.focus();
        e.preventDefault();
        return;
      }
      if (!active) {
        // arrows walk the wall like a spreadsheet
        const step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: grid.cols, ArrowUp: -grid.cols }[e.key];
        if (step === undefined) return;
        const tiles = [...document.querySelectorAll<HTMLElement>(".tile")];
        const cur = tiles.indexOf(document.activeElement as HTMLElement);
        const next = cur < 0 ? 0 : Math.min(tiles.length - 1, Math.max(0, cur + step));
        tiles[next]?.focus();
        e.preventDefault();
        return;
      }
      const list = strip;
      const idx = list.findIndex((f) => f.key === active);
      if (e.key === "Escape") {
        setActive(null);
      } else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        const n = (idx + (e.key === "ArrowDown" ? 1 : list.length - 1)) % list.length;
        setActive(list[n].key);
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
  }, [active, weights, setWeight, setActive, grid.cols, strip]);

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
          families={strip}
          onSelect={(k) => setActive(k)}
          onBack={() => setActive(null)}
          notify={notify}
        />
      ) : (
        <>
          <nav className="filterbar" aria-label="Filter families">
            <div className="chips" role="tablist">
              {(["all", ...GROUPS.map(([g]) => g)] as Filter[]).map((g) => (
                <button
                  key={g}
                  role="tab"
                  aria-selected={filter === g}
                  className={"chip" + (filter === g ? " on" : "")}
                  onClick={() => setFilter(g)}
                >
                  {g === "all" ? "All" : GROUPS.find(([k]) => k === g)![1]}
                  <span className="chip-count">{counts[g]}</span>
                </button>
              ))}
            </div>
            <Credit family={focusFamily} className="credit-bar" />
            <div className="filter-weight">
              <WeightRamp family={focusFamily} weight={globalWeight} onWeight={applyGlobal} />
            </div>
          </nav>
          <main
            ref={wallRef}
            key={filter}
            className="wall"
            style={{ "--cols": grid.cols, "--rows": grid.rows } as React.CSSProperties}
            onPointerLeave={() => setHovered(null)}
          >
            {visible.map((f, i) => (
              <Tile
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
          <Credit family={focusFamily} className="credit-foot" />
        </>
      )}
      <div className={"toast" + (toast ? " show" : "")} role="status" aria-live="polite">
        {toast}
      </div>
    </div>
  );
}
