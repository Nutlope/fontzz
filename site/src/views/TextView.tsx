import { Family } from "../data";

interface Props {
  family: Family;
  weight: number;
}

const SIZES = [40, 28, 20, 16, 14, 12];

export default function TextView({ family, weight }: Props) {
  const ff = { fontFamily: `"${family.name}"` };
  return (
    <div className="textview" style={ff}>
      <article className="tv-article">
        <h2 className="tv-headline" style={{ fontWeight: weight }}>
          {family.headline}
        </h2>
        <p className="tv-lead">{family.blurb}</p>
        <p className="tv-body">
          {family.name} is drawn entirely in code. Every curve, junction and terminal comes from a small set of
          parameters, so all nine weights share one skeleton and interpolate without seams. Spacing and kerning
          were tuned for screens first, which means it holds up in a 13 pixel table cell as well as in a hero
          headline.
        </p>
        <p className="tv-caption" style={{ fontWeight: Math.min(900, Math.max(400, weight)) }}>
          Set in {family.name} at weight {weight}, body at 400.
        </p>
      </article>
      <div className="tv-waterfall" aria-label="Size waterfall">
        {SIZES.map((s) => (
          <div key={s} className="tv-row">
            <span className="tv-size">{s}</span>
            <span className="tv-line" style={{ fontSize: s, fontWeight: weight }}>
              The five boxing wizards jump quickly
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
