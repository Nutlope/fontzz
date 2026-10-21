import { useEffect, useLayoutEffect, useRef } from "react";
import { Family, weightName } from "./data";

interface Props {
  family: Family;
  index: number;
  weight: number;
  preview: string;
  fit: number;
  intro: boolean;
  onFit: (px: number) => void;
  onHover: (h: boolean) => void;
  onOpen: (w: number) => void;
}

const reduceMotion = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/** One row of the index. Moving across it scrubs the weight live. */
export default function IndexBand({ family: f, index, weight, preview, fit, intro, onFit, onHover, onOpen }: Props) {
  const headRef = useRef<HTMLDivElement>(null);
  const nameRef = useRef<HTMLSpanElement>(null);
  const readRef = useRef<HTMLSpanElement>(null);
  const lineRef = useRef<HTMLDivElement>(null);
  const anim = useRef({ cur: intro ? 100 : weight, target: weight, raf: 0, hovering: false });

  const paint = (w: number) => {
    const r = Math.round(w);
    if (nameRef.current) nameRef.current.style.fontWeight = String(r);
    if (readRef.current) readRef.current.textContent = `${weightName(r)} ${r}`;
    if (lineRef.current) lineRef.current.dataset.w = String(r);
  };

  const run = () => {
    const a = anim.current;
    cancelAnimationFrame(a.raf);
    const step = () => {
      a.cur += (a.target - a.cur) * 0.3;
      if (Math.abs(a.target - a.cur) < 0.5) a.cur = a.target;
      paint(a.cur);
      if (a.cur !== a.target) a.raf = requestAnimationFrame(step);
    };
    a.raf = requestAnimationFrame(step);
  };

  // entrance: a quick sweep up from Thin, staggered, only on first load
  useEffect(() => {
    const a = anim.current;
    paint(a.cur);
    if (!intro || reduceMotion()) {
      a.cur = a.target = weight;
      paint(weight);
      return;
    }
    const t = window.setTimeout(() => {
      a.target = weight;
      run();
    }, 80 + index * 45);
    return () => {
      window.clearTimeout(t);
      cancelAnimationFrame(a.raf);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // shrink long preview text so every row fits at its widest weight
  useLayoutEffect(() => {
    const el = nameRef.current;
    const box = el?.parentElement;
    if (!el || !box) return;
    const measure = () => {
      el.style.setProperty("--fit", "9999px");
      const s = parseFloat(getComputedStyle(el).fontSize);
      const prev = el.style.fontWeight;
      el.style.fontWeight = "900";
      const w = el.scrollWidth;
      el.style.fontWeight = prev;
      el.style.removeProperty("--fit");
      const avail = box.clientWidth;
      onFit(w > avail && s > 0 ? Math.floor((avail * s) / w) : Infinity);
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(box);
    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preview, f.key]);

  const onMove = (e: React.PointerEvent) => {
    if (!headRef.current || e.pointerType === "touch") return;
    const r = headRef.current.getBoundingClientRect();
    const pad = Math.min(96, r.width * 0.08);
    const x = Math.min(1, Math.max(0, (e.clientX - r.left - pad) / (r.width - pad * 2)));
    const a = anim.current;
    a.hovering = true;
    a.target = 100 + x * 800;
    if (lineRef.current) lineRef.current.style.transform = `translateX(${e.clientX - r.left}px)`;
    run();
  };

  const onLeave = () => {
    const a = anim.current;
    a.hovering = false;
    onHover(false);
    a.target = weight;
    run();
  };

  const open = () => onOpen(anim.current.hovering ? Math.round(anim.current.cur / 10) * 10 : weight);

  return (
    <div
      ref={headRef}
      className="band"
      style={
        {
          "--fam": `"${f.name}"`,
          "--accent": `var(--accent-${f.key})`,
          "--fit": Number.isFinite(fit) ? `${fit}px` : undefined,
        } as React.CSSProperties
      }
      role="button"
      tabIndex={0}
      aria-label={`${f.name}, ${f.kind}. Open`}
      onPointerEnter={() => onHover(true)}
      onPointerLeave={onLeave}
      onPointerMove={onMove}
      onClick={open}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          open();
        }
      }}
    >
      <span className="band-index">{String(index + 1).padStart(2, "0")}</span>
      <span className="band-name">
        <span ref={nameRef} className="band-name-text">
          {preview || f.name}
        </span>
      </span>
      <span className="band-meta">
        <span className="band-kind">
          {preview && <b>{f.name}</b>}
          {f.kind}
        </span>
        <span ref={readRef} className="band-read" aria-hidden="true" />
      </span>
      <span className="band-arrow" aria-hidden="true">
        <svg viewBox="0 0 16 16" width="16" height="16">
          <path d="M3 8h10m-4-4 4 4-4 4" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <div ref={lineRef} className="scrub-line" aria-hidden="true" />
    </div>
  );
}
