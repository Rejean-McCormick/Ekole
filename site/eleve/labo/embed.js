/* Optional public embedding helper, no user data sent. */
(function(root){'use strict';
 const ID=/^[a-z0-9-]{3,48}$/;
 const LAB_BASE=new URL('./',document.currentScript?.src||location.href);
 function mount(container, options){
  if(!container||typeof container.appendChild!=='function')throw Error('Valid DOM container required');
  const id=String(options&&options.id||'');if(!ID.test(id))throw Error('Unrecognized tool id');
  const frame=document.createElement('iframe');frame.title=String(options.title||'Atelier interactif Ekole');frame.loading='lazy';frame.style.width='100%';frame.style.minHeight=String(Math.max(580,Math.min(1100,Number(options.height)||700)))+'px';frame.style.border='0';frame.referrerPolicy='no-referrer';frame.src=new URL('?outil='+encodeURIComponent(id),LAB_BASE).href;container.appendChild(frame);return frame;
 }
 root.EkoleMiniLabEmbed=Object.freeze({mount});
})(typeof window!=='undefined'?window:globalThis);
