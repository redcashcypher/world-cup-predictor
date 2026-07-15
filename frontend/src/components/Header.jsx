import { NavLink } from "react-router-dom";
import Icon from "./Icon.jsx";

const navLinkClass = ({ isActive }) =>
  [
    "font-mono text-xs uppercase tracking-[0.15em] px-3 py-1.5 border border-border-wireframe",
    isActive
      ? "bg-text-primary text-bg-global"
      : "bg-bg-card text-text-primary hover:bg-accent-primary",
  ].join(" ");

export default function Header() {
  return (
    <header className="flex flex-row items-center justify-between border-b border-border-wireframe bg-bg-global px-5 py-3">
      <div className="flex items-center gap-2">
        <Icon id="icon-fifa" className="h-5 w-5 text-text-primary" />
        <span className="font-mono text-sm font-bold uppercase tracking-[0.2em]">
          World Cup Predictor
        </span>
      </div>
      <nav className="flex items-center gap-2">
        <NavLink to="/" end className={navLinkClass}>
          Live Bracket
        </NavLink>
        <NavLink to="/golden-boot" className={navLinkClass}>
          Golden Boot Race
        </NavLink>
      </nav>
    </header>
  );
}
