import { useEffect, useState } from "react";
import { Family, REPO, REPO_URL } from "./data";

const CACHE = "fontzz-stars";
const TTL = 60 * 60 * 1000; // the unauthenticated API allows 60 calls an hour, so ask at most once

function readCache(): number | null {
  try {
    const c = JSON.parse(localStorage.getItem(CACHE) || "null");
    if (c && Date.now() - c.t < TTL && typeof c.n === "number") return c.n;
  } catch {
    /* storage unavailable */
  }
  return null;
}

const compact = (n: number) =>
  n < 1000 ? String(n) : n < 10000 ? (n / 1000).toFixed(1).replace(/\.0$/, "") + "k" : Math.round(n / 1000) + "k";

/** Star count on GitHub, set in whichever family is in focus, like the wordmark. */
export default function GitHubStars({ family }: { family: Family }) {
  const [stars, setStars] = useState<number | null>(readCache);

  useEffect(() => {
    if (stars !== null) return;
    const ctl = new AbortController();
    fetch(`https://api.github.com/repos/${REPO}`, { signal: ctl.signal, headers: { Accept: "application/vnd.github+json" } })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (typeof d?.stargazers_count !== "number") return;
        setStars(d.stargazers_count);
        try {
          localStorage.setItem(CACHE, JSON.stringify({ n: d.stargazers_count, t: Date.now() }));
        } catch {
          /* storage unavailable */
        }
      })
      .catch(() => {});
    return () => ctl.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <a
      className="gh"
      href={REPO_URL}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={stars === null ? "Star fontzz on GitHub" : `Star fontzz on GitHub, ${stars} stars`}
      title="Star fontzz on GitHub"
      style={{ "--accent": `var(--accent-${family.key})` } as React.CSSProperties}
    >
      <svg className="gh-mark" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
        <path
          fill="currentColor"
          d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8Z"
        />
      </svg>
      <span className="gh-star">
        <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
          <path
            d="M8 1.6l1.93 3.92 4.32.63-3.13 3.05.74 4.3L8 11.47 4.14 13.5l.74-4.3L1.75 6.15l4.32-.63L8 1.6Z"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </svg>
        <span className="gh-count" style={{ fontFamily: `"${family.name}"` }}>
          {stars === null ? "Star" : compact(stars)}
        </span>
      </span>
    </a>
  );
}
