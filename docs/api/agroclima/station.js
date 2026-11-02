/**
 * Read-only Vercel Function proxy for public AgroClima station pages.
 * Only fixed upstream hosts and station-page paths are permitted.
 */
const ORIGIN = "https://agroclima.com";
const PATHS = ["/public/estacion.php", "/3/public/estacion.php"];
const MAX_HTML_BYTES = 2_000_000;
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Accept, Content-Type",
  "Access-Control-Max-Age": "86400",
  "Vary": "Origin"
};

function send(res, status, body) {
  res.status(status);
  for (const [key, value] of Object.entries(CORS)) res.setHeader(key, value);
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  return res.send(JSON.stringify(body));
}

module.exports = async function handler(req, res) {
  if (req.method === "OPTIONS") {
    res.status(204);
    for (const [key, value] of Object.entries(CORS)) res.setHeader(key, value);
    return res.end();
  }
  if (req.method !== "GET") return send(res, 405, { ok: false, error: "method_not_allowed" });

  const rawId = String(req.query?.id || "");
  if (!/^\d{1,4}$/.test(rawId) || Number(rawId) < 1 || Number(rawId) > 9999) {
    return send(res, 400, { ok: false, error: "invalid_station_id" });
  }

  let lastError = "station_page_unavailable";
  for (const path of PATHS) {
    const upstream = new URL(path, ORIGIN);
    upstream.searchParams.set("id", rawId);
    try {
      const response = await fetch(upstream.toString(), {
        method: "GET",
        redirect: "follow",
        signal: AbortSignal.timeout(15000),
        headers: {
          "Accept": "text/html,application/xhtml+xml",
          "User-Agent": "LaboratorioMeteorologicoNacional/1.2 (public station observation viewer)"
        }
      });
      if (!response.ok) {
        lastError = "upstream_http_" + response.status;
        continue;
      }
      const html = await response.text();
      if (!html || html.length < 250 || html.length > MAX_HTML_BYTES) {
        lastError = "upstream_html_invalid_or_too_large";
        continue;
      }
      const lower = html.toLowerCase();
      if (lower.includes("estacion no encontrada") || lower.includes("estación inexistente") || lower.includes("access denied")) {
        lastError = "station_not_available";
        continue;
      }
      return send(res, 200, {
        ok: true,
        provider: "AgroClima",
        station_id: Number(rawId),
        source_url: response.url || upstream.toString(),
        fetched_at: new Date().toISOString(),
        html
      });
    } catch (error) {
      lastError = error?.name === "TimeoutError" || error?.name === "AbortError"
        ? "upstream_timeout"
        : "upstream_fetch_failed";
    }
  }
  return send(res, 502, { ok: false, station_id: Number(rawId), error: lastError });
};
