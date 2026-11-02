/**
 * Read-only AgroClima station-page proxy for the LNM static frontend.
 *
 * Deploy with Cloudflare Workers. This is deliberately NOT an open proxy:
 * the upstream host and allowed URL paths are fixed in this file.
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

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra }
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (request.method !== "GET") return json({ ok: false, error: "method_not_allowed" }, 405);
    if (url.pathname !== "/api/agroclima/station") return json({ ok: false, error: "not_found" }, 404);

    const rawId = url.searchParams.get("id") || "";
    if (!/^\d{1,4}$/.test(rawId) || Number(rawId) < 1 || Number(rawId) > 9999) {
      return json({ ok: false, error: "invalid_station_id" }, 400);
    }

    let lastError = "station_page_unavailable";
    for (const path of PATHS) {
      const upstream = new URL(path, ORIGIN);
      upstream.searchParams.set("id", rawId);
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch(upstream.toString(), {
          method: "GET",
          redirect: "follow",
          signal: controller.signal,
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
        return json({
          ok: true,
          provider: "AgroClima",
          station_id: Number(rawId),
          source_url: response.url || upstream.toString(),
          fetched_at: new Date().toISOString(),
          html
        });
      } catch (error) {
        lastError = error && error.name === "AbortError" ? "upstream_timeout" : "upstream_fetch_failed";
      } finally {
        clearTimeout(timeout);
      }
    }
    return json({ ok: false, station_id: Number(rawId), error: lastError }, 502);
  }
};
