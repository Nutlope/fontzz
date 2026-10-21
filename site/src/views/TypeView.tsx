import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Family, SAMPLES } from "../data";

interface Props {
  family: Family;
  weight: number;
  text: string | null;
  onText: (t: string | null) => void;
}

/** Large editable specimen that always fits the stage. */
export default function TypeView({ family, weight, text, onText }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const ed = useRef<HTMLDivElement>(null);
  const editing = useRef(false);
  const [sampleIdx, setSampleIdx] = useState(-1);
  const raf = useRef(0);

  const content = text ?? (sampleIdx < 0 ? family.sample : SAMPLES[sampleIdx % SAMPLES.length]);

  const fit = useCallback(() => {
    const b = box.current;
    const e = ed.current;
    if (!b || !e) return;
    const W = b.clientWidth;
    const H = b.clientHeight;
    let lo = 16;
    let hi = Math.min(420, H);
    for (let i = 0; i < 14; i++) {
      const mid = (lo + hi) / 2;
      e.style.fontSize = mid + "px";
      if (e.scrollHeight <= H && e.scrollWidth <= W + 1) lo = mid;
      else hi = mid;
    }
    e.style.fontSize = Math.floor(lo) + "px";
  }, []);

  const schedule = useCallback(() => {
    cancelAnimationFrame(raf.current);
    raf.current = requestAnimationFrame(fit);
  }, [fit]);

  // keep the DOM text in sync unless the user is typing
  useLayoutEffect(() => {
    if (ed.current && !editing.current && ed.current.innerText !== content) {
      ed.current.innerText = content;
    }
    fit();
  }, [content, fit]);

  // weight drags: only refit right away if the text overflows, otherwise once it settles
  const settle = useRef(0);
  useLayoutEffect(() => {
    const b = box.current;
    const e = ed.current;
    if (b && e && (e.scrollHeight > b.clientHeight || e.scrollWidth > b.clientWidth + 1)) fit();
    window.clearTimeout(settle.current);
    settle.current = window.setTimeout(fit, 180);
    return () => window.clearTimeout(settle.current);
  }, [weight, fit]);

  useLayoutEffect(() => {
    fit();
  }, [family.key, fit]);

  useEffect(() => {
    const ro = new ResizeObserver(schedule);
    if (box.current) ro.observe(box.current);
    document.fonts?.ready.then(schedule);
    return () => ro.disconnect();
  }, [schedule]);

  const shuffle = () => {
    onText(null);
    setSampleIdx((i) => i + 1);
  };

  return (
    <div className="typeview">
      <div ref={box} className="typeview-box">
        <div
          ref={ed}
          className="specimen"
          contentEditable
          suppressContentEditableWarning
          spellCheck={false}
          aria-label="Editable sample text"
          style={{ fontFamily: `"${family.name}"`, fontWeight: weight }}
          onFocus={() => (editing.current = true)}
          onBlur={() => {
            editing.current = false;
            if (!ed.current?.innerText.trim()) onText(null);
          }}
          onInput={() => {
            const t = ed.current?.innerText ?? "";
            onText(t.trim() ? t : null);
            schedule();
          }}
        />
      </div>
      <div className="typeview-hint">
        <span>Click the text to type your own</span>
        <button className="link-btn" onClick={shuffle}>
          <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
            <path d="M2.5 8a5.5 5.5 0 0 1 9.6-3.7M13.5 8a5.5 5.5 0 0 1-9.6 3.7M12.5 1.8v2.8H9.7M3.5 14.2v-2.8h2.8" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          New sample
        </button>
      </div>
    </div>
  );
}
