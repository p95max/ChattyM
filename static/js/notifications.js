(function(){
  function getCookie(name) {
    const m = document.cookie.split('; ').find(c => c.startsWith(name + '='));
    return m ? decodeURIComponent(m.split('=')[1]) : null;
  }
  const csrftoken = getCookie('csrftoken');

  async function fetchRecent() {
    try {
      const resp = await fetch('/notifications/recent/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin'
      });
      if (!resp.ok) return;
      const json = await resp.json();
      updateDropdown(json.items || [], json.unread_count || 0);
    } catch (e) {
      console.error('notifications fetch failed', e);
    }
  }

  function updateDropdown(items, unread_count) {
    const countEl = document.getElementById('nav-notifications-count');
    if (countEl) {
      if (unread_count > 0) {
        countEl.style.display = 'inline-block';
        countEl.textContent = String(unread_count);
      } else {
        countEl.style.display = 'none';
      }
    }
    const list = document.getElementById('notifications-list');
    if (!list) return;
    list.innerHTML = '';
    if (!items || items.length === 0) {
      list.innerHTML = '<div class="text-muted small p-2">No notifications</div>';
      return;
    }
    items.forEach(it => {
      const a = document.createElement('a');
      a.href = it.data && it.data.url ? it.data.url : '#';
      a.className = 'dropdown-item notification-item' + (it.unread ? ' fw-bold' : '');
      a.dataset.id = it.id;
      const time = new Date(it.created_at);
      a.innerHTML = `<div><small class="text-muted">${time.toLocaleString()}</small></div>
                     <div>${it.actor ? it.actor + ' ' : ''}${it.verb}</div>`;
      list.appendChild(a);
    });
  }

  // click handler to mark single notification read when clicked in dropdown
  document.addEventListener('click', async (e) => {
    const el = e.target.closest('.notification-item');
    if (!el) return;
    const id = el.dataset.id;
    if (!id) return;
    try {
      const resp = await fetch(`/notifications/mark-read/${id}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken || '',
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({})
      });
      if (!resp.ok) return;
      const json = await resp.json();
      const countEl = document.getElementById('nav-notifications-count');
      if (countEl) {
        if (json.unread_count && Number(json.unread_count) > 0) {
          countEl.style.display = 'inline-block';
          countEl.textContent = String(json.unread_count);
        } else {
          countEl.style.display = 'none';
        }
      }
      el.classList.remove('fw-bold');
    } catch (err) {
      console.error(err);
    }
  });

  // mark-all click
  document.addEventListener('click', async (e) => {
    const el = e.target.closest('#mark-all-notifications');
    if (!el) return;
    e.preventDefault();
    try {
      const resp = await fetch('/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken || '',
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({})
      });
      if (!resp.ok) return;
      document.getElementById('nav-notifications-count').style.display = 'none';
      const items = document.querySelectorAll('.notification-item.fw-bold');
      items.forEach(i => i.classList.remove('fw-bold'));
    } catch (err) {
      console.error(err);
    }
  });

  // start polling every 30s and also fetch on DOM load
  document.addEventListener('DOMContentLoaded', function(){
    fetchRecent();
    setInterval(fetchRecent, 30000);
  });
})();
