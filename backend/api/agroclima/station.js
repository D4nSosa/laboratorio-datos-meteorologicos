/**
 * Backend-only AgroClima proxy for Vercel.
 * The Vercel project root is /backend, so it serves API functions only.
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

function decodeHtml(value) {
  return String(value || "")
    .replace(/<br\s*\/?\s*>/gi, " ")
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;|&#160;/gi, " ")
    .replace(/&deg;/gi, "°")
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/\s+/g, " ")
    .trim();
}

function numberOrNull(value) {
  const cleaned = String(value || "").replace(",", ".").replace(/[^\d.+-]/g, "");
  if (!cleaned || cleaned === "." || cleaned === "-") return null;
  const parsed = Number(cleaned);
  return Number.isFinite(parsed) ? parsed : null;
}

function extractCellValues(row) {
  return [...row.matchAll(/<t[dh]\b[^>]*>([\s\S]*?)<\/t[dh]>/gi)]
    .map(match => decodeHtml(match[1]));
}

function parseDateTime(value) {
  const match = String(value || "").match(/(\d{2})-(\d{2})-(\d{4})\s+(\d{2}):(\d{2})/);
  if (!match) return null;
  const [, day, month, year, hour, minute] = match;
  return {
    date: `${year}-${month}-${day}`,
    local: `${year}-${month}-${day}T${hour}:${minute}:00`
  };
}

function parseStationPage(html, stationId, sourceUrl, fetchedAt) {
  const title = decodeHtml((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || "");
  const heading = decodeHtml((html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i) || [])[1] || "");
  const location = decodeHtml((html.match(/Ubicaci[oó]n:\s*([\s\S]*?)<\/p>/i) || [])[1] || "");
  const coordinateText = decodeHtml((html.match(/Coordenadas:\s*<code[^>]*>([\s\S]*?)<\/code>/i) || [])[1] || "");
  const lastLabel = decodeHtml((html.match(/Último registro[\s\S]*?<span[^>]*>([\s\S]*?)<\/span>/i) || [])[1] || "");
  const lastDate = parseDateTime(lastLabel);

  const tables = [...html.matchAll(/<table\b[^>]*>([\s\S]*?)<\/table>/gi)].map(match => match[1]);
  let observations = [];
  for (const table of tables) {
    const rows = [...table.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)].map(match => extractCellValues(match[1])).filter(row => row.length >= 2);
    const headerIndex = rows.findIndex(row => /hora/i.test(row[0] || "") && row.some(cell => /temperatura/i.test(cell)) && row.some(cell => /humedad/i.test(cell)));
    if (headerIndex < 0) continue;
    const headers = rows[headerIndex].map(value => value.toLowerCase());
    const indexOf = pattern => headers.findIndex(value => pattern.test(value));
    const indexes = {
      time: indexOf(/^hora/),
      temperature: indexOf(/temperatura/),
      humidity: indexOf(/humedad/),
      wind: indexOf(/viento/),
      direction: indexOf(/direcci[oó]n/),
      rain: indexOf(/lluvia|precipitaci[oó]n/),
      pressure: indexOf(/presi[oó]n/),
      dewPoint: indexOf(/roc[ií]o/),
      feelsLike: indexOf(/sensaci[oó]n/)
    };
    const date = lastDate?.date || null;
    observations = rows.slice(headerIndex + 1).map(row => {
      const at = row[indexes.time] || "";
      if (!/^\d{1,2}:\d{2}$/.test(at)) return null;
      const get = key => indexes[key] >= 0 ? row[indexes[key]] : null;
      return {
        observed_time: at,
        observed_at_local: date ? `${date}T${at.padStart(5, "0")}:00` : null,
        temperature_c: numberOrNull(get("temperature")),
        humidity_pct: numberOrNull(get("humidity")),
        wind_speed_kmh: numberOrNull(get("wind")),
        wind_direction: get("direction"),
        rain_mm: numberOrNull(get("rain")),
        pressure_hpa: numberOrNull(get("pressure")),
        dew_point_c: numberOrNull(get("dewPoint")),
        feels_like_c: numberOrNull(get("feelsLike"))
      };
    }).filter(Boolean);
    if (observations.length) break;
  }

  const latest = observations.length ? observations[observations.length - 1] : null;
  const current = latest ? {
    ...latest,
    observed_at_local: lastDate?.local || latest.observed_at_local
  } : null;

  return {
    ok: true,
    provider: "AgroClima",
    station_id: stationId,
    station_name: heading.replace(/^Estación:\s*/i, "") || title.replace(/^AgroClima\s*-\s*/i, ""),
    location: location.replace(/^Ubicaci[oó]n:\s*/i, ""),
    coordinates: coordinateText || null,
    source_url: sourceUrl,
    fetched_at: fetchedAt,
    timezone: "America/Argentina/Cordoba",
    latest_observation: current,
    observation_count: observations.length,
    observations,
    // Kept temporarily for the current Pages frontend until the JSON UI is migrated.
    html
  };
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
          "User-Agent": "LaboratorioMeteorologicoNacional/1.3 (public station observation viewer)"
        }
      });
      if (!response.ok) {
        lastError = "upstream_http_" + response.status;
        continue;
      }
      const html = await response.text();
      if (!html || html.length < 250 || Buffer.byteLength(html, "utf8") > MAX_HTML_BYTES) {
        lastError = "upstream_html_invalid_or_too_large";
        continue;
      }
      const lower = html.toLowerCase();
      if (lower.includes("estacion no encontrada") || lower.includes("estación inexistente") || lower.includes("access denied")) {
        lastError = "station_not_available";
        continue;
      }
      const fetchedAt = new Date().toISOString();
      const payload = parseStationPage(html, Number(rawId), response.url || upstream.toString(), fetchedAt);
      if (!payload.observation_count) {
        return send(res, 502, {
          ok: false,
          station_id: Number(rawId),
          error: "observation_table_not_recognized",
          source_url: payload.source_url,
          fetched_at: fetchedAt
        });
      }
      return send(res, 200, payload);
    } catch (error) {
      lastError = error?.name === "TimeoutError" || error?.name === "AbortError"
        ? "upstream_timeout"
        : "upstream_fetch_failed";
    }
  }
  return send(res, 502, { ok: false, station_id: Number(rawId), error: lastError });
};
