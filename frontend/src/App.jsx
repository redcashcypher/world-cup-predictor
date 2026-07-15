import { Routes, Route } from "react-router-dom";
import Header from "./components/Header.jsx";
import LiveBracket from "./pages/LiveBracket.jsx";
import GoldenBootRace from "./pages/GoldenBootRace.jsx";

export default function App() {
  return (
    <div className="wireframe-grid min-h-screen w-full bg-bg-global text-text-primary">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<LiveBracket />} />
          <Route path="/golden-boot" element={<GoldenBootRace />} />
        </Routes>
      </main>
    </div>
  );
}
