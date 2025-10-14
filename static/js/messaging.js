/**
 * Minimal JS for sending messages via AJAX.
 * - Prevents double-submits
 * - Adds new message to #messages-list on success (simple optimistic approach)
 */
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('message-send-form');
  if (!form) return;

  function getCookie(name) {
    const c = document.cookie.split('; ').find(x => x.startsWith(name + '='));
    return c ? decodeURIComponent(c.split('=')[1]) : null;
  }
  const csrftoken = getCookie('csrftoken');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (form.dataset.busy === '1') return;
    form.dataset.busy = '1';

    const data = new FormData(form);
    const url = form.action;
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: data,
        credentials: 'same-origin'
      });
      if (!resp.ok) {
        const text = await resp.text();
        alert('Send failed: ' + resp.status);
        console.error(text);
        return;
      }
      const json = await resp.json();
      if (json.status === 'ok') {
        const list = document.getElementById('messages-list');
        const now = new Date();
        const wrapper = document.createElement('div');
        wrapper.className = 'mb-2';
        wrapper.innerHTML = `<small class="text-muted">You • ${now.getDate()}.${now.getMonth()+1}.${now.getFullYear()} ${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}</small>
          <div class="p-2 border rounded bg-light text-end">${(new DOMParser()).parseFromString(data.get('content'), 'text/html').body.textContent}</div>`;
        list.appendChild(wrapper);
        form.reset();
        window.scrollTo(0, document.body.scrollHeight);
      } else {
        alert('Server error');
      }
    } catch (err) {
      console.error(err);
      alert('Network error');
    } finally {
      form.dataset.busy = '0';
    }
  });
});
