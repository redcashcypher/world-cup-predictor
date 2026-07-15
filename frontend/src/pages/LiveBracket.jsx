import { useEffect, useState } from "react";
import BracketGraph from "../components/BracketGraph.jsx";
import Cubes from "../components/Cubes.jsx";
import FixtureCard from "../components/FixtureCard.jsx";
import MatchLedger from "../components/MatchLedger.jsx";
import SystemAlert from "../components/SystemAlert.jsx";
import { fetchBracket, fetchFixtures } from "../lib/api.js";
import { withMinDelay } from "../lib/timing.js";

export default function LiveBracket() {
  const [matches, setMatches] = useState(null);
  const [bracket, setBracket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    withMinDelay(
      Promise.all([fetchFixtures(), fetchBracket()]),
      2500
    )
      .then(([fixturesPayload, bracketPayload]) => {
        if (cancelled) return;
        setMatches(fixturesPayload.data ?? []);
        setBracket(bracketPayload?.rounds ?? null);
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
    return <Cubes label="Loading Fixtures" />;
  }

  return (
    <div className="flex flex-col">
      {error && <SystemAlert message={error} />}

      {bracket && bracket.length > 0 ? (
        <section className="border-b border-border-wireframe">
          <h1 className="pt-8 text-center font-mono text-sm font-bold uppercase tracking-[0.3em]">
            Live Bracket
          </h1>
          <BracketGraph rounds={bracket} />
        </section>
      ) : (
        <section className="border-b border-border-wireframe px-6 py-6">
          <p className="text-center font-mono text-[11px] uppercase tracking-[0.15em] text-text-primary/50">
            Bracket unlocks once the knockout stage begins
          </p>
        </section>
      )}

      <section className="px-6 pt-8">
        <h2 className="mb-1 font-mono text-sm font-bold uppercase tracking-[0.3em] text-text-primary">
          Upcoming &amp; Live Fixtures
        </h2>
        <p className="mb-4 font-mono text-[11px] uppercase tracking-[0.15em] text-text-primary/50">
          Machine learning win probabilities &amp; tournament telemetry
        </p>
        <div className="mb-6 h-[3px] w-full bg-border-wireframe" />

        {matches && matches.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 pb-8 sm:grid-cols-2 lg:grid-cols-3">
            {[...matches]
              .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
              .map((m, i) => (
                <FixtureCard key={i} match={m} />
              ))}
          </div>
        ) : (
          !error && (
            <p className="pb-8 font-mono text-xs uppercase tracking-[0.15em] text-text-primary/50">
              No fixtures returned by the API.
            </p>
          )
        )}
      </section>

      <section className="border-t border-border-wireframe">
        <h2 className="px-6 py-4 font-mono text-[11px] font-bold uppercase tracking-[0.2em]">
          Match Ledger
        </h2>
        {matches && matches.length > 0 && <MatchLedger matches={matches} />}
      </section>
    </div>
  );
}
