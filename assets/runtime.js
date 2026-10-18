(()=>{
  'use strict';
  const slides=[...document.querySelectorAll('#deck > .slide')];
  if(!slides.length)return;
  const root=document.documentElement,nav=document.querySelector('.slide-nav'),dotsHost=nav.querySelector('.nav-dots');
  const prev=nav.querySelector('.nav-prev'),next=nav.querySelector('.nav-next'),counter=nav.querySelector('.nav-counter');
  const full=nav.querySelector('.nav-fullscreen'),status=document.querySelector('.deck-status');
  const mobile=matchMedia('(max-width:720px)');
  let current=0,touch=null,statusTimer;
  function announce(message){status.textContent=message;clearTimeout(statusTimer);statusTimer=setTimeout(()=>status.textContent='',3200)}
  const dots=slides.map((slide,i)=>{
    const title=slide.dataset.title||slide.querySelector('h1,h2,h3')?.textContent.trim()||`第 ${i+1} 页`;
    slide.id=slide.id||`slide-${i+1}`;
    slide.setAttribute('role','group');slide.setAttribute('aria-roledescription','幻灯片');slide.setAttribute('aria-label',`${i+1} / ${slides.length} · ${title}`);
    const dot=document.createElement('button');dot.type='button';dot.className='nav-dot';dot.title=title;dot.setAttribute('aria-label',`第 ${i+1} 页：${title}`);dot.setAttribute('aria-controls',slide.id);dot.addEventListener('click',()=>go(i));dotsHost.append(dot);return dot;
  });
  function fit(){root.style.setProperty('--deck-scale',Math.min((innerWidth-108)/1440,(innerHeight-42)/810))}
  function fromHash(){let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return 0}const found=slides.findIndex(s=>s.id===id);return found<0?0:found}
  function go(index,{writeHash=true}={}){
    const target=Math.max(0,Math.min(slides.length-1,index));
    const focusedSlide=document.activeElement?.closest('.slide');
    if(focusedSlide&&focusedSlide!==slides[target])document.activeElement.blur();
    const changed=current!==target;current=target;
    slides.forEach((slide,i)=>{const active=i===current;slide.hidden=!active;slide.inert=!active;slide.classList.toggle('is-active',active);slide.setAttribute('aria-hidden',String(!active));if(active)dots[i].setAttribute('aria-current','step');else dots[i].removeAttribute('aria-current')});
    counter.textContent=`${current+1}/${slides.length}`;prev.disabled=current===0;next.disabled=current===slides.length-1;
    if(writeHash){try{history.replaceState(null,'','#'+encodeURIComponent(slides[current].id))}catch{/* File origins may restrict history. */}}
    const dot=dots[current];
    if(mobile.matches){dotsHost.scrollTo({left:Math.max(0,dot.offsetLeft-dotsHost.clientWidth/2),behavior:'auto'});if(changed)window.scrollTo({top:0,behavior:'instant'})}
    else dotsHost.scrollTo({top:Math.max(0,dot.offsetTop-dotsHost.clientHeight/2),behavior:'auto'});
  }
  async function fullscreen(){
    const pending=setTimeout(()=>{if(!document.fullscreenElement)announce('未能进入全屏，请使用浏览器自带的全屏功能。')},1200);
    try{if(document.fullscreenElement)await document.exitFullscreen();else if(root.requestFullscreen)await root.requestFullscreen();else throw new Error('unsupported');clearTimeout(pending)}
    catch{clearTimeout(pending);announce('当前浏览器未开放全屏，可使用浏览器自身的全屏功能。')}
  }
  function interactive(target){return !!target.closest('input,textarea,select,button,a,[contenteditable="true"],.window-body,.table-wrap,[data-interactive]')}
  document.body.classList.add('deck-ready');fit();go(fromHash(),{writeHash:false});
  prev.addEventListener('click',()=>go(current-1));next.addEventListener('click',()=>go(current+1));full.addEventListener('click',fullscreen);
  document.addEventListener('fullscreenchange',()=>{full.setAttribute('aria-label',document.fullscreenElement?'退出全屏':'进入全屏');fit()});
  addEventListener('resize',fit);addEventListener('hashchange',()=>go(fromHash(),{writeHash:false}));
  document.addEventListener('keydown',event=>{
    const navKey=event.target.closest('.slide-nav')&&['ArrowRight','ArrowLeft','PageDown','PageUp','Home','End','f','F'].includes(event.key);
    if(event.defaultPrevented||event.altKey||event.ctrlKey||event.metaKey||(interactive(event.target)&&!navKey))return;
    if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();go(current+1)}
    else if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();go(current-1)}
    else if(event.key==='Home'){event.preventDefault();go(0)}
    else if(event.key==='End'){event.preventDefault();go(slides.length-1)}
    else if(event.key.toLowerCase()==='f'){event.preventDefault();fullscreen()}
  });
  document.querySelector('#deck').addEventListener('touchstart',event=>{touch=null;if(event.touches.length===1&&!interactive(event.target)){const point=event.touches[0];touch={x:point.clientX,y:point.clientY,id:point.identifier}}},{passive:true});
  document.querySelector('#deck').addEventListener('touchend',event=>{if(!touch)return;const point=[...event.changedTouches].find(p=>p.identifier===touch.id);if(!point)return;const dx=point.clientX-touch.x,dy=point.clientY-touch.y;touch=null;if(Math.abs(dx)>65&&Math.abs(dx)>Math.abs(dy)*1.5&&!getSelection()?.toString())go(current+(dx<0?1:-1))},{passive:true});
  document.querySelector('#deck').addEventListener('touchcancel',()=>{touch=null});
  async function copyText(text){
    try{if(navigator.clipboard&&isSecureContext){await navigator.clipboard.writeText(text);return true}}catch{/* Fall back on file origins or denied clipboard permissions. */}
    const field=document.createElement('textarea');field.value=text;field.style.cssText='position:fixed;left:-9999px;top:0';field.setAttribute('aria-hidden','true');document.body.append(field);field.select();let ok=false;try{ok=document.execCommand('copy')}finally{field.remove()}return ok;
  }
  document.querySelectorAll('.copy-code').forEach(button=>{
    let timer;button.addEventListener('click',async()=>{
      const code=button.closest('.window')?.querySelector('pre code');if(!code)return;
      let ok=false;try{ok=await copyText(code.textContent)}catch{/* Selection fallback below. */}
      if(ok){button.textContent='已复制';announce('代码已复制')}else{const range=document.createRange();range.selectNodeContents(code);getSelection().removeAllRanges();getSelection().addRange(range);button.textContent='请选中复制';announce('请复制已选中的代码')}
      clearTimeout(timer);timer=setTimeout(()=>button.textContent='复制',1800);
    });
  });
})();
