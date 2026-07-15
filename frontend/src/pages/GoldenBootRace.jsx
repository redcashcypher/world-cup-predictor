import { Fragment, useEffect, useState } from "react";
import Cubes from "../components/Cubes.jsx";
import Flag from "../components/Flag.jsx";
import Icon from "../components/Icon.jsx";
import SystemAlert from "../components/SystemAlert.jsx";
import { fetchGoldenBoot } from "../lib/api.js";
import { withMinDelay } from "../lib/timing.js";

export default function GoldenBootRace() {
  const [players, setPlayers] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openRow, setOpenRow] = useState(null);

  useEffect(() => {
    let cancelled = false;
    withMinDelay(fetchGoldenBoot(), 2500)
      .then((payload) => {
        if (cancelled) return;
        setPlayers(payload.data ?? []);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <Cubes label="Loading Golden Boot" />;
  }

  return (
    <div className="flex flex-col">
      <h1 className="px-6 pt-8 text-center font-mono text-sm font-bold uppercase tracking-[0.3em]">
        Golden Boot Race
      </h1>

      {error && <SystemAlert message={error} />}

      {players && players.length > 0 && (
        <table className="mt-8 w-full border-t border-border-wireframe font-mono text-xs">
          <thead>
            <tr className="border-b border-border-wireframe text-left uppercase tracking-[0.15em]">
              <th className="px-4 py-2 font-normal">Rank</th>
              <th className="px-4 py-2 font-normal">Player</th>
              <th className="px-4 py-2 font-normal">Team</th>
              <th className="px-4 py-2 font-normal">Goals</th>
              <th className="px-4 py-2 font-normal">Media</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p, i) => {
              const isOpen = openRow === p.rank;
              const isLeader = p.rank <= 3;
              return (
                <Fragment key={p.rank}>
                  <tr
                    className={`border-b border-border-wireframe/50 ${
                      isLeader ? "bg-accent-primary/25" : i % 2 === 0 ? "bg-bg-card" : ""
                    }`}
                  >
                    <td className="px-4 py-2 tabular-nums">
                      <span
                        className={
                          isLeader
                            ? "bg-accent-primary px-1.5 py-0.5 font-bold text-text-primary"
                            : ""
                        }
                      >
                        #{p.rank}
                      </span>
                    </td>
                    <td className="px-4 py-2 normal-case tracking-normal">
                      <span className="flex items-center gap-2">
                        <Icon id="icon-shirt" className="h-3.5 w-3.5" />
                        {p.player}
                        {p.penalties > 0 && (
                          <span className="text-text-primary/40">
                            ({p.penalties} PK)
                          </span>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-2 normal-case tracking-normal">
                      <span className="flex items-center gap-2">
                        <Flag name={p.team} />
                        {p.team}
                      </span>
                    </td>
                    <td className="px-4 py-2 tabular-nums">{p.goals}</td>
                    <td className="px-4 py-2">
                      <button
                        onClick={() => setOpenRow(isOpen ? null : p.rank)}
                        className="border border-border-wireframe bg-bg-card px-2 py-1 uppercase tracking-[0.1em] hover:bg-accent-primary"
                      >
                        {isOpen ? "Close" : "Media"}
                      </button>
                    </td>
                  </tr>
                  {isOpen && (
                    <tr className="border-b border-border-wireframe/50 bg-bg-card">
                      <td colSpan={5} className="px-4 py-4">
                        <div className="flex h-32 w-full max-w-sm items-center justify-center border border-border-wireframe bg-bg-global">
                          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-primary/50">
                            {p.mediaUrl ?? "No media asset returned by API"}
                          </span>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      )}

      {players && players.length === 0 && !error && (
        <p className="px-6 py-8 text-center font-mono text-xs uppercase tracking-[0.15em] text-text-primary/50">
          No Golden Boot standings returned by the API.
        </p>
      )}
    </div>
  );
}
