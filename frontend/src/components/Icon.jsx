/**
 * Strict sprite-sheet icon usage per DRD Section 6.
 * Standalone <img> tags for UI icons are prohibited — always
 * reference /icons.svg via <use>. fill-current / text-current
 * lets the host element's Tailwind color classes drive the icon color.
 */
export default function Icon({ id, className = "h-4 w-4", label }) {
  return (
    <svg
      className={`fill-current text-current ${className}`}
      aria-hidden={label ? undefined : true}
      role={label ? "img" : undefined}
      aria-label={label}
    >
      <use href={`/icons.svg#${id}`} />
    </svg>
  );
}
