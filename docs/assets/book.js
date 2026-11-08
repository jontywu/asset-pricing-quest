
document.addEventListener('DOMContentLoaded',()=>{
 const menu=document.querySelector('.book-sidebar details');
 if(menu&&window.matchMedia('(max-width:900px)').matches)menu.open=false;
 const button=document.querySelector('[data-toggle-code]');
 if(button)button.addEventListener('click',()=>{const hidden=document.body.classList.toggle('book-hide-code');button.textContent=hidden?'显示代码':'隐藏代码';button.setAttribute('aria-pressed',String(hidden));});
 const bar=document.querySelector('.book-progress');
 if(bar){const update=()=>{const span=document.documentElement.scrollHeight-innerHeight;bar.style.width=(span>0?Math.min(100,scrollY/span*100):100)+'%';};addEventListener('scroll',update,{passive:true});update();}
});
