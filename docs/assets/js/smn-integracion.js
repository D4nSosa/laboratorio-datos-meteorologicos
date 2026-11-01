(() => {
'use strict';
const $=id=>document.getElementById(id);
const ROOT='https://w2b.smn.gov.ar/oapi/collections/';
const COLLECTIONS={synop:'urn:wmo:md:ar-smn:slt0ci',auto:'urn:wmo:md:ar-smn:autosmn'};
const ARCHIVE='https://archive-api.open-meteo.com/v1/archive';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(v,n=1)=>Number(v).toLocaleString('es-AR',{maximumFractionDigits:n});
const isoDay=v=>String(v||'').slice(0,10);
const parseDate=v=>{const d=new Date(v);return Number.isNaN(+d)?'—':d.toLocaleString('es-AR',{timeZone:'UTC',dateStyle:'short',timeStyle:'short'})+' UTC';};
async function get(url){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);try{const r=await fetch(url,{headers:{Accept:'application/geo+json, application/json'},signal:controller.signal});const body=await r.text();if(!r.ok)throw Error('HTTP '+r.status+(body?' · '+body.slice(0,180):''));try{return JSON.parse(body);}catch(e){throw Error('La API devolvió una respuesta que no es JSON válido.');}}catch(e){if(e.name==='AbortError')throw Error('Tiempo de espera agotado (20 s)');throw e;}finally{clearTimeout(timer);}}
function feats(d){return d.features||d.items||[];}
function props(f){return f.properties||f;}
function prop(p,k){return p[k]??p[k.toLowerCase()]??null;}
function stationId(p){return prop(p,'wigos_station_identifier')||prop(p,'id')||'';}
function stationName(p){return prop(p,'name')||prop(p,'station_name')||stationId(p)||'Estación SMN';}
function collectionUrl(collection,params){return ROOT+encodeURIComponent(collection)+'/items?'+new URLSearchParams(params);}
const sampleCache=new Map();
function sampleCollection(collection){if(!sampleCache.has(collection))sampleCache.set(collection,get(collectionUrl(collection,{f:'json',limit:'500',sortby:'-reportTime'})));return sampleCache.get(collection);}
function reportTable(id,features){
 const rows=features.map(f=>props(f));
 if(!rows.length){$(id).innerHTML='<p class="lab-muted">Sin reportes devueltos por el servicio para esta consulta.</p>';return;}
 $(id).innerHTML='<div class="lab-table-wrap"><table><thead><tr><th>Fecha UTC</th><th>Estación WIGOS</th><th>Variable</th><th>Valor</th><th>Unidad</th><th>Descripción</th></tr></thead><tbody>'+rows.slice(0,30).map(p=>'<tr><td>'+esc(parseDate(p.phenomenonTime||p.reportTime))+'</td><td>'+esc(p.wigos_station_identifier||'—')+'</td><td>'+esc(p.name||'—')+'</td><td>'+esc(p.value??'—')+'</td><td>'+esc(p.units||'—')+'</td><td>'+esc(p.description||'—')+'</td></tr>').join('')+'</tbody></table></div>';
}
let smnMap,smnLayer,smnStations=[],comparisonRows=[];
async function loadStations(){
 const status=$('smn-station-status');status.textContent='Consultando las estaciones publicadas en WIS2…';
 try{
  const d=await get(collectionUrl('stations',{f:'json',limit:'250'}));
  const fs=feats(d);
  smnStations=fs.map(f=>{const p=props(f),c=f.geometry?.coordinates||[];return {id:stationId(p),name:stationName(p),status:p.status||'—',lat:Number(c[1]),lon:Number(c[0]),props:p};}).filter(s=>s.id);
  const mapped=smnStations.filter(s=>Number.isFinite(s.lat)&&Number.isFinite(s.lon)&&s.lat>=-60&&s.lat<=-20&&s.lon>=-75&&s.lon<=-52);
  $('smn-station-count').textContent=smnStations.length+' estaciones en catálogo';
  const select=$('smn-compare-station');
  select.innerHTML='<option value="">Seleccioná una estación…</option>'+smnStations.slice().sort((a,b)=>a.name.localeCompare(b.name,'es')).map(s=>'<option value="'+esc(s.id)+'">'+esc(s.name)+' · '+esc(s.id)+'</option>').join('');
  const vir=mapped.find(s=>/GOBERNADOR VIRASORO/i.test(s.name))||mapped.slice().sort((a,b)=>Math.hypot(a.lat+28.05,a.lon+56.02)-Math.hypot(b.lat+28.05,b.lon+56.02))[0];
  if(vir)select.value=vir.id;
  if(window.L&&$('smn-map')){
   if(!smnMap){smnMap=L.map('smn-map').setView([-38.5,-63.6],4);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(smnMap);}
   if(smnLayer)smnMap.removeLayer(smnLayer);
   smnLayer=L.layerGroup(mapped.map(s=>L.circleMarker([s.lat,s.lon],{radius:5,color:'#397dc1',fillOpacity:.78}).bindPopup('<b>'+esc(s.name)+'</b><br>WIGOS: '+esc(s.id)+'<br>Estado de catálogo: '+esc(s.status)))).addTo(smnMap);
   setTimeout(()=>smnMap.invalidateSize(),120);
  }
  status.textContent=smnStations.length+' estaciones devueltas por el catálogo; '+mapped.length+' con coordenadas dentro del territorio continental argentino. El estado del catálogo no certifica transmisión activa.';
 }catch(e){$('smn-station-count').textContent='No disponible';status.textContent='No se pudo consultar el catálogo WIS2: '+e.message;}
}
async function latestReports(collection){
 const d=await sampleCollection(collection);
 return feats(d).filter(f=>/air_temperature|temperature/i.test(String(props(f).name||''))).sort((a,b)=>String(props(b).reportTime||props(b).phenomenonTime||'').localeCompare(String(props(a).reportTime||props(a).phenomenonTime||''))).slice(0,30);
}
async function loadLatest(){
 const s=$('smn-station-status');
 const results=await Promise.allSettled([latestReports(COLLECTIONS.synop),latestReports(COLLECTIONS.auto)]);
 if(results[0].status==='fulfilled')reportTable('smn-synop-table',results[0].value);else $('smn-synop-table').innerHTML='<p class="lab-muted">Consulta no disponible: '+esc(results[0].reason.message)+'</p>';
 if(results[1].status==='fulfilled')reportTable('smn-auto-table',results[1].value);else $('smn-auto-table').innerHTML='<p class="lab-muted">Consulta no disponible: '+esc(results[1].reason.message)+'</p>';
 const times=results.flatMap(x=>x.status==='fulfilled'?x.value.map(f=>props(f).phenomenonTime||props(f).reportTime).filter(Boolean):[]).sort();
 if(times.length&&!$('smn-compare-end').value){
  const end=isoDay(times[times.length-1]),d=new Date(end+'T00:00:00Z');d.setUTCDate(d.getUTCDate()-13);
  $('smn-compare-end').value=end;$('smn-compare-start').value=d.toISOString().slice(0,10);
 }
 const counts=results.map(x=>x.status==='fulfilled'?x.value.length:0);
 s.textContent+=' Últimos reportes de temperatura consultados: '+counts[0]+' sinópticos y '+counts[1]+' automáticos. La fecha real de cada registro se muestra en las tablas.';
}
async function getStationTemperature(collection,id,start,end){
 const params={f:'json',limit:'1000',sortby:'reportTime',wigos_station_identifier:id,name:'air_temperature',datetime:start+'/'+end};
 const out=[];let offset=0;
 for(let page=0;page<5;page++){
  params.startindex=String(offset);
  const d=await get(collectionUrl(collection,params)),fs=feats(d);out.push(...fs);
  if(fs.length<1000)break;offset+=fs.length;
 }
 return out.map(f=>props(f)).filter(p=>p.value!==null&&p.value!==undefined&&Number.isFinite(Number(p.value))&&p.phenomenonTime).map(p=>({time:p.phenomenonTime,date:isoDay(p.phenomenonTime),value:Number(p.value),unit:p.units||'—',name:p.name||'air_temperature',reportId:p.reportId||p.id||''})).sort((a,b)=>a.time.localeCompare(b.time));
}
function dailyMean(rows){const m=new Map();rows.forEach(r=>{if(!m.has(r.date))m.set(r.date,[]);m.get(r.date).push(r.value);});return new Map([...m].map(([d,v])=>[d,v.reduce((a,b)=>a+b,0)/v.length]));}
async function getReanalysis(lat,lon,start,end,model){
 const url='https://archive-api.open-meteo.com/v1/archive?'+new URLSearchParams({latitude:String(lat),longitude:String(lon),start_date:start,end_date:end,daily:'temperature_2m_mean',timezone:'UTC',models:model});
 const d=await get(url);return new Map((d.daily?.time||[]).map((date,i)=>[date,d.daily.temperature_2m_mean?.[i]]));
}
function drawComparison(rows){
 if(!rows.length){$('smn-compare-chart').innerHTML='<p class="lab-muted">No hay días coincidentes para graficar.</p>';return;}
 const series=[['smn','SMN · promedio de reportes'],['era5','ERA5'],['era5_land','ERA5-Land']];
 const vals=rows.flatMap(r=>series.map(s=>r[s[0]])).filter(v=>Number.isFinite(v));
 if(!vals.length){$('smn-compare-chart').innerHTML='';return;}
 const lo=Math.floor(Math.min(...vals)-1),hi=Math.ceil(Math.max(...vals)+1),span=Math.max(1,hi-lo),W=1000,H=330,L=62,R=20,T=24,B=48;
 const x=i=>L+i*(W-L-R)/Math.max(1,rows.length-1),y=v=>T+(hi-v)*(H-T-B)/span;
 let svg='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Comparación de temperatura diaria SMN, ERA5 y ERA5-Land">';
 for(let k=0;k<=4;k++){const v=lo+(hi-lo)*k/4,yy=y(v);svg+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+yy+'" y2="'+yy+'" stroke="currentColor" opacity=".15"/><text x="'+(L-9)+'" y="'+(yy+4)+'" fill="currentColor" font-size="11" text-anchor="end">'+fmt(v,0)+'°</text>';}
 series.forEach((s,j)=>{const points=rows.map((r,i)=>Number.isFinite(r[s[0]])?x(i)+','+y(r[s[0]]):null).filter(Boolean).join(' ');svg+='<polyline points="'+points+'" fill="none" stroke="'+['#f0b35b','#54c6a7','#80aee8'][j]+'" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>';});
 [0,Math.floor((rows.length-1)/2),rows.length-1].forEach(i=>{if(i>=0)svg+='<text x="'+x(i)+'" y="'+(H-15)+'" fill="currentColor" font-size="11" text-anchor="middle">'+rows[i].date+'</text>';});
 svg+='</svg><div class="lab-legend">'+series.map((s,j)=>'<span><i style="background:'+['#f0b35b','#54c6a7','#80aee8'][j]+'"></i>'+s[1]+'</span>').join('')+'</div>';
 $('smn-compare-chart').innerHTML=svg;
}
function renderComparison(rows,obsCount){
 comparisonRows=rows;
 const n=rows.length,smnN=rows.filter(r=>Number.isFinite(r.smn)).length,eraN=rows.filter(r=>Number.isFinite(r.era5)).length,landN=rows.filter(r=>Number.isFinite(r.era5_land)).length;
 $('smn-compare-summary').textContent='Días del período: '+n+' · días con observación SMN: '+smnN+' · ERA5: '+eraN+' · ERA5-Land: '+landN+'. SMN: '+obsCount+' reportes individuales agrupados como promedio diario.';
 drawComparison(rows);
 $('smn-compare-table').innerHTML=n?'<table><thead><tr><th>Fecha UTC</th><th>SMN · media de reportes °C</th><th>N reportes</th><th>ERA5 °C</th><th>ERA5-Land °C</th></tr></thead><tbody>'+rows.map(r=>'<tr><td>'+r.date+'</td><td>'+ (Number.isFinite(r.smn)?fmt(r.smn,2):'—')+'</td><td>'+r.smn_count+'</td><td>'+(Number.isFinite(r.era5)?fmt(r.era5,2):'—')+'</td><td>'+(Number.isFinite(r.era5_land)?fmt(r.era5_land,2):'—')+'</td></tr>').join('')+'</tbody></table>':'<p class="lab-muted">No se encontraron fechas coincidentes. Revisá estación y período.</p>';
 $('smn-compare-download').disabled=!n;
}
async function compare(){
 const id=$('smn-compare-station').value,start=$('smn-compare-start').value,end=$('smn-compare-end').value,network=$('smn-compare-network').value;
 const status=$('smn-compare-status');
 if(!id||!start||!end||start>end){status.textContent='Seleccioná estación y un rango de fechas válido.';return;}
 const station=smnStations.find(s=>s.id===id);
 if(!station||!Number.isFinite(station.lat)||!Number.isFinite(station.lon)){status.textContent='La estación no tiene coordenadas válidas para consultar ERA5.';return;}
 if((Date.parse(end)-Date.parse(start))/86400000>366){status.textContent='Para mantener una comparación ágil, limitá el período a un año.';return;}
 status.textContent='Consultando observaciones SMN para '+station.name+'…';
 $('smn-compare-summary').textContent='Descargando reportes y reanálisis…';$('smn-compare-chart').innerHTML='';$('smn-compare-table').innerHTML='';
 try{
  const [obs,era5,land]=await Promise.all([
   getStationTemperature(COLLECTIONS[network],id,start,end),
   getReanalysis(station.lat,station.lon,start,end,'era5'),
   getReanalysis(station.lat,station.lon,start,end,'era5_land')
  ]);
  const smn=dailyMean(obs),dates=new Set([...smn.keys(),...era5.keys(),...land.keys()]);
  const rows=[...dates].sort().map(date=>({date,smn:smn.get(date),smn_count:obs.filter(o=>o.date===date).length,era5:era5.get(date),era5_land:land.get(date)}));
  renderComparison(rows,obs.length);
  status.textContent=station.name+' · '+network+' · '+obs.length+' reportes de temperatura SMN. Coordenadas de estación: '+station.lat.toFixed(4)+', '+station.lon.toFixed(4)+'.';
 }catch(e){status.textContent='La comparación no pudo completarse: '+e.message+'. El catálogo, la API de observaciones o el servicio de reanálisis puede estar temporalmente inaccesible.';}
}

let variableRecords=[];
function discoverVariables(){
 const status=$('smn-variable-status');
 Promise.all([
  sampleCollection(COLLECTIONS.synop),
  sampleCollection(COLLECTIONS.auto)
 ]).then(([syn,aut])=>{
  const names=[...new Set([...feats(syn),...feats(aut)].map(f=>props(f).name).filter(Boolean))].sort();
  $('smn-variable-name').innerHTML='<option value="">Seleccioná una variable…</option>'+names.map(n=>'<option value="'+esc(n)+'">'+esc(n)+'</option>').join('');
  $('smn-variable-station').innerHTML='<option value="">Todas las estaciones</option>'+smnStations.slice().sort((a,b)=>a.name.localeCompare(b.name,'es')).map(s=>'<option value="'+esc(s.id)+'">'+esc(s.name)+' · '+esc(s.id)+'</option>').join('');
  const end=new Date();end.setUTCDate(end.getUTCDate()-1);const start=new Date(end);start.setUTCDate(start.getUTCDate()-6);
  $('smn-variable-end').value=end.toISOString().slice(0,10);
  $('smn-variable-start').value=start.toISOString().slice(0,10);
  status.textContent=names.length+' variables encontradas en una muestra de hasta 500 registros recientes por red. El catálogo no es exhaustivo.';
 }).catch(e=>{status.textContent='No se pudo descubrir la muestra de variables: '+e.message;});
}
async function exploreVariable(){
 const name=$('smn-variable-name').value,network=$('smn-variable-network').value,id=$('smn-variable-station').value,start=$('smn-variable-start').value,end=$('smn-variable-end').value;
 const status=$('smn-variable-status');
 if(!name||!start||!end||start>end){status.textContent='Seleccioná una variable y un rango válido.';return;}
 if((Date.parse(end)-Date.parse(start))/86400000>31){status.textContent='Limitá la consulta a 31 días.';return;}
 status.textContent='Consultando '+name+'…';
 $('smn-variable-table').innerHTML='';$('smn-variable-summary').textContent='';
 try{
  const params={f:'json',limit:'1000',sortby:'-reportTime',name,datetime:start+'/'+end};
  if(id)params.wigos_station_identifier=id;
  const d=await get(collectionUrl(COLLECTIONS[network],params));
  variableRecords=feats(d).map(f=>props(f)).filter(p=>p.value!==null&&p.value!==undefined).map(p=>({
   time:p.phenomenonTime||p.reportTime||'',station:p.wigos_station_identifier||'',
   variable:p.name||name,value:p.value,unit:p.units||'—',
   description:p.description||'',reportId:p.reportId||p.id||''
  })).sort((a,b)=>String(b.time).localeCompare(String(a.time)));
  const shown=variableRecords.slice(0,250);
  $('smn-variable-summary').textContent=variableRecords.length+' registros devueltos. La tabla muestra hasta 250; el CSV incluye todos los registros recibidos.';
  $('smn-variable-table').innerHTML=shown.length?'<div class="lab-table-wrap"><table><thead><tr><th>Fecha/hora UTC</th><th>Estación WIGOS</th><th>Variable</th><th>Valor</th><th>Unidad</th><th>Descripción</th></tr></thead><tbody>'+shown.map(r=>'<tr><td>'+esc(parseDate(r.time))+'</td><td>'+esc(r.station)+'</td><td>'+esc(r.variable)+'</td><td>'+esc(r.value)+'</td><td>'+esc(r.unit)+'</td><td>'+esc(r.description)+'</td></tr>').join('')+'</tbody></table></div>':'<p class="lab-muted">No se encontraron registros. Probá otra red, estación o período.</p>';
  $('smn-variable-download').disabled=!variableRecords.length;
  status.textContent='Consulta finalizada. No se interpolaron ni completaron valores faltantes.';
 }catch(e){variableRecords=[];$('smn-variable-download').disabled=true;status.textContent='Consulta no disponible: '+e.message;}
}
function downloadVariableCSV(){
 if(!variableRecords.length)return;
 const keys=['time','station','variable','value','unit','description','reportId'];
 const head=['fecha_hora_utc','estacion_wigos','variable','valor','unidad','descripcion','id_reporte'];
 const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 const csv=[head.map(quote).join(','),...variableRecords.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\\n');
 const a=document.createElement('a'),u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 a.href=u;a.download='observaciones-variables-smn.csv';a.click();URL.revokeObjectURL(u);
}

function alerts(){
 const s=$('smn-alert-status'),box=$('smn-alert-list');s.textContent='Consultando feed CAP oficial…';box.innerHTML='<p class="lab-muted">Cargando…</p>';
 fetch('https://ssl.smn.gob.ar/feeds/CAP/rss_alertaCAP_nuevo.xml',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.text();}).then(t=>{
  const xml=new DOMParser().parseFromString(t,'application/xml');if(xml.querySelector('parsererror'))throw Error('XML no válido');
  const items=[...xml.querySelectorAll('item')].map(n=>({title:n.querySelector('title')?.textContent||'Alerta meteorológica',description:n.querySelector('description')?.textContent||'',link:n.querySelector('link')?.textContent||'https://www.smn.gob.ar/alertas',date:n.querySelector('pubDate')?.textContent||''}));
  box.innerHTML=items.length?items.slice(0,20).map(a=>'<article class="lab-alert"><strong>'+esc(a.title)+'</strong><small>'+esc(a.date)+'</small><p>'+esc(a.description.replace(/<[^>]*>/g,' ').slice(0,420))+'</p><a href="'+esc(a.link)+'" target="_blank" rel="noopener">Abrir aviso oficial ↗</a></article>').join(''):'<p class="lab-muted">El feed no publica avisos en este momento. Confirmá en el portal oficial.</p>';
  s.textContent=items.length+' avisos devueltos por el feed CAP. Revisá vigencia y área en el documento oficial.';
 }).catch(e=>{box.innerHTML='<p class="lab-muted">No fue posible leer el feed desde este navegador ('+esc(e.message)+'). Puede estar bloqueado por CORS; esto no significa que no existan alertas.</p>';s.textContent='Feed CAP no accesible desde el navegador. Usá el portal oficial.';});
}

let rainRows=[];
function discoverRainVariables(){
 const status=$('smn-rain-status');
 Promise.all([sampleCollection(COLLECTIONS.synop),sampleCollection(COLLECTIONS.auto)]).then(([a,b])=>{
  const names=[...new Set([...feats(a),...feats(b)].map(f=>props(f).name).filter(n=>n&&/precip|rain/i.test(n)))].sort();
  $('smn-rain-variable').innerHTML='<option value="">Seleccioná variable…</option>'+names.map(n=>'<option value="'+esc(n)+'">'+esc(n)+'</option>').join('');
  $('smn-rain-station').innerHTML='<option value="">Seleccioná estación…</option>'+smnStations.slice().sort((x,y)=>x.name.localeCompare(y.name,'es')).map(s=>'<option value="'+esc(s.id)+'">'+esc(s.name)+' · '+esc(s.id)+'</option>').join('');
  const end=new Date();end.setUTCDate(end.getUTCDate()-2);const start=new Date(end);start.setUTCDate(start.getUTCDate()-29);
  $('smn-rain-start').value=start.toISOString().slice(0,10);$('smn-rain-end').value=end.toISOString().slice(0,10);
  status.textContent=names.length?names.length+' variables relacionadas con precipitación encontradas en una muestra reciente. La muestra no es exhaustiva.':'No se detectaron variables de precipitación en la muestra consultada; revisá el explorador general de variables.';
 }).catch(e=>{status.textContent='No se pudo descubrir variables de precipitación: '+e.message;});
}
async function compareRain(){
 const id=$('smn-rain-station').value,network=$('smn-rain-network').value,name=$('smn-rain-variable').value,start=$('smn-rain-start').value,end=$('smn-rain-end').value,status=$('smn-rain-status');
 if(!id||!name||!start||!end||start>end){status.textContent='Seleccioná estación, variable y un período válido.';return;}
 if((Date.parse(end)-Date.parse(start))/86400000>92){status.textContent='Limitá el período a 92 días para esta consulta.';return;}
 const station=smnStations.find(s=>s.id===id);if(!station||!Number.isFinite(station.lat)||!Number.isFinite(station.lon)){status.textContent='La estación no tiene coordenadas válidas.';return;}
 status.textContent='Consultando registros SMN y precipitación diaria ERA5…';$('smn-rain-summary').textContent='';$('smn-rain-metrics').innerHTML='';$('smn-rain-chart').innerHTML='';$('smn-rain-table').innerHTML='';
 try{
  const params={f:'json',limit:'1000',sortby:'-reportTime',wigos_station_identifier:id,name,datetime:start+'/'+end};
  const [d,era]=await Promise.all([
   get(collectionUrl(COLLECTIONS[network],params)),
   get(ARCHIVE+'?'+new URLSearchParams({latitude:String(station.lat),longitude:String(station.lon),start_date:start,end_date:end,daily:'precipitation_sum',timezone:'UTC',models:'era5',precipitation_unit:'mm'}))
  ]);
  const raw=feats(d).map(f=>props(f)).filter(p=>p.value!==null&&p.value!==undefined&&Number.isFinite(Number(p.value))&&p.phenomenonTime);
  const descriptions=[...new Set(raw.map(p=>String(p.description||'').trim()).filter(Boolean))];
  const explicitDaily=descriptions.some(x=>/(24\s*[- ]?h(?:our)?|daily|diari[oa]|24\s*horas)/i.test(x));
  const units=[...new Set(raw.map(p=>String(p.units||'').trim()).filter(Boolean))];
  if(!explicitDaily){
   rainRows=[];
   $('smn-rain-summary').textContent='Se recibieron '+raw.length+' registros SMN. Unidad(es): '+(units.join(', ')||'no informada')+'. Descripción(es): '+(descriptions.join(' | ')||'sin descripción en los registros')+'. No se calculan métricas: el registro no documenta inequívocamente una acumulación diaria/24 h. Revisá los reportes originales antes de establecer equivalencia.';
   $('smn-rain-table').innerHTML=raw.length?'<div class="lab-table-wrap"><table><thead><tr><th>Fecha/hora UTC</th><th>Valor</th><th>Unidad</th><th>Descripción</th></tr></thead><tbody>'+raw.slice(0,100).map(p=>'<tr><td>'+esc(parseDate(p.phenomenonTime))+'</td><td>'+esc(p.value)+'</td><td>'+esc(p.units||'—')+'</td><td>'+esc(p.description||'—')+'</td></tr>').join('')+'</tbody></table></div>':'<p class="lab-muted">La API no devolvió registros para esta combinación.</p>';
   $('smn-rain-download').disabled=true;status.textContent='Comparación bloqueada por definición temporal no verificada. Se conservan los datos originales sin agregarlos.';return;
  }
  const unitOK=units.length===1&&/^(mm|millimeter|millimeters|kg\s*[/]?\s*m-?2)$/i.test(units[0].replace(/²/g,'2'));
  if(!unitOK){$('smn-rain-summary').textContent='La descripción indica acumulación diaria, pero las unidades devueltas ('+(units.join(', ')||'sin unidad')+') no se reconocen como equivalentes de mm. No se calculan métricas.';status.textContent='Unidad no compatible o ambigua.';return;}
  const byDay=new Map();
  raw.forEach(p=>{const date=isoDay(p.phenomenonTime),t=String(p.phenomenonTime);const old=byDay.get(date);if(!old||t>old.time)byDay.set(date,{time:t,value:Number(p.value),unit:p.units||'mm',description:p.description||''});});
  const daily=era.daily||{},dates=daily.time||[];
  rainRows=dates.map((date,i)=>({date,smn:byDay.get(date)?.value,smn_time:byDay.get(date)?.time||'',era5:Number.isFinite(Number(daily.precipitation_sum?.[i]))?Number(daily.precipitation_sum[i]):null,smn_unit:byDay.get(date)?.unit||'',description:byDay.get(date)?.description||''}));
  const pairs=rainRows.filter(r=>Number.isFinite(r.smn)&&Number.isFinite(r.era5));
  if(pairs.length<10){$('smn-rain-metrics').textContent='Métricas no calculadas: solo '+pairs.length+' días emparejados. Se requieren al menos 10 pares para un resumen exploratorio.';}
  else{
   const dif=pairs.map(r=>r.smn-r.era5),bias=dif.reduce((a,b)=>a+b,0)/dif.length,mae=dif.reduce((a,b)=>a+Math.abs(b),0)/dif.length,rmse=Math.sqrt(dif.reduce((a,b)=>a+b*b,0)/dif.length);
   const mx=pairs.reduce((a,r)=>a+r.smn,0)/pairs.length,my=pairs.reduce((a,r)=>a+r.era5,0)/pairs.length;
   const cov=pairs.reduce((a,r)=>a+(r.smn-mx)*(r.era5-my),0),sx=Math.sqrt(pairs.reduce((a,r)=>a+(r.smn-mx)**2,0)),sy=Math.sqrt(pairs.reduce((a,r)=>a+(r.era5-my)**2,0)),corr=sx&&sy?cov/(sx*sy):null;
   $('smn-rain-metrics').innerHTML='<div class="lab-grid"><div class="lab-stat"><b>'+fmt(bias,2)+' mm</b><span>Sesgo medio (SMN − ERA5)</span></div><div class="lab-stat"><b>'+fmt(mae,2)+' mm</b><span>MAE</span></div><div class="lab-stat"><b>'+fmt(rmse,2)+' mm</b><span>RMSE</span></div><div class="lab-stat"><b>'+(corr===null?'—':fmt(corr,3))+'</b><span>Correlación de Pearson</span></div></div>';
  }
  $('smn-rain-summary').textContent=station.name+' · '+raw.length+' reportes recibidos · '+byDay.size+' días con registro diario identificado · '+pairs.length+' pares válidos de '+rainRows.length+' días del período. Se usa el último registro del día UTC cuando existe más de uno; no se suman duplicados.';
  const vals=rainRows.flatMap(r=>[r.smn,r.era5]).filter(Number.isFinite),max=Math.max(1,...vals),W=1000,H=320,L=65,R=20,T=20,B=50,slot=(W-L-R)/Math.max(1,rainRows.length),bw=Math.min(12,slot*.34);
  let svg='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Precipitación diaria SMN y ERA5 en milímetros">';
  for(let k=0;k<=4;k++){const v=max*k/4,y=T+(H-T-B)*(1-k/4);svg+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y+'" y2="'+y+'" stroke="currentColor" opacity=".15"/><text x="'+(L-8)+'" y="'+(y+4)+'" text-anchor="end" fill="currentColor" font-size="11">'+fmt(v,0)+'</text>';}
  rainRows.forEach((r,i)=>{const cx=L+(i+.5)*slot;[['smn',-bw*.65,'#54c6a7'],['era5',bw*.65,'#80aee8']].forEach(([key,off,color])=>{if(Number.isFinite(r[key])){const ht=(r[key]/max)*(H-T-B);svg+='<rect x="'+(cx+off-bw/2)+'" y="'+(H-B-ht)+'" width="'+bw+'" height="'+ht+'" fill="'+color+'"><title>'+r.date+' · '+key+' '+fmt(r[key],2)+' mm</title></rect>';}});});
  [0,Math.floor((rainRows.length-1)/2),rainRows.length-1].forEach(i=>{if(i>=0)svg+='<text x="'+(L+(i+.5)*slot)+'" y="'+(H-15)+'" fill="currentColor" font-size="11" text-anchor="middle">'+rainRows[i].date+'</text>';});
  svg+='</svg><div class="lab-legend"><span><i style="background:#54c6a7"></i>SMN</span><span><i style="background:#80aee8"></i>ERA5</span></div>';$('smn-rain-chart').innerHTML=svg;
  $('smn-rain-table').innerHTML='<div class="lab-table-wrap"><table><thead><tr><th>Fecha UTC</th><th>SMN (mm)</th><th>Hora del reporte</th><th>ERA5 (mm)</th><th>Diferencia (mm)</th></tr></thead><tbody>'+rainRows.map(r=>'<tr><td>'+r.date+'</td><td>'+(Number.isFinite(r.smn)?fmt(r.smn,2):'—')+'</td><td>'+esc(r.smn_time?parseDate(r.smn_time):'—')+'</td><td>'+(Number.isFinite(r.era5)?fmt(r.era5,2):'—')+'</td><td>'+(Number.isFinite(r.smn)&&Number.isFinite(r.era5)?fmt(r.smn-r.era5,2):'—')+'</td></tr>').join('')+'</tbody></table></div>';
  $('smn-rain-download').disabled=!rainRows.length;status.textContent='Consulta finalizada. Se compararon únicamente días UTC con unidad y duración documentadas.';
 }catch(e){rainRows=[];$('smn-rain-download').disabled=true;status.textContent='No se pudo completar la comparación: '+e.message;}
}
function downloadRainCSV(){
 if(!rainRows.length)return;
 const head=['fecha_utc','smn_mm','smn_hora_reporte_utc','era5_mm','diferencia_smn_menos_era5_mm','unidad_smn','descripcion_smn'];
 const q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 const csv=[head.map(q).join(','),...rainRows.map(r=>[r.date,r.smn,r.smn_time,r.era5,Number.isFinite(r.smn)&&Number.isFinite(r.era5)?r.smn-r.era5:'',r.smn_unit,r.description].map(q).join(','))].join('\n');
 const a=document.createElement('a'),u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.href=u;a.download='comparacion-precipitacion-smn-era5.csv';a.click();URL.revokeObjectURL(u);
}

function init(){
 if(!$('smn-map'))return;
 $('smn-refresh').addEventListener('click',()=>{sampleCache.clear();$('smn-station-count').textContent='Actualizando…';$('smn-synop-table').innerHTML='';$('smn-auto-table').innerHTML='';loadStations().then(()=>{loadLatest();discoverVariables();discoverRainVariables();});});
 $('smn-alert-refresh').addEventListener('click',alerts);
 $('smn-compare-run').addEventListener('click',compare);
 $('smn-variable-run').addEventListener('click',exploreVariable);
 $('smn-variable-download').addEventListener('click',downloadVariableCSV);
 $('smn-rain-run').addEventListener('click',compareRain);
 $('smn-rain-download').addEventListener('click',downloadRainCSV);
 $('smn-compare-download').addEventListener('click',()=>{
  if(!comparisonRows.length)return;
  const keys=['date','smn','smn_count','era5','era5_land'],head=['fecha_utc','smn_temperatura_media_reportes_c','cantidad_reportes_smn','era5_temperatura_media_c','era5_land_temperatura_media_c'];
  const q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
  const csv=[head.map(q).join(','),...comparisonRows.map(r=>keys.map(k=>q(r[k])).join(','))].join('\n');
  const a=document.createElement('a'),u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.href=u;a.download='comparacion-smn-era5-era5land.csv';a.click();URL.revokeObjectURL(u);
 });
 $('smn-compare-station').addEventListener('change',()=>{$('smn-compare-status').textContent='Estación seleccionada. Definí el período y ejecutá la comparación.';});
 loadStations().then(()=>{loadLatest();discoverVariables();discoverRainVariables();});alerts();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();