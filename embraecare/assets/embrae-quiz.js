/* Skin quiz, ported from source/pages/skin-quiz.html by tools/build_pages.py. Edit the source and re-run. */

(function(){
var C={"cart": {"addUrl": "/cart/add.js", "cartUrl": "/cart", "variants": {"reset": "", "defend": "", "adapt": "", "protect": "", "bundle": ""}}, "questions": [{"id": "Q01", "t": "How would you describe your experience with skincare?", "h": "", "optional": false, "opt": [{"id": "Q01A", "t": "New to it. I would like some guidance.", "s": ["EXP_BEGINNER"]}, {"id": "Q01B", "t": "I know the basics.", "s": []}, {"id": "Q01C", "t": "Experienced. I know what I like.", "s": ["EXP_FAMILIAR"]}]}, {"id": "Q02", "t": "What does your routine look like right now?", "h": "", "optional": false, "opt": [{"id": "Q02A", "t": "I do not have one yet.", "s": ["ROUTINE_NONE_BASIC"]}, {"id": "Q02B", "t": "A few basic steps, now and then.", "s": ["ROUTINE_NONE_BASIC"]}, {"id": "Q02C", "t": "A few steps most days.", "s": []}, {"id": "Q02D", "t": "A multi-step routine I follow regularly.", "s": ["ROUTINE_MULTI_STEP"]}]}, {"id": "Q03", "t": "What matters most to you right now?", "h": "", "optional": false, "opt": [{"id": "Q03A", "t": "A simple routine I can stick to.", "s": ["GOAL_SIMPLE"]}, {"id": "Q03B", "t": "Skin that feels hydrated and comfortable.", "s": []}, {"id": "Q03C", "t": "Protection that lasts through my day.", "s": ["GOAL_DAILY_PROTECTION"]}, {"id": "Q03D", "t": "A complete routine.", "s": ["GOAL_COMPLETE"]}]}, {"id": "Q04", "t": "How does your skin usually feel by the afternoon?", "h": "", "optional": true, "opt": [{"id": "Q04A", "t": "Balanced and comfortable.", "s": []}, {"id": "Q04B", "t": "Oily or shiny.", "s": []}, {"id": "Q04C", "t": "Dry or tight.", "s": []}, {"id": "Q04D", "t": "Oily in some places, dry in others.", "s": []}, {"id": "Q04E", "t": "It changes a lot, or I am not sure.", "s": []}]}, {"id": "Q05", "t": "On most days, how comfortable does your skin feel?", "h": "", "optional": false, "opt": [{"id": "Q05A", "t": "Comfortable, no complaints.", "s": []}, {"id": "Q05B", "t": "Sometimes dry or tight.", "s": ["COMFORT_PRIORITY"]}, {"id": "Q05C", "t": "I would like it to feel more hydrated and comfortable.", "s": ["COMFORT_PRIORITY"]}]}, {"id": "Q06", "t": "How important is it to look after your skin barrier?", "h": "This is the outer layer of your skin that helps it hold on to moisture.", "optional": false, "opt": [{"id": "Q06A", "t": "Not a priority for me.", "s": []}, {"id": "Q06B", "t": "Somewhat important.", "s": []}, {"id": "Q06C", "t": "Very important.", "s": ["BARRIER_PRIORITY"]}]}, {"id": "Q07", "t": "Where do you spend most of your day?", "h": "", "optional": false, "opt": [{"id": "Q07A", "t": "Mostly indoors.", "s": []}, {"id": "Q07B", "t": "A mix of indoors and outdoors.", "s": []}, {"id": "Q07C", "t": "Often out and about, in heat, humidity, traffic or crowds.", "s": ["EXPOSURE_HIGH"]}]}, {"id": "Q08", "t": "How much time do you spend in the sun?", "h": "", "optional": false, "opt": [{"id": "Q08A", "t": "Very little.", "s": []}, {"id": "Q08B", "t": "Some time most days.", "s": []}, {"id": "Q08C", "t": "A lot, most days.", "s": ["SUN_OUTDOORS"]}]}, {"id": "Q09", "t": "How many steps would you like in your routine?", "h": "", "optional": false, "opt": [{"id": "Q09A", "t": "As few as possible.", "s": ["PREF_MINIMAL"]}, {"id": "Q09B", "t": "A few, nothing too long.", "s": []}, {"id": "Q09C", "t": "A complete routine, every step.", "s": ["PREF_COMPLETE"]}]}, {"id": "Q10", "t": "When you choose skincare, what matters most?", "h": "", "optional": false, "opt": [{"id": "Q10A", "t": "That it is easy to use.", "s": ["GOAL_SIMPLE"]}, {"id": "Q10B", "t": "That it covers every step.", "s": ["GOAL_COMPLETE"]}, {"id": "Q10C", "t": "That it keeps my skin hydrated and comfortable.", "s": []}, {"id": "Q10D", "t": "That it holds up through my day, outdoors and indoors.", "s": ["GOAL_DAILY_PROTECTION"]}]}], "signals": {"EXP_BEGINNER": [3, 0, 0], "ROUTINE_NONE_BASIC": [2, 0, 0], "PREF_MINIMAL": [2, 0, 0], "EXP_FAMILIAR": [0, 3, 0], "ROUTINE_MULTI_STEP": [0, 2, 0], "PREF_COMPLETE": [0, 2, 0], "EXPOSURE_HIGH": [0, 0, 2], "COMFORT_PRIORITY": [0, 0, 2], "BARRIER_PRIORITY": [0, 0, 2], "SUN_OUTDOORS": [0, 0, 1], "GOAL_DAILY_PROTECTION": [0, 0, 1], "GOAL_SIMPLE": [1, 0, 0], "GOAL_COMPLETE": [0, 1, 0]}, "results": [{"id": "start-simple", "n": 1, "head": "Your place to start", "lead": "A simple introduction to the EMBRAE System.", "body": "Three easy steps are enough to begin. Cleanse, moisturize and protect, and let it become a habit. You can add more later, when you are ready.", "steps": ["reset", "adapt", "protect"], "extra": "defend", "extra_t": "When you want to add a step later, the Urban Defense Serum goes in after cleansing and before your moisturizer.", "signals": ["EXP_BEGINNER", "ROUTINE_NONE_BASIC", "PREF_MINIMAL", "GOAL_SIMPLE"], "fallback": "Your answers point to a simple start as the easiest way to build a routine.", "cta": "Shop your three steps", "bundle": false}, {"id": "build-your-routine", "n": 2, "head": "Your EMBRAE System", "lead": "A complete four-step routine, in the order that works best.", "body": "You already know your way around skincare, so here is the full sequence: Reset, Defend, Adapt, Protect. Each step has one job, and together they make a routine that is easy to repeat every day.", "steps": ["reset", "defend", "adapt", "protect"], "extra": null, "extra_t": "", "signals": ["EXP_FAMILIAR", "ROUTINE_MULTI_STEP", "PREF_COMPLETE", "GOAL_COMPLETE"], "fallback": "Your answers point to a complete routine as a good fit.", "cta": "Shop the complete routine", "bundle": true}, {"id": "everyday-support", "n": 3, "head": "Your routine, built around everyday exposure", "lead": "Four steps for days spent out and about.", "body": "Your answers show a busy day, with time outside and a wish for skin that stays comfortable. This routine gives your skin hydration and barrier support morning and evening, and sun protection every morning.", "steps": ["reset", "defend", "adapt", "protect"], "extra": null, "extra_t": "", "signals": ["EXPOSURE_HIGH", "COMFORT_PRIORITY", "BARRIER_PRIORITY", "SUN_OUTDOORS", "GOAL_DAILY_PROTECTION"], "fallback": "Your answers point to steady everyday care as a good fit.", "cta": "Shop the complete routine", "bundle": true}], "products": {"reset": {"name": "Reset Cleanser", "label": "Reset", "role": "A daily gel cleanser that removes buildup and impurities while helping preserve skin comfort.", "when": "Morning and evening", "price": 899, "sym": "p-reset"}, "defend": {"name": "Urban Defense Serum", "label": "Defend", "role": "A daily serum that supports the skin barrier and helps skin feel hydrated, calm and balanced.", "when": "Morning and evening", "price": 1299, "sym": "p-defend"}, "adapt": {"name": "Climate Adapt Moisturizer", "label": "Adapt", "role": "A daily moisturizer that replenishes hydration and supports the skin barrier.", "when": "Morning and evening", "price": 1099, "sym": "p-adapt"}, "protect": {"name": "Daily Shield Sunscreen SPF 50 PA++++", "label": "Protect", "role": "SPF 50 PA++++ sun protection, the final step of your morning routine.", "when": "Every morning, as the last step", "price": 1199, "sym": "p-protect"}}, "reasons": {"EXP_BEGINNER": "You are new to skincare, so a few clear steps will help you build a habit.", "ROUTINE_NONE_BASIC": "You are starting from a light routine, so there is no need to change everything at once.", "PREF_MINIMAL": "You would like as few steps as possible.", "GOAL_SIMPLE": "Keeping things easy matters to you.", "EXP_FAMILIAR": "You already know your way around skincare.", "ROUTINE_MULTI_STEP": "You already follow a multi-step routine.", "PREF_COMPLETE": "You like a complete routine with every step.", "GOAL_COMPLETE": "A complete system matters to you.", "EXPOSURE_HIGH": "You spend a lot of your day out and about, in heat, humidity or traffic.", "COMFORT_PRIORITY": "You would like your skin to feel more comfortable and hydrated.", "BARRIER_PRIORITY": "Looking after your skin barrier is important to you.", "SUN_OUTDOORS": "You spend a lot of time in the sun.", "GOAL_DAILY_PROTECTION": "You want protection that lasts through your day."}, "families": {"exposure": ["EXPOSURE_HIGH"], "comfort": ["COMFORT_PRIORITY", "BARRIER_PRIORITY"], "sun": ["SUN_OUTDOORS"]}, "routineSignals": {"r1": ["EXP_BEGINNER", "ROUTINE_NONE_BASIC", "PREF_MINIMAL"], "r2": ["EXP_FAMILIAR", "ROUTINE_MULTI_STEP", "PREF_COMPLETE"]}};
/* Shopify data from sections/skin-quiz.liquid */
var X=window.EmbraeQuiz||{}, URLS=X.urls||{};
if(X.variants) C.cart.variants=X.variants;
if(X.root){ C.cart.addUrl=X.root+'cart/add.js'; C.cart.cartUrl=X.root+'cart'; }
Object.keys(X.prices||{}).forEach(function(k){ if(C.products[k]) C.products[k].price=X.prices[k]; });
var $=function(s){return document.querySelector(s)};
var qz=$('#quiz'),idx=0,ans={},sid=Math.random().toString(36).slice(2),started=false,lastResult='';
window.dataLayer=window.dataLayer||[];
function track(n,p){p=p||{};p.event=n;p.quiz_id='embrae_skin_quiz';p.session_id=sid;window.dataLayer.push(p);}
var entry=(new URLSearchParams(location.search)).get('entry')||'direct';
track('quiz_view',{entry_point:entry});
function show(id,noscroll){['#qz-qs','#qz-res'].forEach(function(s){$(s).classList.toggle('on',s===id)});if(!noscroll){var t=$('.qcard').getBoundingClientRect().top+window.pageYOffset-96;if(Math.abs(window.pageYOffset-t)>40)window.scrollTo({top:Math.max(0,t),behavior:'smooth'});}}
function render(){
  var q=C.questions[idx];
  $('#qz-count').textContent='Question '+(idx+1)+' of '+C.questions.length;
  $('#qz-fill').style.width=(idx/C.questions.length*100)+'%';
  $('#qz-pg').setAttribute('aria-valuenow',idx);
  $('#qz-qt').textContent=q.t; $('#qz-qh').textContent=q.h||''; $('#qz-qh').style.display=q.h?'block':'none';
  $('#qz-need').textContent='';
  $('#qz-back').hidden=idx===0; $('#qz-skip').hidden=!q.optional;
  var box=$('#qz-opts'); box.innerHTML='';
  q.opt.forEach(function(o){
    var l=document.createElement('label'); l.className='qz-opt';
    var i=document.createElement('input'); i.type='radio'; i.name='qz'; i.value=o.id; if(ans[q.id]===o.id) i.checked=true;
    var d=document.createElement('span'); d.className='dot'; var t=document.createElement('span'); t.textContent=o.t;
    l.appendChild(i);l.appendChild(d);l.appendChild(t); box.appendChild(l);
    i.addEventListener('click',function(e){ if(!started){ started=true; track('quiz_start',{entry_point:entry}); } ans[q.id]=o.id; track('quiz_answer',{question_id:q.id,answer_id:o.id}); $('#qz-need').textContent=''; if(e.detail>0){ setTimeout(next,260); } });
  });
  track('quiz_question_view',{question_id:q.id,question_index:idx+1});
}
function next(){
  var q=C.questions[idx];
  if(!ans[q.id] && !q.optional){ $('#qz-need').textContent='Please choose an answer to continue.'; return; }
  if(idx<C.questions.length-1){ idx++; render(); } else { finish(); }
}
function sig(){ var s=[]; C.questions.forEach(function(q){ var a=ans[q.id]; if(!a) return; q.opt.forEach(function(o){ if(o.id===a) o.s.forEach(function(x){ s.push(x); }); }); }); return s; }
function sc(s,list){ var t=0; s.forEach(function(x){ if(!list||list.indexOf(x)>-1) t+=0; }); return t; }
function pts(s,k){ return s.reduce(function(a,x){ return a+C.signals[x][k]; },0); }
function sub(s,list,k){ return s.filter(function(x){ return list.indexOf(x)>-1; }).reduce(function(a,x){ return a+C.signals[x][k]; },0); }
function decide(s){
  var sc=[pts(s,0),pts(s,1),pts(s,2)];
  var fam=0; for(var f in C.families){ if(s.some(function(x){ return C.families[f].indexOf(x)>-1; })) fam++; }
  var el=[true,true,fam>=2];
  var best=-1; el.forEach(function(e,k){ if(e&&sc[k]>best) best=sc[k]; });
  var tied=[]; el.forEach(function(e,k){ if(e&&sc[k]===best) tied.push(k); });
  if(tied.length===1) return tied[0];
  if(tied.indexOf(2)>-1) return 2;
  var a=sub(s,C.routineSignals.r1,0), b=sub(s,C.routineSignals.r2,1);
  if(a>b) return 0; if(b>a) return 1; return 0;
}
var money=function(n){ return '\u20B9'+n.toLocaleString('en-IN'); };
function cart(keys,rid,pid){
  var msg=$('#qz-cartmsg'), ids=keys.map(function(k){ return C.cart.variants[k]; });
  track('quiz_add_to_cart',{result_id:rid,product_id:pid});
  if(ids.some(function(x){ return !x; })){ msg.textContent='Preview only: add the Shopify variant IDs in the quiz settings to turn on Add to cart.'; return; }
  msg.textContent='Adding to your cart...';
  fetch(C.cart.addUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({items:ids.map(function(id){ return {id:Number(id),quantity:1}; })})})
   .then(function(res){ if(!res.ok) throw 0; return res.json(); })
   .then(function(){ msg.innerHTML='Added to your cart. <a href="'+C.cart.cartUrl+'">View cart</a>'; if(window.EmbraeCart) EmbraeCart.refresh().then(function(){ EmbraeCart.open(); }); })
   .catch(function(){ msg.textContent='Sorry, we could not add that to your cart. Please try again.'; });
}
function finish(){
  $('#qz-fill').style.width='100%';
  track('quiz_complete',{});
  var s=sig(), r=C.results[decide(s)]; lastResult=r.id;
  var why=[]; r.signals.forEach(function(x){ if(s.indexOf(x)>-1 && why.length<3) why.push(C.reasons[x]); });
  if(!why.length) why.push(r.fallback);
  var h='<div class="qr-head"><p class="eyebrow">Your result</p><h1 class="h1">'+r.head+'</h1><p class="lead">'+r.lead+'</p></div>';
  h+='<p class="qr-body">'+r.body+'</p>';
  h+='<div class="qr-why"><h2>Why this suits you</h2><ul>'+why.map(function(w){ return '<li>'+w+'</li>'; }).join('')+'</ul></div>';
  var total=0; h+='<div class="qr-list">';
  r.steps.forEach(function(k,i){ var p=C.products[k]; total+=p.price; h+=row(p,'Step '+(i+1)+' '+p.label,false,k,i); });
  if(r.extra){ var e=C.products[r.extra]; h+='<div class="qr-row opt"><svg viewBox="0 0 220 320" aria-hidden="true"><use href="#'+e.sym+'"/></svg><div><small>Add later</small><b>'+e.name+'</b><p>'+r.extra_t+'</p><a class="lk" href="'+URLS[r.extra]+'" data-p="'+r.extra+'" data-pos="'+(r.steps.length+1)+'">View product</a></div>'+act(r.extra,e)+'</div>'; }
  h+='</div>';
  h+='<div class="qr-cta"><button class="btn" type="button" id="qz-cta">'+r.cta+'</button>';
  if(r.bundle) h+='<p class="sub">All four steps plus a free travel pouch: '+money(X.bundlePrice)+' instead of '+money(X.bundleValue)+'.</p>';
  else h+='<p class="sub">The three steps together: '+money(total)+'.</p>';
  h+='<p class="qr-msg" id="qz-cartmsg" role="status"></p></div><p class="qr-fine">This is a routine suggestion based on your answers, not a medical assessment. If you have a skin condition or concern, please speak to a doctor. We suggest a patch test before you use any new product.</p>';
  h+='<p class="qr-retake"><button class="qz-retake" type="button" id="qz-retake">Retake the quiz</button></p>';
  $('#qz-res').innerHTML=h; show('#qz-res');
  track('quiz_result_view',{result_id:r.id});
  $('#qz-res').onclick=function(e){
    var a=e.target.closest('a[data-p]'); if(a){ track('quiz_product_click',{result_id:r.id,product_id:a.getAttribute('data-p'),position:a.getAttribute('data-pos')||0}); return; }
    var add=e.target.closest('[data-add]'); if(add){ cart([add.getAttribute('data-add')],r.id,add.getAttribute('data-add')); return; }
    if(e.target.closest('#qz-cta')){ cart(r.bundle?['bundle']:r.steps,r.id,r.bundle?'bundle':'routine'); }
  };
  $('#qz-retake').addEventListener('click',function(){ track('quiz_restart',{previous_result_id:lastResult}); ans={}; idx=0; started=false; show('#qz-qs'); render(); });
}
function act(k,p){ return '<div class="qr-act"><span class="qpr">'+money(p.price)+'</span><button class="qr-add" type="button" data-add="'+k+'">Add to cart</button></div>'; }
function row(p,lab,o,k,i){ return '<div class="qr-row"><svg viewBox="0 0 220 320" aria-hidden="true"><use href="#'+p.sym+'"/></svg><div><small>'+lab+'</small><b>'+p.name+'</b><p>'+p.role+'</p><em>'+p.when+'</em><a class="lk" href="'+URLS[k]+'" data-p="'+k+'" data-pos="'+(i+1)+'">View product</a></div>'+act(k,p)+'</div>'; }
render();
$('#qz-back').addEventListener('click',function(){ if(idx>0){ idx--; render(); } });
$('#qz-next').addEventListener('click',next);
$('#qz-skip').addEventListener('click',function(){ var q=C.questions[idx]; delete ans[q.id]; if(idx<C.questions.length-1){ idx++; render(); } else finish(); });
document.addEventListener('keydown',function(e){ if(e.key==='Tab'||e.key.indexOf('Arrow')===0||e.key===' ') qz.classList.add('kb'); });
document.addEventListener('pointerdown',function(){ qz.classList.remove('kb'); });
window.EMBRAE_QUIZ_CONFIG=C;
})();
