// 简单 toast
function showToast(text){
  const t=document.createElement('div');
  Object.assign(t.style,{position:'fixed',bottom:'24px',left:'50%',transform:'translateX(-50%)',background:'#fff',padding:'10px 14px',border:'1px solid #e9e2f3',borderRadius:'12px',zIndex:9999});
  t.textContent=text; document.body.appendChild(t); setTimeout(()=>t.remove(),1600);
}

/* ===== Find: Add/Ignore 后移除卡片（我加别人，与通知无关） ===== */
function removeCandidateCard(id){
  const card=document.querySelector(`.card[data-id="${id}"]`);
  if(card) card.remove();
}
function sendFriendRequestAndRemove(e, id){
  e.preventDefault();
  const fd=new FormData(e.target);
  fetch('/api/friend_request',{method:'POST', body:fd})
    .then(r=>r.json()).then(d=>{ showToast(d.message||'Friend request sent.'); removeCandidateCard(id); });
  return false;
}

/* ===== Notification（别人加我） ===== */
function initNotifications(){
  const open=document.getElementById('openNotifications');
  const modal=document.getElementById('modal');
  const close=document.getElementById('closeModal');
  const clearBtn=document.getElementById('clearNotif');
  const list=document.getElementById('notifList');

  function load(){
    if(!list) return;
    fetch('/api/notifications').then(r=>r.json()).then(d=>{
      list.innerHTML='';
      if(!d.items || !d.items.length){
        const empty=document.createElement('div'); empty.className='empty'; empty.textContent='no notification';
        list.appendChild(empty); return;
      }
      d.items.forEach(n=>{
        const card=document.createElement('div'); card.className='card'; card.style.margin='8px 0';
        card.innerHTML=`<div class="name">A new friend request</div><div class="hint">${n.text}</div>`;
        const actions=document.createElement('div'); actions.className='actions';
        const acc=document.createElement('button'); acc.className='btn'; acc.textContent='Accept';
        acc.onclick=()=>{
          const fd=new FormData(); fd.append('name', n.from_name);
          fetch('/api/notif/accept',{method:'POST', body:fd}).then(r=>r.json()).then(res=>{
            if(res.ok){ showToast('Friend added to Private Chats'); load(); refreshFriendsUI && refreshFriendsUI(); }
          });
        };
        const dec=document.createElement('button'); dec.className='btn ghost'; dec.textContent='Decline';
        dec.onclick=()=>{ fetch('/api/notifications/clear',{method:'POST'}).then(()=>load()); };
        actions.appendChild(acc); actions.appendChild(dec); card.appendChild(actions); list.appendChild(card);
      });
    });
  }
  open && open.addEventListener('click',()=>{ modal.classList.remove('hidden'); load(); });
  close && close.addEventListener('click',()=>modal.classList.add('hidden'));
  clearBtn && clearBtn.addEventListener('click',()=>{ fetch('/api/notifications/clear',{method:'POST'}).then(()=>load()); });
}

/* ===== Chats：每个子页面只绑定自己有的元素 ===== */
function truncatePreview(text, n=36){
  if(!text) return '';
  text = text.replace(/\s+/g,' ').trim();
  return text.length>n ? text.slice(0,n-1)+'…' : text;
}

