import React, { useState, useEffect } from "react";
import { Trophy, TrendingUp, ChevronDown, Lightbulb, Swords } from "lucide-react";

const COLORS = {
  pitchDeep: "#0A2F22",
  pitchMid: "#12402C",
  pitchLine: "#1E5A3E",
  gold: "#F4B942",
  goldDim: "#8A6A28",
  chalk: "#F5F1E6",
  chalkDim: "#A9BDB0",
  red: "#E4483A",
};

function HypeLights({ score }) {
  const lit = Math.round(score / 20);
  return (
    <div style={{ display: "flex", gap: 4 }}>
      {[0, 1, 2, 3, 4].map((i) => (
        <Lightbulb
          key={i}
          size={16}
          style={{
            color: i < lit ? COLORS.gold : COLORS.pitchLine,
            fill: i < lit ? COLORS.gold : "transparent",
          }}
        />
      ))}
    </div>
  );
}

function ProbBar({ probs, home, away }) {
  return (
    <div>
      <div style={{ display: "flex", height: 10, borderRadius: 5, overflow: "hidden", background: COLORS.pitchLine }}>
        <div style={{ width: `${probs.home_win}%`, background: COLORS.gold }} />
        <div style={{ width: `${probs.draw}%`, background: COLORS.chalkDim }} />
        <div style={{ width: `${probs.away_win}%`, background: COLORS.red }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: COLORS.chalkDim }}>
        <span style={{ color: COLORS.gold }}>{home} {probs.home_win}%</span>
        <span>Draw {probs.draw}%</span>
        <span style={{ color: COLORS.red }}>{probs.away_win}% {away}</span>
      </div>
    </div>
  );
}

function MatchCard({ fixture, expanded, onToggle }) {
  return (
    <div
      style={{
        background: COLORS.pitchMid,
        border: `0.5px solid ${COLORS.pitchLine}`,
        borderRadius: 10,
        padding: "16px 18px",
        cursor: "pointer",
      }}
      onClick={onToggle}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
            <span style={{ fontSize: 10, color: COLORS.chalkDim, textTransform: "uppercase", letterSpacing: 1 }}>
              {fixture.stage}
            </span>
            {fixture.rivalry && (
              <span style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 10, color: COLORS.red }}>
                <Swords size={11} /> Rivalry
              </span>
            )}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <HypeLights score={fixture.hype_score} />
          <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: COLORS.gold, marginTop: 4 }}>
            Hype {fixture.hype_score}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "16px 0" }}>
        <span style={{ fontFamily: "'Anton', sans-serif", fontSize: 22, color: COLORS.chalk }}>{fixture.home}</span>
        <span style={{ fontFamily: "'Anton', sans-serif", fontSize: 18, color: COLORS.chalkDim }}>VS</span>
        <span style={{ fontFamily: "'Anton', sans-serif", fontSize: 22, color: COLORS.chalk }}>{fixture.away}</span>
      </div>

      <ProbBar probs={fixture.probabilities} home={fixture.home} away={fixture.away} />

      <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
        <ChevronDown size={14} style={{ color: COLORS.chalkDim, transform: expanded ? "rotate(180deg)" : "none", transition: "transform 0.15s" }} />
      </div>
    </div>
  );
}

export default function App() {
  const [fixtures, setFixtures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    // This is where your React app talks to your FastAPI backend
    fetch("http://127.0.0.1:8000/fixtures")
      .then((res) => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
      })
      .then((data) => {
        setFixtures(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div
      style={{
        background: COLORS.pitchDeep,
        minHeight: "100vh",
        padding: "28px 20px 40px",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
      `}</style>
      
      <div style={{ maxWidth: 640, margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <Trophy size={18} style={{ color: COLORS.gold }} />
          <span style={{ fontSize: 11, color: COLORS.goldDim, letterSpacing: 2, textTransform: "uppercase" }}>
            Watch party predictor · LIVE API
          </span>
        </div>
        <h1 style={{ fontFamily: "'Anton', sans-serif", fontSize: 34, color: COLORS.chalk, margin: "0 0 4px" }}>
          Live Fixture Hype Rankings
        </h1>
        <p style={{ fontSize: 13, color: COLORS.chalkDim, margin: "0 0 24px" }}>
          Powered by FastAPI & scikit-learn on historical World Cup data.
        </p>

        {loading && <div style={{ color: COLORS.chalk }}>Connecting to ML Backend...</div>}
        
        {error && (
          <div style={{ color: COLORS.red, background: COLORS.pitchMid, padding: 16, borderRadius: 8 }}>
            <strong>Connection Failed:</strong> {error} <br/>
            (Is your uvicorn Python server actively running in the other terminal?)
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {!loading && !error && fixtures.map((f) => (
            <MatchCard
              key={f.id}
              fixture={f}
              expanded={expandedId === f.id}
              onToggle={() => setExpandedId(expandedId === f.id ? null : f.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}