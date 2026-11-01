(() => {
'use strict';
const $=id=>document.getElementById(id);
const BASE='https://w2b.smn.gov.ar/oapi/collections/';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const date=v=>{if(!v)return '—';const d=new Date(v);return Number.isNaN(+d)?String(v):d.toLocaleString('es-AR',{dateStyle:'short',timeStyle:'short',timeZone:'UTC'})+' UTC';};
async function get(url){const r=await fetch(url,{headers:{Accept:'application/geo+json, application/json'}});if(!r.ok)throw Error('HTTP '+r.status);return r.json();}
function features(d){return d.features||d.items||d.records||[];}
function props(f){return f.properties||f;}
function first(p,keys){for(const k of keys){const v=p[k];if(v!==undefined&&v!==null&&v!=='')return v;}return '—';}
function stationName(p){return first(p,['name','station_name','stationName','wigos_station_identifier','wmo_station_id','id','identifier']);}
function table(id,rows){const cols=[['name','Estación'],['time','Fecha/hora UTC'],['temperature','Temperatura'],['precipitation','Precipitación'],['wind','Viento'],['humidity','Humedad']];if(!rows.length){$(id).innerHTML='<p class="lab-muted">El servicio no devolvió reportes en esta consulta.</p>';return;}$(id).innerHTML='<div class="lab-table-wrap"><table><thead><tr>'+cols.map(x=>'<th>'+x[1]+'</th>').join('')+'</tr></thead><tbody>'+rows.slice(0,35).map(p=>{const t=first(p,['phenomenonTime','phenomenon_time','datetime','dateTime','time','resultTime']);const v=first(p,['temperature','air_temperature','airTemperature']);const rain=first(p,['precipitation','total_precipitation','precipitation_amount']);const wind=first(p,['wind_speed','windSpeed','wind']);const hum=first(p,['relative_humidity','relativeHumidity','humidity']);return '<tr><td>'+esc(stationName(p))+'</td><td>'+esc(date(t))+'</td><td>'+esc(v)+'</td><td>'+esc(rain)+'</td><td>'+esc(wind)+'</td><td>'+esc(hum)+'</td></tr>';}).join('')+'</tbody></table></div>';}
let smnMap,smnLayer;
async function loadStations(){
 const status=$('smn-station-status');status.textContent='Consultando catálogo WIS2 del SMN…';
 try{
  const d=await get(BASE+'stations/items?f=geojson&limit=1000');
  const fs=features(d);
  const good=fs.filter(f=>Array.isArray(f.geometry?.coordinates)&&f.geometry.coordinates.length>=2&&f.geometry.coordinates.slice(0,2).every(Number.isFinite));
  $('smn-station-count').textContent=good.length+' estaciones con coordenadas';
  if(window.L&&$('smn-map')){
   if(!smnMap){smnMap=L.map('smn-map').setView([-38.5,-63.6],4);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(smnMap);}
   if(smnLayer)smnMap.removeLayer(smnLayer);
   smnLayer=L.layerGroup(good.map(f=>{const p=props(f),c=f.geometry.coordinates;return L.circleMarker([c[1],c[0]],{radius:5,color:'#397dc1',fillOpacity:.75}).bindPopup('<b>'+esc(stationName(p))+'</b><br>'+esc(first(p,['wigos_station_identifier','wmo_station_id','identifier']))+'<br>Catálogo WIS2 SMN');})).addTo(smnMap);
   setTimeout(()=>smnMap.invalidateSize(),100);
  }
  status.textContent=good.length+' estaciones con geometría válida de '+fs.length+' elementos recibidos. El catálogo no implica transmisión activa en tiempo real.';
 }catch(e){$('smn-station-count').textContent='No disponible';status.textContent='No se pudo consultar el catálogo WIS2: '+e.message+'. Consultá el catálogo oficial del SMN.';}
}
async function loadObs(collection,id){
 const d=await get(BASE+encodeURIComponent(collection)+'/items?f=json&limit=500');
 const fs=features(d);return fs.map(f=>{const p=props(f);return {...p,name:stationName(p)};});
}
async function loadObservations(){
 const s=$('smn-station-status');s.textContent='Consultando inventario y reportes publicados por WIS2…';
 const results=await Promise.allSettled([
  loadObs('urn:wmo:md:ar-smn:slt0ci','synop'),
  loadObs('urn:wmo:md:ar-smn:autosmn','auto')
 ]);
 if(results[0].status==='fulfilled')table('smn-synop-table',results[0].value);else $('smn-synop-table').innerHTML='<p class="lab-muted">Consulta fallida: '+esc(results[0].reason.message)+'</p>';
 if(results[1].status==='fulfilled')table('smn-auto-table',results[1].value);else $('smn-auto-table').innerHTML='<p class="lab-muted">Consulta fallida: '+esc(results[1].reason.message)+'</p>';
 const ok=results.filter(x=>x.status==='fulfilled').length;
 s.textContent+=' Reportes: '+(results[0].status==='fulfilled'?results[0].value.length:0)+' sinópticos y '+(results[1].status==='fulfilled'?results[1].value.length:0)+' automáticos devueltos. '+(ok?'Los campos disponibles dependen del reporte y del esquema publicado.':'No se pudieron recuperar reportes en este momento.');
}
async function alerts(){
 const s=$('smn-alert-status'),box=$('smn-alert-list');s.textContent='Consultando feed CAP oficial…';box.innerHTML='<p class="lab-muted">Cargando…</p>';
 try{
  const u='https://ssl.smn.gob.ar/feeds/CAP/rss_alertaCAP_nuevo.xml';
  const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);
  const xml=new DOMParser().parseFromString(await r.text(),'application/xml');if(xml.querySelector('parsererror'))throw Error('El feed no devolvió XML válido');
  const items=[...xml.querySelectorAll('item')].map(n=>({title:n.querySelector('title')?.textContent||'Alerta meteorológica',description:n.querySelector('description')?.textContent||'',link:n.querySelector('link')?.textContent||'https://www.smn.gob.ar/alertas',date:n.querySelector('pubDate')?.textContent||''}));
  box.innerHTML=items.length?items.slice(0,20).map(a=>'<article class="lab-alert"><strong>'+esc(a.title)+'</strong><small>'+esc(a.date)+'</small><p>'+esc(a.description.replace(/<[^>]*>/g,' ').slice(0,420))+'</p><a href="'+esc(a.link)+'" target="_blank" rel="noopener">Abrir aviso oficial ↗</a></article>').join(''):'<p class="lab-muted">El feed no publica avisos en este momento. Confirmá en el portal oficial.</p>';
  s.textContent=items.length+' avisos devueltos por el feed CAP. Revisá vigencia y área en el documento oficial.';
 }catch(e){box.innerHTML='<p class="lab-muted">No fue posible leer el feed desde este navegador ('+esc(e.message)+'). El canal puede bloquear solicitudes CORS; no significa que no existan alertas.</p>';s.textContent='Feed CAP no accesible desde el navegador. Usá el portal oficial.';}
}
function init(){if(!$('smn-map'))return;$('smn-refresh').addEventListener('click',()=>{loadStations();loadObservations();});$('smn-alert-refresh').addEventListener('click',alerts);loadStations();loadObservations();alerts();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();