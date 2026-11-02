/**
 * Public, read-only AgroClima station catalogue.
 * Vercel project root: /backend
 */
const inventory = require("../../data/agroclima/estaciones.json");

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Accept, Content-Type",
  "Access-Control-Max-Age": "86400",
  "Vary": "Origin"
};

module.exports = function handler(req, res) {
  for (const [key, value] of Object.entries(CORS)) res.setHeader(key, value);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "GET") {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    return res.status(405).send(JSON.stringify({ ok: false, error: "method_not_allowed" }));
  }

  const stations = (inventory.stations || [])
    .filter(station => Number.isInteger(Number(station.station_id)))
    .map(station => ({
      provider: station.provider || "AgroClima",
      station_id: Number(station.station_id),
      name: station.name || null,
      latitude: Number.isFinite(Number(station.latitude)) ? Number(station.latitude) : null,
      longitude: Number.isFinite(Number(station.longitude)) ? Number(station.longitude) : null,
      last_observation: station.last_observation || null,
      page_url: station.page_url || null,
      catalog_status: station.catalog_status || "page_validated",
      metadata_quality: station.metadata_quality || "partial",
      coordinate_source: station.coordinate_source || null,
      checked_at_utc: station.checked_at_utc || null
    }));

  const located = stations.filter(s => Number.isFinite(s.latitude) && Number.isFinite(s.longitude)).length;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "public, s-maxage=3600, stale-while-revalidate=86400");
  return res.status(200).send(JSON.stringify({
    ok: true,
    provider: "AgroClima",
    generated_at_utc: inventory.generated_at_utc || null,
    source_map: inventory.source_map || "https://agroclima.com/3/public/mapa.php",
    station_count: stations.length,
    stations_with_coordinates: located,
    metadata_summary: inventory.metadata_summary || null,
    limitations: inventory.limitations || [],
    stations
  }));
};
