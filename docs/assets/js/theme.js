(()=>{'use strict';
const key='observatorio-theme';
const root=document.documentElement;
const button=document.getElementById('theme-toggle');
if(!button)return;
const valid=t=>t==='dark'||t==='light';
let initial='light';
try{const saved=localStorage.getItem(key);if(valid(saved))initial=saved;else if(valid(root.dataset.theme))initial=root.dataset.theme;}catch(_){}
function apply(theme,save){const next=valid(theme)?theme:'light';root.dataset.theme=next;root.style.colorScheme=next;button.textContent=next==='dark'?'☀ Tema claro':'◐ Tema oscuro';button.setAttribute('aria-pressed',String(next==='dark'));button.setAttribute('aria-label',next==='dark'?'Cambiar a tema claro':'Cambiar a tema oscuro');if(save){try{localStorage.setItem(key,next)}catch(_){}}}
apply(initial,false);
button.addEventListener('click',()=>apply(root.dataset.theme==='dark'?'light':'dark',true));
})();