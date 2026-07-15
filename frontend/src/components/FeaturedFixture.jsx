import Flag from "./Flag.jsx";
import Icon from "./Icon.jsx";
import { MLBar } from "./MatchLedger.jsx";

/**
 * The DRD's bracket graph assumes round-tree data from the backend.
 * The real /api/v1/fixtures payload is a flat match list with no
 * parent/child round linkage, so a true bracket can't be derived
 * without guessing. This renders the next live/upcoming match as a
 * single hero node instead, in the same wireframe node styling.
 */
export default function FeaturedFixture({ match }) {
  if (!match) {
    return (
      <div className="mx-auto my-8 flex w-80 items-center justify-center border border-border-wireframe bg-bg-card px-4 py-6 font-mono text-xs uppercase tracking-[0.15em] text-text-primary/50">
        No upcoming fixture found
      </div>
    );
  }

  const isFinal = match.score1 !== null && match.score1 !== undefined;

  return (
    <div className="relative mx-auto my-8 w-full max-w-md border border-border-wireframe bg-bg-card">
      <Icon
        id="icon-football-cyber"
        className="absolute -right-2 -top-2 h-5 w-5 text-accent-secondary"
        label={isFinal ? "Match completed" : "Upcoming match"}
      />
      <div className="flex items-center justify-between border-b border-border-wireframe px-4 py-1.5 font-mono text-[10px] uppercase tracking-[0.15em] text-text-primary/60">
        <span>{match.date} · {match.round}</span>
        <span className="flex items-center gap-1">
          <Icon id="icon-stadium" className="h-3 w-3" />
          {match.stadium}
        </span>
      </div>

      {[
        { team: match.team1, score: match.score1 },
        { team: match.team2, score: match.score2 },
      ].map((row, i) => (
        <div
          key={i}
          className={`flex items-center justify-between px-4 py-3 font-mono text-sm ${
            i === 0 ? "border-b border-border-wireframe" : ""
          }`}
        >
          <span className="flex items-center gap-2 uppercase tracking-wide">
            <Flag name={row.team} />
            {row.team}
          </span>
          <span className="tabular-nums font-bold">
            {isFinal ? row.score : "—"}
          </span>
        </div>
      ))}

      {match.probabilities && (
        <div className="border-t border-border-wireframe px-4 py-3">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-[0.15em] text-text-primary/60">
            ML Forecast
            {match.watchability_score != null && (
              <span className="float-right normal-case tracking-normal">
                Watchability {match.watchability_score}/10
              </span>
            )}
          </div>
          <MLBar probabilities={match.probabilities} />
        </div>
      )}
    </div>
  );
}
