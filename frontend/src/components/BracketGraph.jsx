import Flag from "./Flag.jsx";

const NODE_W = 220;
const NODE_H = 84;
const ROW_GAP = 20;
const COL_GAP = 56;

function winnerOf(match) {
  if (match.score1 == null || match.score2 == null) return null;
  if (match.score1 === match.score2) return null;
  return match.score1 > match.score2 ? match.team1 : match.team2;
}

/** Recursively derive each round's vertical center positions from round 0. */
function computeLayout(rounds) {
  const centers = [];
  const n0 = rounds[0].matches.length;
  centers[0] = Array.from(
    { length: n0 },
    (_, i) => i * (NODE_H + ROW_GAP) + NODE_H / 2
  );
  for (let r = 1; r < rounds.length; r++) {
    const prev = centers[r - 1];
    centers[r] = rounds[r].matches.map((_, i) => (prev[2 * i] + prev[2 * i + 1]) / 2);
  }
  const totalHeight = n0 * NODE_H + (n0 - 1) * ROW_GAP;
  return { centers, totalHeight };
}

export default function BracketGraph({ rounds }) {
  if (!rounds || rounds.length === 0) return null;

  const sizesValid = rounds.every(
    (round, r) => r === 0 || round.matches.length === rounds[r - 1].matches.length / 2
  );
  if (!sizesValid) {
    return (
      <div className="mx-6 my-4 border border-accent-secondary bg-bg-card px-4 py-3 font-mono text-xs uppercase tracking-[0.1em] text-accent-secondary">
        Bracket data malformed: each round must have exactly half the
        matches of the previous round, in bracket-position order.
      </div>
    );
  }

  const { centers, totalHeight } = computeLayout(rounds);
  const totalWidth = rounds.length * NODE_W + (rounds.length - 1) * COL_GAP;

  return (
    <div className="overflow-x-auto px-6 py-8">
      <div
        className="relative mx-auto"
        style={{ width: totalWidth, height: totalHeight }}
      >
        {/* Connector lines */}
        <svg
          className="pointer-events-none absolute inset-0"
          width={totalWidth}
          height={totalHeight}
        >
          {rounds.slice(0, -1).map((round, r) =>
            round.matches.map((match, i) => {
              const parentIdx = Math.floor(i / 2);
              const isPairSecond = i % 2 === 1;
              if (!isPairSecond) return null;

              const y1 = centers[r][i - 1];
              const y2 = centers[r][i];
              const yParent = centers[r + 1][parentIdx];
              const xRight = r * (NODE_W + COL_GAP) + NODE_W;
              const xMid = xRight + COL_GAP / 2;
              const xNext = xRight + COL_GAP;

              const w1 = winnerOf(round.matches[i - 1]);
              const w2 = winnerOf(match);
              const nextMatch = rounds[r + 1].matches[parentIdx];
              const highlight1 =
                w1 && nextMatch && (nextMatch.team1 === w1 || nextMatch.team2 === w1);
              const highlight2 =
                w2 && nextMatch && (nextMatch.team1 === w2 || nextMatch.team2 === w2);

              const stroke = "var(--color-border-wireframe)";
              const strokeWin = "var(--color-accent-primary)";

              return (
                <g key={`${r}-${i}`}>
                  <line x1={xRight} y1={y1} x2={xMid} y2={y1} stroke={highlight1 ? strokeWin : stroke} strokeWidth={1.5} />
                  <line x1={xRight} y1={y2} x2={xMid} y2={y2} stroke={highlight2 ? strokeWin : stroke} strokeWidth={1.5} />
                  <line x1={xMid} y1={y1} x2={xMid} y2={y2} stroke={stroke} strokeWidth={1.5} />
                  <line x1={xMid} y1={yParent} x2={xNext} y2={yParent} stroke={stroke} strokeWidth={1.5} />
                </g>
              );
            })
          )}
        </svg>

        {/* Round labels */}
        {rounds.map((round, r) => (
          <span
            key={round.round}
            className="absolute top-[-28px] font-mono text-[10px] font-bold uppercase tracking-[0.15em] text-text-primary/70"
            style={{ left: r * (NODE_W + COL_GAP), width: NODE_W, textAlign: "center" }}
          >
            {round.round}
          </span>
        ))}

        {/* Match nodes */}
        {rounds.map((round, r) =>
          round.matches.map((match, i) => {
            const isFinalRound = r === rounds.length - 1;
            const winner = winnerOf(match);
            return (
              <div
                key={`${r}-${i}`}
                className="absolute flex flex-col border border-border-wireframe bg-bg-card"
                style={{
                  left: r * (NODE_W + COL_GAP),
                  top: centers[r][i] - NODE_H / 2,
                  width: NODE_W,
                  height: NODE_H,
                }}
              >
                {[match.team1, match.team2].map((team, ti) => {
                  const score = ti === 0 ? match.score1 : match.score2;
                  const isWinner = winner && team === winner;
                  return (
                    <div
                      key={ti}
                      className={`flex flex-1 items-center justify-between px-2 font-mono text-[11px] ${
                        ti === 0 ? "border-b border-border-wireframe" : ""
                      }`}
                      style={{
                        backgroundColor: isWinner ? "var(--color-accent-primary)" : "transparent",
                      }}
                    >
                      <span className="flex min-w-0 items-center gap-1.5 truncate uppercase tracking-wide text-text-primary">
                        <Flag name={team} className="h-3 w-4" />
                        <span className="truncate">{team ?? "TBD"}</span>
                      </span>
                      <span className="pl-1 font-bold tabular-nums text-text-primary">
                        {score ?? "–"}
                      </span>
                    </div>
                  );
                })}

                {isFinalRound && (
                  <span
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-2 py-0.5 font-mono text-[9px] font-bold uppercase tracking-[0.15em] text-bg-card"
                    style={{ backgroundColor: "var(--color-accent-secondary)" }}
                  >
                    Final
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
