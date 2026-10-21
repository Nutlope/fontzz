import { useEffect, useMemo, useState } from "react";
import { BASIC, EXTENDED, Family } from "../data";
import { Theme } from "../App";

interface Props {
  family: Family;
  weight: number;
  theme: Theme;
}

type Seg = number[] | (string | number)[];
interface GlyphRec {
  w: number[];
  c: Seg[][][]; // [master][contour][segment]
}
interface Outlines {
  upm: number;
  xh: number;
  cap: number;
  asc: number;
  desc: number;
  masters: number[];
  glyphs: Record<string, GlyphRec>;
}

const cache = new Map<string, Promise<Outlines>>();
function load(key: string) {
  if (!cache.has(key)) cache.set(key, fetch(`/outlines/${key}.json`).then((r) => r.json()));
  return cache.get(key)!;
}

/** Piecewise linear between masters, the same model the variable font uses. */
function blend(m: number[], vals: number[], w: number) {
  if (w <= m[1]) {
    const t = (w - m[0]) / (m[1] - m[0]);
    return vals[0] + (vals[1] - vals[0]) * t;
  }
  const t = (w - m[1]) / (m[2] - m[1]);
  return vals[1] + (vals[2] - vals[1]) * t;
}

interface Contour {
  d: string;
  nodes: { x: number; y: number; smooth: boolean }[];
  handles: [number, number, number, number][];
}

function interp(o: Outlines, g: GlyphRec, w: number): { width: number; contours: Contour[] } {
  const width = blend(o.masters, g.w, w);
  const contours: Contour[] = [];
  const n = g.c[0].length;
  for (let ci = 0; ci < n; ci++) {
    const segs = g.c[0][ci];
    const num = (si: number, k: number) =>
      blend(
        o.masters,
        [0, 1, 2].map((mi) => Number(g.c[mi][ci][si][k])),
        w,
      );
    let d = "";
    const nodes: Contour["nodes"] = [];
    const handles: Contour["handles"] = [];
    const sx = num(0, 0);
    const sy = num(0, 1);
    d += `M${sx.toFixed(1)} ${sy.toFixed(1)}`;
    let px = sx;
    let py = sy;
    let prevCurve = false;
    nodes.push({ x: sx, y: sy, smooth: false });
    for (let si = 1; si < segs.length; si++) {
      const s = segs[si];
      if (s[0] === "L") {
        const x = num(si, 1);
        const y = num(si, 2);
        d += `L${x.toFixed(1)} ${y.toFixed(1)}`;
        px = x;
        py = y;
        nodes.push({ x, y, smooth: false });
        prevCurve = false;
      } else {
        const v = [1, 2, 3, 4, 5, 6].map((k) => num(si, k));
        d += `C${v.map((q) => q.toFixed(1)).join(" ")}`;
        handles.push([px, py, v[0], v[1]], [v[4], v[5], v[2], v[3]]);
        if (prevCurve && nodes.length) nodes[nodes.length - 1].smooth = true;
        px = v[4];
        py = v[5];
        nodes.push({ x: px, y: py, smooth: true });
        prevCurve = true;
      }
    }
    d += "Z";
    contours.push({ d, nodes, handles });
  }
  return { width, contours };
}

