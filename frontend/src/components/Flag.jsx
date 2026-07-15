import { useState } from "react";

/**
 * National flags render as native <img> to preserve their true color
 * palette (Section 7) — never inline SVG sprites like UI icons.
 * Falls back to a hairline initials box if the asset isn't present yet.
 */
export default function Flag({ code, name, className = "h-4 w-6" }) {
  const [broken, setBroken] = useState(!code);

  if (broken) {
    return (
      <span
        className={`inline-flex items-center justify-center border border-border-wireframe bg-bg-card font-mono text-[9px] uppercase leading-none ${className}`}
        title={name}
      >
        {(code || name || "?").slice(0, 2)}
      </span>
    );
  }

  return (
    <img
      src={`/flags/${code}.svg`}
      alt={name ? `${name} flag` : "flag"}
      className={`inline-block border border-border-wireframe object-cover ${className}`}
      onError={() => setBroken(true)}
    />
  );
}
