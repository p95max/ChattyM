(function(){
  'use strict';

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  function findCountEl(btn) {
    return btn.querySelector('.likes-number') || btn.querySelector('.likes-count');
  }

  function parseCount(el) {
    if (!el) return 0;
    const txt = el.textContent.trim();
    const m = txt.match(/(-?\d+)/);
    return m ? parseInt(m[0], 10) : 0;
  }

  function setCount(el, value) {
    if (!el) return;
    el.textContent = String(value);
  }

  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.like-btn');
    if (!btn) return;
    if (btn.tagName.toLowerCase() === 'a') return;

    const postId = btn.dataset.postId;
    if (!postId) return;

    const countEl = findCountEl(btn);
    const iconEl = btn.querySelector('i');
    const wasLiked = btn.classList.contains('liked');
    const currentCount = parseCount(countEl);

    const newCount = wasLiked ? Math.max(0, currentCount - 1) : (currentCount + 1);
    btn.classList.toggle('liked', !wasLiked);
    btn.setAttribute('aria-pressed', String(!wasLiked));
    btn.title = (!wasLiked) ? 'Unlike' : 'Like';

    if (wasLiked) {
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-outline-primary');
    } else {
      btn.classList.remove('btn-outline-primary');
      btn.classList.add('btn-primary');
    }

    if (iconEl) {
      iconEl.classList.toggle('bi-heart-fill', !wasLiked);
      iconEl.classList.toggle('bi-heart', wasLiked);
    }

    setCount(countEl, newCount);

    if (!wasLiked) {
      const burst = document.createElement('div');
      burst.className = 'likes-burst';
      burst.textContent = '✨';
      document.body.appendChild(burst);
      const rect = btn.getBoundingClientRect();
      burst.style.position = 'fixed';
      burst.style.left = (rect.left + rect.width/2 - 8) + 'px';
      burst.style.top = (rect.top + rect.height/2 - 8) + 'px';
      burst.style.pointerEvents = 'none';
      burst.style.fontSize = '14px';
      burst.style.zIndex = 1200;
      burst.style.transition = 'transform .6s ease, opacity .6s ease';
      requestAnimationFrame(() => {
        burst.style.transform = 'translateY(-36px) scale(1.6)';
        burst.style.opacity = '0';
      });
      setTimeout(()=> burst.remove(), 700);
    }

    const likeUrl = btn.dataset.likeUrl || `/posts/${postId}/like/`;

    try {
      const resp = await fetch(likeUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        },
        body: JSON.stringify({}),
        credentials: 'same-origin'
      });

      if (!resp.ok) throw new Error('Network response not ok: ' + resp.status);

      const data = await resp.json();

      if (data && typeof data.likes_count !== 'undefined') {
        setCount(countEl, Number(data.likes_count));
      }
      let userLiked = null;
      if (data && typeof data.user_liked !== 'undefined') {
        userLiked = !!data.user_liked;
      } else if (data && typeof data.action === 'string') {
        userLiked = data.action === 'liked' || data.action === 'like' || data.action === 'toggled_on';
      }

      if (userLiked !== null) {
        btn.classList.toggle('liked', userLiked);
        btn.setAttribute('aria-pressed', String(userLiked));
        if (iconEl) {
          iconEl.classList.toggle('bi-heart-fill', userLiked);
          iconEl.classList.toggle('bi-heart', !userLiked);
        }
        if (userLiked) {
          btn.classList.remove('btn-outline-primary');
          btn.classList.add('btn-primary');
          btn.title = 'Unlike';
        } else {
          btn.classList.remove('btn-primary');
          btn.classList.add('btn-outline-primary');
          btn.title = 'Like';
        }
      }

    } catch (err) {
      console.error('Like request failed:', err);
      btn.classList.toggle('liked', wasLiked);
      btn.setAttribute('aria-pressed', String(wasLiked));
      if (iconEl) {
        iconEl.classList.toggle('bi-heart-fill', wasLiked);
        iconEl.classList.toggle('bi-heart', !wasLiked);
      }
      if (wasLiked) {
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-primary');
        btn.title = 'Unlike';
      } else {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
        btn.title = 'Like';
      }
      setCount(countEl, currentCount);
    }
  });
})();
