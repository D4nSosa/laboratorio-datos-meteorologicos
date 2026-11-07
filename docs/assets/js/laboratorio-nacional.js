(() => {
'use strict';
const $=id=>document.getElementById(id), api='https://api.open-meteo.com/v1';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(v,d=1)=>Number(v).toLocaleString('es-AR',{maximumFractionDigits:d});
const status=(id,s)=>{if($(id))$(id).textContent=s;};
const csv=t=>{const a=[];let r=[],v='',q=false;for(let i=0;i<t.length;i++){let c=t[i];if(q){if(c==='"'&&t[i+1]==='"'){v+='"';i++;}else if(c==='"')q=false;else v+=c;}else if(c==='"')q=true;else if(c===','){r.push(v);v='';}else if(c==='\n'){r.push(v.replace(/\r$/,''));a.push(r);r=[];v='';}else v+=c;}if(v||r.length){r.push(v);a.push(r);}const h=a.shift()||[];return a.filter(x=>x.some(y=>y!=='')).map(x=>Object.fromEntries(h.map((k,i)=>[k,x[i]||''])));};
async function requestText(u){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);try{const r=await fetch(u,{signal:controller.signal});if(!r.ok)throw Error('HTTP '+r.status);return await r.text();}catch(e){if(e.name==='AbortError')throw Error('Tiempo de espera agotado (20 s)');throw e;}finally{clearTimeout(timer);}}
const json=async u=>{const t=await requestText(u);try{return JSON.parse(t);}catch(e){throw Error('La fuente devolvió una respuesta JSON inválida.');}};
const qs=(u,p)=>u+'?'+new URLSearchParams(p);
const latestEra5Date=()=>{const d=new Date();d.setUTCHours(0,0,0,0);d.setUTCDate(d.getUTCDate()-7);return d.toISOString().slice(0,10);};
let queryRows=[];
function table(id,rows,cols){$(id).innerHTML=rows.length?'<div class="lab-table-wrap"><table><thead><tr>'+cols.map(c=>'<th>'+esc(c[1])+'</th>').join('')+'</tr></thead><tbody>'+rows.slice(0,500).map(r=>'<tr>'+cols.map(c=>'<td>'+esc(r[c[0]]??'—')+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>':'<p class="lab-muted">Sin filas disponibles para esta consulta.</p>';}
function chart(rows){const valid=v=>v!==null&&v!==undefined&&v!==''&&Number.isFinite(Number(v));const vals=rows.map(x=>x.precipitation_mm).filter(valid).map(Number);if(!vals.length){$('national-chart').textContent='Sin valores de precipitación para graficar.';return;}const w=900,h=240,p=44,max=Math.max(...vals,1),span=max||1;const lines=[0,.25,.5,.75,1].map(t=>{let y=h-p-t*(h-2*p);return '<line x1="'+p+'" x2="'+(w-p)+'" y1="'+y+'" y2="'+y+'" stroke="currentColor" opacity=".13"/><text x="'+(p-8)+'" y="'+(y+4)+'" text-anchor="end" fill="currentColor" font-size="11">'+fmt(t*max,0)+'</text>';}).join('');const segments=[];let segment=[];rows.forEach((r,i)=>{if(valid(r.precipitation_mm)){const point=(p+i*(w-2*p)/Math.max(1,rows.length-1))+','+(h-p-Number(r.precipitation_mm)*(h-2*p)/span);segment.push(point);}else if(segment.length){segments.push(segment);segment=[];}});if(segment.length)segments.push(segment);const paths=segments.map(a=>'<polyline points="'+a.join(' ')+'" fill="none" stroke="#54c6a7" stroke-width="3"/>').join('');$('national-chart').innerHTML='<b>Precipitación diaria (mm)</b><svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Serie de precipitación diaria">'+lines+paths+'</svg><div class="lab-axis"><span>'+rows[0].date+'</span><span>'+rows[rows.length-1].date+'</span></div>';}
async function historical(){
 const lat=Number($('lab-lat').value),lon=Number($('lab-lon').value),start=$('lab-start').value,end=$('lab-end').value,source=$('lab-historical-source')?.value||'era5';
 const minDate=source==='power'?'1981-01-01':'1940-01-01',maxDate=source==='power'?latestPowerDate():latestEra5Date(),label=source==='power'?'NASA POWER':'ERA5';
 if(lat < -56||lat > -21||lon < -74||lon > -53||!start||!end||start>end||start<minDate||end>maxDate){status('lab-query-status','Coordenadas o período inválido. '+label+': desde '+minDate+' hasta '+maxDate+'.');return;}
 status('lab-query-status','Consultando '+label+'…');
 try{
  let rows=[],timezone='UTC';
  if(source==='power'){
   const params={parameters:'PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,WS10M,ALLSKY_SFC_SW_DWN',community:'AG',longitude:lon,latitude:lat,start:start.replace(/-/g,''),end:end.replace(/-/g,''),format:'JSON'};
   const d=await json(qs('https://power.larc.nasa.gov/api/temporal/daily/point',params)),p=d.properties?.parameter||{};
   const dates=Object.keys(p.PRECTOTCORR||p.T2M||{}).sort();
   const val=(key,date)=>{const n=Number(p[key]?.[date]);return Number.isFinite(n)&&n>-900?n:null;};
   rows=dates.map(date=>({date:date.slice(0,4)+'-'+date.slice(4,6)+'-'+date.slice(6,8),precipitation_mm:val('PRECTOTCORR',date),temp_media_c:val('T2M',date),temp_max_c:val('T2M_MAX',date),temp_min_c:val('T2M_MIN',date),humedad_media_pct:val('RH2M',date),nubosidad_media_pct:null,presion_media_hpa:null,punto_rocio_c:null,viento_max_kmh:val('WS10M',date),rafaga_max_kmh:null,radiacion_solar_mj_m2:val('ALLSKY_SFC_SW_DWN',date)}));
  }else{
   const d=await json(qs('https://archive-api.open-meteo.com/v1/archive',{latitude:lat,longitude:lon,start_date:start,end_date:end,daily:'precipitation_sum,temperature_2m_mean,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,cloud_cover_mean,relative_humidity_2m_mean,pressure_msl_mean,dew_point_2m_mean',timezone:'auto',models:'era5'}));timezone=d.timezone||'zona horaria del proveedor';
   rows=(d.daily.time||[]).map((date,i)=>({date,precipitation_mm:d.daily.precipitation_sum?.[i],temp_media_c:d.daily.temperature_2m_mean?.[i],temp_max_c:d.daily.temperature_2m_max?.[i],temp_min_c:d.daily.temperature_2m_min?.[i],humedad_media_pct:d.daily.relative_humidity_2m_mean?.[i],nubosidad_media_pct:d.daily.cloud_cover_mean?.[i],presion_media_hpa:d.daily.pressure_msl_mean?.[i],punto_rocio_c:d.daily.dew_point_2m_mean?.[i],viento_max_kmh:d.daily.wind_speed_10m_max?.[i],rafaga_max_kmh:d.daily.wind_gusts_10m_max?.[i],radiacion_solar_mj_m2:null}));
  }
  queryRows=rows;chart(rows);table('national-table',rows,[['date','Fecha'],['precipitation_mm','Lluvia mm'],['temp_media_c','T. media °C'],['temp_max_c','T. máx. °C'],['temp_min_c','T. mín. °C'],['humedad_media_pct','Humedad media %'],['nubosidad_media_pct','Nubosidad media %'],['presion_media_hpa','Presión media hPa'],['punto_rocio_c','Punto de rocío °C'],['viento_max_kmh','Viento máx. km/h'],['rafaga_max_kmh','Ráfaga máx. km/h'],['radiacion_solar_mj_m2','Radiación solar MJ/m²']]);
  $('lab-download').disabled=!rows.length;const missing=rows.filter(r=>r.precipitation_mm===null||r.precipitation_mm===undefined).length;
  status('lab-query-status',rows.length+' días · '+label+' · '+timezone+'. '+missing+' días sin precipitación; se conservan como ausentes. '+(source==='power'?'Estimación diaria NASA POWER en grilla de ~0,5°; no observación puntual.':'Reanálisis ERA5 en grilla; no medición puntual.'));
 }catch(e){status('lab-query-status','Consulta '+label+' fallida: '+e.message+'. Probá un período menor o la otra fuente.');}
}
function latestPowerDate(){const d=new Date();d.setUTCHours(0,0,0,0);d.setUTCDate(d.getUTCDate()-3);return d.toISOString().slice(0,10);}
async function forecast(){status('forecast-status','Consultando pronóstico…');try{const d=await json(qs(api+'/forecast',{latitude:$('lab-lat').value,longitude:$('lab-lon').value,forecast_days:16,timezone:'auto',daily:'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,cloud_cover_mean,relative_humidity_2m_mean,pressure_msl_mean',hourly:'temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,precipitation_probability,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cape'}));const rows=(d.daily.time||[]).map((date,i)=>({date:date,tmax:d.daily.temperature_2m_max?.[i],tmin:d.daily.temperature_2m_min?.[i],rain:d.daily.precipitation_sum?.[i],prob:d.daily.precipitation_probability_max?.[i],cloud:d.daily.cloud_cover_mean?.[i],humidity:d.daily.relative_humidity_2m_mean?.[i],pressure:d.daily.pressure_msl_mean?.[i],wind:d.daily.wind_speed_10m_max?.[i],gust:d.daily.wind_gusts_10m_max?.[i]}));table('forecast-table',rows,[['date','Fecha'],['tmax','Máx. °C'],['tmin','Mín. °C'],['rain','Lluvia mm'],['prob','Prob. lluvia %'],['cloud','Nubosidad media %'],['humidity','Humedad media %'],['pressure','Presión hPa'],['wind','Viento máx. km/h'],['gust','Ráfagas km/h']]);const h=(d.hourly.time||[]).slice(0,48).map((time,i)=>({time:time.replace('T',' '),temp:d.hourly.temperature_2m?.[i],humidity:d.hourly.relative_humidity_2m?.[i],dew:d.hourly.dew_point_2m?.[i],rain:d.hourly.precipitation?.[i],prob:d.hourly.precipitation_probability?.[i],cloud:d.hourly.cloud_cover?.[i],pressure:d.hourly.pressure_msl?.[i],wind:d.hourly.wind_speed_10m?.[i],direction:d.hourly.wind_direction_10m?.[i],gust:d.hourly.wind_gusts_10m?.[i],cape:d.hourly.cape?.[i]}));table('forecast-hourly-table',h,[['time','Hora local'],['temp','Temp. °C'],['humidity','Humedad %'],['dew','P. rocío °C'],['rain','Precip. mm'],['prob','Prob. lluvia %'],['cloud','Nubosidad %'],['pressure','Presión hPa'],['wind','Viento km/h'],['direction','Dirección °'],['gust','Ráfagas km/h'],['cape','CAPE J/kg']]);status('forecast-status','Pronóstico de Open-Meteo · '+(d.timezone||'zona horaria del proveedor')+' · hasta 16 días. Salida de modelo, no observación ni pronóstico oficial del SMN.');}catch(e){status('forecast-status','Pronóstico no disponible: '+e.message);}}
async function searchPlace(){const name=$('lab-place-search').value.trim();if(name.length<2){status('lab-query-status','Escribí al menos dos caracteres para buscar una localidad.');return;}status('lab-query-status','Buscando localidades en Argentina…');try{const d=await json(qs('https://geocoding-api.open-meteo.com/v1/search',{name:name,count:10,language:'es',format:'json',countryCode:'AR'}));const items=d.results||[];const select=$('lab-geocode-results');if(!items.length){select.hidden=true;status('lab-query-status','No se encontraron localidades argentinas con ese nombre.');return;}select.innerHTML=items.map((x,i)=>'<option value="'+i+'">'+esc([x.name,x.admin1,x.admin2].filter(Boolean).join(' · '))+'</option>').join('');select.hidden=false;select._items=items;select.onchange=()=>{const x=items[Number(select.value)];if(!x)return;$('lab-lat').value=Number(x.latitude).toFixed(4);$('lab-lon').value=Number(x.longitude).toFixed(4);status('lab-query-status','Ubicación seleccionada: '+[x.name,x.admin1,x.country].filter(Boolean).join(', ')+' · '+Number(x.latitude).toFixed(4)+', '+Number(x.longitude).toFixed(4)+'.');};select.value='0';select.onchange();}catch(e){status('lab-query-status','No se pudo buscar la localidad: '+e.message);}}

function initDataResearchPicker(){
  const input=$('data-place-search'),run=$('data-place-search-run'),select=$('data-place-results'),investigate=$('data-place-investigate'),note=$('data-place-status');
  if(!input||!run||!select||!investigate||!note)return;
  let chosen=null;
  const search=async()=>{
    const name=input.value.trim();
    if(name.length<2){note.textContent='Escribí al menos dos caracteres para buscar una localidad.';return;}
    run.disabled=true;note.textContent='Buscando localidades argentinas…';chosen=null;investigate.disabled=true;
    try{
      const d=await json(qs('https://geocoding-api.open-meteo.com/v1/search',{name,count:10,language:'es',format:'json',countryCode:'AR'}));
      const items=d.results||[];
      if(!items.length){select.hidden=true;note.textContent='No se encontraron localidades argentinas con ese nombre.';return;}
      select.replaceChildren(...items.map((x,i)=>new Option([x.name,x.admin1,x.admin2].filter(Boolean).join(' · '),String(i))));
      select.hidden=false;
      const choose=()=>{
        chosen=items[Number(select.value)]||null;
        investigate.disabled=!chosen;
        if(chosen)note.textContent='Localidad seleccionada: '+[chosen.name,chosen.admin1,chosen.country].filter(Boolean).join(', ')+' · '+Number(chosen.latitude).toFixed(4)+', '+Number(chosen.longitude).toFixed(4)+'. Se consultará ERA5 para la celda más próxima.';
      };
      select.onchange=choose;select.value='0';choose();
    }catch(e){note.textContent='No se pudo buscar la localidad: '+e.message;}
    finally{run.disabled=false;}
  };
  run.addEventListener('click',search);
  input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();search();}});
  select.addEventListener('change',()=>{});
  investigate.addEventListener('click',()=>{
    if(!chosen)return;
    const lat=Number(chosen.latitude),lon=Number(chosen.longitude);
    if(!Number.isFinite(lat)||!Number.isFinite(lon)||lat < -56||lat > -21||lon < -74||lon > -53){note.textContent='La localidad encontrada está fuera del área de consulta habilitada para Argentina.';return;}
    $('lab-lat').value=lat.toFixed(4);$('lab-lon').value=lon.toFixed(4);
    $('lab-place-search').value=[chosen.name,chosen.admin1].filter(Boolean).join(', ');
    status('lab-query-status','Localidad seleccionada desde Datos y metodología: '+[chosen.name,chosen.admin1,chosen.country].filter(Boolean).join(', ')+'. Preparando consulta histórica ERA5…');
    if(window.lnmActivateView)window.lnmActivateView('national-lab');
    note.textContent='Investigación iniciada para '+[chosen.name,chosen.admin1].filter(Boolean).join(', ')+'. Los resultados aparecerán en el módulo Investigación.';
    setTimeout(()=>{const button=$('lab-run');if(button)button.click();},180);
  });
}
function initGoes(){const img=$('goes-geocolor-image');if(!img)return;const source='https://cdn.star.nesdis.noaa.gov/GOES19/ABI/FD/GEOCOLOR/1808x1808.jpg';const label=$('goes-image-status');let lastRequest=0;const refresh=()=>{lastRequest=Date.now();if(label)label.textContent='Solicitando el último archivo GeoColor publicado por NOAA…';img.src=source+'?cache='+lastRequest;};img.addEventListener('load',()=>{if(label)label.textContent='Imagen descargada '+new Date(lastRequest).toLocaleString('es-AR')+'. Esta es la hora de consulta, no la hora de adquisición: consultá la marca temporal impresa en el producto NOAA.';});img.addEventListener('error',()=>{if(label)label.textContent='No se pudo cargar la imagen satelital. El archivo NOAA puede estar temporalmente no disponible.';});const button=$('goes-refresh');if(button)button.addEventListener('click',refresh);refresh();setInterval(()=>{if(!document.hidden)refresh()},10*60*1000);document.addEventListener('visibilitychange',()=>{if(!document.hidden&&Date.now()-lastRequest>10*60*1000)refresh()});}
function init(){initGoes();initDataResearchPicker();if(!$('national-lab'))return;const latest=latestEra5Date();$('lab-end').value=latest;$('lab-end').max=latest;const d=new Date(latest+'T00:00:00Z');d.setUTCDate(d.getUTCDate()-364);$('lab-start').value=d.toISOString().slice(0,10);$('lab-run').onclick=historical;$('forecast-run').onclick=forecast;$('lab-geocode-run').onclick=searchPlace;$('lab-place-search').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();searchPlace();}});$('lab-download').onclick=()=>{if(!queryRows.length)return;const k=Object.keys(queryRows[0]),q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const b=new Blob([k.map(q).join(',')+'\n'+queryRows.map(r=>k.map(x=>q(r[x])).join(',')).join('\n')],{type:'text/csv'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='consulta-laboratorio.csv';a.click();URL.revokeObjectURL(a.href);};$('lab-preset-virasoro').onclick=()=>{$('lab-lat').value='-28.05';$('lab-lon').value='-56.02';$('lab-place-search').value='Gobernador Virasoro, Corrientes';$('lab-geocode-results').hidden=true;status('lab-query-status','Referencia local: Gobernador Virasoro, Corrientes.');};}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();