export default function GlyphsView({ family, weight }: Props) {
  const [set, setSet] = useState<"basic" | "extended">("basic");
  const [data, setData] = useState<Outlines | null>(null);
  const [hover, setHover] = useState<string | null>(null);
  const [pinned, setPinned] = useState<string>("a");
  const [construct, setConstruct] = useState(true);

  useEffect(() => {
    let live = true;
    load(family.key).then((d) => live && setData(d));
    return () => {
      live = false;
    };
  }, [family.key]);

  const chars = useMemo(() => Array.from(set === "basic" ? BASIC : EXTENDED), [set]);
  const current = hover ?? pinned;
  const rec = data?.glyphs[current];
  const shape = useMemo(() => (data && rec ? interp(data, rec, weight) : null), [data, rec, weight]);

  const ff = { fontFamily: `"${family.name}"` };
  const top = (data?.asc ?? 750) + 70;
  const bot = (data?.desc ?? -210) - 40;
  const vw = Math.max(shape ? shape.width + 300 : 760, 760);
  const cx = shape ? (vw - shape.width) / 2 : vw / 2;
  const metrics: [string, number][] = data
    ? [
        ["Ascender", data.asc],
        ["Cap height", data.cap],
        ["x-height", data.xh],
        ["Baseline", 0],
        ["Descender", data.desc],
      ]
    : [];

  return (
    <div className="glyphs">
      <div className="glyph-grid-wrap">
        <div className={"glyph-grid " + set} style={ff} onPointerLeave={() => setHover(null)}>
          {chars.map((ch) => (
            <button
              key={ch}
              className={"glyph-cell" + (ch === pinned ? " pinned" : "")}
              style={{ fontWeight: weight }}
              onPointerEnter={() => setHover(ch)}
              onFocus={() => setHover(ch)}
              onClick={() => setPinned(ch)}
              aria-label={`Inspect ${ch}`}
            >
              {ch}
            </button>
          ))}
        </div>
        <div className="glyph-sets" role="tablist" aria-label="Character set">
          <button className={"seg" + (set === "basic" ? " on" : "")} onClick={() => setSet("basic")}>
            Basic Latin
          </button>
          <button className={"seg" + (set === "extended" ? " on" : "")} onClick={() => setSet("extended")}>
            Accents and symbols
          </button>
        </div>
      </div>
      <aside className="inspector">
        <div className="insp-head">
          <span className="insp-char" style={{ ...ff, fontWeight: weight }}>
            {current}
          </span>
          <span className="insp-meta">
            <b>U+{current.codePointAt(0)!.toString(16).toUpperCase().padStart(4, "0")}</b>
            <span>{shape ? `Advance ${Math.round(shape.width)}` : "Rendered from the font"}</span>
          </span>
          <button
            className={"seg small" + (construct ? " on" : "")}
            onClick={() => setConstruct((c) => !c)}
            disabled={!shape}
            title="Show the overlapping strokes each glyph is built from"
          >
            Construction
          </button>
        </div>
        <svg className="insp-svg" viewBox={`0 ${-top} ${vw} ${top - bot}`} preserveAspectRatio="xMidYMid meet">
          {metrics.map(([label, y]) => (
            <g key={label} className="metric">
              <line x1={0} x2={vw} y1={-y} y2={-y} />
              <text x={12} y={-y - 14}>
                {label}
              </text>
            </g>
          ))}
          {shape ? (
            <g transform={`translate(${cx} 0) scale(1 -1)`}>
              <line className="adv" x1={0} x2={0} y1={bot} y2={top} />
              <line className="adv" x1={shape.width} x2={shape.width} y1={bot} y2={top} />
              {construct ? (
                <>
                  {shape.contours.map((c, i) => (
                    <path key={"f" + i} d={c.d} className="c-fill" />
                  ))}
                  {shape.contours.map((c, i) => (
                    <path key={"s" + i} d={c.d} className="c-stroke" />
                  ))}
                  {shape.contours.flatMap((c, i) =>
                    c.handles.map((h, j) => (
                      <line key={`h${i}-${j}`} className="c-handle" x1={h[0]} y1={h[1]} x2={h[2]} y2={h[3]} />
                    )),
                  )}
                  {shape.contours.flatMap((c, i) =>
                    c.handles.map((h, j) => <circle key={`hc${i}-${j}`} className="c-ctrl" cx={h[2]} cy={h[3]} r={6} />),
                  )}
                  {shape.contours.flatMap((c, i) =>
                    c.nodes.map((n, j) =>
                      n.smooth ? (
                        <circle key={`n${i}-${j}`} className="c-node" cx={n.x} cy={n.y} r={9} />
                      ) : (
                        <rect key={`n${i}-${j}`} className="c-node" x={n.x - 8} y={n.y - 8} width={16} height={16} />
                      ),
                    ),
                  )}
                </>
              ) : (
                <path d={shape.contours.map((c) => c.d).join(" ")} className="g-fill" />
              )}
            </g>
          ) : (
            <text x={vw / 2} y={0} textAnchor="middle" fontSize={data?.upm ?? 1000} className="g-text" style={{ ...ff, fontWeight: weight }}>
              {current}
            </text>
          )}
        </svg>
        <p className="insp-note">
          {shape
            ? construct
              ? "Each shade is one stroke from the generator. Overlaps merge into a single outline."
              : "The exact outline at this weight, interpolated live."
            : "Accented glyphs are composites of the base letter and a mark."}
        </p>
      </aside>
    </div>
  );
}
