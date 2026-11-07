(() => {
'use strict';
const $ = id => document.getElementById(id);
const ROOT = 'datos/fuentes-externas/';
const STATIONS = ROOT + 'radiosondeos/igra/estaciones-argentina.csv';
const CHIRPS = ROOT + 'precipitacion/chirps-v3/argentina/puntos-diarios/';
const IMERG = ROOT + 'precipitacion/gpm-imerg/late-v07/daily-points-argentina/';
const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function parseCsv(text) {
  const rows=[]; let row=[], value='', quoted=false;
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(quoted){if(c==='"'&&text[i+1]==='"'){value+='"';i++;}else if(c==='"')quoted=false;else value+=c;}
    else if(c==='"')quoted=true;
    else if(c===','){row.push(value);value='';}
    else if(c==='\n'){row.push(value.replace(/\r$/,''));rows.push(row);row=[];value='';}
    else value+=c;
  }
  if(value||row.length){row.push(value.replace(/\r$/,''));rows.push(row);}
  const header=rows.shift()||[];
  return rows.filter(r=>r.some(v=>v!=='')).map(r=>Object.fromEntries(header.map((h,i)=>[h,r[i]||''])));
}
async function gzipText(url) {
  const response=await fetch(url,{cache:'force-cache'});
  if(!response.ok) throw new Error('HTTP '+response.status+' al leer '+url.split('/').pop());
  if(!('DecompressionStream' in window)) throw new Error('Este navegador no permite descomprimir GZIP. Descargá el CSV comprimido desde el catálogo.');
  const stream=response.body.pipeThrough(new DecompressionStream('gzip'));
  return await new Response(stream).text();
}
function status(message){const el=$('historical-data-status');if(el)el.textContent=message;}
function fmt(n,d=1){return Number(n).toLocaleString('es-AR',{maximumFractionDigits:d});}
function monthKeys(start,end){
  const out=[];const a=new Date(start+'T00:00:00Z'),b=new Date(end+'T00:00:00Z');
  let y=a.getUTCFullYear(),m=a.getUTCMonth()+1;
  while(y<b.getUTCFullYear()||(y===b.getUTCFullYear()&&m<=b.getUTCMonth()+1)){
    out.push(String(y)+'-'+String(m).padStart(2,'0'));m++;if(m===13){m=1;y++;}
  }
  return out;
}
function render(rows,source,station){
  const valid=rows.filter(r=>Number.isFinite(Number(r.value)));
  const total=valid.reduce((s,r)=>s+Number(r.value),0);
  const max=valid.reduce((a,r)=>!a||Number(r.value)>Number(a.value)?r:a,null);
  const coverage=rows.length?100*valid.length/rows.length:0;
  $('historical-data-summary').innerHTML=valid.length
    ? '<div class="historical-kpis"><div><small>Registros</small><b>'+fmt(valid.length,0)+'</b></div><div><small>Acumulado diario</small><b>'+fmt(total,1)+' mm</b></div><div><small>Máximo diario</small><b>'+fmt(max.value,2)+' mm</b><small>'+esc(max.date)+'</small></div><div><small>Valores presentes</small><b>'+fmt(coverage,1)+'%</b></div></div>'
    : '<p>No hay registros válidos para el período seleccionado.</p>';
  const points=valid.slice(-500);
  if(points.length){
    const w=900,h=220,p=42,peak=Math.max(1,...points.map(x=>Number(x.value)));
    const coords=points.map((x,i)=>(p+i*(w-2*p)/Math.max(1,points.length-1))+','+(h-p-Number(x.value)*(h-2*p)/peak)).join(' ');
    $('historical-data-chart').innerHTML='<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Serie diaria de precipitación"><line x1="'+p+'" y1="'+(h-p)+'" x2="'+(w-p)+'" y2="'+(h-p)+'" stroke="currentColor" opacity=".35"/><polyline points="'+coords+'" fill="none" stroke="#38b99b" stroke-width="2.4" stroke-linejoin="round"/><text x="'+p+'" y="18" fill="currentColor" font-size="12">'+fmt(peak,1)+' mm</text><text x="'+p+'" y="'+(h-8)+'" fill="currentColor" font-size="10">'+esc(points[0].date)+'</text><text x="'+(w-p)+'" y="'+(h-8)+'" text-anchor="end" fill="currentColor" font-size="10">'+esc(points[points.length-1].date)+'</text></svg>';
  } else $('historical-data-chart').textContent='Sin valores para graficar.';
  const columns=source==='imerg'
    ? [['date','Fecha'],['value','Estimación diaria mm'],['sum','Suma intervalos válidos mm'],['valid','Intervalos válidos'],['completeness','Completitud %']]
    : [['date','Fecha'],['value','Precipitación diaria mm'],['grid','Celda de grilla']];
  $('historical-data-table').innerHTML=rows.length
    ? '<div class="historical-table-scroll"><table><thead><tr>'+columns.map(c=>'<th>'+c[1]+'</th>').join('')+'</tr></thead><tbody>'+rows.slice(-500).reverse().map(r=>'<tr>'+columns.map(c=>'<td>'+esc(r[c[0]]==null?'—':r[c[0]])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'
    : '<p>Sin filas para mostrar.</p>';
  $('historical-data-download').disabled=!rows.length;
  $('historical-data-download').onclick=()=>{
    const header=source==='imerg'?'date,precipitation_mm_day,precipitation_sum_valid_intervals_mm,valid_half_hour_intervals,completeness_pct\n':'date,precipitation_mm_day,grid_latitude,grid_longitude\n';
    const body=rows.map(r=>source==='imerg'
      ? [r.date,r.value,r.sum,r.valid,r.completeness].join(',')
      : [r.date,r.value,r.gridLat,r.gridLon].join(',')).join('\n');
    const blob=new Blob([header+body],{type:'text/csv;charset=utf-8'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=source+'-'+station+'-serie-diaria.csv';a.click();URL.revokeObjectURL(a.href);
  };
}
async function runQuery(){
  const source=$('historical-data-source').value,station=$('historical-data-station').value;
  const start=$('historical-data-start').value,end=$('historical-data-end').value;
  if(!station){status('Seleccioná una estación.');return;}
  if(!start||!end||start>end){status('Revisá el período seleccionado.');return;}
  const keys=monthKeys(start,end);
  if(source==='imerg'&&keys.length>24){status('Para IMERG elegí un período de hasta 24 meses por consulta.');return;}
  const button=$('historical-data-run');button.disabled=true;
  $('historical-data-summary').textContent='';$('historical-data-chart').textContent='';$('historical-data-table').textContent='';
  try{
    let rows=[];
    if(source==='chirps'){
      status('Descargando una serie puntual CHIRPS para '+station+'…');
      const path=CHIRPS+'chirps-v3-final-diario-'+encodeURIComponent(station)+'.csv.gz';
      const parsed=parseCsv(await gzipText(path));
      rows=parsed.filter(r=>r.date>=start&&r.date<=end).map(r=>({
        date:r.date,value:r.precipitation_mm_day,grid:r.grid_latitude+' / '+r.grid_longitude,
        gridLat:r.grid_latitude,gridLon:r.grid_longitude
      }));
    }else{
      status('Consultando '+keys.length+' archivos mensuales IMERG Late V07…');
      const batches=[];
      for(let i=0;i<keys.length;i+=4){
        const part=keys.slice(i,i+4);
        const results=await Promise.all(part.map(async key=>{
          const path=IMERG+'imerg-late-daily-argentina-'+key+'.csv.gz';
          return parseCsv(await gzipText(path));
        }));
        batches.push(...results);
        status('IMERG: '+Math.min(i+4,keys.length)+' / '+keys.length+' meses descargados…');
      }
      rows=batches.flat().filter(r=>r.station_id===station&&r.date>=start&&r.date<=end).map(r=>({
        date:r.date,value:r.precipitation_mm_day,sum:r.precipitation_sum_valid_intervals_mm,
        valid:r.valid_half_hour_intervals,completeness:r.completeness_pct
      }));
    }
    rows.sort((a,b)=>a.date.localeCompare(b.date));
    render(rows,source,station);
    status(rows.length+' registros recuperados · '+(source==='chirps'?'CHIRPS v3 Final/rnl':'NASA GPM IMERG Late V07')+' · '+station+' · '+start+' a '+end+'.');
  }catch(error){status('No se pudo completar la consulta: '+error.message+'. Podés descargar los archivos originales desde los enlaces de fuentes.');}
  finally{button.disabled=false;}
}
async function init(){
  const station=$('historical-data-station');if(!station)return;
  try{
    const list=parseCsv(await (await fetch(STATIONS,{cache:'force-cache'})).text());
    station.replaceChildren(new Option('Elegí una estación…',''));
    list.forEach(s=>station.add(new Option(s.station_name+' · '+s.station_id+' · '+s.geographic_scope,s.station_id)));
    station.value='';
    const today=new Date().toISOString().slice(0,10);
    $('historical-data-end').value=today;
    $('historical-data-start').value='2000-01-01';
    $('historical-data-source').addEventListener('change',()=>{
      $('historical-data-start').value=$('historical-data-source').value==='chirps'?'1981-01-01':'2000-01-01';
      $('historical-data-end').value=today;
      $('historical-data-source-note').textContent=$('historical-data-source').value==='chirps'
        ? 'CHIRPS v3 Final/rnl · 0,05° · serie diaria en la celda más cercana a la estación IGRA. La desagregación diaria rnl utiliza ERA5; no es independiente de ERA5.'
        : 'IMERG Late V07 · 0,1° · estimación derivada de intervalos de 30 minutos. Se muestran suma de intervalos válidos y completitud; no es el producto oficial IMERG Daily ni IMERG Final.';
    });
    $('historical-data-run').addEventListener('click',runQuery);
    status('Catálogo de estaciones listo. Elegí fuente, estación y período para consultar los datos archivados.');
  }catch(error){status('No se pudo cargar el inventario de estaciones: '+error.message);}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();