export default function SystemAlert({ message }) {
  return (
    <div className="mx-6 my-4 border border-accent-secondary bg-bg-card px-4 py-3 font-mono text-xs uppercase tracking-[0.1em] text-accent-secondary">
      <strong className="mr-2">System Alert:</strong>
      {message}
    </div>
  );
}
