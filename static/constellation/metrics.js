// ─────────────────────────────────────────────
// 🌌 Mute Logic — Production Semantic Metrics Module
// ─────────────────────────────────────────────

// Compute semantic metrics from conversation turns via the Flask backend.
export async function computeSemanticMetrics(turns) {
  console.log("🧠 Starting expanded semantic analysis for", turns.length, "turns...");

  // Use same origin as the hosted Flask app
  const endpoint = window.location.origin + "/analyze";

  const payload = {
    turns: turns.map((t) => ({
      id: t[0],
      speaker: t[1],
      text: t[2],
    })),
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    console.error("❌ Error from analysis endpoint:", response.status);
    return [];
  }

  const data = await response.json();
  const analysis = data.analysis;

  if (!analysis || analysis.length === 0) {
    console.warn("⚠️ No analysis data returned from server.");
    return [];
  }

  // Log a preview for sanity check
  console.groupCollapsed("🧩 Semantic Metrics Preview");
  console.table(
    analysis.slice(0, 5).map((a) => ({
      id: a.id,
      speaker: a.speaker,
      coherence: a.coherence.toFixed(2),
      drift: a.drift.toFixed(2),
      entropy: a.entropy.toFixed(2),
      resonance: a.resonance.toFixed(2),
      volatility: a.volatility.toFixed(2),
      novelty: a.novelty.toFixed(2),
      cluster: a.cluster,
    }))
  );
  console.groupEnd();

  return analysis;
}
