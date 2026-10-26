import { AUTHORS, Family } from "./data";

/** "Built by" line; the names take on the family in focus, like the wordmark. */
export default function Credit({ family, className = "" }: { family: Family; className?: string }) {
  return (
    <p className={"credit " + className}>
      Built by{" "}
      {AUTHORS.map(([name, href], i) => (
        <span key={name}>
          {i > 0 && " and "}
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontFamily: `"${family.name}"`, "--accent": `var(--accent-${family.key})` } as React.CSSProperties}
          >
            {name}
          </a>
        </span>
      ))}
    </p>
  );
}
