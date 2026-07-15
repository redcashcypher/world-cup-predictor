import Flag from "./Flag.jsx";
import Icon from "./Icon.jsx";
import { MLBar } from "./MatchLedger.jsx";

/**
 * Structural pattern borrowed from the Uniswap Cup reference
 * (styles.refero.design/style/fabb51a0...): a black team-identity
 * box, a bold monospace hero score, and a filled stage-label tag —
 * but recolored strictly to the DRD Section 3 token table. No pink
 * anywhere; accent-secondary (#BD4444) takes the "stage tag" role,
 * accent-primary (#FFEA93) marks the live/winning state.
 */
export default function FixtureCard({ match }) {
  const isFinal = match.score1 !== null && match.score1 !== undefined;
  const isLive = match.status === "live";
  const team1Wins = isFinal && match.score1 > match.score2;
  const team2Wins = isFinal && match.score2 > match.score1;

  return (
    <div className="flex flex-col border border-border-wireframe bg-bg-card">
      {/* Meta row: date/round tag + venue */}
      <div className="flex items-center justify-between border-b border-border-wireframe px-3 py-2">
        <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.15em] text-text-primary/70">
          <span>{match.date}</span>
          <span
            className="px-1.5 py-0.5 font-bold text-bg-card"
            style={{
              backgroundColor: isLive
                ? "var(--color-accent-primary)"
                : "var(--color-accent-secondary)",
              color: isLive ? "var(--color-text-primary)" : "#ffffff",
            }}
          >
            {isLive ? "LIVE" : match.round}
          </span>
        </div>
        <span className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.1em] text-text-primary/60">
          <Icon id="icon-stadium" className="h-3 w-3" />
          {match.stadium}
        </span>
      </div>

      {/* Scoreboard unit */}
      <div className="flex items-center justify-between gap-3 px-4 py-4">
        <TeamIdentity name={match.team1} align="left" winner={team1Wins} />

        <div className="flex flex-col items-center">
          {isFinal ? (
            <span className="font-mono text-[28px] font-bold leading-none tracking-[-0.02em] text-text-primary">
              {match.score1}
              <span className="mx-1 text-text-primary/40">–</span>
              {match.score2}
            </span>
          ) : (
            <span className="font-mono text-lg font-bold tracking-[-0.02em] text-text-primary/50">
              VS
            </span>
          )}
        </div>

        <TeamIdentity name={match.team2} align="right" winner={team2Wins} />
      </div>

      {/* ML telemetry footer */}
      {match.probabilities && (
        <div className="border-t border-border-wireframe px-4 py-2.5">
          <div className="mb-1 flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.15em] text-text-primary/60">
            <span>ML Forecast</span>
            {match.watchability_score != null && (
              <span>Watchability {match.watchability_score}/10</span>
            )}
          </div>
          <MLBar probabilities={match.probabilities} />
        </div>
      )}
    </div>
  );
}

function TeamIdentity({ name, align, winner }) {
  return (
    <div
      className={`flex min-w-0 flex-1 items-center gap-2 ${
        align === "right" ? "flex-row-reverse text-right" : "text-left"
      }`}
    >
      <span
        className="flex h-7 w-7 shrink-0 items-center justify-center font-mono text-[10px] font-bold uppercase"
        style={{
          backgroundColor: winner
            ? "var(--color-accent-primary)"
            : "var(--color-text-primary)",
          color: winner ? "var(--color-text-primary)" : "#ffffff",
        }}
      >
        {(name || "?").slice(0, 1)}
      </span>
      <Flag name={name} />
      <span className="truncate font-sans text-xs font-semibold uppercase tracking-wide text-text-primary">
        {name}
      </span>
    </div>
  );
}
