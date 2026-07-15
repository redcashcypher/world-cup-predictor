import { useEffect, useRef } from "react";
import gsap from "gsap";

/**
 * Loading screen adapted from the React Bits <Cubes /> component
 * (https://reactbits.dev/animations/cubes), re-themed to the
 * Broadcast Wireframe token set per DRD Section 5:
 *   faceColor    = var(--color-bg-global)   (hollow/wireframe look)
 *   borderStyle  = 1px solid var(--color-border-wireframe)
 *   rippleColor  = var(--color-accent-primary)
 *   shadow       = false, always
 */
const GRID_ROWS = 5;
const GRID_COLS = 8;

export default function Cubes({ label = "LOADING FIXTURES" }) {
  const gridRef = useRef(null);

  useEffect(() => {
    const cubes = gridRef.current?.querySelectorAll(".cube-face");
    if (!cubes || cubes.length === 0) return;

    const tl = gsap.timeline({ repeat: -1, repeatDelay: 0.4 });
    tl.to(cubes, {
      rotateX: 12,
      rotateY: -12,
      duration: 0.5,
      stagger: {
        each: 0.02,
        grid: [GRID_ROWS, GRID_COLS],
        from: "start",
      },
      ease: "power1.inOut",
    }).to(cubes, {
      rotateX: 0,
      rotateY: 0,
      duration: 0.5,
      stagger: {
        each: 0.02,
        grid: [GRID_ROWS, GRID_COLS],
        from: "start",
      },
      ease: "power1.inOut",
    });

    return () => tl.kill();
  }, []);

  const cells = Array.from({ length: GRID_ROWS * GRID_COLS });

  return (
    <div className="flex h-full min-h-[60vh] w-full flex-col items-center justify-center gap-6 bg-bg-global">
      <div
        ref={gridRef}
        className="grid gap-1"
        style={{
          gridTemplateColumns: `repeat(${GRID_COLS}, 1fr)`,
          perspective: "600px",
        }}
      >
        {cells.map((_, i) => (
          <div
            key={i}
            className="cube-face h-6 w-6"
            style={{
              backgroundColor: "var(--color-bg-global)",
              border: "1px solid var(--color-border-wireframe)",
              boxShadow: "none",
              borderRadius: 0,
            }}
          />
        ))}
      </div>
      <span className="font-mono text-[11px] uppercase tracking-[0.3em] text-text-primary/70">
        {label}
      </span>
    </div>
  );
}
