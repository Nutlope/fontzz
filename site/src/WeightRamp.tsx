import { useRef } from "react";
import { Family, WEIGHTS, weightName } from "./data";

interface Props {
  family: Family;
  weight: number;
  onWeight: (w: number) => void;
}

/** Nine weights that double as a slider: drag across them for any value. */
export default function WeightRamp({ family, weight, onWeight }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const at = (clientX: number, snap: boolean) => {
    const r = ref.current!.getBoundingClientRect();
    const cell = r.width / 9;
    const x = Math.min(r.width - cell / 2, Math.max(cell / 2, clientX - r.left));
    const w = 100 + ((x - cell / 2) / (r.width - cell)) * 800;
    onWeight(snap ? Math.round(w / 100) * 100 : Math.round(w));
  };

  const pct = ((weight - 100) / 800) * (100 - 100 / 9) + 50 / 9;
  const nearest = Math.round(weight / 100) * 100;

  return (
    <div className="ramp-wrap">
      <div className="ramp-label">
        <span className="ramp-name">{weightName(weight)}</span>
        <span className="ramp-num">{weight}</span>
      </div>
      <div
        ref={ref}
        className="ramp"
        role="slider"
        tabIndex={0}
        aria-label="Weight"
        aria-valuemin={100}
        aria-valuemax={900}
        aria-valuenow={weight}
        aria-valuetext={`${weightName(weight)} ${weight}`}
        style={{ fontFamily: `"${family.name}"` }}
        onPointerDown={(e) => {
          dragging.current = true;
          (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
          at(e.clientX, false);
        }}
        onPointerMove={(e) => dragging.current && at(e.clientX, false)}
        onPointerUp={(e) => {
          if (dragging.current) at(e.clientX, false);
          dragging.current = false;
        }}
        onPointerCancel={() => (dragging.current = false)}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft" || e.key === "ArrowDown") {
            onWeight(Math.max(100, weight - (e.shiftKey ? 10 : 100)));
            e.preventDefault();
            e.stopPropagation();
          } else if (e.key === "ArrowRight" || e.key === "ArrowUp") {
            onWeight(Math.min(900, weight + (e.shiftKey ? 10 : 100)));
            e.preventDefault();
            e.stopPropagation();
          }
        }}
      >
        {WEIGHTS.map(([w, n]) => (
          <span
            key={w}
            className={"ramp-cell" + (w === nearest ? " near" : "")}
            style={{ fontWeight: w }}
            title={`${n} ${w}`}
            onDoubleClick={() => onWeight(w)}
          >
            Aa
          </span>
        ))}
        <span className="ramp-thumb" style={{ left: `${pct}%` }} />
      </div>
    </div>
  );
}
