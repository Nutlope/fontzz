import { useEffect, useRef, useState } from "react";
import { Family } from "../data";

interface Props {
  family: Family;
  weight: number;
}

const W = 1040;
const H = 520;
const BARS = [38, 52, 44, 61, 58, 72, 66, 80, 74, 91, 86, 100];
const ROWS: [string, string, string, string][] = [
  ["Invoice 2041 paid", "Northwind Labs", "$1,280.00", "2m"],
  ["New seat added", "Atlas Studio", "$48.00", "14m"],
  ["Plan upgraded to Team", "Kestrel Health", "$640.00", "1h"],
  ["Refund issued", "Juniper & Co", "-$96.00", "3h"],
];

/** A small product dashboard set entirely in the family, scaled to fit. */
export default function InterfaceView({ family, weight }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      setScale(Math.min(el.clientWidth / W, el.clientHeight / H, 1.25));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const hw = { fontWeight: weight };
  return (
    <div ref={ref} className="uiview">
      <div className="ui" style={{ fontFamily: `"${family.name}"`, width: W, height: H, transform: `scale(${scale})` }}>
        <aside className="ui-side">
          <div className="ui-brand">
            <span className="ui-logo" />
            <span style={hw}>Lumen</span>
          </div>
          <nav className="ui-nav">
            {["Overview", "Projects", "Customers", "Reports", "Settings"].map((n, i) => (
              <span key={n} className={"ui-nav-item" + (i === 0 ? " on" : "")}>
                <span className="ui-nav-dot" />
                {n}
              </span>
            ))}
          </nav>
          <div className="ui-user">
            <span className="ui-avatar">AK</span>
            <span>
              <b>Ada Kim</b>
              <small>Admin</small>
            </span>
          </div>
        </aside>
        <section className="ui-main">
          <div className="ui-top">
            <div>
              <h3 style={hw}>Good morning, Ada</h3>
              <p>Here is what changed since yesterday.</p>
            </div>
            <div className="ui-buttons">
              <span className="ui-btn">Export</span>
              <span className="ui-btn primary">New project</span>
            </div>
          </div>
          <div className="ui-stats">
            {[
              ["Revenue", "$48,210", "+12.4%", true],
              ["Active users", "12,904", "+3.1%", true],
              ["Churn", "1.82%", "-0.4%", false],
            ].map(([l, v, d, up]) => (
              <div key={l as string} className="ui-card">
                <span className="ui-label">{l}</span>
                <span className="ui-value" style={hw}>
                  {v}
                </span>
                <span className={"ui-delta" + (up ? " up" : "")}>{d} vs last week</span>
              </div>
            ))}
          </div>
          <div className="ui-bottom">
            <div className="ui-card ui-chart">
              <div className="ui-card-head">
                <span style={{ fontWeight: Math.max(500, Math.min(weight, 800)) }}>Weekly signups</span>
                <span className="ui-label">Last 12 weeks</span>
              </div>
              <div className="ui-bars">
                {BARS.map((b, i) => (
                  <span key={i} className={"ui-bar" + (i === BARS.length - 1 ? " hi" : "")} style={{ height: b + "%" }} />
                ))}
              </div>
            </div>
            <div className="ui-card ui-table">
              <div className="ui-card-head">
                <span style={{ fontWeight: Math.max(500, Math.min(weight, 800)) }}>Recent activity</span>
                <span className="ui-label">View all</span>
              </div>
              {ROWS.map((r) => (
                <div key={r[0]} className="ui-row">
                  <span>
                    <b>{r[0]}</b>
                    <small>{r[1]}</small>
                  </span>
                  <span className="ui-amt">{r[2]}</span>
                  <span className="ui-time">{r[3]}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