function bindListFor(kind, listEl, msgBox, iceBox, titleEl, leftBtn, extra){
  if(!listEl) return;
  listEl.querySelectorAll('.thread').forEach(li=>{
    // 初始化预览为最后一条
    const id=parseInt(li.dataset.id);
    const sub=li.querySelector('.t-sub');
    fetch(`/api/messages/${kind}/${id}`).then(r=>r.json()).then(d=>{
      const items=d.items||[];
      const last=items.length ? items[items.length-1].text : (sub ? sub.textContent : '');
      if(sub) sub.textContent = truncatePreview(last);
    });

    li.addEventListener('click',()=>{
      const name = li.dataset.name || li.querySelector('.t-title').textContent;
      const fresh = li.dataset.fresh === 'true';
      if(titleEl) titleEl.textContent = name;

      if(kind==='channel'){
        // Channel：进入 feed 视图（按钮在输入框上方居中）
        extra.enterWrap && (extra.enterWrap.style.display='block');
        extra.chanFeed && (extra.chanFeed.style.display='block');
        extra.chanChat && (extra.chanChat.style.display='none');
        if(leftBtn) leftBtn.textContent = '+';

        fetch(`/api/channel/feed/${id}`).then(r=>r.json()).then(d=>{
          const feed=d.items||[];
          extra.chanFeed.innerHTML='';
          feed.forEach(it=>{
            const div=document.createElement('div'); div.className='msg from';
            div.textContent = `${it.author}: ${it.text}`;
            extra.chanFeed.appendChild(div);
          });
        });

        // 进入社区聊天
        const enterBtn=document.getElementById('enterCommunity');
        if(enterBtn){
          enterBtn.onclick=()=>{
            extra.enterWrap.style.display='none';
            extra.chanFeed.style.display='none';
            extra.chanChat.style.display='block';
            if(leftBtn) leftBtn.textContent='↩';
            fetch(`/api/messages/channel/${id}`).then(r=>r.json()).then(d=>{
              renderMsgs(d.items||[], extra.chanChat);
            });
            // 左侧返回箭头
            if(leftBtn){
              leftBtn.onclick=()=>{
                extra.enterWrap.style.display='block';
                extra.chanFeed.style.display='block';
                extra.chanChat.style.display='none';
                leftBtn.textContent='+';
              };
            }
            // 发送
            extra.composer && extra.composer.addEventListener('submit', extra._chanSubmitOnce || (extra._chanSubmitOnce=(e)=>{
              e.preventDefault();
              const input=document.getElementById('msgInput');
              const text=(input.value||'').trim(); if(!text) return;
              const fd=new FormData(); fd.append('kind','channel'); fd.append('id', id); fd.append('text', text);
              fetch('/api/message/send',{method:'POST', body:fd}).then(r=>r.json()).then(()=>{
                const cur=[...extra.chanChat.querySelectorAll('.msg')].map(m=>({who:m.classList.contains('to')?'me':'them',text:m.textContent}));
                cur.push({who:'me', text}); renderMsgs(cur, extra.chanChat);
                // 更新预览
                const sub2=li.querySelector('.t-sub'); if(sub2) sub2.textContent=truncatePreview(text);
                input.value='';
              });
            }));
          };
        }
        return;
      }

      // Friend/Room：渲染聊天
      if(extra && extra.enterWrap) extra.enterWrap.style.display='none';
      if(extra && extra.chanFeed) extra.chanFeed.style.display='none';
      if(extra && extra.chanChat) extra.chanChat.style.display='none';
      if(leftBtn) leftBtn.textContent='+';

      fetch(`/api/messages/${kind}/${id}`).then(r=>r.json()).then(d=>{
        renderMsgs(d.items||[], msgBox);
        if(kind==='friend' && fresh && (!d.items || d.items.length===0)){
          iceBox && (iceBox.style.display='block');
          // ice 里的三条快捷发送
          document.querySelectorAll('.send-ice').forEach(btn=>{
            btn.onclick=()=>{
              const text=btn.dataset.text;
              const fd=new FormData(); fd.append('kind','friend'); fd.append('id', id); fd.append('text', text);
              fetch('/api/message/send',{method:'POST', body:fd}).then(()=> {
                iceBox.style.display='none';
                const cur=[...msgBox.querySelectorAll('.msg')].map(m=>({who:m.classList.contains('to')?'me':'them',text:m.textContent}));
                cur.push({who:'me', text}); renderMsgs(cur, msgBox);
                const sub2=li.querySelector('.t-sub'); if(sub2) sub2.textContent=truncatePreview(text);
              });
            };
          });
        }else{
          iceBox && (iceBox.style.display='none');
        }
      });

      // 发送消息
      if(extra && extra.composer){
        extra.composer.onsubmit=(e)=>{
          e.preventDefault();
          const input=document.getElementById('msgInput');
          const text=(input.value||'').trim(); if(!text) return;
          const fd=new FormData(); fd.append('kind', kind); fd.append('id', id); fd.append('text', text);
          fetch('/api/message/send',{method:'POST', body:fd}).then(r=>r.json()).then(()=>{
            const cur=[...msgBox.querySelectorAll('.msg')].map(m=>({who:m.classList.contains('to')?'me':'them',text:m.textContent}));
            cur.push({who:'me', text}); renderMsgs(cur, msgBox);
            const sub2=li.querySelector('.t-sub'); if(sub2) sub2.textContent=truncatePreview(text);
            input.value=''; iceBox && (iceBox.style.display='none');
          });
        };
      }
    });
  });
}

function renderMsgs(arr, targetEl){
  targetEl.innerHTML='';
  arr.forEach(m=>{
    const d=document.createElement('div');
    d.className='msg '+(m.who==='me'?'to':'from');
    d.textContent=m.text||'';
    targetEl.appendChild(d);
  });
  targetEl.scrollTop = targetEl.scrollHeight;
}

/* ===== 页面入口绑定 ===== */
window.addEventListener('DOMContentLoaded',()=>{
  initNotifications();

  // Private
  if(document.getElementById('privateList')){
    const list=document.getElementById('privateList');
    const msg = document.getElementById('messages');
    const ice = document.getElementById('icebreaker');
    const title = document.getElementById('convTitle');
    const leftBtn = document.getElementById('leftBtn');
    const composer = document.getElementById('composer');
    window.refreshFriendsUI = function(){
      fetch('/api/state/friends').then(r=>r.json()).then(d=>{
        list.innerHTML='';
        d.friends.forEach(f=>{
          const li=document.createElement('li'); li.className='thread';
          li.dataset.kind='friend'; li.dataset.id=f.id; li.dataset.name=f.name; li.dataset.fresh=f.fresh?'true':'false';
          li.innerHTML=`<div class="avatar placeholder">${f.name[0]}</div>
            <div class="meta"><div class="t-title">${f.name}</div><div class="t-sub">Start a conversation</div></div>
            <div class="t-time">now</div>`;
          list.appendChild(li);
        });
        bindListFor('friend', list, msg, ice, title, leftBtn, {composer});
      });
    };
    // 初次绑定
    bindListFor('friend', list, msg, ice, title, leftBtn, {composer});
  }

  // Rooms
  if(document.getElementById('roomList')){
    const list=document.getElementById('roomList');
    const msg = document.getElementById('messages');
    const title = document.getElementById('convTitle');
    const leftBtn = document.getElementById('leftBtn');
    const composer = document.getElementById('composer');
    bindListFor('room', list, msg, null, title, leftBtn, {composer});
  }

  // Channels
  if(document.getElementById('channelList')){
    const list=document.getElementById('channelList');
    const title = document.getElementById('convTitle');
    const leftBtn = document.getElementById('leftBtn');
    const composer = document.getElementById('composer');
    const chanFeed = document.getElementById('channelFeed');
    const enterWrap = document.getElementById('enterWrap');
    const chanChat = document.getElementById('channelChat');
    bindListFor('channel', list, null, null, title, leftBtn, {composer, chanFeed, enterWrap, chanChat});
  }
});
