import Flag from "./Flag.jsx";
import Icon from "./Icon.jsx";

/**
 * Consumes the real /api/v1/fixtures schema:
 * { date, round, stadium, team1, team2, score1, score2,
 *   probabilities?: { team1_win, draw, team2_win }, watchability_score? }
 */
export default function MatchLedger({ matches }) {
  const sorted = [...matches].sort((a, b) => (a.date < b.date ? 1 : -1));

  return (
    <table className="w-full border-t border-border-wireframe font-mono text-xs">
      <thead>
        <tr className="border-b border-border-wireframe bg-bg-card text-left uppercase tracking-[0.15em] text-text-primary">
          <th className="px-4 py-2 font-normal">Matchup</th>
          <th className="px-4 py-2 font-normal">Scoreline</th>
          <th className="px-4 py-2 font-normal">Venue</th>
          <th className="px-4 py-2 font-normal">ML Win Probability</th>
          <th className="px-4 py-2 font-normal">Watchability</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((m, i) => {
          const probabilities = m.probabilities ?? m.probability ?? null;
          const watchability =
            m.watchability_score ?? m.watchabilityScore ?? m.watchability ?? null;
          return (
          <tr
            key={i}
            className={`border-b border-border-wireframe/50 ${
              i % 2 === 0 ? "bg-bg-card" : "bg-transparent"
            }`}
          >
            <td className="px-4 py-2">
              <span className="flex flex-col gap-0.5">
                <span className="flex items-center gap-2 uppercase tracking-wide">
                  <Flag name={m.team1} />
                  {m.team1}
                  <span className="text-text-primary/50">vs</span>
                  <Flag name={m.team2} />
                  {m.team2}
                </span>
                <span className="normal-case tracking-normal text-[10px] text-text-primary/50">
                  {m.date} · {m.round}
                </span>
              </span>
            </td>
            <td className="px-4 py-2 tabular-nums">
              {m.score1 !== null && m.score1 !== undefined
                ? `${m.score1} – ${m.score2}`
                : "—"}
            </td>
            <td className="px-4 py-2">
              <span className="flex items-center gap-1.5 normal-case tracking-normal text-text-primary/80">
                <Icon id="icon-stadium" className="h-3.5 w-3.5" />
                {m.stadium}
              </span>
            </td>
            <td className="px-4 py-2">
              {probabilities ? (
                <MLBar probabilities={probabilities} />
              ) : (
                <span className="text-text-primary/40">—</span>
              )}
            </td>
            <td className="px-4 py-2 tabular-nums">
              {watchability != null ? `${watchability}/10` : "—"}
            </td>
          </tr>
          );
        })}
      </tbody>
    </table>
  );
}

/** Tri-color ML telemetry bar using the strict Section 2 token mapping. */
export function MLBar({ probabilities }) {
  const { team1_win, draw, team2_win } = probabilities;
  return (
    <span className="flex flex-col gap-1">
      <span className="flex h-2 w-32 overflow-hidden border border-border-wireframe">
        <span style={{ width: `${team1_win}%`, backgroundColor: "var(--color-ml-win)" }} />
        <span style={{ width: `${draw}%`, backgroundColor: "var(--color-ml-draw)" }} />
        <span style={{ width: `${team2_win}%`, backgroundColor: "var(--color-ml-loss)" }} />
      </span>
      <span className="flex justify-between text-[10px] tabular-nums text-text-primary/70">
        <span>{team1_win}%</span>
        <span>D {draw}%</span>
        <span>{team2_win}%</span>
      </span>
    </span>
  );
}
