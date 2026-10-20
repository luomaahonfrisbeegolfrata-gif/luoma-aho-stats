// Cloudflare Worker: vieraskirjalomake -> GitHub Issue (odottaa hyväksyntää). Asetukset: ks. ANALYYSI.md
// Muuttujat: ALLOWED_ORIGIN (esim. https://luomaahonfrisbeegolfrata-gif.github.io), REPO (esim. omistaja/luoma-aho-stats), secret GITHUB_TOKEN
export default {
  async fetch(req, env) {
    const origin = req.headers.get("Origin") || "";
    const ok = origin === env.ALLOWED_ORIGIN;
    const cors = { "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN, "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin" };
    const reply = (status, message) => new Response(JSON.stringify({ ok: status === 200, message }), { status, headers: { ...cors, "Content-Type": "application/json" } });
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (req.method !== "POST" || !ok) return reply(403, "Ei sallittu");
    let b;
    try { b = await req.json(); } catch { return reply(400, "Virheellinen pyyntö"); }
    if (b.website) return reply(200, "OK"); // honeypot: botti saa "onnistumisen", mitään ei tallenneta
    const clean = (s, n) => String(s ?? "").replace(/`/g, "'").trim().slice(0, n);
    const name = clean(b.name, 30) || "Anonyymi", message = clean(b.message, 500), rating = Number(b.rating);
    if (message.length < 3 || !Number.isInteger(rating) || rating < 1 || rating > 5) return reply(400, "Tarkista viesti ja tähdet");
    const res = await fetch(`https://api.github.com/repos/${env.REPO}/issues`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.GITHUB_TOKEN}`, Accept: "application/vnd.github+json", "User-Agent": "luoma-aho-vieraskirja", "Content-Type": "application/json" },
      body: JSON.stringify({ title: `Vieraskirja: ${name.replace(/[\r\n]/g, " ")} (${rating}★)`, labels: ["vieraskirja"], body: "```json\n" + JSON.stringify({ name, message, rating }, null, 2) + "\n```" }),
    });
    return res.ok ? reply(200, "Kiitos!") : reply(502, "Tallennus epäonnistui");
  },
};
