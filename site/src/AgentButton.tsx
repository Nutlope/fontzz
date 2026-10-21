import { useEffect, useRef, useState } from "react";

interface Props {
  prompt: () => string;
  className: string;
  notify: (msg: string) => void;
}

async function writeClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // older browsers and some embedded views block the async API
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;opacity:0;pointer-events:none";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    ta.remove();
    if (!ok) throw new Error("copy blocked");
  }
}

/** Copies an install prompt for an AI coding agent, with inline confirmation. */
export default function AgentButton({ prompt, className, notify }: Props) {
  const [done, setDone] = useState(false);
  const timer = useRef<number>();
  useEffect(() => () => window.clearTimeout(timer.current), []);

  const copy = async () => {
    try {
      await writeClipboard(prompt());
      setDone(true);
      notify("Prompt copied. Paste it into your coding agent.");
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setDone(false), 1800);
    } catch {
      notify("Copy failed, your browser blocked the clipboard");
    }
  };

  return (
    <button
      className={className + (done ? " is-done" : "")}
      onClick={copy}
      title="Copy a prompt that tells your coding agent how to install this"
    >
      <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
        {done ? (
          <path d="M3.5 8.5 6.5 11.5 12.5 4.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        ) : (
          <path d="M8 1.75c.4 3.1 1.9 4.85 5.25 6.25C9.9 9.4 8.4 11.15 8 14.25 7.6 11.15 6.1 9.4 2.75 8 6.1 6.6 7.6 4.85 8 1.75Z" fill="currentColor" />
        )}
      </svg>
      <span className="swap">
        <span aria-hidden={done}>Give to your agent</span>
        <span aria-hidden={!done}>Copied</span>
      </span>
    </button>
  );
}
