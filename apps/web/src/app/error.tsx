"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div style={{ padding: 32, fontFamily: "monospace", background: "#1a1a2e", color: "#e0e0e0", minHeight: "100vh" }}>
      <h2 style={{ color: "#ff6b6b", marginBottom: 16 }}>⚠ Client Error</h2>
      <pre style={{ background: "#0d0d1a", padding: 16, borderRadius: 8, overflow: "auto", color: "#ff6b6b" }}>
        {error.message}
      </pre>
      <pre style={{ background: "#0d0d1a", padding: 16, borderRadius: 8, marginTop: 16, overflow: "auto", fontSize: 12, color: "#aaa" }}>
        {error.stack}
      </pre>
      <button onClick={reset} style={{ marginTop: 16, padding: "8px 16px", background: "#4a9eff", border: "none", borderRadius: 4, color: "white", cursor: "pointer" }}>
        Retry
      </button>
    </div>
  );
}
